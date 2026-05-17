from __future__ import annotations

import py_compile
import unittest
from pathlib import Path

from tests.python.test_support.project_paths import ANALYSIS_SCRIPTS_DIR


class TestAllAnalysisScriptsCompile(unittest.TestCase):
    def test_all_analysis_scripts_compile(self) -> None:
        scripts = sorted(ANALYSIS_SCRIPTS_DIR.glob("*.py"))

        self.assertGreater(
            len(scripts),
            0,
            "No Python scripts were found in analysis/scripts.",
        )

        for script_path in scripts:
            with self.subTest(script=str(script_path)):
                py_compile.compile(str(script_path), doraise=True)

    def test_no_temporary_patch_scripts_are_left_in_analysis_scripts(self) -> None:
        temporary_patch_scripts = sorted(ANALYSIS_SCRIPTS_DIR.glob("patch_*.py"))

        self.assertEqual(
            [],
            temporary_patch_scripts,
            "Temporary patch scripts must not be committed or left in analysis/scripts.",
        )

    def test_expected_campaign_scripts_exist(self) -> None:
        expected_scripts = [
            "generate_experiment_campaign_plan.py",
            "verify_experiment_campaign_plan.py",
            "generate_campaign_batch_blueprints.py",
            "verify_campaign_batch_blueprints.py",
            "generate_campaign_perturbation_plans.py",
            "verify_campaign_perturbation_plans.py",
            "generate_executable_campaign_batch_configs.py",
            "verify_executable_campaign_batch_configs.py",
            "run_executable_campaign_batches.py",
            "verify_campaign_execution_index.py",
            "generate_campaign_result_summary.py",
            "verify_campaign_result_summary.py",
            "inspect_campaign_result_semantics.py",
            "audit_service_delay_impact.py",
            "verify_service_delay_impact_audit.py",
            "audit_policy_trigger_behavior.py",
            "verify_policy_trigger_behavior_audit.py",
            "generate_campaign_decision_matrix.py",
            "verify_campaign_decision_matrix.py",
            "generate_campaign_ranking_profile_sensitivity.py",
            "verify_campaign_ranking_profile_sensitivity.py",
            "generate_campaign_final_diagnostic_report.py",
            "integrate_ranking_sensitivity_into_final_diagnostic_report.py",
            "verify_final_diagnostic_ranking_integration.py",
            "verify_campaign_final_diagnostic_report.py",
            "run_full_campaign_pipeline.py",
            "verify_full_campaign_pipeline.py",
        ]

        for script_name in expected_scripts:
            with self.subTest(script=script_name):
                self.assertTrue(
                    (ANALYSIS_SCRIPTS_DIR / script_name).exists(),
                    f"Expected script is missing: {script_name}",
                )


if __name__ == "__main__":
    unittest.main()