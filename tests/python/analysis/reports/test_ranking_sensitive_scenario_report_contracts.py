from __future__ import annotations

import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]

GENERATOR_SCRIPT = (
    PROJECT_ROOT
    / "analysis"
    / "scripts"
    / "generate_ranking_sensitive_scenario_report.py"
)

VERIFIER_SCRIPT = (
    PROJECT_ROOT
    / "analysis"
    / "scripts"
    / "verify_ranking_sensitive_scenario_report.py"
)


VALID_SENSITIVITY_REASONS = {
    "recommended_policy_changes_across_profiles",
    "same_policy_but_recommendation_class_changes_across_profiles",
    "ranking_summary_marked_as_not_stable",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        shell=False,
    )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "ranking_profile_count",
        "sensitive_to_ranking_profile",
        "sensitivity_reason",
        "unique_recommended_policy_count",
        "unique_recommendation_class_count",
        "recommended_policies",
        "recommendation_classes",
        "stability_class",
        "investigation_status",
        "interpretation",
        "recommended_profile_policy_pairs",
        "scenario_id",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_minimum_valid_markdown(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        "\n".join(
            [
                "# FieldOps Lab ranking-sensitive scenario report",
                "",
                "## Input status",
                "",
                "## Overall result",
                "",
                "## Sensitive scenarios",
                "",
                "## Required investigation",
                "",
                "## Conservative interpretation",
                "",
            ]
        ),
        encoding="utf-8",
    )


