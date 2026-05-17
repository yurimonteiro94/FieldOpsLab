from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def load_module(relative_path: str, module_name: str):
    path = PROJECT_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FinalReportsExperimentalDesignIntegrationTests(unittest.TestCase):
    def test_project_status_exposes_experimental_design_context(self) -> None:
        module = load_module(
            "analysis/scripts/generate_project_status_report.py",
            "fieldops_project_status_for_experimental_design_tests",
        )

        report = module.build_report()
        metrics = report["summary_metrics"]

        self.assertGreater(metrics["experimental_design_experiment_count"], 0)
        self.assertGreater(metrics["experimental_design_scenario_count"], 0)
        self.assertGreater(metrics["experimental_design_replication_count"], 0)
        self.assertTrue(metrics["experimental_design_reproducible"])

        quality_files = {
            item["quality_file"]
            for item in report["quality_summaries"]
        }

        self.assertIn(
            "analysis/reports/experimental_design_matrix_quality_check.json",
            quality_files,
        )

    def test_scientific_validation_plan_uses_experimental_design_as_quality_input(self) -> None:
        module = load_module(
            "analysis/scripts/generate_scientific_validation_plan.py",
            "fieldops_scientific_validation_for_experimental_design_tests",
        )

        report = module.build_report()
        context = report["context"]

        self.assertGreater(context["experimental_design_experiment_count"], 0)
        self.assertGreater(context["experimental_design_scenario_count"], 0)
        self.assertGreater(context["experimental_design_replication_count"], 0)
        self.assertTrue(context["experimental_design_reproducible"])

        quality_paths = {
            item["path"]
            for item in report["quality_inputs"]
        }

        self.assertIn(
            "analysis/reports/experimental_design_matrix_quality_check.json",
            quality_paths,
        )

        actions = {
            item["id"]: item
            for item in report["validation_actions"]
        }

        self.assertIn("SCI-001", actions)
        self.assertEqual(actions["SCI-001"]["status"], "in_progress")

        risk_text = "\n".join(report["open_scientific_risks"]).lower()
        self.assertIn("experimental design matrix", risk_text)
        self.assertIn("statistical comparison", risk_text)


if __name__ == "__main__":
    unittest.main()
