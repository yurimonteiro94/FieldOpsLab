import csv
import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def extract_rows(data: dict) -> list[dict]:
    for key in ["rows", "decision_rows", "final_diagnostic_rows", "matrix_rows"]:
        value = data.get(key)
        if isinstance(value, list):
            return value
    return []


class CampaignReportConsistencyTests(unittest.TestCase):
    def test_final_diagnostic_json_csv_and_markdown_are_consistent(self) -> None:
        json_path = REPORTS_DIR / "campaign_final_diagnostic_report.json"
        csv_path = REPORTS_DIR / "campaign_final_diagnostic_report.csv"
        md_path = REPORTS_DIR / "campaign_final_diagnostic_report.md"

        self.assertTrue(json_path.exists(), f"Missing file: {json_path}")
        self.assertTrue(csv_path.exists(), f"Missing file: {csv_path}")
        self.assertTrue(md_path.exists(), f"Missing file: {md_path}")

        data = load_json(json_path)
        json_rows = extract_rows(data)
        csv_rows = load_csv_rows(csv_path)
        markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(len(json_rows), 12)
        self.assertEqual(len(csv_rows), 12)

        json_batch_ids = {str(row.get("batch_id", "")) for row in json_rows}
        csv_batch_ids = {str(row.get("batch_id", "")) for row in csv_rows}

        self.assertEqual(json_batch_ids, csv_batch_ids)

        for batch_id in json_batch_ids:
            self.assertIn(
                batch_id,
                markdown,
                f"Markdown final diagnostic report does not mention batch {batch_id}.",
            )

        required_csv_columns = {
            "batch_id",
            "scenario_family_id",
            "severity_id",
            "provisional_action",
            "evidence_strength",
            "scientific_use_status",
            "ranking_stability_class",
            "ranking_unique_policy_count",
        }

        self.assertTrue(
            required_csv_columns.issubset(set(csv_rows[0].keys())),
            f"Missing required CSV columns: {required_csv_columns - set(csv_rows[0].keys())}",
        )

    def test_ranking_sensitivity_summary_is_consistent_with_final_report(self) -> None:
        final_json_path = REPORTS_DIR / "campaign_final_diagnostic_report.json"
        sensitivity_json_path = REPORTS_DIR / "campaign_ranking_profile_sensitivity.json"

        final_data = load_json(final_json_path)
        sensitivity_data = load_json(sensitivity_json_path)

        final_rows = extract_rows(final_data)

        scenario_summary = (
            sensitivity_data.get("scenario_summary")
            or sensitivity_data.get("scenario_summaries")
            or sensitivity_data.get("scenario_rows")
            or []
        )

        self.assertEqual(len(final_rows), 12)
        self.assertEqual(len(scenario_summary), 12)

        final_batch_ids = {str(row.get("batch_id", "")) for row in final_rows}
        sensitivity_batch_ids = {str(row.get("batch_id", "")) for row in scenario_summary}

        self.assertEqual(final_batch_ids, sensitivity_batch_ids)

        for row in final_rows:
            batch_id = str(row.get("batch_id", ""))
            self.assertTrue(batch_id)

            self.assertIn(
                str(row.get("ranking_stability_class", "")),
                {"stable_across_profiles", "same_policy_different_class", "sensitive_to_ranking_profile"},
                f"Unexpected ranking stability class for {batch_id}",
            )

            self.assertGreaterEqual(
                int(row.get("ranking_unique_policy_count", 0)),
                1,
                f"Invalid ranking_unique_policy_count for {batch_id}",
            )

    def test_campaign_decision_matrix_has_no_empty_trigger_classes(self) -> None:
        data = load_json(REPORTS_DIR / "campaign_decision_matrix.json")
        rows = extract_rows(data)

        self.assertEqual(len(rows), 12)

        for row in rows:
            batch_id = str(row.get("batch_id", ""))

            self.assertTrue(
                str(row.get("threshold_with_greedy_trigger_class", "")).strip(),
                f"Empty threshold_with_greedy_trigger_class for {batch_id}",
            )

            self.assertTrue(
                str(row.get("threshold_without_solver_trigger_class", "")).strip(),
                f"Empty threshold_without_solver_trigger_class for {batch_id}",
            )


if __name__ == "__main__":
    unittest.main()