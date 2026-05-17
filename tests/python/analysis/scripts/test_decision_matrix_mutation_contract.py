import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "analysis" / "scripts"


class DecisionMatrixMutationContractTests(unittest.TestCase):
    def test_verifier_rejects_missing_trigger_class_regression(self) -> None:
        source_json = REPORTS_DIR / "campaign_decision_matrix.json"
        source_md = REPORTS_DIR / "campaign_decision_matrix.md"
        source_csv = REPORTS_DIR / "campaign_decision_matrix.csv"

        self.assertTrue(source_json.exists())
        self.assertTrue(source_md.exists())
        self.assertTrue(source_csv.exists())

        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            mutated_json = temp_dir / "campaign_decision_matrix_mutated.json"
            copied_md = temp_dir / "campaign_decision_matrix.md"
            copied_csv = temp_dir / "campaign_decision_matrix.csv"
            output_md = temp_dir / "quality_check.md"
            output_json = temp_dir / "quality_check.json"

            data = json.loads(source_json.read_text(encoding="utf-8"))
            rows = data.get("rows", [])

            self.assertTrue(rows, "Expected decision matrix rows in source JSON.")

            rows[0].pop("threshold_with_greedy_trigger_class", None)

            mutated_json.write_text(
                json.dumps(data, indent=4, ensure_ascii=False),
                encoding="utf-8",
            )

            copied_md.write_text(source_md.read_text(encoding="utf-8"), encoding="utf-8")
            copied_csv.write_text(source_csv.read_text(encoding="utf-8"), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "verify_campaign_decision_matrix.py"),
                    str(mutated_json),
                    str(copied_md),
                    str(copied_csv),
                    str(output_md),
                    str(output_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(
                completed.returncode,
                0,
                (
                    "Decision matrix verifier accepted a mutated report missing "
                    "threshold_with_greedy_trigger_class.\n"
                    f"stdout:\n{completed.stdout}\n"
                    f"stderr:\n{completed.stderr}"
                ),
            )

            self.assertTrue(output_json.exists(), "Verifier did not write quality JSON.")

            quality = json.loads(output_json.read_text(encoding="utf-8"))

            self.assertFalse(
                bool(quality.get("all_required_checks_passed", True)),
                "Verifier wrote a passing quality report for mutated input.",
            )

            problems = "\n".join(str(problem) for problem in quality.get("problems", []))

            self.assertIn(
                "threshold_with_greedy_trigger_class",
                problems,
                "Verifier failed but did not point to the missing trigger class field.",
            )

    def test_verifier_rejects_csv_row_count_mismatch(self) -> None:
        source_json = REPORTS_DIR / "campaign_decision_matrix.json"
        source_md = REPORTS_DIR / "campaign_decision_matrix.md"
        source_csv = REPORTS_DIR / "campaign_decision_matrix.csv"

        with tempfile.TemporaryDirectory() as temp_dir_text:
            temp_dir = Path(temp_dir_text)

            copied_json = temp_dir / "campaign_decision_matrix.json"
            copied_md = temp_dir / "campaign_decision_matrix.md"
            mutated_csv = temp_dir / "campaign_decision_matrix_mutated.csv"
            output_md = temp_dir / "quality_check.md"
            output_json = temp_dir / "quality_check.json"

            copied_json.write_text(source_json.read_text(encoding="utf-8"), encoding="utf-8")
            copied_md.write_text(source_md.read_text(encoding="utf-8"), encoding="utf-8")

            with source_csv.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.reader(file))

            self.assertGreater(len(rows), 2, "Expected header plus multiple CSV rows.")

            with mutated_csv.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows[:-1])

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "verify_campaign_decision_matrix.py"),
                    str(copied_json),
                    str(copied_md),
                    str(mutated_csv),
                    str(output_md),
                    str(output_json),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(
                completed.returncode,
                0,
                (
                    "Decision matrix verifier accepted CSV with a missing row.\n"
                    f"stdout:\n{completed.stdout}\n"
                    f"stderr:\n{completed.stderr}"
                ),
            )

            quality = json.loads(output_json.read_text(encoding="utf-8"))

            self.assertFalse(bool(quality.get("all_required_checks_passed", True)))
            self.assertGreater(int(quality.get("problem_count", 0)), 0)


if __name__ == "__main__":
    unittest.main()