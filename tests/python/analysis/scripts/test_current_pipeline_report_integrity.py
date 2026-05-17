from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path
from typing import Any

from tests.python.test_support.project_paths import ANALYSIS_REPORTS_DIR


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


class TestCurrentPipelineReportIntegrity(unittest.TestCase):
    def test_full_campaign_pipeline_manifest_exposes_ranking_integration_step(self) -> None:
        manifest_path = ANALYSIS_REPORTS_DIR / "full_campaign_pipeline_manifest.json"

        self.assertTrue(
            manifest_path.exists(),
            "Full campaign pipeline manifest is missing. Run the full pipeline before relying on final reports.",
        )

        manifest = load_json(manifest_path)
        steps = manifest.get("steps", [])
        step_names = {str(step.get("name", "")) for step in steps}

        required_steps = {
            "generate_campaign_ranking_profile_sensitivity",
            "verify_campaign_ranking_profile_sensitivity",
            "integrate_ranking_sensitivity_into_final_diagnostic_report",
            "verify_final_diagnostic_ranking_integration",
        }

        missing = sorted(required_steps - step_names)

        self.assertEqual(
            [],
            missing,
            f"Full pipeline manifest is missing required ranking integration steps: {missing}",
        )

    def test_final_diagnostic_report_contains_ranking_integration_in_json_markdown_and_csv(self) -> None:
        final_json_path = ANALYSIS_REPORTS_DIR / "campaign_final_diagnostic_report.json"
        final_md_path = ANALYSIS_REPORTS_DIR / "campaign_final_diagnostic_report.md"
        final_csv_path = ANALYSIS_REPORTS_DIR / "campaign_final_diagnostic_report.csv"

        for path in [final_json_path, final_md_path, final_csv_path]:
            with self.subTest(path=str(path)):
                self.assertTrue(path.exists(), f"Required final diagnostic file is missing: {path}")
                self.assertGreater(path.stat().st_size, 0, f"Required final diagnostic file is empty: {path}")

        final_json = load_json(final_json_path)
        final_md = final_md_path.read_text(encoding="utf-8")
        final_csv_rows = load_csv(final_csv_path)

        rows = final_json.get("rows", [])
        self.assertEqual(12, len(rows), "Final diagnostic JSON must expose 12 campaign rows.")
        self.assertEqual(12, len(final_csv_rows), "Final diagnostic CSV must expose 12 campaign rows.")

        self.assertIn(
            "Ranking profile sensitivity integration",
            final_md,
            "Final diagnostic Markdown must expose the ranking sensitivity integration section.",
        )

        for row in rows:
            with self.subTest(batch=row.get("batch_id")):
                self.assertTrue(
                    str(row.get("ranking_stability_class", "")).strip(),
                    "Each final diagnostic row must expose ranking_stability_class.",
                )
                self.assertIn(
                    "ranking_unique_policy_count",
                    row,
                    "Each final diagnostic row must expose ranking_unique_policy_count.",
                )

        for row in final_csv_rows:
            with self.subTest(batch=row.get("batch_id")):
                self.assertTrue(
                    str(row.get("ranking_stability_class", "")).strip(),
                    "Each final diagnostic CSV row must expose ranking_stability_class.",
                )

    def test_final_ranking_integration_quality_check_passed(self) -> None:
        quality_path = ANALYSIS_REPORTS_DIR / "campaign_final_ranking_integration_quality_check.json"

        self.assertTrue(
            quality_path.exists(),
            "Final ranking integration quality check JSON is missing.",
        )

        quality = load_json(quality_path)

        self.assertTrue(
            quality.get("all_required_checks_passed", False),
            "Final ranking integration quality check must pass.",
        )
        self.assertEqual(
            0,
            quality.get("problem_count", -1),
            "Final ranking integration quality check must have zero problems.",
        )
        self.assertEqual(12, quality.get("json_row_count"))
        self.assertEqual(12, quality.get("csv_row_count"))
        self.assertEqual(4, quality.get("ranking_profile_count"))
        self.assertEqual(144, quality.get("ranking_row_count"))

    def test_full_pipeline_quality_check_includes_final_ranking_integration_quality_file(self) -> None:
        quality_path = ANALYSIS_REPORTS_DIR / "full_campaign_pipeline_quality_check.json"

        self.assertTrue(
            quality_path.exists(),
            "Full campaign pipeline quality check JSON is missing.",
        )

        quality = load_json(quality_path)
        quality_checks = quality.get("quality_checks", [])

        checked_paths = {str(item.get("path", "")) for item in quality_checks}

        self.assertIn(
            "analysis\\reports\\campaign_final_ranking_integration_quality_check.json",
            checked_paths,
            "Full pipeline quality check must include final ranking integration quality file.",
        )


if __name__ == "__main__":
    unittest.main()