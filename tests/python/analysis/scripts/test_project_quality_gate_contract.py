from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_SCRIPT = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module() -> ModuleType:
    module_name = "fieldops_quality_gate_contract_test_module"
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


class ProjectQualityGateContractTests(unittest.TestCase):
    def test_quality_gate_script_exists(self) -> None:
        self.assertTrue(QUALITY_GATE_SCRIPT.exists())

    def test_quick_quality_gate_has_expected_core_steps(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)

        self.assertEqual(
            step_names(steps),
            [
                "cmake_configure",
                "cmake_build",
                "fieldops_cpp_tests",
                "ctest",
                "python_unittest",
                "generate_test_inventory_report",
                "verify_test_inventory_report",
            ],
        )

    def test_full_quality_gate_includes_campaign_pipeline_steps_after_tests(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)

        self.assertEqual(
            step_names(steps),
            [
                "cmake_configure",
                "cmake_build",
                "fieldops_cpp_tests",
                "ctest",
                "python_unittest",
                "generate_test_inventory_report",
                "verify_test_inventory_report",
                "run_full_campaign_pipeline",
                "verify_full_campaign_pipeline",
            ],
        )

    def test_python_unittest_step_uses_project_test_tree(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        step = step_by_name(steps, "python_unittest")

        self.assertEqual(
            step.command,
            [
                "py",
                "-3",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(Path("tests") / "python"),
                "-p",
                "test_*.py",
                "-v",
            ],
        )

    def test_full_pipeline_verification_uses_quality_check_outputs(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)
        step = step_by_name(steps, "verify_full_campaign_pipeline")

        self.assertEqual(step.command[0:3], ["py", "-3", str(Path("analysis") / "scripts" / "verify_full_campaign_pipeline.py")])

        expected_paths = [
            str(Path("analysis") / "reports" / "full_campaign_pipeline_manifest.json"),
            str(Path("analysis") / "reports" / "full_campaign_pipeline_report.md"),
            str(Path("analysis") / "reports" / "full_campaign_pipeline_log.txt"),
            str(Path("analysis") / "reports" / "full_campaign_pipeline_quality_check.md"),
            str(Path("analysis") / "reports" / "full_campaign_pipeline_quality_check.json"),
        ]

        self.assertEqual(step.command[3:], expected_paths)

    def test_quality_gate_contains_no_temporary_patch_script_reference(self) -> None:
        source = QUALITY_GATE_SCRIPT.read_text(encoding="utf-8").lower()

        self.assertNotIn("patch_", source)


if __name__ == "__main__":
    unittest.main()