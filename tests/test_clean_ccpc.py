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


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clean_ccpc.py"
COLUMNS = "AELEC FELECCION EDOCVE EDONOM MPIOCVE MPIONOM SECCION TIPOSEC DEF DEL SEXO EDAD LN SV NV NS".split()


def row(state=1, **changes):
    values = dict(zip(COLUMNS, [
        "2024", "06/02/2024", str(state), f"Entity {state}", "1", "Municipality",
        "1", "U", "1", "1", "0", "18", "10", "6", "3", "1",
    ]))
    values.update(changes)
    return values


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "data" / "raw").mkdir(parents=True)
        self.members = {f"state-{state}.csv": [row(state)] for state in range(1, 33)}

    def prepare(self, columns=COLUMNS):
        archive = self.root / "data" / "raw" / "fixture.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for name, rows in self.members.items():
                text = io.StringIO(newline="")
                writer = csv.DictWriter(text, fieldnames=columns, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
                output.writestr(name, text.getvalue().encode("utf-8-sig"))
        manifest = [{
            "election_year": 2024, "local_path": "data/raw/fixture.zip",
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "bytes": archive.stat().st_size, "members": list(self.members),
        }]
        (self.root / "data" / "sources.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.originals = {
            path: path.read_bytes() for path in (self.root / "data").rglob("*") if path.is_file()
        }

    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def assert_originals_unchanged(self):
        for path, content in self.originals.items():
            self.assertEqual(path.read_bytes(), content, path.name)

    def assert_rejected(self, expected_error):
        result = self.run_command("--chunk-size", "1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(expected_error, result.stderr)
        self.assert_originals_unchanged()
        processed = self.root / "data" / "processed"
        self.assertTrue(not processed.exists() or not list(processed.iterdir()))

    def test_aggregation_rates_anomalies_and_reproducibility(self):
        self.members["state-1.csv"] += [
            row(EDAD="24", LN="30", SV="9", NV="18", NS="3", DEF="01.0", DEL=" "),
            row(EDAD="25", SEXO="2", LN="4", SV="0", NV="0", NS="4"),
            row(EDAD="140", LN="2", SV="1", NV="1", NS="0"),
        ]
        # Los faltantes distritales deben ser consistentes para una misma sección.
        for value in self.members["state-1.csv"]:
            value["DEL"] = " "
        self.prepare()
        result = self.run_command("--chunk-size", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "ok")
        destination = self.root / "data" / "processed" / "ccpc_2024"
        with (destination / "table.csv").open(encoding="utf-8", newline="") as stream:
            table = list(csv.DictReader(stream))
        group = next(item for item in table if item["EDOCVE"] == "01" and item["age_band"] == "18-24")
        self.assertEqual([int(group[name]) for name in ("LN", "SV", "NV", "NS")], [40, 15, 21, 4])
        self.assertAlmostEqual(float(group["participation_pct"]), 100 * 15 / 36, places=6)
        self.assertAlmostEqual(float(group["abstention_pct"]), 100 * 21 / 36, places=6)
        self.assertEqual(float(group["unspecified_pct"]), 10)
        self.assertEqual(float(group["known_coverage_pct"]), 90)
        unknown = next(item for item in table if item["SEXO"] == "2")
        self.assertEqual(unknown["age_band"], "25-34")
        self.assertEqual(unknown["participation_pct"], "")
        self.assertEqual(unknown["abstention_pct"], "")
        self.assertEqual(unknown["known_denominator"], "0")
        self.assertEqual(float(unknown["unspecified_pct"]), 100)
        self.assertEqual(len(table), 34)  # Solo combinaciones observadas.
        report = json.loads((destination / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["source_rows"], 35)
        self.assertEqual(report["source_totals"], {"LN": 356, "SV": 202, "NV": 115, "NS": 39})
        self.assertEqual(report["source_totals"], report["analytical_totals"])
        self.assertEqual(report["missing_district_rows"], {"DEF": 0, "DEL": 4})
        self.assertEqual(report["age_over_110_rows"], 1)
        self.assertEqual(report["zero_known_denominator_rows"], 1)
        self.assertEqual(report["excluded_rows"], 0)
        self.assertEqual(report["election_date_literals"], ["06/02/2024"])
        self.assertEqual(report["suppression_policy"], "undocumented; unknown count tokens are rejected, never imputed")
        self.assertEqual(report["checks"]["totals_reconciled"], True)
        self.assert_originals_unchanged()
        repeated = self.run_command("--chunk-size", "3", "--run-name", "repeat")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        for name in ("table.csv", "report.json"):
            self.assertEqual((destination / name).read_bytes(), (destination.parent / "repeat" / name).read_bytes())
        before = {path: path.read_bytes() for path in destination.iterdir()}
        refused = self.run_command()
        self.assertEqual(refused.returncode, 1)
        self.assertIn("ya existe", refused.stderr)
        self.assertEqual(before, {path: path.read_bytes() for path in destination.iterdir()})

    def test_all_age_boundaries_preserve_counts(self):
        ages = [18, 24, 25, 34, 35, 44, 45, 59, 60, 110, 111, 140]
        self.members["state-1.csv"] = [row(EDAD=str(age)) for age in ages]
        self.prepare()
        result = self.run_command("--chunk-size", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        with (self.root / "data/processed/ccpc_2024/table.csv").open(encoding="utf-8", newline="") as stream:
            groups = [item for item in csv.DictReader(stream) if item["EDOCVE"] == "01"]
        self.assertEqual([(item["age_band"], int(item["LN"])) for item in groups], [
            ("18-24", 20), ("25-34", 20), ("35-44", 20), ("45-59", 20), ("60+", 40),
        ])
        self.assert_originals_unchanged()

    def test_duplicate_keys_within_and_between_chunks_are_rejected(self):
        self.members["state-1.csv"].append(row(EDOCVE="01", EDAD="018"))
        self.prepare()
        for size in (1, 10):
            with self.subTest(chunk_size=size):
                result = self.run_command("--chunk-size", str(size))
                self.assertEqual(result.returncode, 1)
                self.assertIn("clave duplicada", result.stderr)
                self.assert_originals_unchanged()

    def test_entity_overlap_between_members_is_rejected(self):
        self.members["state-2.csv"] = [row()]
        self.prepare()
        self.assert_rejected("entidad repetida")

    def test_schema_and_geographic_consistency(self):
        for changes, expected in [
            ({"MPIOCVE": "2"}, "atributos de sección"),
            ({"MPIONOM": "Other"}, "nombre municipal"),
            ({"EDONOM": "Other"}, "nombre de entidad"),
        ]:
            with self.subTest(changes=changes):
                self.members["state-1.csv"] = [row(), row(EDAD="19", **changes)]
                self.prepare()
                self.assert_rejected(expected)
        self.members["state-1.csv"] = [row()]
        self.prepare(columns=COLUMNS[:-1])
        self.assert_rejected("esquema")

    def test_invalid_domains_and_unknown_counts_fail_without_imputation(self):
        cases = [
            ("LN", "", "conteo faltante"), ("SV", "*", "supresión no documentada"),
            ("NV", "NA", "supresión no documentada"), ("NS", "-1", "conteo inválido"),
            ("SV", "1.5", "conteo inválido"), ("LN", "0", "rango"),
            ("NS", "2", "LN = SV + NV + NS"), ("EDAD", "17", "rango"),
            ("EDOCVE", "33", "rango"), ("MPIOCVE", "0", "rango"),
            ("SECCION", "0", "rango"), ("SEXO", "3", "rango"),
            ("DEF", "41", "rango"), ("DEL", "46", "rango"),
            ("TIPOSEC", "X", "TIPOSEC"), ("AELEC", "2021", "AELEC"),
            ("EDONOM", " ", "etiqueta faltante"), ("FELECCION", "", "etiqueta faltante"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field, value=value):
                self.members["state-1.csv"] = [row(**{field: value})]
                self.prepare()
                self.assert_rejected(error)

    def test_manifest_integrity_inventory_and_coverage(self):
        self.prepare()
        (self.root / "data/raw/fixture.zip").write_bytes(b"changed")
        # La entrada modificada intencionalmente es la referencia para comprobar su preservación tras el rechazo.
        self.originals[self.root / "data/raw/fixture.zip"] = b"changed"
        self.assert_rejected("integridad")
        self.members.pop("state-32.csv")
        self.prepare()
        self.assert_rejected("32 CSV")

    def test_help_and_invalid_options_do_not_write(self):
        result = self.run_command("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Limpia y valida CCPC 2024", " ".join(result.stdout.split()))
        for arguments in [("--unexpected",), ("--chunk-size", "0"), ("--run-name", "../raw")]:
            with self.subTest(arguments=arguments):
                result = self.run_command(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        self.assertEqual(list((self.root / "data").iterdir()), [self.root / "data/raw"])


if __name__ == "__main__":
    unittest.main()
