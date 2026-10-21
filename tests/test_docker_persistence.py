import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(
    os.environ.get("RUN_DOCKER_HOST_PROBES") == "1",
    "Prueba opcional de persistencia desde el equipo anfitrión; requiere la imagen local construida",
)
class DockerPersistenceTests(unittest.TestCase):
    def test_persistence_and_original_integrity_in_isolated_workspace(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="hackathon-docker-") as temporary:
            root = Path(temporary)
            for name in ("compose.yaml", "requirements.txt"):
                shutil.copy2(source / name, root / name)
            for name in ("scripts", "tests"):
                shutil.copytree(source / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
            for name in ("data/raw", "data/processed", "outputs"):
                (root / name).mkdir(parents=True, exist_ok=True)
            original = root / "data/raw/synthetic.bin"
            manifest = root / "data/sources.json"
            original.write_bytes(b"synthetic original")
            manifest.write_bytes(b"[]")

            def hashes():
                return [hashlib.sha256(path.read_bytes()).hexdigest() for path in (original, manifest)]

            def run_python(code, service="analysis"):
                profile = ["--profile", "download"] if service == "download" else []
                result = subprocess.run(
                    ["docker", "compose", *profile, "run", "--rm", "-T", service, "python", "-"],
                    cwd=root, input=code, text=True, capture_output=True, timeout=120,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            before = hashes()
            run_python("""import errno
from pathlib import Path
for name in ('data/raw/synthetic.bin', 'data/sources.json'):
    try:
        Path(name).write_bytes(b'forbidden')
    except OSError as error:
        assert error.errno == errno.EROFS
    else:
        raise AssertionError('Se esperaba un archivo original de solo lectura: ' + name)
for name in ('outputs/result.bin', 'data/processed/table.bin', '/tmp/ephemeral.bin'):
    Path(name).write_bytes(bytes(range(256)))
""")
            self.assertEqual(hashes(), before)
            for name in ("outputs/result.bin", "data/processed/table.bin"):
                self.assertEqual((root / name).read_bytes(), bytes(range(256)))
            second = run_python("""import json
from pathlib import Path
assert not Path('/tmp/ephemeral.bin').exists()
print(json.dumps([Path(name).read_bytes().hex() for name in
                  ('outputs/result.bin', 'data/processed/table.bin')]))
""")
            self.assertEqual(json.loads(second), [bytes(range(256)).hex()] * 2)
            run_python("""from pathlib import Path
pending = Path('data/sources.json.part')
pending.write_bytes(b'[]')
pending.replace('data/sources.json')
Path('data/raw/download-sentinel').write_bytes(b'synthetic only')
""", service="download")
            self.assertEqual(hashes(), before)
            self.assertFalse((root / "data/sources.json.part").exists())
            self.assertEqual((root / "data/raw/download-sentinel").read_bytes(), b"synthetic only")


if __name__ == "__main__":
    unittest.main()
