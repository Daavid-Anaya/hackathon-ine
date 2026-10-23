"""Pruebas de regresión de la CLI pública para modelos anuales separados y referencias fijas."""

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_compare_segments import BANDS, CHECKS, COUNTS


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/compare_history.py"
YEARS = (2009, 2012, 2015, 2018, 2021, 2024)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.shifts = {2009: 180, 2012: 100, 2015: 100, 2018: 50, 2021: 0, 2024: 0}
        self.prepare()

    def prepare(self):
        self.before = {}
        for year in YEARS:
            bundle = self.root / "data/processed/ccpc_all" / str(year)
            bundle.mkdir(parents=True, exist_ok=True)
            rows = []
            for state in range(1, 9):
                for group in range(6):
                    voters = 200 + group * 120 + state - self.shifts[year]
                    rows.append({
                        "AELEC": year, "EDOCVE": f"{state:02d}", "SEXO": str(group // 5),
                        "age_band": BANDS[group % 5], "LN": 1000, "SV": voters,
                        "NV": 950 - voters, "NS": 50,
                        **{f"age_over_110_{name}": 0 for name in COUNTS},
                    })
            if year == 2024:
                rows.append({**rows[0], "SEXO": "2", "LN": 2, "SV": 1, "NV": 1, "NS": 0})
            with (bundle / "table.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report = {
                "election_year": year, "unit": ["EDOCVE", "SEXO", "age_band"],
                "checks": dict.fromkeys(CHECKS, True), "analytical_rows": len(rows),
                "analytical_totals": {name: sum(row[name] for row in rows) for name in COUNTS},
                "table_sha256": hashlib.sha256((bundle / "table.csv").read_bytes()).hexdigest(),
            }
            (bundle / "report.json").write_text(json.dumps(report), encoding="utf-8")
            self.before.update({path: path.read_bytes() for path in bundle.iterdir()})

    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, check=False, timeout=180,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def assert_inputs_unchanged(self):
        for path, content in self.before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_all_years_are_separate_and_reuse_the_annual_comparison(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        summary = json.loads(result.stdout)
        self.assertEqual(summary["annual_candidates"], 36)
        folder = self.root / "outputs/t07_history"
        report = json.loads((folder / "report.json").read_text())
        self.assertEqual(report["selection"], "deferred_to_T08")
        self.assertEqual(set(report["annual"]), set(map(str, YEARS)))
        for year, annual in report["annual"].items():
            self.assertEqual(len(annual["candidates"]), 6)
            self.assertEqual(annual["input"]["election_year"], int(year))
            self.assertEqual(annual["eligibility"]["baseline"]["eligible_groups"], 48)
            self.assertEqual(annual["eligibility"]["baseline"]["excluded_groups"], int(year == "2024"))
            for candidate in annual["candidates"]:
                self.assertEqual(sum(item["groups"] for item in candidate["clusters"]), 48)
                self.assertEqual(candidate["leave_entity_out_ari"]["evaluated"], 8)
                self.assertEqual(len(candidate["sensitivities"]), 7)
        self.assertEqual({path.name for path in folder.iterdir()}, {
            "report.json", "annual_comparison.csv", "fixed_reference.csv", "pairwise.csv",
        })
        self.assert_inputs_unchanged()

    def test_fixed_definitions_detect_absolute_change_without_relabeling_people(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / "outputs/t07_history/report.json").read_text())
        self.assertEqual(len(report["references"]), 6)  # Tres valores de k por serie electoral.
        for reference in report["references"]:
            self.assertEqual(len(reference["centroids_pct"]), reference["k"])
            self.assertEqual(len(reference["boundaries_pct"]), reference["k"] - 1)
            self.assertEqual(reference["reference_year"], 2024 if "2024" in reference["series"] else 2021)
            for year, summaries in reference["years"].items():
                self.assertEqual(len(summaries), reference["k"])
                self.assertEqual(sum(item["groups"] for item in summaries), 48)
                self.assertAlmostEqual(sum(item["ln_share_pct"] for item in summaries), 100)
                self.assertEqual([item["reference_rank"] for item in summaries], list(range(1, reference["k"] + 1)))
        self.assertEqual(len(report["pairs"]), 18)
        allowed = [{2012, 2018, 2024}, {2009, 2015, 2021}]
        for pair in report["pairs"]:
            self.assertTrue(any({pair["from_year"], pair["to_year"]}.issubset(series) for series in allowed))
            self.assertEqual(pair["common_groups"], 48)
            expected = 100 * (self.shifts[pair["from_year"]] - self.shifts[pair["to_year"]]) / 950
            self.assertAlmostEqual(pair["mean_delta_pp"], expected)
            self.assertAlmostEqual(pair["median_delta_pp"], expected)
            self.assertAlmostEqual(pair["spearman_rate_rank"], 1)
            # Las seis nubes sintéticas tienen una única partición de seis conglomerados;
            # con k=4/5, fusiones igualmente buenas pueden diferir tras cambios de punto flotante.
            if pair["k"] == 6:
                self.assertAlmostEqual(pair["annual_ari"]["kmeans"], 1)
            self.assertEqual(sum(item["groups"] for item in pair["aggregate_key_movements"]), 48)
        pair = next(item for item in report["pairs"] if item["from_year"] == 2009 and item["to_year"] == 2021 and item["k"] == 6)
        self.assertLess(pair["same_reference_band_group_pct"], 100)
        self.assertTrue(any(item["groups"] == 0 for reference in report["references"]
                            for item in reference["years"][str(min(map(int, reference["years"])))]))
        self.assert_inputs_unchanged()

    def test_repeat_is_identical_and_existing_outputs_are_not_overwritten(self):
        for name in ("first", "repeat"):
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        snapshot = {path: path.read_bytes() for path in (self.root / "outputs").rglob("*") if path.is_file()}
        for filename in ("report.json", "annual_comparison.csv", "fixed_reference.csv", "pairwise.csv"):
            self.assertEqual((self.root / "outputs/first" / filename).read_bytes(),
                             (self.root / "outputs/repeat" / filename).read_bytes())
        result = self.run_command("--run-name", "first")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("ya existe", result.stderr)
        for path, content in snapshot.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_inputs_unchanged()

    def test_invalid_historical_data_refuses_the_entire_bundle(self):
        path = self.root / "data/processed/ccpc_all/2021/table.csv"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace(",0,18-24,", ",2,18-24,", 1), encoding="utf-8")
        report_path = path.with_name("report.json")
        report = json.loads(report_path.read_text())
        report["table_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        report_path.write_text(json.dumps(report))
        self.before.update({path: path.read_bytes(), report_path: report_path.read_bytes()})
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("SEXO", result.stderr)
        self.assertFalse((self.root / "outputs").exists())
        self.assert_inputs_unchanged()

    def test_help_and_invalid_options_are_no_write(self):
        result = self.run_command("--help")
        self.assertEqual(result.returncode, 0)
        for option in ("--root", "--input", "--run-name"):
            self.assertIn(option, result.stdout)
        for arguments in [("--unknown",), ("--run-name", "../previous"), ("--input", "missing")]:
            result = self.run_command(*arguments)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertFalse((self.root / "outputs").exists())
        self.assert_inputs_unchanged()


if __name__ == "__main__":
    unittest.main()