class RankingSensitiveScenarioReportContractTests(unittest.TestCase):
    def test_ranking_sensitive_scenario_report_scripts_compile_and_have_main_guard(
        self,
    ) -> None:
        compile_result = run_command(
            [
                "py",
                "-3",
                "-m",
                "py_compile",
                str(GENERATOR_SCRIPT),
                str(VERIFIER_SCRIPT),
            ]
        )

        self.assertEqual(
            compile_result.returncode,
            0,
            compile_result.stderr + compile_result.stdout,
        )

        generator_source = GENERATOR_SCRIPT.read_text(encoding="utf-8")
        verifier_source = VERIFIER_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('if __name__ == "__main__":', generator_source)
        self.assertIn("raise SystemExit(main())", generator_source)

        self.assertIn('if __name__ == "__main__":', verifier_source)
        self.assertIn("raise SystemExit(main())", verifier_source)

    def test_generator_and_verifier_accept_current_ranking_sensitive_scenario_report(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp_path = Path(temporary_directory)

            output_md = temp_path / "ranking_sensitive_scenario_report.md"
            output_json = temp_path / "ranking_sensitive_scenario_report.json"
            output_csv = temp_path / "ranking_sensitive_scenario_report.csv"
            quality_md = temp_path / "ranking_sensitive_scenario_quality_check.md"
            quality_json = temp_path / "ranking_sensitive_scenario_quality_check.json"

            generate_result = run_command(
                [
                    "py",
                    "-3",
                    str(GENERATOR_SCRIPT),
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ]
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = run_command(
                [
                    "py",
                    "-3",
                    str(VERIFIER_SCRIPT),
                    str(output_json),
                    str(output_md),
                    str(output_csv),
                    str(quality_md),
                    str(quality_json),
                ]
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            quality_report = json.loads(quality_json.read_text(encoding="utf-8"))

            self.assertEqual(
                report["report_type"],
                "ranking_sensitive_scenario_report",
            )

            self.assertTrue(report["input_status"]["all_required_inputs_available"])
            self.assertTrue(report["input_status"]["source_exists"])
            self.assertTrue(report["input_status"]["source_has_summary_rows"])
            self.assertTrue(report["input_status"]["source_has_ranking_rows"])

            summary = report["summary"]

            self.assertGreater(summary["scenario_summary_count"], 0)
            self.assertGreater(summary["ranking_row_count"], 0)
            self.assertGreater(summary["ranking_profile_count"], 0)

            self.assertGreaterEqual(summary["sensitive_scenario_count"], 1)
            self.assertGreaterEqual(
                summary["class_change_sensitive_scenario_count"],
                1,
            )

            self.assertEqual(
                summary["sensitive_scenario_count"]
                + summary["stable_scenario_count"],
                summary["scenario_summary_count"],
            )

            self.assertEqual(
                summary["ranking_fragility_status"],
                "some_scenarios_sensitive_to_ranking_profile",
            )

            sensitive_scenarios = report["sensitive_scenarios"]

            self.assertEqual(
                len(sensitive_scenarios),
                summary["sensitive_scenario_count"],
            )

            observed_reasons = {
                scenario["sensitivity_reason"] for scenario in sensitive_scenarios
            }

            self.assertTrue(
                observed_reasons.issubset(VALID_SENSITIVITY_REASONS),
                observed_reasons,
            )

            self.assertIn(
                "same_policy_but_recommendation_class_changes_across_profiles",
                observed_reasons,
            )

            for scenario in sensitive_scenarios:
                self.assertTrue(scenario["sensitive_to_ranking_profile"])
                self.assertGreater(scenario["ranking_profile_count"], 0)
                self.assertGreaterEqual(
                    scenario["unique_recommended_policy_count"],
                    1,
                )
                self.assertGreaterEqual(
                    scenario["unique_recommendation_class_count"],
                    1,
                )
                self.assertTrue(scenario["recommended_policies"])
                self.assertTrue(scenario["recommendation_classes"])
                self.assertTrue(scenario["investigation_status"])
                self.assertTrue(scenario["interpretation"])

                if (
                    scenario["sensitivity_reason"]
                    == "recommended_policy_changes_across_profiles"
                ):
                    self.assertGreaterEqual(
                        scenario["unique_recommended_policy_count"],
                        2,
                    )
                    self.assertGreaterEqual(
                        len(scenario["recommended_policies"]),
                        2,
                    )
                    self.assertEqual(
                        scenario["investigation_status"],
                        "requires_policy_change_explanation",
                    )

                if (
                    scenario["sensitivity_reason"]
                    == "same_policy_but_recommendation_class_changes_across_profiles"
                ):
                    self.assertGreaterEqual(
                        scenario["unique_recommendation_class_count"],
                        2,
                    )
                    self.assertGreaterEqual(
                        len(scenario["recommendation_classes"]),
                        2,
                    )
                    self.assertEqual(
                        scenario["investigation_status"],
                        "requires_recommendation_class_explanation",
                    )

            self.assertTrue(quality_report["all_required_checks_passed"])
            self.assertEqual(quality_report["problem_count"], 0)

    def test_verifier_rejects_invalid_sensitive_scenario_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp_path = Path(temporary_directory)

            input_json = temp_path / "ranking_sensitive_scenario_report.json"
            input_md = temp_path / "ranking_sensitive_scenario_report.md"
            input_csv = temp_path / "ranking_sensitive_scenario_report.csv"
            quality_md = temp_path / "ranking_sensitive_scenario_quality_check.md"
            quality_json = temp_path / "ranking_sensitive_scenario_quality_check.json"

            invalid_scenario = {
                "batch_id": "invalid_batch",
                "scenario_id": "invalid_scenario",
                "scenario_family_id": "service_delay_only",
                "severity_id": "moderate",
                "ranking_profile_count": 4,
                "sensitive_to_ranking_profile": True,
                "sensitivity_reason": (
                    "same_policy_but_recommendation_class_changes_across_profiles"
                ),
                "unique_recommended_policy_count": 1,
                "unique_recommendation_class_count": 1,
                "recommended_policies": ["no_replanning_policy_v1"],
                "recommendation_classes": ["weak_or_tied"],
                "stability_class": "same_policy_different_class",
                "recommended_profile_policy_pairs": (
                    "balanced_operational=no_replanning_policy_v1+"
                    "replanning_not_implemented_v1"
                ),
                "investigation_status": "requires_recommendation_class_explanation",
                "interpretation": "Invalid class-sensitive row for verifier test.",
            }

            report = {
                "report_type": "ranking_sensitive_scenario_report",
                "generated_at_local": "2026-01-01T00:00:00",
                "input_status": {
                    "all_required_inputs_available": True,
                    "source_path": "analysis/reports/campaign_ranking_profile_sensitivity.json",
                    "source_exists": True,
                    "source_report_type": "campaign_ranking_profile_sensitivity",
                    "source_scenario_summary_count": 1,
                    "source_ranking_row_count": 4,
                    "source_ranking_profile_count": 4,
                    "source_has_summary_rows": True,
                    "source_has_ranking_rows": True,
                },
                "summary": {
                    "scenario_summary_count": 1,
                    "ranking_row_count": 4,
                    "ranking_profile_count": 4,
                    "sensitive_scenario_count": 1,
                    "policy_change_sensitive_scenario_count": 0,
                    "class_change_sensitive_scenario_count": 1,
                    "stable_scenario_count": 0,
                    "ranking_fragility_status": (
                        "some_scenarios_sensitive_to_ranking_profile"
                    ),
                },
                "sensitive_scenarios": [invalid_scenario],
                "interpretation": {
                    "conservative_reading": "Invalid test fixture.",
                    "scientific_warning": "Invalid test fixture.",
                },
            }

            write_json(input_json, report)
            write_minimum_valid_markdown(input_md)

            csv_row = dict(invalid_scenario)
            csv_row["recommended_policies"] = "no_replanning_policy_v1"
            csv_row["recommendation_classes"] = "weak_or_tied"
            write_csv(input_csv, [csv_row])

            verify_result = run_command(
                [
                    "py",
                    "-3",
                    str(VERIFIER_SCRIPT),
                    str(input_json),
                    str(input_md),
                    str(input_csv),
                    str(quality_md),
                    str(quality_json),
                ]
            )

            self.assertNotEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            output = verify_result.stderr + verify_result.stdout

            self.assertIn(
                "unique_recommendation_class_count must be at least 2",
                output,
            )
            self.assertIn(
                "recommendation_classes must contain at least 2 classes",
                output,
            )


if __name__ == "__main__":
    unittest.main()