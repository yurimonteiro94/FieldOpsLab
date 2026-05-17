import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = PROJECT_ROOT / "analysis" / "scripts"


CRITICAL_CLI_SCRIPTS = [
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


class AnalysisScriptUsageContractTests(unittest.TestCase):
    def test_critical_scripts_reject_missing_arguments(self) -> None:
        for script_name in CRITICAL_CLI_SCRIPTS:
            with self.subTest(script_name=script_name):
                script_path = SCRIPTS_DIR / script_name

                self.assertTrue(
                    script_path.exists(),
                    f"Expected script does not exist: {script_path}",
                )

                completed = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=PROJECT_ROOT,
                    text=True,
                    capture_output=True,
                )

                combined_output = f"{completed.stdout}\n{completed.stderr}"

                self.assertNotEqual(
                    completed.returncode,
                    0,
                    (
                        f"{script_name} accepted a call with no arguments.\n"
                        f"stdout:\n{completed.stdout}\n"
                        f"stderr:\n{completed.stderr}"
                    ),
                )

                self.assertTrue(
                    "Usage:" in combined_output
                    or "usage:" in combined_output
                    or "ERROR:" in combined_output
                    or "Error:" in combined_output,
                    (
                        f"{script_name} failed without explaining usage or error.\n"
                        f"stdout:\n{completed.stdout}\n"
                        f"stderr:\n{completed.stderr}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()