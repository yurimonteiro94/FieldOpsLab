from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
QUALITY_GATE_PATH = PROJECT_ROOT / "analysis" / "scripts" / "run_project_quality_gate.py"


def load_quality_gate_module():
    spec = importlib.util.spec_from_file_location(
        "fieldops_quality_gate_for_ranking_sensitivity_explanation_tests",
        QUALITY_GATE_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run_project_quality_gate.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def step_names(steps) -> list[str]:
    return [step.name for step in steps]


def command_text(step) -> str:
    return " ".join(str(part) for part in step.command)


def step_by_name(steps, name: str):
    for step in steps:
        if step.name == name:
            return step

    raise AssertionError(f"Missing quality gate step: {name}")


def try_build_steps(function: Any, args: tuple[Any, ...], kwargs: dict[str, Any]):
    try:
        steps = function(*args, **kwargs)
    except TypeError:
        return None

    if steps is None:
        return None

    try:
        step_names(steps)
    except Exception:
        return None

    return steps


def collect_step_candidates(module: Any):
    candidates = []

    function_names = [
        "quality_gate_steps",
        "build_steps",
        "build_quality_gate_steps",
        "build_quick_steps",
        "build_full_steps",
        "build_quick_quality_gate_steps",
        "build_full_quality_gate_steps",
    ]

    call_shapes = [
        ((), {}),
        ((True,), {}),
        ((False,), {}),
        (("quick",), {}),
        (("full",), {}),
        ((), {"quick": True}),
        ((), {"quick": False}),
        ((), {"full": True}),
        ((), {"full": False}),
        ((), {"include_full_pipeline": True}),
        ((), {"include_full_pipeline": False}),
    ]

    for function_name in function_names:
        function = getattr(module, function_name, None)

        if function is None:
            continue

        for args, kwargs in call_shapes:
            steps = try_build_steps(function, args, kwargs)

            if steps is None:
                continue

            candidates.append(
                {
                    "function_name": function_name,
                    "args": args,
                    "kwargs": kwargs,
                    "steps": steps,
                    "names": step_names(steps),
                }
            )

    return candidates


def build_quick_quality_gate_steps(module: Any):
    candidates = collect_step_candidates(module)

    for candidate in candidates:
        names = candidate["names"]

        if "run_full_campaign_pipeline" not in names:
            return candidate["steps"]

    available = [
        {
            "function_name": candidate["function_name"],
            "args": candidate["args"],
            "kwargs": candidate["kwargs"],
            "names": candidate["names"],
        }
        for candidate in candidates
    ]

    raise AssertionError(
        "Could not identify quick quality gate steps. "
        f"Available candidates: {available}"
    )


def build_full_quality_gate_steps(module: Any):
    candidates = collect_step_candidates(module)

    for candidate in candidates:
        names = candidate["names"]

        if "run_full_campaign_pipeline" in names:
            return candidate["steps"]

    available = [
        {
            "function_name": candidate["function_name"],
            "args": candidate["args"],
            "kwargs": candidate["kwargs"],
            "names": candidate["names"],
        }
        for candidate in candidates
    ]

    raise AssertionError(
        "Could not identify full quality gate steps. "
        f"Available candidates: {available}"
    )


class QualityGateRankingSensitivityExplanationIntegrationTests(unittest.TestCase):
    def test_quick_quality_gate_generates_explanation_after_ranking_sensitive_report(self) -> None:
        module = load_quality_gate_module()

        names = step_names(build_quick_quality_gate_steps(module))

        self.assertIn("generate_ranking_sensitive_scenario_report", names)
        self.assertIn("verify_ranking_sensitive_scenario_report", names)
        self.assertIn("generate_ranking_sensitivity_explanation_report", names)
        self.assertIn("verify_ranking_sensitivity_explanation_report", names)
        self.assertIn("generate_project_status_report", names)

        self.assertLess(
            names.index("verify_ranking_sensitive_scenario_report"),
            names.index("generate_ranking_sensitivity_explanation_report"),
        )
        self.assertLess(
            names.index("verify_ranking_sensitivity_explanation_report"),
            names.index("generate_project_status_report"),
        )

    def test_full_quality_gate_generates_explanation_after_ranking_sensitive_report(self) -> None:
        module = load_quality_gate_module()

        names = step_names(build_full_quality_gate_steps(module))

        self.assertIn("run_full_campaign_pipeline", names)
        self.assertIn("verify_full_campaign_pipeline", names)
        self.assertIn("generate_ranking_sensitive_scenario_report", names)
        self.assertIn("verify_ranking_sensitive_scenario_report", names)
        self.assertIn("generate_ranking_sensitivity_explanation_report", names)
        self.assertIn("verify_ranking_sensitivity_explanation_report", names)
        self.assertIn("generate_project_status_report", names)

        self.assertLess(
            names.index("verify_full_campaign_pipeline"),
            names.index("generate_ranking_sensitive_scenario_report"),
        )
        self.assertLess(
            names.index("verify_ranking_sensitive_scenario_report"),
            names.index("generate_ranking_sensitivity_explanation_report"),
        )
        self.assertLess(
            names.index("verify_ranking_sensitivity_explanation_report"),
            names.index("generate_project_status_report"),
        )

    def test_ranking_sensitivity_explanation_steps_are_not_duplicated(self) -> None:
        module = load_quality_gate_module()

        for steps in [
            build_quick_quality_gate_steps(module),
            build_full_quality_gate_steps(module),
        ]:
            names = step_names(steps)

            self.assertEqual(
                names.count("generate_ranking_sensitivity_explanation_report"),
                1,
            )
            self.assertEqual(
                names.count("verify_ranking_sensitivity_explanation_report"),
                1,
            )

    def test_ranking_sensitivity_explanation_steps_use_expected_files(self) -> None:
        module = load_quality_gate_module()

        steps = build_quick_quality_gate_steps(module)

        generate_step = step_by_name(
            steps,
            "generate_ranking_sensitivity_explanation_report",
        )
        verify_step = step_by_name(
            steps,
            "verify_ranking_sensitivity_explanation_report",
        )

        generate_command = command_text(generate_step)
        verify_command = command_text(verify_step)

        self.assertIn(
            "analysis\\scripts\\generate_ranking_sensitivity_explanation_report.py",
            generate_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.md",
            generate_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.json",
            generate_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.csv",
            generate_command,
        )

        self.assertIn(
            "analysis\\scripts\\verify_ranking_sensitivity_explanation_report.py",
            verify_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.json",
            verify_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.md",
            verify_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_report.csv",
            verify_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_quality_check.md",
            verify_command,
        )
        self.assertIn(
            "analysis\\reports\\ranking_sensitivity_explanation_quality_check.json",
            verify_command,
        )


if __name__ == "__main__":
    unittest.main()
