import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"


REQUIRED_QUALITY_REPORTS = [
    "experiment_campaign_plan_quality_check.json",
    "campaign_batch_blueprint_quality_check.json",
    "campaign_perturbation_plan_quality_check.json",
    "campaign_executable_batch_config_quality_check.json",
    "campaign_execution_quality_check.json",
    "campaign_result_summary_quality_check.json",
    "campaign_result_semantic_inspection.json",
    "service_delay_impact_audit_quality_check.json",
    "policy_trigger_behavior_audit_quality_check.json",
    "campaign_decision_matrix_quality_check.json",
    "campaign_ranking_profile_sensitivity_quality_check.json",
    "campaign_final_ranking_integration_quality_check.json",
    "campaign_final_diagnostic_report_quality_check.json",
    "full_campaign_pipeline_quality_check.json",
]


class QualityReportContractTests(unittest.TestCase):
    def test_required_quality_reports_exist_and_pass(self) -> None:
        for file_name in REQUIRED_QUALITY_REPORTS:
            with self.subTest(file_name=file_name):
                path = REPORTS_DIR / file_name

                self.assertTrue(path.exists(), f"Missing quality report: {path}")

                data = json.loads(path.read_text(encoding="utf-8"))

                pass_keys = [
                    "all_required_checks_passed",
                    "all_semantic_checks_passed",
                ]

                pass_values = [data.get(key) for key in pass_keys if key in data]

                self.assertTrue(
                    pass_values,
                    f"Quality report does not expose a recognized pass flag: {path}",
                )

                self.assertTrue(
                    any(bool(value) for value in pass_values),
                    f"Quality report is not passing: {path}",
                )

                self.assertEqual(
                    int(data.get("problem_count", data.get("semantic_problem_count", 0))),
                    0,
                    f"Quality report contains problems: {path}",
                )

    def test_full_pipeline_quality_report_knows_all_required_quality_files(self):
        from pathlib import Path
        import json

        quality_report_path = Path("analysis/reports/full_campaign_pipeline_quality_check.json")
        report = json.loads(quality_report_path.read_text(encoding="utf-8"))

        quality_names = {
            Path(item.get("path", "")).name
            for item in report.get("quality_checks", [])
        }

        expected_quality_names = {
            "experiment_campaign_plan_quality_check.json",
            "campaign_batch_blueprint_quality_check.json",
            "campaign_perturbation_plan_quality_check.json",
            "campaign_executable_batch_config_quality_check.json",
            "campaign_execution_quality_check.json",
            "campaign_result_summary_quality_check.json",
            "service_delay_impact_audit_quality_check.json",
            "policy_trigger_behavior_audit_quality_check.json",
            "campaign_decision_matrix_quality_check.json",
            "campaign_ranking_profile_sensitivity_quality_check.json",
            "campaign_final_ranking_integration_quality_check.json",
            "campaign_final_diagnostic_report_quality_check.json",
        }

        missing = expected_quality_names - quality_names
        self.assertFalse(
            missing,
            f"Full pipeline quality check does not include these required quality reports: {sorted(missing)}",
        )

        output_names = {
            Path(item.get("path", "")).name
            for item in report.get("output_checks", [])
        }

        self.assertIn("campaign_result_semantic_inspection.json", output_names)

        self.assertNotIn(
            "full_campaign_pipeline_quality_check.json",
            quality_names,
            "The full pipeline quality check should not be required to list itself as an input quality file.",
        )
    def test_no_patch_scripts_left_in_analysis_scripts(self) -> None:
        patch_scripts = sorted(
            path.name
            for path in (PROJECT_ROOT / "analysis" / "scripts").glob("patch_*.py")
        )

        self.assertEqual(
            patch_scripts,
            [],
            f"Temporary patch scripts should not remain in analysis/scripts: {patch_scripts}",
        )


if __name__ == "__main__":
    unittest.main()