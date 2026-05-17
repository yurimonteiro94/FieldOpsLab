from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]

PROJECT_STATUS_GENERATOR = (
    PROJECT_ROOT / "analysis" / "scripts" / "generate_project_status_report.py"
)

SCIENTIFIC_VALIDATION_GENERATOR = (
    PROJECT_ROOT / "analysis" / "scripts" / "generate_scientific_validation_plan.py"
)

PROJECT_STATUS_VERIFIER = (
    PROJECT_ROOT / "analysis" / "scripts" / "verify_project_status_report.py"
)

SCIENTIFIC_VALIDATION_VERIFIER = (
    PROJECT_ROOT / "analysis" / "scripts" / "verify_scientific_validation_plan.py"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FinalReportsRankingExplanationIntegrationTests(unittest.TestCase):
    def test_project_status_exposes_ranking_explanation_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            output_md = temp / "project_status_report.md"
            output_json = temp / "project_status_report.json"
            output_csv = temp / "project_status_report.csv"
            quality_md = temp / "project_status_quality_check.md"
            quality_json = temp / "project_status_quality_check.json"

            generate_result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_STATUS_GENERATOR),
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_STATUS_VERIFIER),
                    str(output_json),
                    str(output_md),
                    str(output_csv),
                    str(quality_md),
                    str(quality_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = read_json(output_json)
            metrics = report["summary_metrics"]
            quality_files = {
                item["quality_file"] for item in report["quality_summaries"]
            }

            self.assertIn(
                "analysis/reports/ranking_sensitive_scenario_quality_check.json",
                quality_files,
            )
            self.assertIn(
                "analysis/reports/ranking_sensitivity_explanation_quality_check.json",
                quality_files,
            )
            self.assertGreaterEqual(
                metrics["ranking_sensitivity_explanation_count"],
                1,
            )
            self.assertGreaterEqual(
                metrics["ranking_sensitivity_explanation_count"],
                metrics["ranking_sensitive_scenario_count"],
            )
            self.assertTrue(metrics["all_sensitive_scenarios_have_explanation"])

    def test_scientific_validation_plan_uses_ranking_explanation_as_quality_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)

            status_md = PROJECT_ROOT / "analysis" / "reports" / "project_status_report.md"
            status_json = PROJECT_ROOT / "analysis" / "reports" / "project_status_report.json"
            status_csv = PROJECT_ROOT / "analysis" / "reports" / "project_status_report.csv"

            subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_STATUS_GENERATOR),
                    str(status_md),
                    str(status_json),
                    str(status_csv),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            output_md = temp / "scientific_validation_plan.md"
            output_json = temp / "scientific_validation_plan.json"
            output_csv = temp / "scientific_validation_plan.csv"
            quality_md = temp / "scientific_validation_plan_quality_check.md"
            quality_json = temp / "scientific_validation_plan_quality_check.json"

            generate_result = subprocess.run(
                [
                    sys.executable,
                    str(SCIENTIFIC_VALIDATION_GENERATOR),
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = subprocess.run(
                [
                    sys.executable,
                    str(SCIENTIFIC_VALIDATION_VERIFIER),
                    str(output_json),
                    str(output_md),
                    str(output_csv),
                    str(quality_md),
                    str(quality_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = read_json(output_json)
            quality_paths = {item["path"] for item in report["quality_inputs"]}
            context = report["context"]

            self.assertIn(
                "analysis/reports/ranking_sensitive_scenario_quality_check.json",
                quality_paths,
            )
            self.assertIn(
                "analysis/reports/ranking_sensitivity_explanation_quality_check.json",
                quality_paths,
            )
            self.assertGreaterEqual(
                context["ranking_sensitivity_explanation_count"],
                1,
            )
            self.assertTrue(context["all_sensitive_scenarios_have_explanation"])

            risk_text = "\n".join(report["open_scientific_risks"]).lower()
            self.assertIn("diagnostic explanation", risk_text)
            self.assertIn("not statistical proof", risk_text)


if __name__ == "__main__":
    unittest.main()
