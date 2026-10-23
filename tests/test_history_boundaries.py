"""Regresiones autónomas derivadas de las comprobaciones independientes de verificación histórica."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
YEARS = (2009, 2012, 2015, 2018, 2021, 2024)
COUNTS = ("LN", "SV", "NV", "NS")
CHECKS = ("source_integrity_before_after", "schema", "key_uniqueness_exact", "domains",
          "geographic_consistency", "accounting_identity", "entity_coverage", "totals_reconciled")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {path.relative_to(root): digest(path) for path in root.rglob("*") if path.is_file()}


def write_bundle(root, year, rows):
    folder = root / "data/processed/ccpc_all" / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = dict(election_year=year, unit=["EDOCVE", "SEXO", "age_band"],
                  checks=dict.fromkeys(CHECKS, True), analytical_rows=len(rows),
                  analytical_totals={name: sum(row[name] for row in rows) for name in COUNTS},
                  table_sha256=digest(folder / "table.csv"))
    (folder / "report.json").write_text(json.dumps(report), encoding="utf-8")


class HistoricalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for year in YEARS:
            rows = []
            for state in (1, 2):
                for group in range(6):
                    rate = 30 + 10 * group - (0 if year in (2021, 2024) else 15)
                    rows.append(dict(
                        AELEC=year, EDOCVE=str(state), SEXO=str(group // 5),
                        age_band=("18-24", "25-34", "35-44", "45-59", "60+")[group % 5],
                        LN=1000, SV=rate * 10, NV=1000 - rate * 10, NS=0,
                        **{"age_over_110_" + name: 0 for name in COUNTS},
                    ))
            # D=30 y 80% de cobertura cumplen los criterios; sus vecinos inmediatos no.
            for state, sv, nv, ns in ((3, 12, 18, 0), (4, 32, 48, 20), (5, 12, 17, 0),
                                      (6, 32, 47, 21), (7, 0, 0, 20)):
                rows.append({**rows[0], "EDOCVE": str(state), "LN": sv + nv + ns, "SV": sv, "NV": nv, "NS": ns})
            if year == 2018:
                rows = [{**row, "EDOCVE": str(int(row["EDOCVE"]) + 10)} for row in rows]
            write_bundle(self.root, year, rows)

    def command(self, script, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / script), "--root", str(self.root), *arguments],
            capture_output=True, text=True, timeout=180, check=False,
        )

    def test_threshold_ties_empty_bins_and_missing_key_matches(self):
        before = snapshot(self.root)
        result = self.command("compare_history.py")
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        folder = self.root / "outputs/t07_history"
        report = json.loads((folder / "report.json").read_text())
        self.assertEqual(report["pipeline_sha256"], digest(ROOT / "scripts/compare_history.py"))
        self.assertEqual(report["comparison_engine_sha256"], digest(ROOT / "scripts/compare_segments.py"))
        for annual in report["annual"].values():
            self.assertEqual(annual["eligibility"]["baseline"]["eligible_groups"], 14)
            self.assertEqual(annual["eligibility"]["baseline"]["excluded_groups"], 3)
        reference = next(item for item in report["references"] if item["reference_year"] == 2024 and item["k"] == 6)
        for centroid, expected in zip(reference["centroids_pct"], (30, 40, 50, 60, 70, 80)):
            self.assertAlmostEqual(centroid, expected)
        self.assertEqual([item["groups"] for item in reference["years"]["2012"]], [6, 4, 2, 2, 0, 0])
        self.assertIsNone(reference["years"]["2012"][-1]["participation_pct"])
        for pair in report["pairs"]:
            if 2018 in (pair["from_year"], pair["to_year"]):
                self.assertEqual(pair["status"], "unavailable")
                self.assertEqual(pair["common_groups"], 0)
        for path, value in before.items():
            self.assertEqual(digest(self.root / path), value)
        for name, count in (("annual_comparison.csv", 288), ("fixed_reference.csv", 90), ("pairwise.csv", 18)):
            with (folder / name).open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), count)

    def test_incomplete_and_tampered_bundles_preserve_prior_results(self):
        prior = self.root / "outputs/prior"
        prior.mkdir(parents=True)
        (prior / "report.json").write_text("conservar los bytes previos", encoding="utf-8")
        folder = self.root / "data/processed/ccpc_all/2021"
        table, report_path = folder / "table.csv", folder / "report.json"
        original_table, original_report = table.read_bytes(), report_path.read_bytes()
        for mode, message in (("checksum", "suma de comprobación"), ("empty", "Solo se admite 2021"),
                               ("wrong_year", "Solo se admite 2021"), ("checks", "Faltan comprobaciones T06"),
                               ("totals", "totales analíticos T06 no coinciden"), ("missing", "table.csv")):
            with self.subTest(mode=mode):
                table.write_bytes(original_table)
                report_path.write_bytes(original_report)
                report = json.loads(original_report)
                if mode == "missing":
                    table.rename(folder / "saved.csv")
                elif mode in ("checksum", "empty", "wrong_year"):
                    text = table.read_text(encoding="utf-8")
                    text = text + "\n" if mode == "checksum" else (
                        text.splitlines()[0] + "\n" if mode == "empty" else text.replace("2021,", "2018,"))
                    table.write_text(text, encoding="utf-8")
                    if mode != "checksum":
                        report["table_sha256"] = digest(table)
                elif mode == "checks":
                    report["checks"]["domains"] = False
                else:
                    report["analytical_rows"] += 1
                report_path.write_text(json.dumps(report), encoding="utf-8")
                before = snapshot(self.root)
                result = self.command("compare_history.py")
                self.assertEqual((result.returncode, result.stdout), (1, ""))
                self.assertIn(message, result.stderr)
                self.assertEqual(snapshot(self.root), before)
                self.assertEqual(list(prior.parent.iterdir()), [prior])

    def test_original_command_still_rejects_a_historical_bundle(self):
        before = snapshot(self.root)
        result = self.command("compare_segments.py", "--input", "data/processed/ccpc_all/2018")
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        self.assertEqual(result.stderr, "error: Se esperaba la unidad T06 de 2024\n")
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
