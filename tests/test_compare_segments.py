"""Ejercita la CLI de T07 con tablas agregadas sintéticas, nunca con conjuntos de datos originales."""

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_segments.py"
BANDS = ["18-24", "25-34", "35-44", "45-59", "60+"]
COUNTS = ["LN", "SV", "NV", "NS"]
CHECKS = ["source_integrity_before_after", "schema", "key_uniqueness_exact", "domains",
          "geographic_consistency", "accounting_identity", "entity_coverage", "totals_reconciled"]


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / "data/processed/ccpc_all/2024"
        self.bundle.mkdir(parents=True)
        self.rows = []
        for state in range(1, 9):
            for group in range(6):
                voters = 200 + group * 280 + state
                counts = dict(LN=2000, SV=voters, NV=1900 - voters, NS=100)
                self.rows.append({
                    "AELEC": 2024, "EDOCVE": f"{state:02d}", "SEXO": str(group // 5),
                    "age_band": BANDS[group % 5], **counts,
                    **{f"age_over_110_{name}": 0 for name in COUNTS},
                })
        # Estas categorías reales permanecen en la entrada, pero no entran en el ajuste base.
        for sex, counts in [("2", dict(LN=2, SV=1, NV=1, NS=0)),
                            ("1", dict(LN=10, SV=0, NV=0, NS=10))]:
            self.rows.append({**self.rows[0], "SEXO": sex, "age_band": "45-59", **counts})
        for name, value in dict(LN=10, SV=6, NV=3, NS=1).items():
            self.rows[4][f"age_over_110_{name}"] = value
        self.prepare()

    def prepare(self):
        table = self.bundle / "table.csv"
        with table.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
        report = {"election_year": 2024, "unit": ["EDOCVE", "SEXO", "age_band"],
                  "table_sha256": hashlib.sha256(table.read_bytes()).hexdigest(),
                  "checks": dict.fromkeys(CHECKS, True), "analytical_rows": len(self.rows),
                  "analytical_totals": {
                      name: sum(int(row[name]) if str(row[name]).lstrip("-").isdigit() else 0
                                for row in self.rows) for name in COUNTS}}
        (self.bundle / "report.json").write_text(json.dumps(report), encoding="utf-8")
        self.before = {path: path.read_bytes() for path in self.bundle.iterdir()}

    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=90,
        )

    def assert_inputs_unchanged(self):
        for path, content in self.before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_comparison_covers_methods_k_sensitivities_and_count_based_summaries(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "ok")
        folder = self.root / "outputs/t07_comparison"
        self.assertEqual({path.name for path in folder.iterdir()}, {"report.json", "comparison.csv"})
        report = json.loads((folder / "report.json").read_text())
        self.assertEqual(report["input"]["rows"], 50)
        self.assertEqual(report["eligibility"]["baseline"]["eligible_groups"], 48)
        self.assertEqual(report["eligibility"]["baseline"]["excluded_totals"]["LN"], 12)
        self.assertEqual(report["config"]["baseline_features"], ["participation_pct"])
        self.assertEqual(report["config"]["seeds"], list(range(20)))
        self.assertEqual(len(report["candidates"]), 6)
        for candidate in report["candidates"]:
            self.assertIn(candidate["k"], [4, 5, 6])
            self.assertEqual(candidate["status"], "ok")
            self.assertEqual(len(candidate["clusters"]), candidate["k"])
            self.assertEqual(sum(item["groups"] for item in candidate["clusters"]), 48)
            self.assertEqual(sum(item["LN"] for item in candidate["clusters"]), 96000)
            for item in candidate["clusters"]:
                self.assertAlmostEqual(item["participation_pct"], 100 * item["SV"] / (item["SV"] + item["NV"]))
                self.assertAlmostEqual(sum(item["age_ln_share_pct"].values()), 100)
                self.assertAlmostEqual(sum(item["sex_ln_share_pct"].values()), 100)
            self.assertEqual(candidate["leave_entity_out_ari"]["evaluated"], 8)
            seed_result = candidate["seed_stability_ari"]
            if candidate["method"] == "kmeans":
                self.assertEqual(seed_result["evaluated"], 19)
            else:
                self.assertIsNone(seed_result)
            scenarios = {item["scenario"]: item for item in candidate["sensitivities"]}
            self.assertEqual(set(scenarios), {
                "min_d15", "min_d60", "coverage70", "coverage90", "ln_weighted",
                "participation_unspecified", "without_age_over_110",
            })
            for name, sensitivity in scenarios.items():
                if name == "ln_weighted" and candidate["method"] == "ward":
                    self.assertEqual(sensitivity["status"], "not_applicable")
                else:
                    self.assertEqual(sensitivity["status"], "ok")
                    self.assertIn("ari_on_common_groups", sensitivity)
            if candidate["k"] == 6:
                self.assertGreater(candidate["silhouette"], 0.95)
                self.assertEqual([item["groups"] for item in candidate["clusters"]], [8] * 6)
        self.assert_inputs_unchanged()

    def test_reproducible_bytes_and_overwrite_refusal(self):
        for name in ["first", "repeat"]:
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        for name in ["report.json", "comparison.csv"]:
            self.assertEqual((self.root / "outputs/first" / name).read_bytes(),
                             (self.root / "outputs/repeat" / name).read_bytes())
        snapshot = {path: path.read_bytes() for path in (self.root / "outputs").rglob("*") if path.is_file()}
        result = self.run_command("--run-name", "first")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("ya existe", result.stderr)
        for path, content in snapshot.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_inputs_unchanged()

    def test_thresholds_and_age_sensitivity_change_the_accounted_population(self):
        self.rows[0].update(SV=201, NV=1299, NS=500)  # 75% de cobertura conocida.
        self.rows[1].update(LN=50, SV=20, NV=25, NS=5)  # D=45, exactamente 90% de cobertura.
        self.rows[-2].update(LN=16, SV=9, NV=7)  # Se conserva por separado; elegible solo con D>=15.
        self.prepare()
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / "outputs/t07_comparison/report.json").read_text())
        counts = {name: values["eligible_groups"] for name, values in report["eligibility"].items()}
        self.assertEqual(counts["baseline"], 47)
        self.assertEqual(counts["min_d15"], 48)
        self.assertEqual(counts["min_d60"], 46)
        self.assertEqual(counts["coverage70"], 48)
        self.assertEqual(counts["coverage90"], 47)
        age = report["eligibility"]["without_age_over_110"]
        self.assertEqual(age["removed_age_over_110_totals"], dict(LN=10, SV=6, NV=3, NS=1))
        for name, values in report["eligibility"].items():
            for field in COUNTS:
                self.assertEqual(values["eligible_totals"][field] + values["excluded_totals"][field]
                                 + values["removed_age_over_110_totals"][field], report["input"]["totals"][field])
        self.assert_inputs_unchanged()

    def test_cached_rates_are_not_used_as_features(self):
        result = self.run_command("--run-name", "counts")
        self.assertEqual(result.returncode, 0, result.stderr)
        for row in self.rows:
            row.update(participation_pct="wrong", abstention_pct="wrong", known_denominator="wrong",
                       unspecified_pct="wrong", known_coverage_pct="wrong")
        self.prepare()
        result = self.run_command("--run-name", "cached")
        self.assertEqual(result.returncode, 0, result.stderr)
        reports = [json.loads((self.root / "outputs" / name / "report.json").read_text())
                   for name in ("counts", "cached")]
        self.assertEqual(reports[0]["candidates"], reports[1]["candidates"])
        self.assert_inputs_unchanged()

    def test_invalid_tables_fail_without_publication_or_input_mutation(self):
        original = [dict(row) for row in self.rows]
        for changes, message in [({"AELEC": 2021}, "2024"), ({"SV": "*"}, "SV"),
                                 ({"NS": -1}, "NS"), ({"NS": 99}, "contable"),
                                 ({"SEXO": 3}, "SEXO"), ({"age_band": "unknown"}, "age_band"),
                                 ({"age_over_110_LN": 9999}, "age_over_110")]:
            with self.subTest(changes=changes):
                self.rows = [dict(row) for row in original]
                self.rows[0].update(changes)
                self.prepare()
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)
                self.assertFalse((self.root / "outputs").exists())
                self.assert_inputs_unchanged()
        self.rows = original + [dict(original[0])]
        self.prepare()
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicadas", result.stderr)
        self.assertFalse((self.root / "outputs").exists())

    def test_provenance_and_unusable_data_are_rejected(self):
        report_path = self.bundle / "report.json"
        for field, value in [("table_sha256", "wrong"), ("checks", {}), ("analytical_rows", 1)]:
            with self.subTest(field=field):
                self.prepare()
                report = json.loads(report_path.read_text())
                report[field] = value
                report_path.write_text(json.dumps(report))
                self.before[report_path] = report_path.read_bytes()
                result = self.run_command()
                self.assertEqual(result.returncode, 1)
                self.assertFalse((self.root / "outputs").exists())
                self.assert_inputs_unchanged()
        self.rows = self.rows[-2:]
        self.prepare()
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertIn("escenario base", result.stderr)
        self.assertFalse((self.root / "outputs").exists())

    def test_help_and_invalid_arguments_do_not_write(self):
        result = self.run_command("--help")
        self.assertEqual(result.returncode, 0)
        for option in ["--root", "--input", "--run-name"]:
            self.assertIn(option, result.stdout)
        for arguments in [("--unknown",), ("--run-name", "../data"), ("--run-name", "."),
                          ("--input", "missing")]:
            with self.subTest(arguments=arguments):
                result = self.run_command(*arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertFalse((self.root / "outputs").exists())
        self.assert_inputs_unchanged()


if __name__ == "__main__":
    unittest.main()
