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


def project_path(*parts: str) -> str:
    return str(Path(*parts))


def npm_executable() -> str:
    if sys.platform.startswith("win"):
        return "npm.cmd"

    return "npm"


def quality_gate_steps(include_full_pipeline: bool) -> list[QualityGateStep]:
    steps = [
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
            command=[project_path("build", "fieldops_tests.exe")],
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
                project_path("tests", "python"),
                "-p",
                "test_*.py",
                "-v",
            ],
        ),
        QualityGateStep(
            name="web_build",
            command=[
                npm_executable(),
                "--prefix",
                project_path("apps", "web"),
                "run",
                "build",
            ],
        ),
        QualityGateStep(
            name="web_unit_tests",
            command=[
                npm_executable(),
                "--prefix",
                project_path("apps", "web"),
                "run",
                "test",
                "--",
                "--run",
            ],
        ),
        QualityGateStep(
            name="generate_test_inventory_report",
            command=[
                "py",
                "-3",
                project_path("analysis", "scripts", "generate_test_inventory_report.py"),
                project_path("analysis", "reports", "test_inventory_report.md"),
                project_path("analysis", "reports", "test_inventory_report.json"),
                project_path("analysis", "reports", "test_inventory_report.csv"),
            ],
        ),
        QualityGateStep(
            name="verify_test_inventory_report",
            command=[
                "py",
                "-3",
                project_path("analysis", "scripts", "verify_test_inventory_report.py"),
                project_path("analysis", "reports", "test_inventory_report.json"),
                project_path("analysis", "reports", "test_inventory_report.md"),
                project_path("analysis", "reports", "test_inventory_report.csv"),
                project_path("analysis", "reports", "test_inventory_quality_check.md"),
                project_path("analysis", "reports", "test_inventory_quality_check.json"),
            ],
        ),
    ]

    if include_full_pipeline:
        steps.extend(
            [
                QualityGateStep(
                    name="run_full_campaign_pipeline",
                    command=[
                        "py",
                        "-3",
                        project_path("analysis", "scripts", "run_full_campaign_pipeline.py"),
                        project_path("build", "fieldops_lab.exe"),
                    ],
                ),
                QualityGateStep(
                    name="verify_full_campaign_pipeline",
                    command=[
                        "py",
                        "-3",
                        project_path("analysis", "scripts", "verify_full_campaign_pipeline.py"),
                        project_path(
                            "analysis",
                            "reports",
                            "full_campaign_pipeline_manifest.json",
                        ),
                        project_path(
                            "analysis",
                            "reports",
                            "full_campaign_pipeline_report.md",
                        ),
                        project_path(
                            "analysis",
                            "reports",
                            "full_campaign_pipeline_log.txt",
                        ),
                        project_path(
                            "analysis",
                            "reports",
                            "full_campaign_pipeline_quality_check.md",
                        ),
                        project_path(
                            "analysis",
                            "reports",
                            "full_campaign_pipeline_quality_check.json",
                        ),
                    ],
                ),
            ]
        )

    steps.extend(
        [
            QualityGateStep(
                name="generate_ranking_sensitive_scenario_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "generate_ranking_sensitive_scenario_report.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.csv",
                    ),
                ],
            ),
            QualityGateStep(
                name="verify_ranking_sensitive_scenario_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "verify_ranking_sensitive_scenario_report.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_report.csv",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_quality_check.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitive_scenario_quality_check.json",
                    ),
                ],
            ),
            QualityGateStep(
                name="generate_ranking_sensitivity_explanation_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "generate_ranking_sensitivity_explanation_report.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.csv",
                    ),
                ],
            ),
            QualityGateStep(
                name="verify_ranking_sensitivity_explanation_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "verify_ranking_sensitivity_explanation_report.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_report.csv",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_quality_check.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "ranking_sensitivity_explanation_quality_check.json",
                    ),
                ],
            ),
            QualityGateStep(
                name="generate_experimental_design_matrix",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "generate_experimental_design_matrix.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.csv",
                    ),
                ],
            ),
            QualityGateStep(
                name="verify_experimental_design_matrix",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "verify_experimental_design_matrix.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix.csv",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix_quality_check.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "experimental_design_matrix_quality_check.json",
                    ),
                ],
            ),
            QualityGateStep(
                name="generate_project_status_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "generate_project_status_report.py",
                    ),
                    project_path("analysis", "reports", "project_status_report.md"),
                    project_path("analysis", "reports", "project_status_report.json"),
                    project_path("analysis", "reports", "project_status_report.csv"),
                ],
            ),
            QualityGateStep(
                name="verify_project_status_report",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "verify_project_status_report.py",
                    ),
                    project_path("analysis", "reports", "project_status_report.json"),
                    project_path("analysis", "reports", "project_status_report.md"),
                    project_path("analysis", "reports", "project_status_report.csv"),
                    project_path(
                        "analysis",
                        "reports",
                        "project_status_quality_check.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "project_status_quality_check.json",
                    ),
                ],
            ),
            QualityGateStep(
                name="generate_scientific_validation_plan",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "generate_scientific_validation_plan.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.csv",
                    ),
                ],
            ),
            QualityGateStep(
                name="verify_scientific_validation_plan",
                command=[
                    "py",
                    "-3",
                    project_path(
                        "analysis",
                        "scripts",
                        "verify_scientific_validation_plan.py",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.json",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan.csv",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan_quality_check.md",
                    ),
                    project_path(
                        "analysis",
                        "reports",
                        "scientific_validation_plan_quality_check.json",
                    ),
                ],
            ),
        ]
    )

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
        help="Run the structural quality gate without executing the full campaign pipeline.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    include_full_pipeline = not args.quick
    return run_quality_gate(include_full_pipeline=include_full_pipeline)


if __name__ == "__main__":
    raise SystemExit(main())