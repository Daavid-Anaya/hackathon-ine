"""Public CLI regression tests for internal T12 profile cards."""

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate_profile_cards.py"


class ProfileCardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.profiles = self.root / "profiles.csv"
        self.cross = self.root / "cross.csv"
        profiles, cross = [], []
        for index in range(1, 6):
            pid = f"CCPC-2024-K5-P{index:02d}"
            profiles.append(dict(
                profile_id=pid, year=2024, LN=1000, SV=300 + index * 50,
                NV=650 - index * 50, NS=50, ln_share_pct=20,
                participation_pct=100 * (300 + index * 50) / 950,
                unspecified_pct=5, entities=index + 10,
                age_ln_share_pct=json.dumps({"18-24": 20, "25-34": 30,
                                             "35-44": 10, "45-59": 20, "60+": 20}),
                sex_ln_share_pct=json.dumps({"0": 40, "1": 60}),
            ))
            for kind, weight in (("U", 5), ("M", 3), ("R", 2)):
                cross.append(dict(profile_id=pid, TIPOSEC=kind, LN=100 * weight,
                                  SV=(30 + index * 5) * weight,
                                  NV=(65 - index * 5) * weight, NS=5 * weight,
                                  within_profile_ln_share_pct=10 * weight))
        self.write_csv(self.profiles, profiles)
        self.write_csv(self.cross, cross)
        self.before = self.snapshot()

    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def run_command(self, *args, isolated=False):
        return subprocess.run(
            [sys.executable, *(["-S"] if isolated else []), "-B", str(SCRIPT), "--profiles", str(self.profiles),
             "--cross", str(self.cross), "--output", str(self.root / "cards"), *args],
            capture_output=True, text=True, encoding="utf-8", timeout=180,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_html_retains_five_cards_numbers_and_standalone_limits(self):
        result = self.run_command("--html-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["profiles"], 5)
        for index in range(1, 6):
            text = (self.root / f"cards/ficha_P{index:02d}.html").read_text(encoding="utf-8")
            for expected in ("Borrador interno", "revisión de divulgación", "hipótesis",
                             "Fuente operativa propuesta", "Sin contacto individualizado",
                             "No aplica", "20.0%", "60.0%", "30.0%", "50.0%",
                             "profiles.csv", "cross.csv", "300 dpi"):
                self.assertIn(expected, text)
            self.assertNotIn("Ficha Oficial", text)
            self.assertNotIn("alta movilidad y predominio", text)
            self.assertNotIn("compromiso cívico sobresaliente", text.lower())
            self.assertIn(f"{100 * (300 + index * 50) / 950:.1f}%", text)
        p5 = (self.root / "cards/ficha_P05.html").read_text(encoding="utf-8")
        self.assertIn("rampas funcionales", p5)
        self.assertIn("o con rampa", p5)
        p1 = (self.root / "cards/ficha_P01.html").read_text(encoding="utf-8")
        self.assertIn("domingo", p1)
        report = json.loads((self.root / "cards/report.json").read_text())
        self.assertTrue(report["internal_only"])
        self.assertFalse(report["exported"])
        for name, digest in report["artifacts_sha256"].items():
            self.assertEqual(hashlib.sha256((self.root / "cards" / name).read_bytes()).hexdigest(), digest)
        for name, content in self.before.items():
            self.assertEqual((self.root / name).read_bytes(), content)

    def test_existing_output_is_rejected_and_html_repeat_is_identical(self):
        first = self.run_command("--html-only")
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.snapshot()
        again = self.run_command("--html-only")
        self.assertEqual(again.returncode, 1)
        self.assertEqual(again.stdout, "")
        self.assertIn("already exists", again.stderr)
        self.assertEqual(self.snapshot(), before)
        repeat = self.run_command("--html-only", "--output", str(self.root / "repeat"))
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        for path in (self.root / "cards").iterdir():
            self.assertEqual(path.read_bytes(), (self.root / "repeat" / path.name).read_bytes())

    def test_invalid_inputs_fail_without_partial_output(self):
        original = self.profiles.read_bytes()
        with self.profiles.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        mutations = (
            lambda r: r.pop(),
            lambda r: r[0].update(participation_pct="nan"),
            lambda r: r[0].update(age_ln_share_pct='{"18-24": 101}'),
            lambda r: r[0].update(SV="0"),
            lambda r: r[0].update(profile_id=r[1]["profile_id"]),
            lambda r: r[0].update(year="2020"),
            lambda r: r[0].update(LN="1000.5"),
            lambda r: r[0].update(age_ln_share_pct="{}"),
            lambda r: r[0].update(sex_ln_share_pct='{"0": 101, "1": -1}'),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                changed = [dict(row) for row in rows]
                mutate(changed)
                self.write_csv(self.profiles, changed)
                before = self.snapshot()
                result = self.run_command("--html-only")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.snapshot(), before)
        self.profiles.write_bytes(original)
        with self.cross.open(encoding="utf-8", newline="") as stream:
            cross = list(csv.DictReader(stream))
        cross[0]["LN"] = "501"
        self.write_csv(self.cross, cross)
        result = self.run_command("--html-only")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root / "cards").exists())

    def test_missing_browser_and_unknown_options_fail_without_writes(self):
        result = self.run_command("--browser", str(self.root / "missing-browser"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.snapshot(), self.before)
        result = self.run_command("--unknown-option")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.snapshot(), self.before)

    def test_optional_dependency_and_conflicting_options_fail_without_writes(self):
        cases = (
            ((), False, "PDF/PNG export needs --browser"),
            (("--html-only", "--browser", "unused"), False, "--browser cannot be combined"),
            (("--html-only", "--output", str(self.root / "absent/cards")), False, "Output parent must already exist"),
            (("--browser", "missing"), True, "PDF/PNG export requires PyMuPDF"),
        )
        for arguments, isolated, expected in cases:
            with self.subTest(arguments=arguments):
                result = self.run_command(*arguments, isolated=isolated)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(expected, result.stderr)
                self.assertEqual(self.snapshot(), self.before)

    def test_html_without_site_packages_accepts_valid_zero_compositions(self):
        with self.profiles.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        for row in rows:
            row.update(age_ln_share_pct='{"18-24": 100}',
                       sex_ln_share_pct='{"0": 0, "1": 100}')
        self.write_csv(self.profiles, rows)
        before = self.snapshot()
        result = self.run_command("--html-only", isolated=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        for index in range(1, 6):
            text = (self.root / f"cards/ficha_P{index:02d}.html").read_text(encoding="utf-8")
            self.assertIn("100.0%", text)
            self.assertIn("0.0%", text)

    @unittest.skipUnless(os.environ.get("T12_BROWSER"), "Set T12_BROWSER for real PDF/PNG integration")
    def test_actual_pdf_png_exports(self):
        import pymupdf
        result = self.run_command("--browser", os.environ["T12_BROWSER"])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / "cards/report.json").read_text())
        self.assertTrue(report["exported"])
        self.assertEqual(len(report["render_checks"]), 5)
        for index in range(1, 6):
            with pymupdf.open(self.root / f"cards/ficha_P{index:02d}.pdf") as doc:
                self.assertEqual(len(doc), 1)
                self.assertAlmostEqual(doc[0].rect.width, 612, delta=1)
                self.assertAlmostEqual(doc[0].rect.height, 792, delta=1)
                self.assertIn("Borrador interno", doc[0].get_text())
                self.assertIn("60.0%", doc[0].get_text())
            png = pymupdf.Pixmap(str(self.root / f"cards/ficha_P{index:02d}.png"))
            self.assertEqual((png.width, png.height), (2550, 3300))
            self.assertEqual((png.xres, png.yres), (300, 300))
        with pymupdf.open(self.root / "cards/cuaderno_fichas_todas.pdf") as doc:
            self.assertEqual(len(doc), 5)


if __name__ == "__main__":
    unittest.main()
