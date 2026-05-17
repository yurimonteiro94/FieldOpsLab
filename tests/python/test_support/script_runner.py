from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from typing import Sequence

from tests.python.test_support.project_paths import PROJECT_ROOT


def run_python_script(
    script_path: Path,
    args: Sequence[Path | str],
    timeout_seconds: int = 60,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(script_path), *[str(arg) for arg in args]]

    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
    )


def assert_script_success(
    test_case: unittest.TestCase,
    result: subprocess.CompletedProcess[str],
) -> None:
    if result.returncode != 0:
        test_case.fail(
            "Expected script to succeed, but it failed.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def assert_script_failure(
    test_case: unittest.TestCase,
    result: subprocess.CompletedProcess[str],
) -> None:
    if result.returncode == 0:
        test_case.fail(
            "Expected script to fail, but it succeeded.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )