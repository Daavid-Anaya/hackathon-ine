"""Comprueba el diagnóstico territorial mediante la CLI y fuentes sintéticas."""

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/diagnose_section_types.py"
COLUMNS = "AELEC FELECCION EDOCVE EDONOM MPIOCVE MPIONOM SECCION TIPOSEC DEF DEL SEXO EDAD LN SV NV NS".split()
COUNTS = ("LN", "SV", "NV", "NS")
CHECKS = "source_integrity_before_after schema key_uniqueness_exact domains geographic_consistency accounting_identity entity_coverage totals_reconciled".split()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SectionTypeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / "data/processed/ccpc_all/2024"
        self.bundle.mkdir(parents=True)
        (self.root / "data/raw").mkdir()
        archive = self.root / "data/raw/2024.zip"
        aggregate = {}
        members = []
        with zipfile.ZipFile(archive, "w") as output:
            for state in range(1, 33):
                rows = []
                for kind, sizes in (("U", (900, 100)), ("M", (500, 500)), ("R", (100, 900))):
                    for sex in (0, 1):
                        for age, size, rate in zip((22, 50), sizes, (0.2, 0.8)):
                            row = dict(zip(COLUMNS, (2024, "02/06/2024", state, f"E{state}", 1,
                                                     "Municipio", len(rows) + 1, kind, 1, 1,
                                                     sex, age, size, int(size * rate), size - int(size * rate), 0)))
                            rows.append(row)
                            key = (f"{state:02d}", str(sex), "18-24" if age == 22 else "45-59")
                            totals = aggregate.setdefault(key, dict.fromkeys(COUNTS, 0))
                            for name in COUNTS:
                                totals[name] += row[name]
                stream = io.StringIO(newline="")
                writer = csv.DictWriter(stream, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
                member = f"{state:02d}.csv"
                output.writestr(member, stream.getvalue())
                members.append({"member": member, "entity": f"{state:02d}", "rows": len(rows)})
        table = self.bundle / "table.csv"
        records = [{"AELEC": 2024, "EDOCVE": key[0], "SEXO": key[1], "age_band": key[2], **counts,
                    **{f"age_over_110_{name}": 0 for name in COUNTS}} for key, counts in sorted(aggregate.items())]
        with table.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        self.report = {"election_year": 2024, "unit": ["EDOCVE", "SEXO", "age_band"],
                       "table_sha256": sha(table), "checks": dict.fromkeys(CHECKS, True),
                       "analytical_rows": len(records), "members": members, "source_rows": 384,
                       "analytical_totals": {name: sum(row[name] for row in records) for name in COUNTS},
                       "source": {"local_path": "data/raw/2024.zip", "bytes": archive.stat().st_size,
                                  "sha256": sha(archive)}}
        self.report_path = self.bundle / "report.json"
        self.report_path.write_text(json.dumps(self.report), encoding="utf-8")
        self.original = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def run_command(self, *arguments):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
                              capture_output=True, text=True, timeout=90,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def assert_unchanged(self):
        for path, expected in self.original.items():
            self.assertEqual(path.read_bytes(), expected)

    def test_separates_types_and_standardizes_common_composition(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "internal_diagnostic")
        folder = self.root / "outputs/section_types_2024"
        report = json.loads((folder / "report.json").read_text())
        self.assertFalse(report["publication_authorized"])
        self.assertEqual(report["source_rows"], 384)
        self.assertEqual(report["common_composition"]["strata"], 128)
        self.assertEqual(report["totals"], self.report["analytical_totals"])
        with (folder / "summary.csv").open(newline="") as stream:
            rows = {row["TIPOSEC"]: row for row in csv.DictReader(stream)}
        self.assertEqual(set(rows), {"U", "M", "R"})
        for kind, rate in (("U", 26), ("M", 50), ("R", 74)):
            self.assertAlmostEqual(float(rows[kind]["participation_pct"]), rate)
            self.assertAlmostEqual(float(rows[kind]["standardized_participation_pct"]), 50)
            self.assertAlmostEqual(float(rows[kind]["common_known_share_pct"]), 100)
        self.assert_unchanged()

    def test_reproducibility_and_no_overwrite(self):
        for name in ("first", "second"):
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        first = self.root / "outputs/first"
        second = self.root / "outputs/second"
        self.assertEqual({path.name for path in first.iterdir()}, {"summary.csv", "report.json", "README.md"})
        for path in first.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
        before = {path: path.read_bytes() for path in first.iterdir()}
        result = self.run_command("--run-name", "first")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        for path, expected in before.items():
            self.assertEqual(path.read_bytes(), expected)
        self.assert_unchanged()

    def test_changed_source_is_rejected_without_output(self):
        archive = self.root / "data/raw/2024.zip"
        with archive.open("ab") as stream:
            stream.write(b"changed")
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertFalse((self.root / "outputs/section_types_2024").exists())

    def test_unknown_participation_is_not_zero_or_imputed_common_support(self):
        archive = self.root / "data/raw/2024.zip"
        with zipfile.ZipFile(archive) as source:
            contents = {name: list(csv.DictReader(io.StringIO(source.read(name).decode())))
                        for name in source.namelist()}
        with zipfile.ZipFile(archive, "w") as output:
            for name, records in contents.items():
                for row in records:
                    if row["TIPOSEC"] == "R":
                        row.update(SV=0, NV=0, NS=row["LN"])
                stream = io.StringIO(newline="")
                writer = csv.DictWriter(stream, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(records)
                output.writestr(name, stream.getvalue())
        table = self.bundle / "table.csv"
        with table.open(newline="") as stream:
            records = list(csv.DictReader(stream))
        for row in records:
            sv, nv = (20, 80) if row["age_band"] == "18-24" else (720, 180)
            row.update(SV=int(row["SV"]) - sv, NV=int(row["NV"]) - nv, NS=sv + nv)
        with table.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        self.report.update(table_sha256=sha(table), analytical_totals={
            name: sum(int(row[name]) for row in records) for name in COUNTS})
        self.report["source"].update(sha256=sha(archive), bytes=archive.stat().st_size)
        self.report_path.write_text(json.dumps(self.report))
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        folder = self.root / "outputs/section_types_2024"
        with (folder / "summary.csv").open(newline="") as stream:
            rows = {row["TIPOSEC"]: row for row in csv.DictReader(stream)}
        self.assertEqual(rows["R"]["participation_pct"], "")
        self.assertEqual(float(rows["R"]["unspecified_pct"]), 100)
        self.assertTrue(all(row["standardized_participation_pct"] == "" for row in rows.values()))
        report = json.loads((folder / "report.json").read_text())
        self.assertEqual(report["common_composition"]["strata"], 0)


if __name__ == "__main__":
    unittest.main()
