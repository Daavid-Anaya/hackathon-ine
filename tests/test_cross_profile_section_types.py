"""Verifica por CLI el cruce territorial sin reajustar perfiles sintéticos fijos."""

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_diagnose_section_types as fixture


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/cross_profile_section_types.py"
COUNTS = ("LN", "SV", "NV", "NS")
FILES = "profiles.csv assignments.csv historical_assignments.csv fixed_reference.csv exclusions.csv annual_comparison.csv pairwise.csv t07_evidence.json".split()


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class ProfileSectionTests(unittest.TestCase):
    def setUp(self):
        self.source = fixture.SectionTypeTests()
        self.source.setUp()
        self.addCleanup(self.source.doCleanups)
        self.root = self.source.root
        self.output = self.root / "outputs/t08_profiles_final"
        self.output.mkdir(parents=True)
        with (self.source.bundle / "table.csv").open(newline="") as stream:
            table = list(csv.DictReader(stream))
        self.assignments = [{"profile_id": f"CCPC-2024-K5-P{(int(row['EDOCVE']) - 1) % 5 + 1:02d}",
                             "year": 2024, **{key: row[key] for key in ("EDOCVE", "SEXO", "age_band", *COUNTS)}}
                            for row in table]
        write_rows(self.output / "assignments.csv", self.assignments)
        profiles = []
        total_ln = sum(int(row["LN"]) for row in table)
        for number in range(1, 6):
            identity = f"CCPC-2024-K5-P{number:02d}"
            selected = [row for row in self.assignments if row["profile_id"] == identity]
            counts = {name: sum(int(row[name]) for row in selected) for name in COUNTS}
            profiles.append({"profile_id": identity, "year": 2024, "groups": len(selected),
                             "entities": len({row["EDOCVE"] for row in selected}), **counts,
                             "participation_pct": 100 * counts["SV"] / (counts["SV"] + counts["NV"]),
                             "ln_share_pct": 100 * counts["LN"] / total_ln})
        write_rows(self.output / "profiles.csv", profiles)
        for name in FILES:
            if not (self.output / name).exists():
                (self.output / name).write_text("[]\n")
        self.report = {"contract": "t08-profiles/v1", "internal_only": True,
                       "selection": {"year": 2024, "method": "kmeans", "k": 5,
                                     "scenario": "baseline", "features": ["participation_pct"]},
                       "inputs": {"2024": {"table_sha256": fixture.sha(self.source.bundle / "table.csv"),
                                             "report_sha256": fixture.sha(self.source.bundle / "report.json")}}}
        self.refresh()

    def refresh(self):
        self.report["artifacts_sha256"] = {name: fixture.sha(self.output / name) for name in FILES}
        (self.output / "report.json").write_text(json.dumps(self.report))
        self.before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def run_command(self, *arguments):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
                              capture_output=True, text=True, timeout=90,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def assert_inputs_unchanged(self):
        for path, expected in self.before.items():
            self.assertEqual(path.read_bytes(), expected)

    def test_cross_inherits_fixed_profiles_and_reconciles_totals(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "internal_fixed_profile_cross")
        folder = self.root / "outputs/profile_section_types_2024"
        with (folder / "cross.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 15)
        report = json.loads((folder / "report.json").read_text())
        self.assertFalse(report["publication_authorized"])
        self.assertFalse(report["models_refitted"])
        self.assertEqual(report["assigned_totals"], self.source.report["analytical_totals"])
        for number in range(1, 6):
            identity = f"CCPC-2024-K5-P{number:02d}"
            selected = [row for row in rows if row["profile_id"] == identity]
            self.assertEqual({row["TIPOSEC"] for row in selected}, {"U", "M", "R"})
            for row in selected:
                self.assertAlmostEqual(float(row["participation_pct"]), {"U": 26, "M": 50, "R": 74}[row["TIPOSEC"]])
                self.assertAlmostEqual(float(row["standardized_participation_pct"]), 50)
                self.assertAlmostEqual(float(row["within_profile_ln_share_pct"]), 100 / 3)
            self.assertAlmostEqual(report["profiles"][identity]["parent_participation_pct"], 50)
        self.assert_inputs_unchanged()

    def test_rehashed_incompatible_or_duplicate_assignments_are_rejected(self):
        for mode in ("counts", "duplicate", "missing"):
            with self.subTest(mode=mode):
                rows = [dict(row) for row in self.assignments]
                if mode == "counts":
                    rows[0]["SV"] = int(rows[0]["SV"]) + 1
                elif mode == "duplicate":
                    rows.append(dict(rows[0]))
                else:
                    rows.pop()
                write_rows(self.output / "assignments.csv", rows)
                self.refresh()
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertFalse((self.root / "outputs/profile_section_types_2024").exists())
                self.assert_inputs_unchanged()

    def test_repeatability_and_overwrite_refusal(self):
        for name in ("first", "repeat"):
            result = self.run_command("--run-name", name)
            self.assertEqual(result.returncode, 0, result.stderr)
        first = self.root / "outputs/first"
        repeat = self.root / "outputs/repeat"
        self.assertEqual({path.name for path in first.iterdir()}, {"cross.csv", "report.json", "README.md"})
        for path in first.iterdir():
            self.assertEqual(path.read_bytes(), (repeat / path.name).read_bytes())
        before = {path: path.read_bytes() for path in first.iterdir()}
        result = self.run_command("--run-name", "first")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        for path, expected in before.items():
            self.assertEqual(path.read_bytes(), expected)
        self.assert_inputs_unchanged()


if __name__ == "__main__":
    unittest.main()
