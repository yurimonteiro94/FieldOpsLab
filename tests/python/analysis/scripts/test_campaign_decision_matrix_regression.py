from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.python.test_support.json_tools import read_csv, read_json, write_csv, write_json, write_text
from tests.python.test_support.project_paths import ANALYSIS_SCRIPTS_DIR
from tests.python.test_support.script_runner import (
    assert_script_failure,
    assert_script_success,
    run_python_script,
)


class TestCampaignDecisionMatrixRegression(unittest.TestCase):
    def test_generator_reads_trigger_behavior_class_not_only_trigger_class(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            summary_json = temp_dir / "campaign_result_summary.json"
            semantic_json = temp_dir / "campaign_result_semantic_inspection.json"
            service_json = temp_dir / "service_delay_impact_audit.json"
            trigger_json = temp_dir / "policy_trigger_behavior_audit.json"

            output_md = temp_dir / "campaign_decision_matrix.md"
            output_json = temp_dir / "campaign_decision_matrix.json"
            output_csv = temp_dir / "campaign_decision_matrix.csv"

            write_json(
                summary_json,
                {
                    "rows": [
                        {
                            "batch_id": "campaign_travel_delay_only_moderate_batch",
                            "scenario_family_id": "travel_delay_only",
                            "severity_id": "moderate",
                            "recommendation_class": "replanning_tradeoff",
                            "recommended_policy_id": "threshold_delay_replanning_policy_v1",
                            "recommended_replanning_method_id": "greedy_replanning_solver_v1",
                            "has_clear_winner": True,
                            "mean_delta_objective_value": -52,
                            "mean_delta_makespan": 3,
                            "mean_delta_total_travel_time": -17,
                        }
                    ]
                },
            )

            write_json(
                semantic_json,
                {
                    "rows": [
                        {
                            "batch_id": "campaign_travel_delay_only_moderate_batch",
                            "scenario_family_id": "travel_delay_only",
                            "severity_id": "moderate",
                            "problem_count": 0,
                            "warning_count": 0,
                            "baseline_travel_delta": 50,
                            "baseline_service_delta": 0,
                        }
                    ]
                },
            )

            write_json(
                service_json,
                {
                    "rows": [
                        {
                            "batch_id": "campaign_travel_delay_only_moderate_batch",
                            "family": "travel_delay_only",
                            "severity": "moderate",
                            "service_effect_class": "not_service_related",
                            "service_warning_count": 0,
                            "warning_count": 0,
                        }
                    ]
                },
            )

            write_json(
                trigger_json,
                {
                    "rows": [
                        {
                            "batch_id": "campaign_travel_delay_only_moderate_batch",
                            "family": "travel_delay_only",
                            "severity": "moderate",
                            "option": "threshold_with_greedy_replanning",
                            "experiment_count": 3,
                            "policy_should_replan_count": 3,
                            "replanning_request_count": 3,
                            "replanning_success_count": 3,
                            "replanning_applied_count": 3,
                            "mean_delta_objective": -52,
                            "mean_delta_makespan": 3,
                            "mean_delta_travel": -17,
                            "mean_delta_service": 0,
                            "mean_delta_lateness": 0,
                            "trigger_behavior_class": "triggered_and_applied",
                            "warning_count": 0,
                            "warnings": "",
                        },
                        {
                            "batch_id": "campaign_travel_delay_only_moderate_batch",
                            "family": "travel_delay_only",
                            "severity": "moderate",
                            "option": "threshold_without_solver",
                            "experiment_count": 3,
                            "policy_should_replan_count": 3,
                            "replanning_request_count": 3,
                            "replanning_success_count": 0,
                            "replanning_applied_count": 0,
                            "mean_delta_objective": 15,
                            "mean_delta_makespan": 15,
                            "mean_delta_travel": 50,
                            "mean_delta_service": 0,
                            "mean_delta_lateness": 0,
                            "trigger_behavior_class": "triggered_without_solver",
                            "warning_count": 0,
                            "warnings": "",
                        },
                    ]
                },
            )

            result = run_python_script(
                ANALYSIS_SCRIPTS_DIR / "generate_campaign_decision_matrix.py",
                [
                    summary_json,
                    semantic_json,
                    service_json,
                    trigger_json,
                    output_md,
                    output_json,
                    output_csv,
                ],
            )

            assert_script_success(self, result)

            generated = read_json(output_json)
            rows = generated.get("rows", [])

            self.assertEqual(1, len(rows))

            row = rows[0]

            self.assertEqual(
                "triggered_and_applied",
                row.get("threshold_with_greedy_trigger_class"),
            )
            self.assertEqual(
                "triggered_without_solver",
                row.get("threshold_without_solver_trigger_class"),
            )
            self.assertEqual(6, row.get("threshold_should_replan_count"))
            self.assertEqual(6, row.get("threshold_request_count"))
            self.assertEqual(3, row.get("threshold_applied_count"))

            csv_rows = read_csv(output_csv)
            self.assertEqual(
                "triggered_and_applied",
                csv_rows[0].get("threshold_with_greedy_trigger_class"),
            )

    def test_verifier_rejects_empty_required_trigger_class(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            matrix_json = temp_dir / "campaign_decision_matrix.json"
            matrix_md = temp_dir / "campaign_decision_matrix.md"
            matrix_csv = temp_dir / "campaign_decision_matrix.csv"
            quality_md = temp_dir / "campaign_decision_matrix_quality_check.md"
            quality_json = temp_dir / "campaign_decision_matrix_quality_check.json"

            row = {
                "batch_id": "campaign_travel_delay_only_moderate_batch",
                "scenario_family_id": "travel_delay_only",
                "severity_id": "moderate",
                "recommendation_class": "replanning_tradeoff",
                "recommended_policy_id": "threshold_delay_replanning_policy_v1",
                "recommended_replanning_method_id": "greedy_replanning_solver_v1",
                "has_clear_winner": True,
                "mean_delta_objective_value": -52,
                "mean_delta_makespan": 3,
                "mean_delta_total_travel_time": -17,
                "semantic_status": "ok",
                "semantic_problem_count": 0,
                "semantic_warning_count": 0,
                "service_effect_class": "not_service_related",
                "service_warning_count": 0,
                "threshold_with_greedy_trigger_class": "",
                "threshold_without_solver_trigger_class": "triggered_without_solver",
                "threshold_should_replan_count": 6,
                "threshold_request_count": 6,
                "threshold_applied_count": 3,
                "provisional_action": "replan_candidate_with_makespan_monitoring",
                "evidence_strength": "medium",
                "methodological_caution": "test fixture",
            }

            write_json(
                matrix_json,
                {
                    "report_type": "fieldops_lab_campaign_decision_matrix",
                    "rows": [row],
                    "overview": {
                        "matrix_row_count": 1,
                    },
                },
            )
            write_text(matrix_md, "# FieldOps Lab campaign decision matrix\n")
            write_csv(matrix_csv, [row])

            result = run_python_script(
                ANALYSIS_SCRIPTS_DIR / "verify_campaign_decision_matrix.py",
                [
                    matrix_json,
                    matrix_md,
                    matrix_csv,
                    quality_md,
                    quality_json,
                ],
            )

            assert_script_failure(self, result)

            quality = read_json(quality_json)
            self.assertFalse(quality.get("all_required_checks_passed", True))
            self.assertGreater(quality.get("problem_count", 0), 0)


if __name__ == "__main__":
    unittest.main()