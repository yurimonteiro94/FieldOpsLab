from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module() -> ModuleType:
    module_name = "fieldops_quality_gate_contract_test_module"
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


class ProjectQualityGateContractTests(unittest.TestCase):
    def test_quality_gate_script_exists(self) -> None:
        self.assertTrue(QUALITY_GATE.exists())

    def test_quality_gate_contains_no_temporary_patch_script_reference(self) -> None:
        source = QUALITY_GATE.read_text(encoding="utf-8").lower()
        self.assertNotIn("patch_", source)
        self.assertNotIn("temporary", source)

    def test_quick_quality_gate_has_expected_core_steps(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        names = [step.name for step in steps]

        self.assertEqual(
            names,
            [
                "cmake_configure",
                "cmake_build",
                "fieldops_cpp_tests",
                "ctest",
                "python_unittest",
                "generate_test_inventory_report",
                "verify_test_inventory_report",
                "generate_project_status_report",
                "verify_project_status_report",
                "generate_scientific_validation_plan",
                "verify_scientific_validation_plan",
            ],
        )

    def test_full_quality_gate_includes_campaign_pipeline_before_project_status(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)
        names = [step.name for step in steps]

        self.assertEqual(
            names,
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
                "generate_project_status_report",
                "verify_project_status_report",
                "generate_scientific_validation_plan",
                "verify_scientific_validation_plan",
            ],
        )

    def test_python_unittest_step_uses_project_test_tree(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)

        python_step = next(step for step in steps if step.name == "python_unittest")
        text = command_text(python_step)

        self.assertIn("unittest", text)
        self.assertIn("discover", text)
        self.assertIn("tests", text)
        self.assertIn("python", text)
        self.assertIn("test_*.py", text)

    def test_full_pipeline_verification_uses_quality_check_outputs(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)

        verify_step = next(step for step in steps if step.name == "verify_full_campaign_pipeline")
        text = command_text(verify_step)

        self.assertIn("verify_full_campaign_pipeline.py", text)
        self.assertIn("full_campaign_pipeline_manifest.json", text)
        self.assertIn("full_campaign_pipeline_report.md", text)
        self.assertIn("full_campaign_pipeline_log.txt", text)
        self.assertIn("full_campaign_pipeline_quality_check.md", text)
        self.assertIn("full_campaign_pipeline_quality_check.json", text)

    def test_project_status_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)

        generate_step = next(step for step in steps if step.name == "generate_project_status_report")
        verify_step = next(step for step in steps if step.name == "verify_project_status_report")

        generate_text = command_text(generate_step)
        verify_text = command_text(verify_step)

        self.assertIn("generate_project_status_report.py", generate_text)
        self.assertIn("project_status_report.md", generate_text)
        self.assertIn("project_status_report.json", generate_text)
        self.assertIn("project_status_report.csv", generate_text)

        self.assertIn("verify_project_status_report.py", verify_text)
        self.assertIn("project_status_report.json", verify_text)
        self.assertIn("project_status_report.md", verify_text)
        self.assertIn("project_status_report.csv", verify_text)
        self.assertIn("project_status_quality_check.md", verify_text)
        self.assertIn("project_status_quality_check.json", verify_text)


if __name__ == "__main__":
    unittest.main()