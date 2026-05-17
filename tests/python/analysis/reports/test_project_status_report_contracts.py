from __future__ import annotations

import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def run_python_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["py", "-3", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        shell=False,
    )


class ProjectStatusReportContractTests(unittest.TestCase):
    def test_generator_and_verifier_accept_current_project_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            status_md = temp_dir / "project_status_report.md"
            status_json = temp_dir / "project_status_report.json"
            status_csv = temp_dir / "project_status_report.csv"
            quality_md = temp_dir / "project_status_quality_check.md"
            quality_json = temp_dir / "project_status_quality_check.json"

            generate_result = run_python_script(
                "analysis/scripts/generate_project_status_report.py",
                str(status_md),
                str(status_json),
                str(status_csv),
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stdout + generate_result.stderr,
            )

            verify_result = run_python_script(
                "analysis/scripts/verify_project_status_report.py",
                str(status_json),
                str(status_md),
                str(status_csv),
                str(quality_md),
                str(quality_json),
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stdout + verify_result.stderr,
            )

            status = json.loads(status_json.read_text(encoding="utf-8"))
            metrics = status["summary_metrics"]

            self.assertGreater(metrics["analysis_script_count"], 0)
            self.assertGreater(metrics["python_test_count"], 0)
            self.assertGreater(metrics["cpp_test_source_count"], 0)
            self.assertEqual(metrics["script_without_direct_python_test_count"], 0)
            self.assertEqual(metrics["script_needing_test_review_count"], 0)
            self.assertGreater(metrics["pipeline_step_count"], 0)
            self.assertEqual(metrics["pipeline_failed_step_count"], 0)
            self.assertGreater(metrics["final_diagnostic_row_count"], 0)
            self.assertGreater(metrics["ranking_row_count"], 0)
            self.assertGreater(metrics["scenario_summary_count"], 0)
            self.assertIn(
                metrics["ranking_fragility_status"],
                {
                    "some_scenarios_sensitive_to_ranking_profile",
                    "no_policy_change_detected_under_current_profiles",
                },
            )

            quality = json.loads(quality_json.read_text(encoding="utf-8"))
            self.assertTrue(quality["all_required_checks_passed"])
            self.assertEqual(quality["problem_count"], 0)

    def test_verifier_rejects_zero_test_inventory_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            status_md = temp_dir / "project_status_report.md"
            status_json = temp_dir / "project_status_report.json"
            status_csv = temp_dir / "project_status_report.csv"
            quality_md = temp_dir / "project_status_quality_check.md"
            quality_json = temp_dir / "project_status_quality_check.json"

            status_md.write_text("# Dummy project status\n", encoding="utf-8")

            status = {
                "report_type": "fieldops_lab_project_status_report",
                "summary_metrics": {
                    "engineering_status": "passed_current_structural_quality_gate",
                    "scientific_status": "diagnostic_only_with_methodological_warnings",
                    "structural_all_required_checks_passed": True,
                    "analysis_script_count": 0,
                    "python_test_count": 0,
                    "cpp_test_source_count": 0,
                    "script_without_direct_python_test_count": 0,
                    "script_needing_test_review_count": 0,
                    "pipeline_step_count": 1,
                    "pipeline_failed_step_count": 0,
                    "final_diagnostic_row_count": 1,
                    "ranking_row_count": 1,
                    "scenario_summary_count": 1,
                    "sensitive_to_ranking_profile_count": 0,
                    "ranking_fragility_status": "no_policy_change_detected_under_current_profiles",
                    "methodological_warning_count": 0,
                },
                "quality_summaries": [
                    {
                        "quality_file": "dummy.json",
                        "exists": True,
                        "passed": True,
                        "problem_count": 0,
                        "warning_count": 0,
                    }
                ],
            }

            status_json.write_text(
                json.dumps(status, indent=2),
                encoding="utf-8",
            )

            with status_csv.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["category", "field", "value"],
                )
                writer.writeheader()
                for index in range(16):
                    writer.writerow(
                        {
                            "category": "dummy",
                            "field": f"field_{index}",
                            "value": "0",
                        }
                    )

            verify_result = run_python_script(
                "analysis/scripts/verify_project_status_report.py",
                str(status_json),
                str(status_md),
                str(status_csv),
                str(quality_md),
                str(quality_json),
            )

            self.assertNotEqual(verify_result.returncode, 0)
            self.assertIn("analysis_script_count must be positive", verify_result.stderr + verify_result.stdout)
            self.assertIn("python_test_count must be positive", verify_result.stderr + verify_result.stdout)
            self.assertIn("cpp_test_source_count must be positive", verify_result.stderr + verify_result.stdout)

    def test_project_status_report_scripts_compile_and_have_main_guard(self) -> None:
        script_paths = [
            PROJECT_ROOT / "analysis" / "scripts" / "generate_project_status_report.py",
            PROJECT_ROOT / "analysis" / "scripts" / "verify_project_status_report.py",
        ]

        for path in script_paths:
            source = path.read_text(encoding="utf-8")
            self.assertIn('if __name__ == "__main__":', source)
            self.assertIn("raise SystemExit(main())", source)

            result = run_python_script("-m", "py_compile", str(path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()