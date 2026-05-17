import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = PROJECT_ROOT / "analysis" / "scripts"


class VerifierNegativeContractTests(unittest.TestCase):
    def run_script(self, script_name: str, *args: Path) -> subprocess.CompletedProcess[str]:
        script_path = SCRIPTS_DIR / script_name

        self.assertTrue(
            script_path.exists(),
            f"Expected script does not exist: {script_path}",
        )

        return subprocess.run(
            [sys.executable, str(script_path), *[str(arg) for arg in args]],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
        )

    def assert_verifier_rejects_invalid_report(self, script_name: str) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            invalid_json = temp_dir / "invalid_input.json"
            placeholder_md = temp_dir / "placeholder.md"
            placeholder_csv = temp_dir / "placeholder.csv"
            output_md = temp_dir / "quality_check.md"
            output_json = temp_dir / "quality_check.json"

            invalid_json.write_text("{}", encoding="utf-8")
            placeholder_md.write_text("# Placeholder\n", encoding="utf-8")
            placeholder_csv.write_text("placeholder\n", encoding="utf-8")

            completed = self.run_script(
                script_name,
                invalid_json,
                placeholder_md,
                placeholder_csv,
                output_md,
                output_json,
            )

            self.assertNotEqual(
                completed.returncode,
                0,
                (
                    f"{script_name} accepted an invalid empty JSON report.\n"
                    f"stdout:\n{completed.stdout}\n"
                    f"stderr:\n{completed.stderr}"
                ),
            )

            if output_json.exists():
                data = json.loads(output_json.read_text(encoding="utf-8"))

                if "all_required_checks_passed" in data:
                    self.assertFalse(
                        data["all_required_checks_passed"],
                        f"{script_name} wrote a passing quality report for invalid input.",
                    )

                if "problem_count" in data:
                    self.assertGreater(
                        int(data["problem_count"]),
                        0,
                        f"{script_name} did not report problems for invalid input.",
                    )

    def test_campaign_result_summary_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report("verify_campaign_result_summary.py")

    def test_campaign_execution_index_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report("verify_campaign_execution_index.py")

    def test_service_delay_impact_audit_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report("verify_service_delay_impact_audit.py")

    def test_policy_trigger_behavior_audit_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report("verify_policy_trigger_behavior_audit.py")

    def test_campaign_decision_matrix_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report("verify_campaign_decision_matrix.py")

    def test_campaign_ranking_profile_sensitivity_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report(
            "verify_campaign_ranking_profile_sensitivity.py"
        )

    def test_campaign_final_diagnostic_report_verifier_rejects_empty_json(self) -> None:
        self.assert_verifier_rejects_invalid_report(
            "verify_campaign_final_diagnostic_report.py"
        )


if __name__ == "__main__":
    unittest.main()