import json
from importlib.metadata import version
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


class EnvironmentTests(unittest.TestCase):
    def test_public_help_uses_spanish_descriptions(self):
        root = Path(__file__).resolve().parents[1]
        descriptions = {
            "check_environment.py": "Comprueba Python, Pandas y Scikit-learn con datos sintéticos",
            "download_ccpc.py": "Descarga las fuentes oficiales CCPC de 2009–2024 sin extraerlas.",
        }
        for script, description in descriptions.items():
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(root / "scripts" / script), "--help"],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                help_text = " ".join(result.stdout.split())
                self.assertIn(description, help_text)
                if script == "download_ccpc.py":
                    self.assertIn("--inspect", help_text)
                    self.assertIn("Verifica los hashes sin conexión", help_text)

    def test_public_inspection_error_is_spanish_and_preserves_manifest(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "scripts").mkdir()
            data = workspace / "data"
            data.mkdir()
            script = workspace / "scripts" / "download_ccpc.py"
            shutil.copy2(root / "scripts" / "download_ccpc.py", script)
            manifest = data / "sources.json"
            manifest.write_bytes(b"[]")
            result = subprocess.run(
                [sys.executable, str(script), "--inspect"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("El manifiesto no contiene las siete fuentes esperadas", result.stderr)
            self.assertEqual(manifest.read_bytes(), b"[]")
            self.assertEqual(list(data.iterdir()), [manifest])

    def test_installed_versions_match_the_hashed_lock(self):
        root = Path(__file__).resolve().parents[1]
        lock = (root / "requirements.txt").read_text(encoding="utf-8")
        pins = re.findall(r"^([\w-]+)==(\S+)", lock, re.MULTILINE)
        self.assertTrue({"pandas", "scikit-learn"} <= dict(pins).keys())
        self.assertNotEqual(sys.prefix, sys.base_prefix)
        for name, pinned in pins:
            with self.subTest(package=name):
                self.assertEqual(version(name), pinned)
        for block in re.split(r"(?m)^(?=[\w-]+==)", lock)[1:]:
            self.assertRegex(block, r"--hash=sha256:[0-9a-f]{64}(?:\s|$)")

    def test_commands_reject_explicit_invalid_options(self):
        root = Path(__file__).resolve().parents[1]
        for script in ("download_ccpc.py", "check_environment.py"):
            for argument in ("--unexpected", "--inspect=false"):
                with self.subTest(script=script, argument=argument):
                    result = subprocess.run(
                        [sys.executable, str(root / "scripts" / script), argument],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("error:", result.stderr)

    def test_public_smoke_command_checks_both_libraries(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "check_environment.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["smoke_test"], "ok")
        self.assertEqual(report["python"], ".".join(map(str, sys.version_info[:3])))
        self.assertTrue(report["pandas"])
        self.assertTrue(report["scikit-learn"])
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
