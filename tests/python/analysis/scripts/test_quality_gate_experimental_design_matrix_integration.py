from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_PATH = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


EXPECTED_GENERATE_FRAGMENTS = [
    r"analysis\scripts\generate_experimental_design_matrix.py",
    r"analysis\reports\experimental_design_matrix.md",
    r"analysis\reports\experimental_design_matrix.json",
    r"analysis\reports\experimental_design_matrix.csv",
]

EXPECTED_VERIFY_FRAGMENTS = [
    r"analysis\scripts\verify_experimental_design_matrix.py",
    r"analysis\reports\experimental_design_matrix.json",
    r"analysis\reports\experimental_design_matrix.md",
    r"analysis\reports\experimental_design_matrix.csv",
    r"analysis\reports\experimental_design_matrix_quality_check.md",
    r"analysis\reports\experimental_design_matrix_quality_check.json",
]


def load_quality_gate_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "fieldops_quality_gate_for_experimental_design_tests",
        QUALITY_GATE_PATH,
    )

    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load module from {QUALITY_GATE_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def build_steps(module: Any, *, full: bool) -> list[Any]:
    if not hasattr(module, "quality_gate_steps"):
        raise AssertionError("run_project_quality_gate.py must expose quality_gate_steps.")

    builder = module.quality_gate_steps

    attempts = [
        lambda: builder(full=full),
        lambda: builder(run_full_pipeline=full),
        lambda: builder(full_pipeline=full),
        lambda: builder(quick=not full),
        lambda: builder(full),
        lambda: builder(),
    ]

    last_error: TypeError | None = None

    for attempt in attempts:
        try:
            return list(attempt())
        except TypeError as exc:
            last_error = exc

    raise AssertionError(
        "Could not call quality_gate_steps with a known signature."
    ) from last_error


def step_name(step: Any) -> str:
    if hasattr(step, "name"):
        return str(step.name)

    if isinstance(step, dict):
        return str(step.get("name", ""))

    return ""


def step_command(step: Any) -> list[str]:
    if hasattr(step, "command"):
        return [str(item) for item in step.command]

    if isinstance(step, dict):
        return [str(item) for item in step.get("command", [])]

    return []


def step_names(steps: list[Any]) -> list[str]:
    return [step_name(step) for step in steps]


def command_text(step: Any) -> str:
    return " ".join(step_command(step))


def assert_order_if_both_exist(
    test_case: unittest.TestCase,
    names: list[str],
    before: str,
    after: str,
) -> None:
    if before in names and after in names:
        test_case.assertLess(names.index(before), names.index(after))


class QualityGateExperimentalDesignMatrixIntegrationTests(unittest.TestCase):
    def test_quick_quality_gate_generates_experimental_design_before_project_status(
        self,
    ) -> None:
        module = load_quality_gate_module()
        names = step_names(build_steps(module, full=False))

        self.assertIn("generate_experimental_design_matrix", names)
        self.assertIn("verify_experimental_design_matrix", names)
        self.assertIn("generate_project_status_report", names)

        assert_order_if_both_exist(
            self,
            names,
            "verify_ranking_sensitivity_explanation_report",
            "generate_experimental_design_matrix",
        )
        assert_order_if_both_exist(
            self,
            names,
            "generate_experimental_design_matrix",
            "verify_experimental_design_matrix",
        )
        assert_order_if_both_exist(
            self,
            names,
            "verify_experimental_design_matrix",
            "generate_project_status_report",
        )

    def test_full_quality_gate_generates_experimental_design_before_project_status(
        self,
    ) -> None:
        module = load_quality_gate_module()
        names = step_names(build_steps(module, full=True))

        self.assertIn("generate_experimental_design_matrix", names)
        self.assertIn("verify_experimental_design_matrix", names)
        self.assertIn("generate_project_status_report", names)

        assert_order_if_both_exist(
            self,
            names,
            "verify_ranking_sensitivity_explanation_report",
            "generate_experimental_design_matrix",
        )
        assert_order_if_both_exist(
            self,
            names,
            "generate_experimental_design_matrix",
            "verify_experimental_design_matrix",
        )
        assert_order_if_both_exist(
            self,
            names,
            "verify_experimental_design_matrix",
            "generate_project_status_report",
        )

    def test_experimental_design_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        for full in [False, True]:
            names = step_names(build_steps(module, full=full))

            self.assertEqual(names.count("generate_experimental_design_matrix"), 1)
            self.assertEqual(names.count("verify_experimental_design_matrix"), 1)

    def test_experimental_design_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()
        steps = build_steps(module, full=False)

        by_name = {step_name(step): step for step in steps}

        self.assertIn("generate_experimental_design_matrix", by_name)
        self.assertIn("verify_experimental_design_matrix", by_name)

        generate_command = command_text(by_name["generate_experimental_design_matrix"])
        verify_command = command_text(by_name["verify_experimental_design_matrix"])

        for fragment in EXPECTED_GENERATE_FRAGMENTS:
            self.assertIn(fragment, generate_command)

        for fragment in EXPECTED_VERIFY_FRAGMENTS:
            self.assertIn(fragment, verify_command)


if __name__ == "__main__":
    unittest.main()