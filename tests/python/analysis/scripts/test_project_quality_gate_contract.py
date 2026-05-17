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
    module_name = "fieldops_project_quality_gate_contract_module"

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


class ProjectQualityGateContractTests(unittest.TestCase):
    def test_quality_gate_script_exists(self) -> None:
        self.assertTrue(QUALITY_GATE_SCRIPT.exists())

    def test_quick_quality_gate_has_expected_core_steps(self) -> None:
        module = load_quality_gate_module()

        names = step_names(module, include_full_pipeline=False)

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
                "generate_ranking_sensitive_scenario_report",
                "verify_ranking_sensitive_scenario_report",
                "generate_project_status_report",
                "verify_project_status_report",
                "generate_scientific_validation_plan",
                "verify_scientific_validation_plan",
            ],
        )

    def test_full_quality_gate_includes_campaign_pipeline_before_project_status(
        self,
    ) -> None:
        module = load_quality_gate_module()

        names = step_names(module, include_full_pipeline=True)

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
                "generate_ranking_sensitive_scenario_report",
                "verify_ranking_sensitive_scenario_report",
                "generate_project_status_report",
                "verify_project_status_report",
                "generate_scientific_validation_plan",
                "verify_scientific_validation_plan",
            ],
        )

    def test_python_unittest_step_uses_project_test_tree(self) -> None:
        module = load_quality_gate_module()

        step = step_by_name(
            module,
            include_full_pipeline=False,
            step_name="python_unittest",
        )

        self.assertIn("unittest", step.command)
        self.assertIn("discover", step.command)
        self.assertIn("-s", step.command)
        self.assertIn(str(Path("tests") / "python"), step.command)
        self.assertIn("-p", step.command)
        self.assertIn("test_*.py", step.command)

    def test_full_pipeline_verification_uses_quality_check_outputs(self) -> None:
        module = load_quality_gate_module()

        step = step_by_name(
            module,
            include_full_pipeline=True,
            step_name="verify_full_campaign_pipeline",
        )

        text = command_text(step.command)

        self.assertIn(
            str(Path("analysis") / "reports" / "full_campaign_pipeline_manifest.json"),
            text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "full_campaign_pipeline_report.md"),
            text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "full_campaign_pipeline_log.txt"),
            text,
        )
        self.assertIn(
            str(
                Path("analysis")
                / "reports"
                / "full_campaign_pipeline_quality_check.md"
            ),
            text,
        )
        self.assertIn(
            str(
                Path("analysis")
                / "reports"
                / "full_campaign_pipeline_quality_check.json"
            ),
            text,
        )

    def test_project_status_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()

        generate_step = step_by_name(
            module,
            include_full_pipeline=False,
            step_name="generate_project_status_report",
        )
        verify_step = step_by_name(
            module,
            include_full_pipeline=False,
            step_name="verify_project_status_report",
        )

        generate_text = command_text(generate_step.command)
        verify_text = command_text(verify_step.command)

        self.assertIn(
            str(Path("analysis") / "scripts" / "generate_project_status_report.py"),
            generate_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.md"),
            generate_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.json"),
            generate_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.csv"),
            generate_text,
        )

        self.assertIn(
            str(Path("analysis") / "scripts" / "verify_project_status_report.py"),
            verify_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.json"),
            verify_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.md"),
            verify_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_report.csv"),
            verify_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_quality_check.md"),
            verify_text,
        )
        self.assertIn(
            str(Path("analysis") / "reports" / "project_status_quality_check.json"),
            verify_text,
        )

    def test_quality_gate_contains_no_temporary_patch_script_reference(self) -> None:
        source = QUALITY_GATE_SCRIPT.read_text(encoding="utf-8").lower()

        self.assertNotIn("patch_quality_gate", source)
        self.assertNotIn("patch_project_status", source)
        self.assertNotIn("patch_scientific", source)


if __name__ == "__main__":
    unittest.main()