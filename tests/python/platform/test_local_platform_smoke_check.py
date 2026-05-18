from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMOKE_CHECK_SCRIPT = (
    PROJECT_ROOT / "analysis" / "scripts" / "run_local_platform_smoke_check.py"
)


class LocalPlatformSmokeCheckTests(unittest.TestCase):
    def test_smoke_check_script_exists(self) -> None:
        self.assertTrue(SMOKE_CHECK_SCRIPT.exists())

    def test_smoke_check_script_uses_safe_subprocess_invocation(self) -> None:
        source = SMOKE_CHECK_SCRIPT.read_text(encoding="utf-8").lower()

        self.assertIn("subprocess.popen", source)
        self.assertNotIn("shell=true", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("exec(", source)

    def test_smoke_check_script_validates_read_only_contract(self) -> None:
        source = SMOKE_CHECK_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("allows_arbitrary_command_execution", source)
        self.assertIn("read_only", source)
        self.assertIn("POST", source)
        self.assertIn("405", source)
        self.assertIn("/api/v1/health", source)
        self.assertIn("/api/v1/project-status", source)
        self.assertIn("/api/v1/reports", source)
        self.assertIn("/api/v1/experimental-design-matrix", source)

    def test_local_platform_smoke_check_passes(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SMOKE_CHECK_SCRIPT),
                "--timeout-seconds",
                "15",
            ],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )

        self.assertEqual(
            completed.returncode,
            0,
            msg=(
                "Local platform smoke check failed.\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            ),
        )

        self.assertIn(
            "FieldOps Lab local platform smoke check passed.",
            completed.stdout,
        )
        self.assertIn("/api/v1/health 200", completed.stdout)
        self.assertIn("/api/v1/project-status 200", completed.stdout)
        self.assertIn("/api/v1/reports 200", completed.stdout)
        self.assertIn("/api/v1/experimental-design-matrix 200", completed.stdout)
        self.assertIn("POST /api/v1/health 405", completed.stdout)


if __name__ == "__main__":
    unittest.main()