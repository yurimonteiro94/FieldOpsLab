from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_PATH = (
    PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"
)


def load_quality_gate_module():
    module_name = "fieldops_quality_gate_ranking_sensitive_test_module"

    spec = importlib.util.spec_from_file_location(module_name, QUALITY_GATE_PATH)

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run_project_quality_gate.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def step_names(steps) -> list[str]:
    return [step.name for step in steps]


def command_text(step) -> str:
    return " ".join(str(part) for part in step.command).replace("/", "\\")


class QualityGateRankingSensitiveScenarioIntegrationTests(unittest.TestCase):
    def test_quick_quality_gate_generates_ranking_sensitive_report_before_project_status(
        self,
    ) -> None:
        module = load_quality_gate_module()

        steps = module.quality_gate_steps(include_full_pipeline=False)
        names = step_names(steps)

        self.assertEqual(names.count("generate_ranking_sensitive_scenario_report"), 1)
        self.assertEqual(names.count("verify_ranking_sensitive_scenario_report"), 1)

        self.assertLess(
            names.index("verify_test_inventory_report"),
            names.index("generate_ranking_sensitive_scenario_report"),
        )
        self.assertLess(
            names.index("generate_ranking_sensitive_scenario_report"),
            names.index("verify_ranking_sensitive_scenario_report"),
        )
        self.assertLess(
            names.index("verify_ranking_sensitive_scenario_report"),
            names.index("generate_project_status_report"),
        )

        self.assertNotIn("run_full_campaign_pipeline", names)
        self.assertNotIn("verify_full_campaign_pipeline", names)

    def test_full_quality_gate_generates_ranking_sensitive_report_after_full_pipeline(
        self,
    ) -> None:
        module = load_quality_gate_module()

        steps = module.quality_gate_steps(include_full_pipeline=True)
        names = step_names(steps)

        self.assertEqual(names.count("generate_ranking_sensitive_scenario_report"), 1)
        self.assertEqual(names.count("verify_ranking_sensitive_scenario_report"), 1)

        self.assertLess(
            names.index("verify_full_campaign_pipeline"),
            names.index("generate_ranking_sensitive_scenario_report"),
        )
        self.assertLess(
            names.index("generate_ranking_sensitive_scenario_report"),
            names.index("verify_ranking_sensitive_scenario_report"),
        )
        self.assertLess(
            names.index("verify_ranking_sensitive_scenario_report"),
            names.index("generate_project_status_report"),
        )

    def test_ranking_sensitive_quality_gate_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()

        steps = module.quality_gate_steps(include_full_pipeline=False)
        steps_by_name = {step.name: step for step in steps}

        generate_command = command_text(
            steps_by_name["generate_ranking_sensitive_scenario_report"]
        )
        verify_command = command_text(
            steps_by_name["verify_ranking_sensitive_scenario_report"]
        )

        for fragment in [
            "analysis\\scripts\\generate_ranking_sensitive_scenario_report.py",
            "analysis\\reports\\ranking_sensitive_scenario_report.md",
            "analysis\\reports\\ranking_sensitive_scenario_report.json",
            "analysis\\reports\\ranking_sensitive_scenario_report.csv",
        ]:
            self.assertIn(fragment, generate_command)

        for fragment in [
            "analysis\\scripts\\verify_ranking_sensitive_scenario_report.py",
            "analysis\\reports\\ranking_sensitive_scenario_report.json",
            "analysis\\reports\\ranking_sensitive_scenario_report.md",
            "analysis\\reports\\ranking_sensitive_scenario_report.csv",
            "analysis\\reports\\ranking_sensitive_scenario_quality_check.md",
            "analysis\\reports\\ranking_sensitive_scenario_quality_check.json",
        ]:
            self.assertIn(fragment, verify_command)

    def test_ranking_sensitive_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        for include_full_pipeline in [False, True]:
            steps = module.quality_gate_steps(
                include_full_pipeline=include_full_pipeline
            )
            names = step_names(steps)

            self.assertEqual(
                names.count("generate_ranking_sensitive_scenario_report"),
                1,
            )
            self.assertEqual(
                names.count("verify_ranking_sensitive_scenario_report"),
                1,
            )


if __name__ == "__main__":
    unittest.main()