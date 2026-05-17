from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]

GENERATOR = PROJECT_ROOT / "analysis" / "scripts" / "generate_scientific_validation_plan.py"
VERIFIER = PROJECT_ROOT / "analysis" / "scripts" / "verify_scientific_validation_plan.py"


def run_python(args: list[Path | str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["py", "-3", *[str(arg) for arg in args]],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )


class ScientificValidationPlanContractTests(unittest.TestCase):
    def test_scientific_validation_plan_scripts_compile_and_have_main_guard(self) -> None:
        compile_result = run_python(["-m", "py_compile", GENERATOR, VERIFIER])
        self.assertEqual(
            compile_result.returncode,
            0,
            compile_result.stderr + compile_result.stdout,
        )

        for script in [GENERATOR, VERIFIER]:
            source = script.read_text(encoding="utf-8")
            self.assertIn('if __name__ == "__main__":', source)
            self.assertIn("raise SystemExit(main())", source)

    def test_generator_and_verifier_accept_current_scientific_validation_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)

            markdown_path = temp / "scientific_validation_plan.md"
            json_path = temp / "scientific_validation_plan.json"
            csv_path = temp / "scientific_validation_plan.csv"
            quality_markdown_path = temp / "scientific_validation_plan_quality_check.md"
            quality_json_path = temp / "scientific_validation_plan_quality_check.json"

            generate_result = run_python(
                [
                    GENERATOR,
                    markdown_path,
                    json_path,
                    csv_path,
                ]
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = run_python(
                [
                    VERIFIER,
                    json_path,
                    markdown_path,
                    csv_path,
                    quality_markdown_path,
                    quality_json_path,
                ]
            )

            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = json.loads(json_path.read_text(encoding="utf-8"))
            quality = json.loads(quality_json_path.read_text(encoding="utf-8"))

            self.assertEqual(report["report_type"], "scientific_validation_plan")
            self.assertEqual(report["validation_stage"], "diagnostic_to_experimental_transition")
            self.assertGreaterEqual(len(report["validation_actions"]), 8)
            self.assertTrue(quality["all_required_checks_passed"])
            self.assertEqual(quality["problem_count"], 0)

            categories = {action["category"] for action in report["validation_actions"]}
            self.assertIn("experimental_design", categories)
            self.assertIn("statistical_validation", categories)
            self.assertIn("external_validation", categories)
            self.assertIn("methodological_limitations", categories)

            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("This plan does not prove scientific validity", markdown)
            self.assertIn("## Validation actions", markdown)

    def test_verifier_rejects_empty_validation_action_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)

            json_path = temp / "invalid_scientific_validation_plan.json"
            markdown_path = temp / "invalid_scientific_validation_plan.md"
            csv_path = temp / "invalid_scientific_validation_plan.csv"
            quality_markdown_path = temp / "quality.md"
            quality_json_path = temp / "quality.json"

            invalid_report = {
                "report_type": "scientific_validation_plan",
                "validation_stage": "diagnostic_to_experimental_transition",
                "structural_inputs_available": True,
                "structural_inputs_passed": True,
                "context": {
                    "scientific_status": "diagnostic_only_with_methodological_warnings",
                },
                "quality_inputs": [
                    {
                        "path": "analysis/reports/project_status_quality_check.json",
                        "exists": True,
                        "passed": True,
                        "problem_count": 0,
                        "warning_count": 0,
                    }
                ],
                "open_scientific_risks": [
                    "The current report is intentionally invalid for testing."
                ],
                "validation_actions": [],
                "conservative_conclusion": (
                    "This plan does not prove scientific validity."
                ),
            }

            json_path.write_text(
                json.dumps(invalid_report, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            markdown_path.write_text(
                "# Invalid plan\n\nThis plan does not prove scientific validity.\n\n## Validation actions\n",
                encoding="utf-8",
            )
            csv_path.write_text(
                "id,priority,category,action,acceptance_criterion,evidence_output,status\n",
                encoding="utf-8",
            )

            verify_result = run_python(
                [
                    VERIFIER,
                    json_path,
                    markdown_path,
                    csv_path,
                    quality_markdown_path,
                    quality_json_path,
                ]
            )

            self.assertNotEqual(verify_result.returncode, 0)
            self.assertIn(
                "validation_actions must contain at least 8 actions",
                verify_result.stderr + verify_result.stdout,
            )


if __name__ == "__main__":
    unittest.main()