from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class TestInventoryReportContractTests(unittest.TestCase):
    def test_generator_and_verifier_accept_current_project_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)
            output_md = temp_dir / "test_inventory_report.md"
            output_json = temp_dir / "test_inventory_report.json"
            output_csv = temp_dir / "test_inventory_report.csv"
            quality_md = temp_dir / "test_inventory_quality_check.md"
            quality_json = temp_dir / "test_inventory_quality_check.json"

            generate_result = run_command(
                [
                    sys.executable,
                    "analysis/scripts/generate_test_inventory_report.py",
                    str(output_md),
                    str(output_json),
                    str(output_csv),
                ]
            )

            self.assertEqual(
                generate_result.returncode,
                0,
                generate_result.stdout + generate_result.stderr,
            )

            verify_result = run_command(
                [
                    sys.executable,
                    "analysis/scripts/verify_test_inventory_report.py",
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
                verify_result.stdout + verify_result.stderr,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            quality = json.loads(quality_json.read_text(encoding="utf-8"))

            self.assertEqual(report["report_type"], "fieldops_lab_test_inventory_report")
            self.assertTrue(report["all_required_checks_passed"])
            self.assertGreater(report["overview"]["analysis_script_count"], 0)
            self.assertGreater(report["overview"]["python_test_count"], 0)
            self.assertGreater(report["overview"]["cpp_test_source_count"], 0)
            self.assertEqual(report["overview"]["row_count"], len(report["rows"]))

            self.assertEqual(
                quality["report_type"],
                "fieldops_lab_test_inventory_quality_check",
            )
            self.assertTrue(quality["all_required_checks_passed"])
            self.assertEqual(quality["problem_count"], 0)

    def test_verifier_rejects_invalid_inventory_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)
            bad_json = temp_dir / "bad_inventory.json"
            bad_md = temp_dir / "bad_inventory.md"
            bad_csv = temp_dir / "bad_inventory.csv"
            quality_md = temp_dir / "quality.md"
            quality_json = temp_dir / "quality.json"

            bad_json.write_text("{}", encoding="utf-8")
            bad_md.write_text("# Wrong title\n", encoding="utf-8")
            bad_csv.write_text("script_path,status\n", encoding="utf-8")

            result = run_command(
                [
                    sys.executable,
                    "analysis/scripts/verify_test_inventory_report.py",
                    str(bad_json),
                    str(bad_md),
                    str(bad_csv),
                    str(quality_md),
                    str(quality_json),
                ]
            )

            self.assertNotEqual(result.returncode, 0)

            quality = json.loads(quality_json.read_text(encoding="utf-8"))
            self.assertFalse(quality["all_required_checks_passed"])
            self.assertGreater(quality["problem_count"], 0)


if __name__ == "__main__":
    unittest.main()