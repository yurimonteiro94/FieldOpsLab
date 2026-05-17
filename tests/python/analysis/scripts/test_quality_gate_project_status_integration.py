from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_SCRIPT = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module():
    module_name = "fieldops_quality_gate_project_status_test_module"
    spec = importlib.util.spec_from_file_location(module_name, QUALITY_GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {QUALITY_GATE_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def normalized_command(step) -> list[str]:
    return [str(part).replace("/", "\\") for part in step.command]


class QualityGateProjectStatusIntegrationTests(unittest.TestCase):
    def test_project_status_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        for include_full_pipeline in (False, True):
            names = [
                step.name
                for step in module.quality_gate_steps(
                    include_full_pipeline=include_full_pipeline
                )
            ]

            self.assertEqual(names.count("generate_project_status_report"), 1)
            self.assertEqual(names.count("verify_project_status_report"), 1)

    def test_quick_quality_gate_generates_project_status_after_test_inventory(self) -> None:
        module = load_quality_gate_module()
        names = [step.name for step in module.quality_gate_steps(include_full_pipeline=False)]

        self.assertLess(
            names.index("verify_test_inventory_report"),
            names.index("generate_project_status_report"),
        )
        self.assertLess(
            names.index("generate_project_status_report"),
            names.index("verify_project_status_report"),
        )

    def test_full_quality_gate_generates_project_status_after_full_pipeline(self) -> None:
        module = load_quality_gate_module()
        names = [step.name for step in module.quality_gate_steps(include_full_pipeline=True)]

        self.assertLess(
            names.index("verify_full_campaign_pipeline"),
            names.index("generate_project_status_report"),
        )
        self.assertLess(
            names.index("generate_project_status_report"),
            names.index("verify_project_status_report"),
        )

    def test_project_status_quality_gate_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)

        generate_step = next(
            step for step in steps if step.name == "generate_project_status_report"
        )
        verify_step = next(
            step for step in steps if step.name == "verify_project_status_report"
        )

        generate_command = normalized_command(generate_step)
        verify_command = normalized_command(verify_step)

        self.assertIn("analysis\\scripts\\generate_project_status_report.py", generate_command)
        self.assertIn("analysis\\reports\\project_status_report.md", generate_command)
        self.assertIn("analysis\\reports\\project_status_report.json", generate_command)
        self.assertIn("analysis\\reports\\project_status_report.csv", generate_command)

        self.assertIn("analysis\\scripts\\verify_project_status_report.py", verify_command)
        self.assertIn("analysis\\reports\\project_status_report.json", verify_command)
        self.assertIn("analysis\\reports\\project_status_report.md", verify_command)
        self.assertIn("analysis\\reports\\project_status_report.csv", verify_command)
        self.assertIn("analysis\\reports\\project_status_quality_check.md", verify_command)
        self.assertIn("analysis\\reports\\project_status_quality_check.json", verify_command)


if __name__ == "__main__":
    unittest.main()