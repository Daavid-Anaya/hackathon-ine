"""Regressions derived from independent verification of the Linux renderer."""

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path("/workspace")
SCRIPT = ROOT / "scripts/generate_profile_cards.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    return {str(path): digest(path)
            for name in ("t08_profiles_final", "profile_section_types_2024", "t12_profile_cards")
            for path in (ROOT / "outputs" / name).rglob("*") if path.is_file()}


def run(*args):
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=180)


@unittest.skipUnless(os.environ.get("HACKATHON_CONTAINER_ROLE") == "profile-cards",
                     "Requires isolated renderer service")
class IndependentRendererTests(unittest.TestCase):
    def test_actual_export_rejection_and_integrity(self):
        import pymupdf

        with tempfile.TemporaryDirectory(prefix="independent-cards-") as temporary:
            output = Path(temporary) / "cards"
            before = protected()
            result = run("--browser", "/usr/bin/chromium", "--output", str(output))
            self.assertEqual((result.returncode, result.stderr), (0, ""))
            self.assertEqual(json.loads(result.stdout), {
                "profiles": 5, "exported": True, "output": str(output),
            })
            self.assertEqual(protected(), before)
            with (ROOT / "outputs/t08_profiles_final/profiles.csv").open(
                    encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            texts = []
            for index, million in enumerate(("13.3", "21.2", "23.1", "25.0", "15.8"), 1):
                stem = output / f"ficha_P{index:02d}"
                with pymupdf.open(stem.with_suffix(".pdf")) as pdf:
                    self.assertEqual(len(pdf), 1)
                    page = pdf[0]
                    self.assertEqual(tuple(page.rect), (0, 0, 612, 792))
                    text = page.get_text()
                    texts.append(text)
                    for expected in (f"{million} millones", "Borrador interno", "T14",
                                     "hipótesis", "No aplica", "Sin contacto individualizado"):
                        self.assertIn(expected, text)
                    for key in ("participation_pct", "ln_share_pct", "unspecified_pct"):
                        self.assertIn(f"{float(rows[index - 1][key]):.1f}%", text)
                    spans = [span for block in page.get_text("dict")["blocks"] if block["type"] == 0
                             for line in block["lines"] for span in line["spans"]
                             if span["text"].strip()]
                    self.assertGreaterEqual(min(span["size"] for span in spans), 8)
                    self.assertTrue(all(page.rect.contains(pymupdf.Rect(span["bbox"]))
                                        for span in spans))
                png = pymupdf.Pixmap(str(stem.with_suffix(".png")))
                self.assertEqual((png.width, png.height, png.xres, png.yres), (2550, 3300, 300, 300))
            with pymupdf.open(output / "cuaderno_fichas_todas.pdf") as notebook:
                self.assertEqual(len(notebook), 5)
                self.assertEqual([page.get_text() for page in notebook], texts)
            report = json.loads((output / "report.json").read_text())
            self.assertTrue(report["internal_only"])
            for name, expected in report["artifacts_sha256"].items():
                self.assertEqual(digest(output / name), expected)
            for name, directory in (("profiles.csv", "t08_profiles_final"),
                                    ("cross.csv", "profile_section_types_2024")):
                self.assertEqual(report["inputs_sha256"][name], digest(ROOT / "outputs" / directory / name))
            hashes = {path.name: digest(path) for path in output.iterdir()}
            cases = [("--browser", "/usr/bin/chromium", "--output", str(output))]
            # A fresh clone can have inputs without a retained canonical bundle yet.
            if (ROOT / "outputs/t12_profile_cards").exists():
                cases.append(())
            for arguments in cases:
                rejected = run(*arguments)
                self.assertEqual((rejected.returncode, rejected.stdout, rejected.stderr),
                                 (1, "", "Error: Output already exists; choose another --output\n"))
                self.assertEqual({path.name: digest(path) for path in output.iterdir()}, hashes)
                self.assertEqual(protected(), before)

    def test_inner_browser_sandbox(self):
        with tempfile.TemporaryDirectory(prefix="independent-sandbox-") as temporary:
            command = [
                "/usr/bin/chromium", "--headless=new", "--disable-gpu", "--no-first-run",
                "--no-default-browser-check", "--disable-extensions", "--disable-background-networking",
                "--host-resolver-rules=MAP * ~NOTFOUND", f"--user-data-dir={temporary}",
                "--allow-chrome-scheme-url", "--dump-dom", "chrome://sandbox/",
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stderr)
            for label in ("PID namespaces", "Network namespaces", "Seccomp-BPF sandbox",
                          "Seccomp-BPF sandbox supports TSYNC"):
                self.assertRegex(result.stdout, re.escape(label) + r"</td>\s*<td[^>]*>Yes</td>")
            self.assertRegex(result.stdout, r"Layer 1 Sandbox</td>\s*<td[^>]*>Namespace</td>")
            self.assertIn("You are adequately sandboxed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
