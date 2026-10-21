import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "download_ccpc.py"


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("download_ccpc", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_download_preserves_bytes_and_records_provenance(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("dictionary.txt", "Aggregate counts only")
        original = payload.getvalue()
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.zip"
            with patch.object(self.module, "urlopen", return_value=io.BytesIO(original)):
                receipt = self.module.acquire("https://portal.ine.mx/source.zip", destination)
            self.assertEqual(destination.read_bytes(), original)
            self.assertEqual(receipt["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(receipt["bytes"], len(original))
            self.assertEqual(receipt["members"], ["dictionary.txt"])
            self.assertEqual(receipt["url"], "https://portal.ine.mx/source.zip")
            self.assertTrue(receipt["downloaded_at_utc"].endswith("+00:00"))

    def test_existing_original_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.zip"
            destination.write_bytes(b"original")
            with self.assertRaises(FileExistsError):
                self.module.acquire("https://portal.ine.mx/source.zip", destination)
            self.assertEqual(destination.read_bytes(), b"original")

    def test_invalid_archive_leaves_no_original_or_partial_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.zip"
            with patch.object(self.module, "urlopen", return_value=io.BytesIO(b"<html>error</html>")):
                with self.assertRaises(zipfile.BadZipFile):
                    self.module.acquire("https://portal.ine.mx/source.zip", destination)
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_interrupted_partial_is_preserved_without_blocking_new_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "manual.pdf"
            partial = Path(temporary) / "manual.pdf.part"
            partial.write_bytes(b"interrupted")
            original = b"%PDF-1.7\nfixture"
            with patch.object(self.module, "urlopen", return_value=io.BytesIO(original)):
                self.module.acquire("https://portal.ine.mx/manual.pdf", destination)
            self.assertEqual(destination.read_bytes(), original)
            self.assertEqual(partial.read_bytes(), b"interrupted")

    def test_invalid_pdf_and_timeout_preserve_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / "original.zip"
            existing.write_bytes(b"untouched")
            destination = root / "manual.pdf"
            with patch.object(self.module, "urlopen", return_value=io.BytesIO(b"<html>error</html>")):
                with self.assertRaisesRegex(ValueError, "Se esperaba una firma PDF"):
                    self.module.acquire("https://portal.ine.mx/manual.pdf", destination)
            with patch.object(self.module, "urlopen", side_effect=TimeoutError("fixture timeout")):
                with self.assertRaisesRegex(TimeoutError, "fixture timeout"):
                    self.module.acquire("https://portal.ine.mx/manual.pdf", destination)
            self.assertEqual(list(root.iterdir()), [existing])
            self.assertEqual(existing.read_bytes(), b"untouched")

    def test_batch_rechecks_originals_without_network_or_manifest_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = {"election_year": None, "url": "https://portal.ine.mx/manual.pdf"}
            with patch.object(self.module, "ROOT", root), patch.object(self.module, "SOURCES", [source]):
                with patch.object(self.module, "urlopen", return_value=io.BytesIO(b"%PDF-1.7\nfixture")):
                    self.module.main()
                manifest = root / "data" / "sources.json"
                before = manifest.read_bytes()
                with patch.object(self.module, "urlopen") as network:
                    self.module.main()
                    network.assert_not_called()
                self.assertEqual(manifest.read_bytes(), before)
                receipt = json.loads(before)[0]
                self.assertEqual(receipt["local_path"], "data/raw/manual.pdf")
                self.assertEqual(receipt["landing_url"], self.module.LANDING)
                original = root / receipt["local_path"]
                original.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "Archivo original sin registro o modificado"):
                    self.module.main()
                self.assertEqual(original.read_bytes(), b"changed")
                self.assertEqual(manifest.read_bytes(), before)

    def test_inspection_verifies_hash_and_reads_documentation_not_records(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("01_descripcioncampos.txt", "Totals by age and territory")
            archive.writestr("state.csv", "AGE,TOTAL\nprivate-record-not-for-output\n")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = {"election_year": 2024, "url": "https://portal.ine.mx/fixture.zip"}
            with patch.object(self.module, "ROOT", root), patch.object(self.module, "SOURCES", [source]):
                with patch.object(self.module, "urlopen", return_value=io.BytesIO(payload.getvalue())):
                    self.module.main()
                report = self.module.inspect_sources()
                self.assertEqual(report[0]["csv_count"], 1)
                self.assertEqual(report[0]["csv_header"], "AGE,TOTAL")
                self.assertEqual(report[0]["documentation"][0]["text"], "Totals by age and territory")
                self.assertNotIn("private-record", json.dumps(report))
                (root / "data" / "raw" / "fixture.zip").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "Falló la comprobación de integridad"):
                    self.module.inspect_sources()


if __name__ == "__main__":
    unittest.main()
