"""Pruebas de la lista explícita de campos de la versión reducida para difusión."""

import csv
from decimal import Decimal, ROUND_HALF_UP
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


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/prepare_disclosure_summary.py"
FILES = {"profiles.csv", "historical_reference.csv", "annual_metrics.csv",
         "historical_comparison.csv", "manifest.json", "README.md"}
COLUMNS = {
    "profiles.csv": ["profile_id", "year", "participation_pct", "ln_share_pct"],
    "historical_reference.csv": ["series", "reference_year", "year", "reference_id", "participation_pct", "ln_share_pct"],
    "annual_metrics.csv": ["year", "method", "k", "silhouette"],
    "historical_comparison.csv": ["series", "reference_year", "from_year", "to_year", "mean_delta_pp",
                                  "spearman_rate_rank", "same_reference_band_group_pct", "annual_kmeans_ari"],
}


class DisclosureSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = fixtures.HistoryTests()
        cls.fixture.setUp()
        cls.addClassCleanup(cls.fixture.temporary.cleanup)
        result = cls.fixture.run_command()
        if result.returncode:
            raise AssertionError(result.stderr)
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/export_profiles.py"),
                                 "--root", str(cls.fixture.root), "--run-name", "t08_profiles_final"],
                                capture_output=True, text=True, timeout=180, check=False)
        if result.returncode:
            raise AssertionError(result.stderr)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        shutil.copytree(self.fixture.root, self.root)
        self.source = self.root / "outputs/t08_profiles_final"
        self.destination = self.root / "outputs/t08_disclosure_summary"
        self.before = self.snapshot()

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def run_command(self, *arguments):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
                              capture_output=True, text=True, timeout=120, check=False,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def rows(self, name, source=False):
        folder = self.source if source else self.destination
        with (folder / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def rewrite_report(self, report):
        (self.source / "report.json").write_text(json.dumps(report), encoding="utf-8")

    def rehash(self, name):
        report = json.loads((self.source / "report.json").read_text())
        report["artifacts_sha256"][name] = hashlib.sha256((self.source / name).read_bytes()).hexdigest()
        self.rewrite_report(report)

    def assert_unchanged(self, before):
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)

    def test_allowlisted_draft_preserves_six_years_without_detailed_counts(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertFalse(json.loads(result.stdout)["publication_authorized"])
        self.assertEqual({path.name for path in self.destination.iterdir()}, FILES)
        for name, fields in COLUMNS.items():
            self.assertEqual(list(self.rows(name)[0]), fields)
        self.assertEqual(len(self.rows("profiles.csv")), 5)
        self.assertEqual(len(self.rows("historical_reference.csv")), 30)
        self.assertEqual(len(self.rows("annual_metrics.csv")), 36)
        self.assertEqual(len(self.rows("historical_comparison.csv")), 6)
        self.assertEqual({int(row["year"]) for row in self.rows("historical_reference.csv")}, set(fixtures.YEARS))
        for row in self.rows("historical_reference.csv"):
            expected = "2024" if row["year"] in ("2012", "2018", "2024") else "2021"
            self.assertEqual(row["reference_year"], expected)
            self.assertTrue(row["reference_id"].startswith(f"CCPC-REF-{expected}-K5-R"))
        manifest = json.loads((self.destination / "manifest.json").read_text())
        self.assertEqual(manifest["contract"], "disclosure-summary/v1")
        self.assertEqual(manifest["status"], "draft_pending_review")
        self.assertFalse(manifest["publication_authorized"])
        self.assertEqual(manifest["rounding"], {"percent_decimals": 1, "coefficient_decimals": 2, "mode": "ROUND_HALF_UP"})
        self.assertEqual({row["year"] for row in manifest["sources"]}, set(fixtures.YEARS))
        self.assertTrue(manifest["limitations"])
        self.assertEqual(manifest["source_report_sha256"], hashlib.sha256((self.source / "report.json").read_bytes()).hexdigest())
        for name, digest in manifest["artifacts_sha256"].items():
            self.assertEqual(hashlib.sha256((self.destination / name).read_bytes()).hexdigest(), digest)
        self.assert_unchanged(self.before)

    def test_rounding_matches_internal_values_and_excludes_other_reference_k(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        for internal, public in zip(self.rows("profiles.csv", source=True), self.rows("profiles.csv"), strict=True):
            for field in ("participation_pct", "ln_share_pct"):
                expected = Decimal(internal[field]).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                self.assertEqual(public[field], str(expected))
        for name in COLUMNS:
            for row in self.rows(name):
                for field, value in row.items():
                    if field.endswith("_pct") or field == "mean_delta_pp":
                        self.assertRegex(value, r"^-?\d+\.\d$|^$")
                    elif field in ("silhouette", "spearman_rate_rank", "annual_kmeans_ari"):
                        self.assertRegex(value, r"^-?\d+\.\d{2}$|^$")
        self.assert_unchanged(self.before)

    def test_unrecognized_text_and_columns_do_not_cross_the_boundary(self):
        marker = "PRIVATE_SENTINEL_SHOULD_NOT_ESCAPE"
        report = json.loads((self.source / "report.json").read_text())
        report["private_notes"] = marker
        report["limitations"] = [marker]
        self.rewrite_report(report)
        path = self.source / "profiles.csv"
        rows = self.rows("profiles.csv", source=True)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=[*rows[0], "private_notes"])
            writer.writeheader()
            writer.writerows({**row, "private_notes": marker} for row in rows)
        self.rehash("profiles.csv")
        before = self.snapshot()
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in self.destination.iterdir():
            self.assertNotIn(marker, path.read_text(encoding="utf-8"))
        self.assert_unchanged(before)

    def test_tampering_incomplete_history_and_invalid_numbers_fail_without_output(self):
        original = self.snapshot()
        cases = ("checksum", "missing_year", "wrong_selection", "invalid_number", "invalid_id", "unsafe_artifact_path")
        for case in cases:
            with self.subTest(case=case):
                for name, content in original.items():
                    (self.root / name).write_bytes(content)
                report = json.loads((self.source / "report.json").read_text())
                if case == "checksum":
                    (self.source / "profiles.csv").write_bytes(b"modified")
                elif case == "missing_year":
                    report["inputs"].pop("2009")
                    self.rewrite_report(report)
                elif case == "wrong_selection":
                    report["selection"]["k"] = 6
                    self.rewrite_report(report)
                elif case == "unsafe_artifact_path":
                    report["artifacts_sha256"]["../../private.json"] = "0" * 64
                    self.rewrite_report(report)
                else:
                    path = self.source / "profiles.csv"
                    rows = self.rows("profiles.csv", source=True)
                    rows[0]["participation_pct" if case == "invalid_number" else "profile_id"] = "NaN" if case == "invalid_number" else "PRIVATE-ID"
                    with path.open("w", encoding="utf-8", newline="") as stream:
                        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                        writer.writeheader()
                        writer.writerows(rows)
                    self.rehash("profiles.csv")
                before = self.snapshot()
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(result.stdout, "")
                self.assertFalse(self.destination.exists())
                self.assertEqual(self.snapshot(), before)

    def test_repeat_overwrite_refusal_help_and_invalid_options(self):
        help_result = self.run_command("--help")
        self.assertEqual(help_result.returncode, 0)
        for option in ("--root", "--input", "--run-name"):
            self.assertIn(option, help_result.stdout)
        for arguments in (("--unknown",), ("--run-name", "../escape"), ("--input", "../escape")):
            result = self.run_command(*arguments)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(self.snapshot(), self.before)
        for name in ("t08_disclosure_summary", "repeat"):
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        for name in FILES:
            self.assertEqual((self.destination / name).read_bytes(), (self.destination.parent / "repeat" / name).read_bytes())
        before = self.snapshot()
        result = self.run_command()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("ya existe", result.stderr)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
