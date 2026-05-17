from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"

PROJECT_STATUS_JSON = REPORTS_DIR / "project_status_report.json"

QUALITY_FILE_PATHS = [
    REPORTS_DIR / "full_campaign_pipeline_quality_check.json",
    REPORTS_DIR / "test_inventory_quality_check.json",
    REPORTS_DIR / "campaign_final_diagnostic_report_quality_check.json",
    REPORTS_DIR / "campaign_ranking_profile_sensitivity_quality_check.json",
    REPORTS_DIR / "campaign_final_ranking_integration_quality_check.json",
    REPORTS_DIR / "project_status_quality_check.json",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        return data

    return {}


def recursive_find(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]

        for value in data.values():
            found = recursive_find(value, key)
            if found is not None:
                return found

    if isinstance(data, list):
        for item in data:
            found = recursive_find(item, key)
            if found is not None:
                return found

    return None


def as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"yes", "true", "passed", "pass", "ok"}:
            return True
        if normalized in {"no", "false", "failed", "fail"}:
            return False

    return default


def as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default

    return default


def as_str(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default

    text = str(value).strip()
    if not text:
        return default

    return text


def summarize_quality_file(path: Path) -> dict[str, Any]:
    data = read_json(path)

    passed_value = recursive_find(data, "all_required_checks_passed")
    if passed_value is None:
        passed_value = recursive_find(data, "passed")

    problems = recursive_find(data, "problems")
    warnings = recursive_find(data, "warnings")

    problem_count = recursive_find(data, "problem_count")
    warning_count = recursive_find(data, "warning_count")

    if problem_count is None and isinstance(problems, list):
        problem_count = len(problems)

    if warning_count is None and isinstance(warnings, list):
        warning_count = len(warnings)

    return {
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "exists": path.exists(),
        "passed": as_bool(passed_value, default=False),
        "problem_count": as_int(problem_count, default=0),
        "warning_count": as_int(warning_count, default=0),
    }


def build_validation_actions(context: dict[str, Any]) -> list[dict[str, str]]:
    actions = [
        {
            "id": "SCI-001",
            "priority": "high",
            "category": "experimental_design",
            "action": "Define a broader experimental design with controlled factors for instance size, demand density, delay type, delay severity, policy, and random seed.",
            "acceptance_criterion": "A complete experiment matrix exists and each scenario can be reproduced from explicit configuration files.",
            "evidence_output": "experiment_design_matrix",
            "status": "pending",
        },
        {
            "id": "SCI-002",
            "priority": "high",
            "category": "experimental_design",
            "action": "Run repeated replications for each scenario instead of relying on a single deterministic diagnostic run.",
            "acceptance_criterion": "Each scenario-policy combination has enough replications to estimate variability, confidence intervals, and ranking stability.",
            "evidence_output": "replication_result_dataset",
            "status": "pending",
        },
        {
            "id": "SCI-003",
            "priority": "high",
            "category": "statistical_validation",
            "action": "Add statistical comparison of policies using confidence intervals, effect sizes, and appropriate paired or non-parametric tests.",
            "acceptance_criterion": "Policy recommendations are supported by statistical evidence, not only by point estimates or isolated ranking tables.",
            "evidence_output": "statistical_policy_comparison_report",
            "status": "pending",
        },
        {
            "id": "SCI-004",
            "priority": "high",
            "category": "methodological_limitations",
            "action": "Separate engineering validity from scientific validity in every final report and presentation artifact.",
            "acceptance_criterion": "Reports clearly state that current structural consistency does not prove scientific validity.",
            "evidence_output": "project_status_report",
            "status": "in_progress",
        },
        {
            "id": "SCI-005",
            "priority": "medium",
            "category": "robustness_analysis",
            "action": "Evaluate whether policy recommendations remain stable under different ranking profiles and objective weights.",
            "acceptance_criterion": "Sensitive scenarios are explicitly identified and robust recommendations are distinguished from fragile recommendations.",
            "evidence_output": "ranking_profile_sensitivity_report",
            "status": "in_progress",
        },
        {
            "id": "SCI-006",
            "priority": "medium",
            "category": "external_validation",
            "action": "Prepare at least one real or semi-real company instance for external validation after the synthetic campaign is stable.",
            "acceptance_criterion": "The project includes a documented mapping from real operation data to FieldOps Lab input data.",
            "evidence_output": "real_case_mapping_document",
            "status": "pending",
        },
        {
            "id": "SCI-007",
            "priority": "medium",
            "category": "perturbation_modeling",
            "action": "Justify perturbation distributions, delay ranges, and event frequencies with literature, operational data, or conservative assumptions.",
            "acceptance_criterion": "Every perturbation family has a documented rationale and can be traced to either data, literature, or declared assumption.",
            "evidence_output": "perturbation_model_rationale",
            "status": "pending",
        },
        {
            "id": "SCI-008",
            "priority": "medium",
            "category": "traceability",
            "action": "Create traceability from scenario descriptors to diagnostics, ranking sensitivity, final recommendation, and scientific limitation.",
            "acceptance_criterion": "For each scenario, the final recommendation can be traced back to input assumptions, metrics, and warnings.",
            "evidence_output": "scenario_recommendation_traceability_report",
            "status": "pending",
        },
        {
            "id": "SCI-009",
            "priority": "low",
            "category": "presentation_readiness",
            "action": "Prepare a concise explanation for non-technical stakeholders separating what the platform already proves from what it only diagnoses.",
            "acceptance_criterion": "A non-technical summary exists and avoids overstating the scientific maturity of the current campaign.",
            "evidence_output": "stakeholder_validation_summary",
            "status": "pending",
        },
    ]

    sensitive_count = as_int(context.get("sensitive_to_ranking_profile_count"), default=0)

    if sensitive_count > 0:
        actions.append(
            {
                "id": "SCI-010",
                "priority": "high",
                "category": "robustness_analysis",
                "action": "Investigate scenarios where the recommended policy changes under different ranking profiles.",
                "acceptance_criterion": "Every ranking-sensitive scenario has an explanation of which metrics caused the policy change.",
                "evidence_output": "ranking_fragility_explanation_report",
                "status": "pending",
            }
        )
    else:
        actions.append(
            {
                "id": "SCI-010",
                "priority": "medium",
                "category": "robustness_analysis",
                "action": "Confirm whether the absence of ranking sensitivity remains true after broader instances and replications.",
                "acceptance_criterion": "Ranking stability is confirmed on a broader experimental campaign.",
                "evidence_output": "extended_ranking_stability_report",
                "status": "pending",
            }
        )

    return actions


def build_open_scientific_risks(context: dict[str, Any]) -> list[str]:
    risks = [
        "The current campaign is structurally consistent, but it is still not enough to prove general scientific validity.",
        "Current recommendations may depend on the selected scenario set, ranking profile, and diagnostic assumptions.",
        "The project still needs broader experiments, repeated replications, and statistical comparisons before strong conclusions.",
    ]

    methodological_warning_count = as_int(context.get("methodological_warning_count"), default=0)
    sensitive_count = as_int(context.get("sensitive_to_ranking_profile_count"), default=0)

    if methodological_warning_count > 0:
        risks.append(
            f"The current reports still expose {methodological_warning_count} methodological warning(s)."
        )

    if sensitive_count > 0:
        risks.append(
            f"The current ranking sensitivity analysis found {sensitive_count} scenario(s) sensitive to ranking profile choice."
        )

    return risks


def build_report() -> dict[str, Any]:
    project_status = read_json(PROJECT_STATUS_JSON)
    quality_inputs = [summarize_quality_file(path) for path in QUALITY_FILE_PATHS]

    methodological_warning_count = recursive_find(project_status, "methodological_warning_count")
    if methodological_warning_count is None:
        methodological_warning_count = sum(
            item["warning_count"] for item in quality_inputs
        )

    context = {
        "engineering_status": as_str(
            recursive_find(project_status, "engineering_status"),
            default="unknown",
        ),
        "scientific_status": as_str(
            recursive_find(project_status, "scientific_status"),
            default="unknown",
        ),
        "structural_all_required_checks_passed": as_bool(
            recursive_find(project_status, "structural_all_required_checks_passed"),
            default=False,
        ),
        "analysis_script_count": as_int(
            recursive_find(project_status, "analysis_script_count"),
            default=0,
        ),
        "python_test_count": as_int(
            recursive_find(project_status, "python_test_count"),
            default=0,
        ),
        "cpp_test_source_count": as_int(
            recursive_find(project_status, "cpp_test_source_count"),
            default=0,
        ),
        "pipeline_step_count": as_int(
            recursive_find(project_status, "pipeline_step_count"),
            default=0,
        ),
        "pipeline_failed_step_count": as_int(
            recursive_find(project_status, "pipeline_failed_step_count"),
            default=0,
        ),
        "final_diagnostic_row_count": as_int(
            recursive_find(project_status, "final_diagnostic_row_count"),
            default=0,
        ),
        "ranking_row_count": as_int(
            recursive_find(project_status, "ranking_row_count"),
            default=0,
        ),
        "scenario_summary_count": as_int(
            recursive_find(project_status, "scenario_summary_count"),
            default=0,
        ),
        "sensitive_to_ranking_profile_count": as_int(
            recursive_find(project_status, "sensitive_to_ranking_profile_count"),
            default=0,
        ),
        "ranking_fragility_status": as_str(
            recursive_find(project_status, "ranking_fragility_status"),
            default="unknown",
        ),
        "methodological_warning_count": as_int(
            methodological_warning_count,
            default=0,
        ),
    }

    actions = build_validation_actions(context)
    risks = build_open_scientific_risks(context)

    quality_inputs_available = all(item["exists"] for item in quality_inputs)
    quality_inputs_passed = all(item["passed"] for item in quality_inputs)

    return {
        "report_type": "scientific_validation_plan",
        "validation_stage": "diagnostic_to_experimental_transition",
        "structural_inputs_available": quality_inputs_available,
        "structural_inputs_passed": quality_inputs_passed,
        "context": context,
        "quality_inputs": quality_inputs,
        "open_scientific_risks": risks,
        "validation_actions": actions,
        "conservative_conclusion": (
            "The project is structurally consistent and ready for the next scientific validation phase. "
            "This plan does not prove scientific validity. It defines what must be done before stronger scientific claims are made."
        ),
    }


def write_json_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)


