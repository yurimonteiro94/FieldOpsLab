from __future__ import annotations

import json
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]

GENERATOR = (
    PROJECT_ROOT
    / "analysis"
    / "scripts"
    / "generate_ranking_sensitivity_explanation_report.py"
)

VERIFIER = (
    PROJECT_ROOT
    / "analysis"
    / "scripts"
    / "verify_ranking_sensitivity_explanation_report.py"
)


class RankingSensitivityExplanationReportContractTests(unittest.TestCase):
    def test_ranking_sensitivity_explanation_scripts_compile_and_have_main_guard(
        self,
    ) -> None:
        self.assertTrue(GENERATOR.exists())
        self.assertTrue(VERIFIER.exists())

        py_compile.compile(str(GENERATOR), doraise=True)
        py_compile.compile(str(VERIFIER), doraise=True)

        generator_source = GENERATOR.read_text(encoding="utf-8")
        verifier_source = VERIFIER.read_text(encoding="utf-8")

        self.assertIn('if __name__ == "__main__":', generator_source)
        self.assertIn('if __name__ == "__main__":', verifier_source)
        self.assertIn("raise SystemExit(main())", generator_source)
        self.assertIn("raise SystemExit(main())", verifier_source)

    def test_generator_and_verifier_accept_current_explanation_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            output_md = temp_path / "ranking_sensitivity_explanation_report.md"
            output_json = temp_path / "ranking_sensitivity_explanation_report.json"
            output_csv = temp_path / "ranking_sensitivity_explanation_report.csv"
            quality_md = temp_path / "ranking_sensitivity_explanation_quality_check.md"
            quality_json = temp_path / "ranking_sensitivity_explanation_quality_check.json"

            generate_result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = subprocess.run(
                [
                    sys.executable,
                    str(VERIFIER),
                    str(output_json),
                    str(output_md),
                    str(output_csv),
                    str(quality_md),
                    str(quality_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            quality = json.loads(quality_json.read_text(encoding="utf-8"))

            self.assertEqual(
                report["report_type"],
                "ranking_sensitivity_explanation_report",
            )
            self.assertTrue(report["input_status"]["all_required_inputs_available"])
            self.assertGreaterEqual(report["summary"]["explanation_count"], 1)
            self.assertTrue(
                report["summary"]["all_sensitive_scenarios_have_explanation"]
            )
            self.assertGreaterEqual(
                report["summary"]["class_change_explanation_count"]
                + report["summary"]["policy_change_explanation_count"],
                1,
            )
            self.assertTrue(quality["all_required_checks_passed"])

            for explanation in report["explanations"]:
                self.assertTrue(explanation["batch_id"])
                self.assertTrue(explanation["sensitive_to_ranking_profile"])
                self.assertTrue(explanation["profile_explanations"])
                self.assertTrue(explanation["interpretation"])

    def test_verifier_rejects_invalid_explanation_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            input_json = temp_path / "invalid_report.json"
            input_md = temp_path / "invalid_report.md"
            input_csv = temp_path / "invalid_report.csv"
            quality_md = temp_path / "quality.md"
            quality_json = temp_path / "quality.json"

            input_json.write_text(
                json.dumps(
                    {
                        "report_type": "ranking_sensitivity_explanation_report",
                        "input_status": {
                            "all_required_inputs_available": False,
                            "sensitive_scenario_report_path": "",
                            "ranking_sensitivity_source_path": "",
                            "sensitive_scenario_report_exists": False,
                            "ranking_sensitivity_source_exists": False,
                            "sensitive_scenario_count": 0,
                            "source_ranking_row_count": 0,
                            "source_recommended_row_count": 0,
                        },
                        "summary": {
                            "source_sensitive_scenario_count": 0,
                            "explanation_count": 0,
                            "policy_change_explanation_count": 0,
                            "class_change_explanation_count": 0,
                            "all_sensitive_scenarios_have_explanation": False,
                            "source_ranking_row_count": 0,
                            "source_recommended_row_count": 0,
                        },
                        "explanations": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            input_md.write_text("# Broken report\n", encoding="utf-8")
            input_csv.write_text("bad_column\nbad_value\n", encoding="utf-8")

            verify_result = subprocess.run(
                [
                    sys.executable,
                    str(VERIFIER),
                    str(input_json),
                    str(input_md),
                    str(input_csv),
                    str(quality_md),
                    str(quality_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(verify_result.returncode, 0)

            combined_output = verify_result.stderr + verify_result.stdout

            self.assertIn("all_required_inputs_available must be true", combined_output)
            self.assertIn("explanation_count must be positive", combined_output)
            self.assertIn("explanations must not be empty", combined_output)
            self.assertIn("Markdown is missing section", combined_output)
            self.assertIn("CSV is missing required columns", combined_output)

            quality = json.loads(quality_json.read_text(encoding="utf-8"))
            self.assertFalse(quality["all_required_checks_passed"])
            self.assertGreater(quality["problem_count"], 0)


if __name__ == "__main__":
    unittest.main()