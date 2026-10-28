"""Configuration and opt-in runtime checks for the isolated card renderer."""

import errno
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("docker"), "Requires the Docker Compose client")
class ProfileCardsComposeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["docker", "compose", "--profile", "profile-cards", "config", "--format", "json"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.config = json.loads(result.stdout)

    def test_exporter_is_separate_opt_in_and_sandboxed(self):
        self.assertIn("profile-cards", self.config["services"])
        renderer = self.config["services"]["profile-cards"]
        self.assertEqual(renderer["profiles"], ["profile-cards"])
        self.assertEqual(renderer["build"]["dockerfile"], "Dockerfile.profile-cards")
        self.assertEqual(renderer["user"], "1000:1000")
        self.assertTrue(renderer["read_only"])
        self.assertEqual(renderer["network_mode"], "none")
        self.assertEqual(renderer["cap_drop"], ["ALL"])
        self.assertFalse(renderer.get("privileged", False))
        self.assertFalse(renderer.get("cap_add"))
        options = renderer["security_opt"]
        self.assertTrue(any(option.startswith("no-new-privileges") for option in options))
        self.assertTrue(any("profile-cards-seccomp.json" in option for option in options))
        self.assertFalse(any("unconfined" in option for option in options))
        self.assertEqual(renderer["environment"]["T12_BROWSER"], "/usr/bin/chromium")
        self.assertEqual(renderer["command"], [
            "python", "-B", "scripts/generate_profile_cards.py", "--browser", "/usr/bin/chromium",
        ])
        mounts = {item["target"]: item for item in renderer["volumes"]}
        for target in ("/workspace/scripts", "/workspace/tests",
                       "/workspace/outputs/t08_profiles_final",
                       "/workspace/outputs/profile_section_types_2024"):
            self.assertTrue(mounts[target]["read_only"], target)
            self.assertFalse(mounts[target]["bind"]["create_host_path"], target)
        self.assertFalse(mounts["/workspace/outputs"].get("read_only", False))
        self.assertNotIn("/workspace/data", mounts)
        analysis = self.config["services"]["analysis"]
        self.assertEqual(analysis["build"]["dockerfile"], "Dockerfile")
        self.assertEqual(analysis["network_mode"], "none")
        self.assertTrue(analysis["read_only"])
        self.assertEqual(analysis["environment"]["HACKATHON_CONTAINER_ROLE"], "analysis")

    def test_build_inputs_are_explicit_and_policy_fails_closed(self):
        dockerfile = (ROOT / "Dockerfile.profile-cards").read_text(encoding="utf-8")
        ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        self.assertIn("!Dockerfile.profile-cards", ignore)
        self.assertIn("!requirements-profile-cards.txt", ignore)
        self.assertIn("!docker/profile-cards-fonts.conf", ignore)
        self.assertIn("python:3.12.10-slim-bookworm@sha256:", dockerfile)
        self.assertIn("snapshot.debian.org", dockerfile)
        self.assertIn("requirements-profile-cards.txt", dockerfile)
        self.assertIn("chromium", dockerfile)
        self.assertIn("fonts-liberation2", dockerfile)
        self.assertNotIn("--no-sandbox", dockerfile)
        policy = json.loads((ROOT / "docker/profile-cards-seccomp.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["defaultAction"], "SCMP_ACT_ERRNO")
        allowed = {name for rule in policy["syscalls"]
                   if rule["action"] == "SCMP_ACT_ALLOW" and not rule.get("includes")
                   for name in rule["names"]}
        self.assertTrue({"clone", "setns", "unshare"} <= allowed)
        self.assertTrue({"mount", "bpf", "keyctl", "ptrace"}.isdisjoint(allowed))


@unittest.skipUnless(os.environ.get("HACKATHON_CONTAINER_ROLE") == "profile-cards",
                     "Requires the profile-cards Docker service")
class ProfileCardsRuntimeTests(unittest.TestCase):
    def test_nonroot_offline_readonly_runtime(self):
        self.assertEqual(sys.version_info[:2], (3, 12))
        self.assertNotEqual(sys.prefix, sys.base_prefix)
        self.assertNotEqual(os.getuid(), 0)
        status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines()
                      if ":" in line)
        self.assertEqual(int(status["CapEff"].strip(), 16), 0)
        self.assertEqual(status["NoNewPrivs"].strip(), "1")
        self.assertEqual(status["Seccomp"].strip(), "2")
        self.assertEqual({path.name for path in Path("/sys/class/net").iterdir()}, {"lo"})
        self.assertFalse(Path("/workspace/data").exists())
        for directory in ("/workspace/scripts", "/workspace/tests",
                          "/workspace/outputs/t08_profiles_final",
                          "/workspace/outputs/profile_section_types_2024"):
            with self.subTest(directory=directory):
                probe = Path(directory) / f".renderer-check-{uuid.uuid4().hex}"
                try:
                    with self.assertRaises(OSError) as rejected:
                        with probe.open("x", encoding="utf-8") as stream:
                            stream.write("synthetic mount check")
                    self.assertIn(rejected.exception.errno, (errno.EROFS, errno.EACCES))
                finally:
                    if probe.exists():
                        probe.unlink()

    def test_declared_linux_fonts_and_browser(self):
        for requested, expected in (("Arial", "Liberation Sans"), ("Georgia", "Liberation Serif")):
            result = subprocess.run(["fc-match", "-f", "%{family}", requested],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, expected)
        result = subprocess.run([os.environ["T12_BROWSER"], "--version"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Chromium", result.stdout)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "writable.txt"
            target.write_text("temporary renderer output", encoding="utf-8")
            self.assertEqual(target.read_text(encoding="utf-8"), "temporary renderer output")


if __name__ == "__main__":
    unittest.main()
