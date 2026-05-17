from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_SCRIPT = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module():
    module_name = "fieldops_project_quality_gate_contract_test_module"
    spec = importlib.util.spec_from_file_location(module_name, QUALITY_GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {QUALITY_GATE_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def normalized_command(step) -> list[str]:
    return [str(part).replace("/", "\\") for part in step.command]


class ProjectQualityGateContractTests(unittest.TestCase):
    def test_quality_gate_script_exists(self) -> None:
        self.assertTrue(QUALITY_GATE_SCRIPT.exists())

    def test_quick_quality_gate_has_expected_core_steps(self) -> None:
        module = load_quality_gate_module()
        names = [step.name for step in module.quality_gate_steps(include_full_pipeline=False)]

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
            ],
        )

    def test_full_quality_gate_includes_campaign_pipeline_before_project_status(self) -> None:
        module = load_quality_gate_module()
        names = [step.name for step in module.quality_gate_steps(include_full_pipeline=True)]

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
            ],
        )

    def test_python_unittest_step_uses_project_test_tree(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=False)
        python_step = next(step for step in steps if step.name == "python_unittest")
        command = normalized_command(python_step)

        self.assertIn("unittest", command)
        self.assertIn("discover", command)
        self.assertIn("tests\\python", command)
        self.assertIn("test_*.py", command)
        self.assertIn("-v", command)

    def test_full_pipeline_verification_uses_quality_check_outputs(self) -> None:
        module = load_quality_gate_module()
        steps = module.quality_gate_steps(include_full_pipeline=True)
        verify_step = next(step for step in steps if step.name == "verify_full_campaign_pipeline")
        command = normalized_command(verify_step)

        self.assertIn("analysis\\reports\\full_campaign_pipeline_manifest.json", command)
        self.assertIn("analysis\\reports\\full_campaign_pipeline_report.md", command)
        self.assertIn("analysis\\reports\\full_campaign_pipeline_log.txt", command)
        self.assertIn("analysis\\reports\\full_campaign_pipeline_quality_check.md", command)
        self.assertIn("analysis\\reports\\full_campaign_pipeline_quality_check.json", command)

    def test_quality_gate_contains_no_temporary_patch_script_reference(self) -> None:
        source = QUALITY_GATE_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("patch_", source)


if __name__ == "__main__":
    unittest.main()