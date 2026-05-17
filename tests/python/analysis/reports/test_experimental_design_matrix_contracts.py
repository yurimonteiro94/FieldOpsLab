from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
GENERATOR = PROJECT_ROOT / "analysis" / "scripts" / "generate_experimental_design_matrix.py"
VERIFIER = PROJECT_ROOT / "analysis" / "scripts" / "verify_experimental_design_matrix.py"


class ExperimentalDesignMatrixContractTests(unittest.TestCase):
    def run_script(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_scripts_compile_and_have_main_guard(self) -> None:
        for script in [GENERATOR, VERIFIER]:
            self.assertTrue(script.exists(), f"Missing script: {script}")

            compile_result = self.run_script(["-m", "py_compile", str(script)])
            self.assertEqual(
                compile_result.returncode,
                0,
                compile_result.stderr + compile_result.stdout,
            )

            text = script.read_text(encoding="utf-8")
            self.assertIn('if __name__ == "__main__":', text)

    def test_generator_and_verifier_accept_current_experimental_design_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_md = temp_path / "experimental_design_matrix.md"
            output_json = temp_path / "experimental_design_matrix.json"
            output_csv = temp_path / "experimental_design_matrix.csv"
            quality_md = temp_path / "experimental_design_matrix_quality_check.md"
            quality_json = temp_path / "experimental_design_matrix_quality_check.json"

            generate_result = self.run_script(
                [
                    str(GENERATOR),
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ]
            )
            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stderr + generate_result.stdout,
            )

            verify_result = self.run_script(
                [
                    str(VERIFIER),
                    str(output_json),
                    str(output_md),
                    str(output_csv),
                    str(quality_md),
                    str(quality_json),
                ]
            )
            self.assertEqual(
                verify_result.returncode,
                0,
                verify_result.stderr + verify_result.stdout,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            quality = json.loads(quality_json.read_text(encoding="utf-8"))

            self.assertEqual(report["report_type"], "experimental_design_matrix")
            self.assertEqual(report["scientific_stage"], "experimental_design")
            self.assertTrue(quality["all_required_checks_passed"])
            self.assertEqual(quality["problem_count"], 0)

            summary = report["summary"]
            self.assertEqual(summary["instance_size_level_count"], 3)
            self.assertEqual(summary["demand_density_level_count"], 3)
            self.assertEqual(summary["delay_family_count"], 4)
            self.assertEqual(summary["severity_count"], 3)
            self.assertEqual(summary["policy_count"], 2)
            self.assertEqual(summary["replication_count"], 3)
            self.assertEqual(summary["scenario_count"], 108)
            self.assertEqual(summary["experiment_count"], 648)

            with output_csv.open("r", newline="", encoding="utf-8") as file:
                csv_rows = list(csv.DictReader(file))

            self.assertEqual(len(csv_rows), 648)
            self.assertEqual(len({row["experiment_id"] for row in csv_rows}), 648)

            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("# FieldOps Lab experimental design matrix", markdown)
            self.assertIn("does not prove scientific validity", markdown.lower())

    def test_verifier_rejects_empty_experimental_design_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_json = temp_path / "bad.json"
            input_md = temp_path / "bad.md"
            input_csv = temp_path / "bad.csv"
            quality_md = temp_path / "quality.md"
            quality_json = temp_path / "quality.json"

            input_json.write_text(
                json.dumps(
                    {
                        "report_type": "experimental_design_matrix",
                        "scientific_stage": "experimental_design",
                        "summary": {
                            "experiment_count": 0,
                            "scenario_count": 0,
                            "all_experiments_reproducible_from_explicit_factors": False,
                        },
                        "factor_summary": {},
                        "rows": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            input_md.write_text("# FieldOps Lab experimental design matrix\n", encoding="utf-8")
            input_csv.write_text("experiment_id,scenario_id\n", encoding="utf-8")

            verify_result = self.run_script(
                [
                    str(VERIFIER),
                    str(input_json),
                    str(input_md),
                    str(input_csv),
                    str(quality_md),
                    str(quality_json),
                ]
            )

            self.assertNotEqual(verify_result.returncode, 0)
            quality = json.loads(quality_json.read_text(encoding="utf-8"))
            self.assertFalse(quality["all_required_checks_passed"])
            self.assertGreater(quality["problem_count"], 0)


if __name__ == "__main__":
    unittest.main()