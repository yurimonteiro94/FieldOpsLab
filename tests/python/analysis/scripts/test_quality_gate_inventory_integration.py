from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_SCRIPT = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module() -> ModuleType:
    module_name = "fieldops_quality_gate_inventory_test_module"
    spec = importlib.util.spec_from_file_location(module_name, QUALITY_GATE_SCRIPT)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module spec for {QUALITY_GATE_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def step_names(steps: list[object]) -> list[str]:
    return [str(step.name) for step in steps]


def step_by_name(steps: list[object], name: str) -> object:
    for step in steps:
        if step.name == name:
            return step

    raise AssertionError(f"Step {name!r} was not found. Steps: {step_names(steps)}")


class QualityGateInventoryIntegrationTests(unittest.TestCase):
    def test_quality_gate_generates_and_verifies_test_inventory_after_python_tests(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        names = step_names(steps)

        self.assertLess(names.index("python_unittest"), names.index("generate_test_inventory_report"))
        self.assertLess(names.index("generate_test_inventory_report"), names.index("verify_test_inventory_report"))

    def test_test_inventory_quality_gate_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)

        generate_step = step_by_name(steps, "generate_test_inventory_report")
        verify_step = step_by_name(steps, "verify_test_inventory_report")

        self.assertEqual(
            generate_step.command,
            [
                "py",
                "-3",
                str(Path("analysis") / "scripts" / "generate_test_inventory_report.py"),
                str(Path("analysis") / "reports" / "test_inventory_report.md"),
                str(Path("analysis") / "reports" / "test_inventory_report.json"),
                str(Path("analysis") / "reports" / "test_inventory_report.csv"),
            ],
        )

        self.assertEqual(
            verify_step.command,
            [
                "py",
                "-3",
                str(Path("analysis") / "scripts" / "verify_test_inventory_report.py"),
                str(Path("analysis") / "reports" / "test_inventory_report.json"),
                str(Path("analysis") / "reports" / "test_inventory_report.md"),
                str(Path("analysis") / "reports" / "test_inventory_report.csv"),
                str(Path("analysis") / "reports" / "test_inventory_quality_check.md"),
                str(Path("analysis") / "reports" / "test_inventory_quality_check.json"),
            ],
        )

    def test_inventory_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        names = step_names(steps)

        self.assertEqual(names.count("generate_test_inventory_report"), 1)
        self.assertEqual(names.count("verify_test_inventory_report"), 1)


if __name__ == "__main__":
    unittest.main()