def write_csv_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "priority",
        "category",
        "action",
        "acceptance_criterion",
        "evidence_output",
        "status",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for action in report["validation_actions"]:
            writer.writerow({field: action.get(field, "") for field in fieldnames})


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    context = report["context"]
    quality_inputs = report["quality_inputs"]
    risks = report["open_scientific_risks"]
    actions = report["validation_actions"]

    lines = [
        "# FieldOps Lab scientific validation plan",
        "",
        "This report converts the current diagnostic state into a conservative scientific validation plan.",
        "",
        "This plan does not prove scientific validity. It defines what must be done before stronger scientific claims are made.",
        "",
        "## Overall result",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| validation_stage | {report['validation_stage']} |",
        f"| structural_inputs_available | {'yes' if report['structural_inputs_available'] else 'no'} |",
        f"| structural_inputs_passed | {'yes' if report['structural_inputs_passed'] else 'no'} |",
        f"| engineering_status | {context['engineering_status']} |",
        f"| scientific_status | {context['scientific_status']} |",
        "",
        "## Current evidence snapshot",
        "",
        "| Category | Field | Value |",
        "| --- | --- | ---: |",
        f"| tests | analysis_script_count | {context['analysis_script_count']} |",
        f"| tests | python_test_count | {context['python_test_count']} |",
        f"| tests | cpp_test_source_count | {context['cpp_test_source_count']} |",
        f"| pipeline | pipeline_step_count | {context['pipeline_step_count']} |",
        f"| pipeline | pipeline_failed_step_count | {context['pipeline_failed_step_count']} |",
        f"| diagnostics | final_diagnostic_row_count | {context['final_diagnostic_row_count']} |",
        f"| ranking_sensitivity | ranking_row_count | {context['ranking_row_count']} |",
        f"| ranking_sensitivity | scenario_summary_count | {context['scenario_summary_count']} |",
        f"| ranking_sensitivity | sensitive_to_ranking_profile_count | {context['sensitive_to_ranking_profile_count']} |",
        f"| warnings | methodological_warning_count | {context['methodological_warning_count']} |",
        "",
        "## Quality inputs",
        "",
        "| Quality file | Exists | Passed | Problems | Warnings |",
        "| --- | --- | --- | ---: | ---: |",
    ]

    for item in quality_inputs:
        lines.append(
            f"| `{item['path']}` | {'yes' if item['exists'] else 'no'} | "
            f"{'yes' if item['passed'] else 'no'} | {item['problem_count']} | {item['warning_count']} |"
        )

    lines.extend(
        [
            "",
            "## Open scientific risks",
            "",
        ]
    )

    for risk in risks:
        lines.append(f"- {risk}")

    lines.extend(
        [
            "",
            "## Validation actions",
            "",
            "| ID | Priority | Category | Action | Acceptance criterion | Status |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for action in actions:
        lines.append(
            f"| {action['id']} | {action['priority']} | {action['category']} | "
            f"{action['action']} | {action['acceptance_criterion']} | {action['status']} |"
        )

    lines.extend(
        [
            "",
            "## Conservative conclusion",
            "",
            report["conservative_conclusion"],
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: generate_scientific_validation_plan.py "
            "<output_markdown> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    markdown_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])
    csv_path = Path(sys.argv[3])

    report = build_report()

    write_markdown_report(report, markdown_path)
    write_json_report(report, json_path)
    write_csv_report(report, csv_path)

    print(f"Scientific validation plan markdown written to: {markdown_path}")
    print(f"Scientific validation plan JSON written to: {json_path}")
    print(f"Scientific validation plan CSV written to: {csv_path}")
    print("Scientific validation plan completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())