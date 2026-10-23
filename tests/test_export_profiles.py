"""Pruebas de la selección T08 y sus exportaciones por la CLI pública."""

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import test_compare_history as fixtures


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/export_profiles.py"
YEARS = fixtures.YEARS


class ExportProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Una ejecución genuina de T07 prepara evidencia compartida de solo lectura.
        cls.fixture = fixtures.HistoryTests()
        cls.fixture.setUp()
        cls.addClassCleanup(cls.fixture.temporary.cleanup)
        result = cls.fixture.run_command()
        if result.returncode:
            raise AssertionError(result.stderr)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        shutil.copytree(self.fixture.root, self.root)
        self.before = self.snapshot()

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, check=False, timeout=180,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def read_json(self, name):
        return json.loads((self.root / "outputs/t08_profiles" / name).read_text(encoding="utf-8"))

    def read_csv(self, name):
        with (self.root / "outputs/t08_profiles" / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def assert_originals_unchanged(self):
        for name, content in self.before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)

    def test_selected_profiles_have_identifiers_counts_composition_and_mapping(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["profiles"], 5)
        report = self.read_json("report.json")
        self.assertEqual(report["contract"], "t08-profiles/v1")
        self.assertTrue(report["internal_only"])
        self.assertEqual(report["selection"]["year"], 2024)
        self.assertEqual(report["selection"]["method"], "kmeans")
        self.assertEqual(report["selection"]["k"], 5)
        self.assertEqual(report["selection"]["scenario"], "baseline")
        profiles, assignments = self.read_csv("profiles.csv"), self.read_csv("assignments.csv")
        self.assertEqual([row["profile_id"] for row in profiles],
                         [f"CCPC-2024-K5-P{rank:02d}" for rank in range(1, 6)])
        self.assertEqual(len(assignments), 48)
        self.assertEqual(len({(row["EDOCVE"], row["SEXO"], row["age_band"]) for row in assignments}), 48)
        self.assertEqual({row["year"] for row in assignments}, {"2024"})
        self.assertEqual({row["SEXO"] for row in assignments}, {"0", "1"})
        for profile in profiles:
            members = [row for row in assignments if row["profile_id"] == profile["profile_id"]]
            self.assertEqual(len(members), int(profile["groups"]))
            for field in ("LN", "SV", "NV", "NS"):
                self.assertEqual(sum(int(row[field]) for row in members), int(profile[field]))
            self.assertAlmostEqual(float(profile["participation_pct"]),
                                   100 * int(profile["SV"]) / (int(profile["SV"]) + int(profile["NV"])))
            self.assertAlmostEqual(sum(json.loads(profile["age_ln_share_pct"]).values()), 100)
            self.assertAlmostEqual(sum(json.loads(profile["sex_ln_share_pct"]).values()), 100)
        centers = [float(row["centroid_pct"]) for row in profiles]
        self.assertEqual(centers, sorted(centers))
        for row in assignments:
            rate = 100 * int(row["SV"]) / (int(row["SV"]) + int(row["NV"]))
            nearest = min(range(5), key=lambda index: (rate - centers[index]) ** 2)
            self.assertEqual(row["profile_id"], profiles[nearest]["profile_id"])
        excluded = self.read_csv("exclusions.csv")
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["SEXO"], "2")
        self.assertEqual(int(excluded[0]["LN"]), 2)
        self.assertIn("denominador", excluded[0]["reason"])
        self.assertNotIn("participation_pct", excluded[0])
        self.assert_originals_unchanged()

    def test_six_year_history_keeps_all_candidates_and_separate_reference_definitions(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = self.read_json("t07_evidence.json")
        self.assertEqual(set(evidence["annual"]), set(map(str, YEARS)))
        self.assertEqual(sum(len(annual["candidates"]) for annual in evidence["annual"].values()), 36)
        self.assertEqual(len(self.read_csv("annual_comparison.csv")), 36 * 8)
        self.assertEqual(len(self.read_csv("pairwise.csv")), 18)
        references = self.read_csv("fixed_reference.csv")
        self.assertEqual(len(references), 90)
        assignments = self.read_csv("historical_assignments.csv")
        self.assertEqual(len(assignments), 6 * 3 * 48)
        self.assertEqual({row["year"] for row in assignments}, set(map(str, YEARS)))
        for year in YEARS:
            expected_reference = "2024" if year in (2012, 2018, 2024) else "2021"
            for k in (4, 5, 6):
                rows = [row for row in references if row["year"] == str(year) and row["k"] == str(k)]
                members = [row for row in assignments if row["year"] == str(year) and row["k"] == str(k)]
                self.assertEqual(len(rows), k)
                self.assertEqual({row["reference_year"] for row in rows}, {expected_reference})
                self.assertEqual(sum(int(row["LN"]) for row in rows), 48000)
                self.assertEqual(sum(int(row["groups"]) for row in rows), 48)
                self.assertAlmostEqual(sum(float(row["ln_share_pct"]) for row in rows), 100)
                for row in rows:
                    matched = [item for item in members if item["reference_id"] == row["reference_id"]]
                    self.assertEqual(len(matched), int(row["groups"]))
                    self.assertEqual(sum(int(item["LN"]) for item in matched), int(row["LN"]))
        empty = [row for row in references if row["groups"] == "0"]
        self.assertTrue(empty)
        self.assertTrue(all(row["participation_pct"] == "" for row in empty))
        self.assertTrue(all(not row["reference_id"].startswith("CCPC-2024-K5-P") for row in references))
        self.assert_originals_unchanged()

    def test_repeated_exports_are_identical_and_outputs_are_never_overwritten(self):
        for name in ("t08_profiles", "repeat"):
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        report = self.read_json("report.json")
        for filename, digest in report["artifacts_sha256"].items():
            original = self.root / "outputs/t08_profiles" / filename
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), digest)
        for path in (self.root / "outputs/t08_profiles").iterdir():
            self.assertEqual(path.read_bytes(), (self.root / "outputs/repeat" / path.name).read_bytes())
        before = self.snapshot()
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("ya existe", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assert_originals_unchanged()

    def test_stale_or_incomplete_history_is_rejected_without_partial_export(self):
        path = self.root / "outputs/t07_history/report.json"
        original = path.read_bytes()
        mutations = (
            lambda report: report.update(contract="unknown"),
            lambda report: report["annual"].pop("2009"),
            lambda report: report["annual"]["2012"]["input"].update(table_sha256="0" * 64),
            lambda report: report["annual"]["2024"]["candidates"][0].update(silhouette=0),
            lambda report: report["annual"]["2018"]["candidates"].pop(),
            lambda report: report["annual"]["2024"]["candidates"][0].update(seed_stability_ari={}),
            lambda report: report["references"][0]["centroids_pct"].__setitem__(0, -1),
            lambda report: report["pairs"].pop(),
            lambda report: report["environment"].update(sklearn="0.0.0"),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                report = json.loads(original)
                mutate(report)
                path.write_text(json.dumps(report), encoding="utf-8")
                before = self.snapshot()
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(result.stdout, "")
                self.assertIn("error:", result.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertFalse((self.root / "outputs/t08_profiles").exists())

    def test_invalid_historical_input_rejects_whole_export(self):
        path = self.root / "data/processed/ccpc_all/2021/table.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        before = self.snapshot()
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("comprobaci", result.stderr)
        self.assertFalse((self.root / "outputs/t08_profiles").exists())
        self.assertEqual(self.snapshot(), before)

    def test_help_and_invalid_arguments_do_not_write(self):
        result = self.run_command("--help")
        self.assertEqual(result.returncode, 0)
        for option in ("--root", "--input", "--history", "--run-name"):
            self.assertIn(option, result.stdout)
        for arguments in (("--unknown",), ("--run-name", "../escape"),
                          ("--input", "../escape"), ("--history", "../escape.json"),
                          ("--input", "missing"), ("--history", "outputs/missing.json")):
            with self.subTest(arguments=arguments):
                result = self.run_command(*arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.snapshot(), self.before)


if __name__ == "__main__":
    unittest.main()
