from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_SCRIPT = (
    PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"
)


def load_quality_gate_module() -> ModuleType:
    module_name = "fieldops_quality_gate_web_integration_module"

    spec = importlib.util.spec_from_file_location(
        module_name,
        QUALITY_GATE_SCRIPT,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run_project_quality_gate.py")

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def step_names(module: ModuleType, include_full_pipeline: bool) -> list[str]:
    return [
        step.name
        for step in module.quality_gate_steps(
            include_full_pipeline=include_full_pipeline
        )
    ]


def step_by_name(
    module: ModuleType,
    include_full_pipeline: bool,
    step_name: str,
):
    for step in module.quality_gate_steps(
        include_full_pipeline=include_full_pipeline
    ):
        if step.name == step_name:
            return step

    raise AssertionError(f"Step not found: {step_name}")


def command_text(command: list[str]) -> str:
    return " ".join(command)


class QualityGateWebIntegrationTests(unittest.TestCase):
    def test_quick_quality_gate_includes_web_build_and_tests(self) -> None:
        module = load_quality_gate_module()

        names = step_names(module, include_full_pipeline=False)

        self.assertIn("web_build", names)
        self.assertIn("web_unit_tests", names)

    def test_full_quality_gate_includes_web_build_and_tests(self) -> None:
        module = load_quality_gate_module()

        names = step_names(module, include_full_pipeline=True)

        self.assertIn("web_build", names)
        self.assertIn("web_unit_tests", names)

    def test_web_steps_run_after_python_tests_and_before_reports(self) -> None:
        module = load_quality_gate_module()

        names = step_names(module, include_full_pipeline=False)

        self.assertLess(
            names.index("python_unittest"),
            names.index("web_build"),
        )
        self.assertLess(
            names.index("web_build"),
            names.index("web_unit_tests"),
        )
        self.assertLess(
            names.index("web_unit_tests"),
            names.index("generate_test_inventory_report"),
        )

    def test_web_build_step_uses_root_safe_npm_prefix(self) -> None:
        module = load_quality_gate_module()

        step = step_by_name(
            module,
            include_full_pipeline=False,
            step_name="web_build",
        )

        text = command_text(step.command)

        self.assertIn(step.command[0], ["npm", "npm.cmd"])
        self.assertIn("--prefix", step.command)
        self.assertIn(str(Path("apps") / "web"), step.command)
        self.assertIn("run", step.command)
        self.assertIn("build", step.command)
        self.assertNotIn("cd apps", text.lower())
        self.assertNotIn("cd .\\apps", text.lower())

    def test_web_unit_test_step_uses_vitest_run_mode(self) -> None:
        module = load_quality_gate_module()

        step = step_by_name(
            module,
            include_full_pipeline=False,
            step_name="web_unit_tests",
        )

        text = command_text(step.command)

        self.assertIn(step.command[0], ["npm", "npm.cmd"])
        self.assertIn("--prefix", step.command)
        self.assertIn(str(Path("apps") / "web"), step.command)
        self.assertIn("run", step.command)
        self.assertIn("test", step.command)
        self.assertIn("--run", step.command)
        self.assertNotIn("cd apps", text.lower())
        self.assertNotIn("cd .\\apps", text.lower())

    def test_web_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        quick_names = step_names(module, include_full_pipeline=False)
        full_names = step_names(module, include_full_pipeline=True)

        self.assertEqual(quick_names.count("web_build"), 1)
        self.assertEqual(quick_names.count("web_unit_tests"), 1)
        self.assertEqual(full_names.count("web_build"), 1)
        self.assertEqual(full_names.count("web_unit_tests"), 1)


if __name__ == "__main__":
    unittest.main()