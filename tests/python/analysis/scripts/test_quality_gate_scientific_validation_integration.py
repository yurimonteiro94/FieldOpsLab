from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module() -> ModuleType:
    module_name = "fieldops_quality_gate_scientific_validation_test_module"
    spec = importlib.util.spec_from_file_location(module_name, QUALITY_GATE)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def command_text(step: object) -> str:
    command = getattr(step, "command")
    return " ".join(str(part) for part in command)


class QualityGateScientificValidationIntegrationTests(unittest.TestCase):
    def test_quick_quality_gate_generates_scientific_validation_after_project_status(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        names = [step.name for step in steps]

        self.assertLess(
            names.index("verify_project_status_report"),
            names.index("generate_scientific_validation_plan"),
        )
        self.assertLess(
            names.index("generate_scientific_validation_plan"),
            names.index("verify_scientific_validation_plan"),
        )

    def test_full_quality_gate_generates_scientific_validation_after_full_pipeline_and_project_status(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)
        names = [step.name for step in steps]

        self.assertLess(
            names.index("verify_full_campaign_pipeline"),
            names.index("generate_project_status_report"),
        )
        self.assertLess(
            names.index("verify_project_status_report"),
            names.index("generate_scientific_validation_plan"),
        )
        self.assertLess(
            names.index("generate_scientific_validation_plan"),
            names.index("verify_scientific_validation_plan"),
        )

    def test_scientific_validation_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        for include_full_pipeline in [False, True]:
            steps = module.quality_gate_steps(include_full_pipeline=include_full_pipeline)
            names = [step.name for step in steps]

            self.assertEqual(names.count("generate_scientific_validation_plan"), 1)
            self.assertEqual(names.count("verify_scientific_validation_plan"), 1)

    def test_scientific_validation_quality_gate_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)

        generate_step = next(step for step in steps if step.name == "generate_scientific_validation_plan")
        verify_step = next(step for step in steps if step.name == "verify_scientific_validation_plan")

        generate_text = command_text(generate_step)
        verify_text = command_text(verify_step)

        self.assertIn("generate_scientific_validation_plan.py", generate_text)
        self.assertIn("scientific_validation_plan.md", generate_text)
        self.assertIn("scientific_validation_plan.json", generate_text)
        self.assertIn("scientific_validation_plan.csv", generate_text)

        self.assertIn("verify_scientific_validation_plan.py", verify_text)
        self.assertIn("scientific_validation_plan.json", verify_text)
        self.assertIn("scientific_validation_plan.md", verify_text)
        self.assertIn("scientific_validation_plan.csv", verify_text)
        self.assertIn("scientific_validation_plan_quality_check.md", verify_text)
        self.assertIn("scientific_validation_plan_quality_check.json", verify_text)


if __name__ == "__main__":
    unittest.main()