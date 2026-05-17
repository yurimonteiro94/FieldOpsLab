from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module():
    module_name = "fieldops_test_run_project_quality_gate"

    spec = importlib.util.spec_from_file_location(
        module_name,
        SCRIPT_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SCRIPT_PATH}")

    module = importlib.util.module_from_spec(spec)

    # Required for dataclasses and other runtime introspection features.
    sys.modules[module_name] = module

    spec.loader.exec_module(module)
    return module


class ProjectQualityGateContractTests(unittest.TestCase):
    def test_quality_gate_script_exists(self):
        self.assertTrue(SCRIPT_PATH.exists())

    def test_quick_quality_gate_has_expected_core_steps(self):
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
            ],
        )

    def test_full_quality_gate_includes_campaign_pipeline_steps_after_tests(self):
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
                "run_full_campaign_pipeline",
                "verify_full_campaign_pipeline",
            ],
        )

    def test_python_unittest_step_uses_project_test_tree(self):
        module = load_quality_gate_module()

        steps = module.quality_gate_steps(include_full_pipeline=False)
        python_step = next(step for step in steps if step.name == "python_unittest")

        command_text = " ".join(python_step.command)

        self.assertIn("-m unittest discover", command_text)
        self.assertIn("tests", command_text)
        self.assertIn("python", command_text)
        self.assertIn("test_*.py", command_text)

    def test_full_pipeline_verification_uses_quality_check_outputs(self):
        module = load_quality_gate_module()

        steps = module.quality_gate_steps(include_full_pipeline=True)
        verify_step = next(step for step in steps if step.name == "verify_full_campaign_pipeline")

        command_text = " ".join(verify_step.command)

        self.assertIn("full_campaign_pipeline_manifest.json", command_text)
        self.assertIn("full_campaign_pipeline_report.md", command_text)
        self.assertIn("full_campaign_pipeline_log.txt", command_text)
        self.assertIn("full_campaign_pipeline_quality_check.md", command_text)
        self.assertIn("full_campaign_pipeline_quality_check.json", command_text)


if __name__ == "__main__":
    unittest.main()