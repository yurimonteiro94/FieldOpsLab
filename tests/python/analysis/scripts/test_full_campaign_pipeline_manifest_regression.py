import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"


EXPECTED_PIPELINE_ORDER = [
    "generate_experiment_campaign_plan",
    "verify_experiment_campaign_plan",
    "generate_campaign_batch_blueprints",
    "verify_campaign_batch_blueprints",
    "generate_campaign_perturbation_plans",
    "verify_campaign_perturbation_plans",
    "generate_executable_campaign_batch_configs",
    "connect_campaign_batch_configs_to_perturbation_plans",
    "verify_executable_campaign_batch_configs",
    "run_executable_campaign_batches",
    "verify_campaign_execution_index",
    "generate_campaign_result_summary",
    "verify_campaign_result_summary",
    "inspect_campaign_result_semantics",
    "audit_service_delay_impact",
    "verify_service_delay_impact_audit",
    "audit_policy_trigger_behavior",
    "verify_policy_trigger_behavior_audit",
    "generate_campaign_decision_matrix",
    "verify_campaign_decision_matrix",
    "generate_campaign_ranking_profile_sensitivity",
    "verify_campaign_ranking_profile_sensitivity",
    "generate_campaign_final_diagnostic_report",
    "integrate_ranking_sensitivity_into_final_diagnostic_report",
    "verify_final_diagnostic_ranking_integration",
    "verify_campaign_final_diagnostic_report",
]


class FullCampaignPipelineManifestRegressionTests(unittest.TestCase):
    def load_manifest(self) -> dict:
        manifest_path = REPORTS_DIR / "full_campaign_pipeline_manifest.json"

        self.assertTrue(
            manifest_path.exists(),
            f"Pipeline manifest does not exist: {manifest_path}",
        )

        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def test_manifest_contains_expected_ordered_pipeline_steps(self) -> None:
        manifest = self.load_manifest()

        steps = manifest.get("steps", [])
        step_names = [str(step.get("name", "")) for step in steps]

        self.assertEqual(
            len(step_names),
            int(manifest.get("step_count", -1)),
            "Manifest step_count does not match the actual step list length.",
        )

        for expected_step in EXPECTED_PIPELINE_ORDER:
            self.assertIn(
                expected_step,
                step_names,
                f"Missing expected pipeline step: {expected_step}",
            )

        actual_positions = [step_names.index(step) for step in EXPECTED_PIPELINE_ORDER]

        self.assertEqual(
            actual_positions,
            sorted(actual_positions),
            "Pipeline steps exist but are not in the expected order.",
        )

    def test_manifest_exposes_ranking_sensitivity_outputs(self) -> None:
        manifest = self.load_manifest()
        outputs = manifest.get("important_outputs", {})

        expected_output_keys = [
            "campaign_ranking_profile_sensitivity",
            "campaign_ranking_profile_sensitivity_quality_check",
            "campaign_final_diagnostic_report",
            "campaign_final_ranking_integration_quality_check",
            "campaign_final_diagnostic_quality_check",
        ]

        for key in expected_output_keys:
            self.assertIn(
                key,
                outputs,
                f"Manifest does not expose important output key: {key}",
            )

            output_path = PROJECT_ROOT / str(outputs[key])

            self.assertTrue(
                output_path.exists(),
                f"Manifest points to a missing output file for {key}: {output_path}",
            )

    def test_manifest_reports_successful_pipeline(self) -> None:
        manifest = self.load_manifest()

        self.assertTrue(
            bool(manifest.get("all_steps_passed", False)),
            "Current full pipeline manifest is not marked as successful.",
        )

        self.assertEqual(
            int(manifest.get("failed_step_count", -1)),
            0,
            "Current full pipeline manifest reports failed steps.",
        )


if __name__ == "__main__":
    unittest.main()