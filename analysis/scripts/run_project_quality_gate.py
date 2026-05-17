from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class QualityGateStep:
    name: str
    command: list[str]


def _path(*parts: str) -> str:
    return str(Path(*parts))


def _base_steps() -> list[QualityGateStep]:
    return [
        QualityGateStep(
            name="cmake_configure",
            command=["cmake", "-S", ".", "-B", "build", "-G", "Ninja"],
        ),
        QualityGateStep(
            name="cmake_build",
            command=["cmake", "--build", "build"],
        ),
        QualityGateStep(
            name="fieldops_cpp_tests",
            command=[_path("build", "fieldops_tests.exe")],
        ),
        QualityGateStep(
            name="ctest",
            command=["ctest", "--test-dir", "build", "--output-on-failure"],
        ),
        QualityGateStep(
            name="python_unittest",
            command=[
                "py",
                "-3",
                "-m",
                "unittest",
                "discover",
                "-s",
                _path("tests", "python"),
                "-p",
                "test_*.py",
                "-v",
            ],
        ),
    ]


def _test_inventory_steps() -> list[QualityGateStep]:
    return [
        QualityGateStep(
            name="generate_test_inventory_report",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "generate_test_inventory_report.py"),
                _path("analysis", "reports", "test_inventory_report.md"),
                _path("analysis", "reports", "test_inventory_report.json"),
                _path("analysis", "reports", "test_inventory_report.csv"),
            ],
        ),
        QualityGateStep(
            name="verify_test_inventory_report",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "verify_test_inventory_report.py"),
                _path("analysis", "reports", "test_inventory_report.json"),
                _path("analysis", "reports", "test_inventory_report.md"),
                _path("analysis", "reports", "test_inventory_report.csv"),
                _path("analysis", "reports", "test_inventory_quality_check.md"),
                _path("analysis", "reports", "test_inventory_quality_check.json"),
            ],
        ),
    ]


def _full_campaign_pipeline_steps() -> list[QualityGateStep]:
    return [
        QualityGateStep(
            name="run_full_campaign_pipeline",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "run_full_campaign_pipeline.py"),
                _path("build", "fieldops_lab.exe"),
            ],
        ),
        QualityGateStep(
            name="verify_full_campaign_pipeline",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "verify_full_campaign_pipeline.py"),
                _path("analysis", "reports", "full_campaign_pipeline_manifest.json"),
                _path("analysis", "reports", "full_campaign_pipeline_report.md"),
                _path("analysis", "reports", "full_campaign_pipeline_log.txt"),
                _path("analysis", "reports", "full_campaign_pipeline_quality_check.md"),
                _path("analysis", "reports", "full_campaign_pipeline_quality_check.json"),
            ],
        ),
    ]


def _project_status_steps() -> list[QualityGateStep]:
    return [
        QualityGateStep(
            name="generate_project_status_report",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "generate_project_status_report.py"),
                _path("analysis", "reports", "project_status_report.md"),
                _path("analysis", "reports", "project_status_report.json"),
                _path("analysis", "reports", "project_status_report.csv"),
            ],
        ),
        QualityGateStep(
            name="verify_project_status_report",
            command=[
                "py",
                "-3",
                _path("analysis", "scripts", "verify_project_status_report.py"),
                _path("analysis", "reports", "project_status_report.json"),
                _path("analysis", "reports", "project_status_report.md"),
                _path("analysis", "reports", "project_status_report.csv"),
                _path("analysis", "reports", "project_status_quality_check.md"),
                _path("analysis", "reports", "project_status_quality_check.json"),
            ],
        ),
    ]


def quality_gate_steps(include_full_pipeline: bool) -> list[QualityGateStep]:
    steps = []
    steps.extend(_base_steps())
    steps.extend(_test_inventory_steps())

    if include_full_pipeline:
        steps.extend(_full_campaign_pipeline_steps())

    steps.extend(_project_status_steps())
    return steps


def print_step_header(index: int, total: int, step: QualityGateStep) -> None:
    print("")
    print(f"===== QUALITY GATE STEP {index}/{total}: {step.name} =====")
    print(" ".join(step.command))
    print("")


def run_quality_gate(include_full_pipeline: bool) -> int:
    steps = quality_gate_steps(include_full_pipeline=include_full_pipeline)

    for index, step in enumerate(steps, start=1):
        print_step_header(index, len(steps), step)

        completed = subprocess.run(
            step.command,
            cwd=PROJECT_ROOT,
            shell=False,
        )

        if completed.returncode != 0:
            print("")
            print(f"ERROR: quality gate failed at step: {step.name}", file=sys.stderr)
            print(f"Return code: {completed.returncode}", file=sys.stderr)
            return completed.returncode

    print("")
    print("QUALITY GATE PASSED.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the FieldOps Lab project quality gate."
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help=(
            "Run build, C++ tests, CTest, Python tests, test inventory, "
            "and project status, but skip the full campaign pipeline."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    include_full_pipeline = not args.quick
    return run_quality_gate(include_full_pipeline=include_full_pipeline)


if __name__ == "__main__":
    raise SystemExit(main())