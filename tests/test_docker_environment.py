import errno
import os
from pathlib import Path
import tempfile
import unittest
import uuid


@unittest.skipUnless(
    os.environ.get("HACKATHON_CONTAINER_ROLE") == "analysis",
    "Requiere el servicio analysis de Docker Compose",
)
class DockerEnvironmentTests(unittest.TestCase):
    def test_container_does_not_run_as_root(self):
        self.assertNotEqual(os.getuid(), 0)

    def test_code_and_originals_reject_writes(self):
        for directory in ("/workspace/scripts", "/workspace/data", "/workspace/data/raw"):
            with self.subTest(directory=directory):
                probe = Path(directory) / f".docker-check-{uuid.uuid4().hex}"
                try:
                    try:
                        with probe.open("x", encoding="utf-8") as stream:
                            stream.write("synthetic boundary check")
                    except OSError as error:
                        self.assertIn(error.errno, (errno.EROFS, errno.EACCES))
                    else:
                        self.fail(f"Se esperaba un montaje de solo lectura: {directory}")
                finally:
                    if probe.exists():
                        probe.unlink()

    def test_generated_directories_are_writable(self):
        for directory in ("/workspace/data/processed", "/workspace/outputs"):
            with self.subTest(directory=directory):
                with tempfile.TemporaryDirectory(prefix=".docker-check-", dir=directory) as temporary:
                    result = Path(temporary) / "synthetic.txt"
                    result.write_text("synthetic output", encoding="utf-8")
                    self.assertEqual(result.read_text(encoding="utf-8"), "synthetic output")


if __name__ == "__main__":
    unittest.main()
