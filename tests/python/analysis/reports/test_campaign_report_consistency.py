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

    def test_ranking_sensitivity_summary_is_consistent_with_final_report(self):
        from pathlib import Path
        import json

        reports_dir = Path("analysis/reports")

        def load_json(path: Path) -> dict:
            return json.loads(path.read_text(encoding="utf-8"))

        def first_present(row: dict, keys: list[str], default=""):
            for key in keys:
                value = row.get(key)
                if value not in (None, ""):
                    return value
            return default

        def parse_int_like(value) -> int:
            if isinstance(value, bool):
                return int(value)

            if isinstance(value, int):
                return value

            if isinstance(value, float):
                return int(value)

            if isinstance(value, str):
                text = value.strip()
                if text.isdigit():
                    return int(text)

            return 0

        def collect_policy_ids_from_text(text: str) -> set[str]:
            policies: set[str] = set()

            for segment in text.split(";"):
                segment = segment.strip()
                if not segment:
                    continue

                rhs = segment.split("=", 1)[-1].strip()
                policy = rhs.split("+", 1)[0].strip()

                if policy.endswith("_policy_v1") or "_policy_" in policy:
                    policies.add(policy)

            return policies

        def collect_policy_ids_for_batch(node, batch_id: str) -> set[str]:
            policies: set[str] = set()

            if isinstance(node, list):
                for item in node:
                    policies.update(collect_policy_ids_for_batch(item, batch_id))
                return policies

            if not isinstance(node, dict):
                if isinstance(node, str):
                    policies.update(collect_policy_ids_from_text(node))
                return policies

            node_batch_id = node.get("batch_id")
            if node_batch_id not in (None, "", batch_id):
                return policies

            for key in [
                "recommended_policy_id",
                "policy_id",
                "recommended_policy",
                "policy",
            ]:
                value = node.get(key)
                if isinstance(value, str) and (value.endswith("_policy_v1") or "_policy_" in value):
                    policies.add(value)

            for key in [
                "profile_recommendations",
                "ranking_profile_recommendations",
                "recommendations_by_profile",
            ]:
                value = node.get(key)

                if isinstance(value, str):
                    policies.update(collect_policy_ids_from_text(value))
                elif isinstance(value, (dict, list)):
                    policies.update(collect_policy_ids_for_batch(value, batch_id))

            for value in node.values():
                if isinstance(value, (dict, list)):
                    policies.update(collect_policy_ids_for_batch(value, batch_id))

            return policies

        def summary_unique_policy_count(summary_row: dict, ranking: dict, batch_id: str) -> int:
            direct_value = first_present(
                summary_row,
                [
                    "ranking_unique_policy_count",
                    "unique_policy_count",
                    "unique_policies",
                    "unique_recommended_policy_count",
                    "recommended_policy_count",
                ],
                0,
            )

            direct_count = parse_int_like(direct_value)
            if direct_count > 0:
                return direct_count

            for key in [
                "profile_recommendations",
                "ranking_profile_recommendations",
                "recommendations_by_profile",
            ]:
                value = summary_row.get(key)

                if isinstance(value, str):
                    policies = collect_policy_ids_from_text(value)
                    if policies:
                        return len(policies)

                if isinstance(value, (dict, list)):
                    policies = collect_policy_ids_for_batch(value, batch_id)
                    if policies:
                        return len(policies)

            policies = collect_policy_ids_for_batch(ranking, batch_id)
            return len(policies)

        def find_scenario_summary(node):
            if isinstance(node, list):
                if len(node) == 12 and all(isinstance(item, dict) for item in node):
                    keys = set()
                    for item in node:
                        keys.update(item.keys())

                    has_batch_ids = all(item.get("batch_id") for item in node)
                    has_ranking_signal = any(
                        key in keys
                        for key in [
                            "ranking_stability_class",
                            "stability_class",
                            "stability",
                            "unique_policy_count",
                            "ranking_unique_policy_count",
                            "profile_recommendations",
                            "ranking_profile_recommendations",
                        ]
                    )

                    if has_batch_ids and has_ranking_signal:
                        return node

                for item in node:
                    found = find_scenario_summary(item)
                    if found:
                        return found

            if isinstance(node, dict):
                for value in node.values():
                    found = find_scenario_summary(value)
                    if found:
                        return found

            return []

        ranking = load_json(reports_dir / "campaign_ranking_profile_sensitivity.json")
        final = load_json(reports_dir / "campaign_final_diagnostic_report.json")

        scenario_summary = find_scenario_summary(ranking)
        final_rows = final.get("rows", [])

        self.assertEqual(len(scenario_summary), 12)
        self.assertEqual(len(final_rows), 12)

        summary_by_batch = {row["batch_id"]: row for row in scenario_summary}
        final_by_batch = {row["batch_id"]: row for row in final_rows}

        self.assertEqual(set(summary_by_batch.keys()), set(final_by_batch.keys()))

        for batch_id, final_row in final_by_batch.items():
            summary_row = summary_by_batch[batch_id]

            final_stability = first_present(final_row, ["ranking_stability_class"])
            summary_stability = first_present(
                summary_row,
                ["ranking_stability_class", "stability_class", "stability"],
            )

            self.assertTrue(final_stability, f"Missing final ranking stability for {batch_id}")
            self.assertTrue(summary_stability, f"Missing sensitivity ranking stability for {batch_id}")
            self.assertEqual(final_stability, summary_stability)

            final_unique_policy_count = int(
                first_present(final_row, ["ranking_unique_policy_count"], 0)
            )
            derived_summary_count = summary_unique_policy_count(summary_row, ranking, batch_id)

            self.assertGreater(
                derived_summary_count,
                0,
                f"Could not derive unique policy count from ranking sensitivity report for {batch_id}",
            )

            self.assertEqual(final_unique_policy_count, derived_summary_count)
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