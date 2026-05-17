from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def path_text(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data


def load_json_or_empty(relative_path: str) -> dict[str, Any]:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return {}

    return load_json(path)


def int_value(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return int(value)
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def bool_value(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"yes", "true", "1"}:
            return True
        if text in {"no", "false", "0"}:
            return False

    return default


def first_count(data: dict[str, Any], keys: list[str], default: int = 0) -> int:
    for key in keys:
        if key in data:
            return int_value(data.get(key), default)

    return default


def count_list_value(data: dict[str, Any], keys: list[str]) -> int:
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            return len(value)

    return 0


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def quality_summary(relative_path: str) -> dict[str, Any]:
    path = PROJECT_ROOT / relative_path

    if not path.exists():
        return {
            "quality_file": relative_path,
            "exists": False,
            "passed": False,
            "problem_count": 1,
            "warning_count": 0,
        }

    data = load_json(path)

    return {
        "quality_file": relative_path,
        "exists": True,
        "passed": bool_value(data.get("all_required_checks_passed", False)),
        "problem_count": int_value(data.get("problem_count", 0)),
        "warning_count": int_value(data.get("warning_count", 0)),
    }


def build_report() -> dict[str, Any]:
    full_pipeline_quality = load_json_or_empty(
        "analysis/reports/full_campaign_pipeline_quality_check.json"
    )
    full_pipeline_manifest = load_json_or_empty(
        "analysis/reports/full_campaign_pipeline_manifest.json"
    )
    test_inventory_quality = load_json_or_empty(
        "analysis/reports/test_inventory_quality_check.json"
    )
    final_diagnostic_quality = load_json_or_empty(
        "analysis/reports/campaign_final_diagnostic_report_quality_check.json"
    )
    ranking_quality = load_json_or_empty(
        "analysis/reports/campaign_ranking_profile_sensitivity_quality_check.json"
    )
    ranking_report = load_json_or_empty(
        "analysis/reports/campaign_ranking_profile_sensitivity.json"
    )
    final_ranking_integration_quality = load_json_or_empty(
        "analysis/reports/campaign_final_ranking_integration_quality_check.json"
    )
    ranking_sensitive_scenario_report = load_json_or_empty(
        "analysis/reports/ranking_sensitive_scenario_report.json"
    )
    ranking_sensitivity_explanation_report = load_json_or_empty(
        "analysis/reports/ranking_sensitivity_explanation_report.json"
    )

    quality_files = [
        "analysis/reports/full_campaign_pipeline_quality_check.json",
        "analysis/reports/test_inventory_quality_check.json",
        "analysis/reports/campaign_final_diagnostic_report_quality_check.json",
        "analysis/reports/campaign_ranking_profile_sensitivity_quality_check.json",
        "analysis/reports/campaign_final_ranking_integration_quality_check.json",
        "analysis/reports/ranking_sensitive_scenario_quality_check.json",
        "analysis/reports/ranking_sensitivity_explanation_quality_check.json",
    ]

    quality_summaries = [quality_summary(path) for path in quality_files]
    structural_all_required_checks_passed = all(
        item["passed"] for item in quality_summaries
    )

    methodological_warning_count = int_value(
        final_diagnostic_quality.get("warning_count", 0)
    )

    engineering_status = (
        "passed_current_structural_quality_gate"
        if structural_all_required_checks_passed
        else "structural_quality_gate_has_problems"
    )

    scientific_status = (
        "diagnostic_only_with_methodological_warnings"
        if methodological_warning_count > 0
        else "diagnostic_only_no_methodological_warnings_detected"
    )

    scenario_summary_count = first_count(
        ranking_quality,
        ["scenario_summary_count"],
        default=0,
    )

    if scenario_summary_count == 0:
        scenario_summary_count = count_list_value(
            ranking_report,
            [
                "scenario_summaries",
                "scenario_summary",
                "scenario_sensitivity_summary",
            ],
        )

    sensitive_to_ranking_profile_count = first_count(
        final_ranking_integration_quality,
        ["sensitive_to_ranking_profile_count"],
        default=0,
    )

    if sensitive_to_ranking_profile_count == 0:
        sensitive_to_ranking_profile_count = first_count(
            ranking_quality,
            ["sensitive_to_ranking_profile_count"],
            default=0,
        )

    ranking_fragility_status = (
        "some_scenarios_sensitive_to_ranking_profile"
        if sensitive_to_ranking_profile_count > 0
        else "no_policy_change_detected_under_current_profiles"
    )

    ranking_sensitive_summary = ranking_sensitive_scenario_report.get("summary", {})
    if not isinstance(ranking_sensitive_summary, dict):
        ranking_sensitive_summary = {}

    ranking_explanation_summary = ranking_sensitivity_explanation_report.get("summary", {})
    if not isinstance(ranking_explanation_summary, dict):
        ranking_explanation_summary = {}

    ranking_sensitive_scenario_count = int_value(
        ranking_sensitive_summary.get("sensitive_scenario_count", 0)
    )
    ranking_sensitivity_explanation_count = int_value(
        ranking_explanation_summary.get("explanation_count", 0)
    )
    policy_change_explanation_count = int_value(
        ranking_explanation_summary.get("policy_change_explanation_count", 0)
    )
    class_change_explanation_count = int_value(
        ranking_explanation_summary.get("class_change_explanation_count", 0)
    )
    all_sensitive_scenarios_have_explanation = bool(
        ranking_explanation_summary.get("all_sensitive_scenarios_have_explanation", False)
    )

    summary_metrics = {
        "engineering_status": engineering_status,
        "scientific_status": scientific_status,
        "structural_all_required_checks_passed": structural_all_required_checks_passed,
        "analysis_script_count": first_count(
            test_inventory_quality,
            ["analysis_script_count"],
        ),
        "python_test_count": first_count(
            test_inventory_quality,
            ["python_test_count"],
        ),
        "cpp_test_source_count": first_count(
            test_inventory_quality,
            ["cpp_test_source_count"],
        ),
        "script_without_direct_python_test_count": first_count(
            test_inventory_quality,
            ["script_without_direct_python_test_count"],
        ),
        "script_needing_test_review_count": first_count(
            test_inventory_quality,
            ["script_needing_test_review_count"],
        ),
        "pipeline_step_count": first_count(
            full_pipeline_quality,
            ["step_count"],
            default=first_count(full_pipeline_manifest, ["step_count"]),
        ),
        "pipeline_failed_step_count": first_count(
            full_pipeline_quality,
            ["failed_step_count"],
            default=first_count(full_pipeline_manifest, ["failed_step_count"]),
        ),
        "final_diagnostic_row_count": first_count(
            final_diagnostic_quality,
            ["row_count", "json_row_count"],
            default=count_csv_rows(REPORTS_DIR / "campaign_final_diagnostic_report.csv"),
        ),
        "ranking_row_count": first_count(
            ranking_quality,
            ["ranking_row_count", "row_count"],
        ),
        "scenario_summary_count": scenario_summary_count,
        "sensitive_to_ranking_profile_count": sensitive_to_ranking_profile_count,
        "ranking_fragility_status": ranking_fragility_status,
        "ranking_sensitive_scenario_count": ranking_sensitive_scenario_count,
        "ranking_sensitivity_explanation_count": ranking_sensitivity_explanation_count,
        "policy_change_explanation_count": policy_change_explanation_count,
        "class_change_explanation_count": class_change_explanation_count,
        "all_sensitive_scenarios_have_explanation": all_sensitive_scenarios_have_explanation,
        "methodological_warning_count": methodological_warning_count,
    }

    ranking_sensitive_summary = ranking_sensitive_scenario_report.get("summary", {})
    if not isinstance(ranking_sensitive_summary, dict):
        ranking_sensitive_summary = {}

    ranking_explanation_summary = ranking_sensitivity_explanation_report.get("summary", {})
    if not isinstance(ranking_explanation_summary, dict):
        ranking_explanation_summary = {}

    ranking_sensitive_scenario_count = int_value(
        ranking_sensitive_summary.get("sensitive_scenario_count", 0)
    )
    ranking_sensitivity_explanation_count = int_value(
        ranking_explanation_summary.get("explanation_count", 0)
    )
    policy_change_explanation_count = int_value(
        ranking_explanation_summary.get("policy_change_explanation_count", 0)
    )
    class_change_explanation_count = int_value(
        ranking_explanation_summary.get("class_change_explanation_count", 0)
    )
    all_sensitive_scenarios_have_explanation = bool(
        ranking_explanation_summary.get("all_sensitive_scenarios_have_explanation", False)
    )

    return {
        "report_type": "fieldops_lab_project_status_report",
        "generated_at_local": now_text(),
        "summary_metrics": summary_metrics,
        "quality_summaries": quality_summaries,
        "next_actions": [
            "Keep strengthening tests when a script receives new behavior.",
            "Avoid treating diagnostic reports as scientific proof before broader instances and statistical validation.",
            "Use the full quality gate before important commits or before presenting results.",
        ],
    }


def summary_rows(report: dict[str, Any]) -> list[dict[str, str]]:
    metrics = report["summary_metrics"]

    rows = [
        ("overall", "engineering_status", metrics["engineering_status"]),
        ("overall", "scientific_status", metrics["scientific_status"]),
        (
            "overall",
            "structural_all_required_checks_passed",
            "yes" if metrics["structural_all_required_checks_passed"] else "no",
        ),
        ("tests", "analysis_script_count", metrics["analysis_script_count"]),
        ("tests", "python_test_count", metrics["python_test_count"]),
        ("tests", "cpp_test_source_count", metrics["cpp_test_source_count"]),
        (
            "tests",
            "script_without_direct_python_test_count",
            metrics["script_without_direct_python_test_count"],
        ),
        (
            "tests",
            "script_needing_test_review_count",
            metrics["script_needing_test_review_count"],
        ),
        ("pipeline", "pipeline_step_count", metrics["pipeline_step_count"]),
        (
            "pipeline",
            "pipeline_failed_step_count",
            metrics["pipeline_failed_step_count"],
        ),
        (
            "final_diagnostic",
            "final_diagnostic_row_count",
            metrics["final_diagnostic_row_count"],
        ),
        ("ranking_sensitivity", "ranking_row_count", metrics["ranking_row_count"]),
        (
            "ranking_sensitivity",
            "scenario_summary_count",
            metrics["scenario_summary_count"],
        ),
        (
            "ranking_sensitivity",
            "sensitive_to_ranking_profile_count",
            metrics["sensitive_to_ranking_profile_count"],
        ),
        (
            "ranking_sensitivity",
            "ranking_fragility_status",
            metrics["ranking_fragility_status"],
        ),
        (
            "ranking_sensitivity_explanation",
            "ranking_sensitive_scenario_count",
            metrics["ranking_sensitive_scenario_count"],
        ),
        (
            "ranking_sensitivity_explanation",
            "ranking_sensitivity_explanation_count",
            metrics["ranking_sensitivity_explanation_count"],
        ),
        (
            "ranking_sensitivity_explanation",
            "policy_change_explanation_count",
            metrics["policy_change_explanation_count"],
        ),
        (
            "ranking_sensitivity_explanation",
            "class_change_explanation_count",
            metrics["class_change_explanation_count"],
        ),
        (
            "ranking_sensitivity_explanation",
            "all_sensitive_scenarios_have_explanation",
            "yes" if metrics["all_sensitive_scenarios_have_explanation"] else "no",
        ),
        (
            "warnings",
            "methodological_warning_count",
            metrics["methodological_warning_count"],
        ),
    ]

    return [
        {
            "category": str(category),
            "field": str(field),
            "value": str(value),
        }
        for category, field, value in rows
    ]


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["category", "field", "value"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    metrics = report["summary_metrics"]
    rows = summary_rows(report)

    lines: list[str] = []

    lines.append("# FieldOps Lab project status report")
    lines.append("")
    lines.append(
        "This report summarizes the current engineering and diagnostic status of the project."
    )
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| engineering_status | {metrics['engineering_status']} |")
    lines.append(f"| scientific_status | {metrics['scientific_status']} |")
    lines.append(
        "| structural_all_required_checks_passed | "
        f"{'yes' if metrics['structural_all_required_checks_passed'] else 'no'} |"
    )
    lines.append("")

    lines.append("## Summary metrics")
    lines.append("")
    lines.append("| Category | Field | Value |")
    lines.append("| --- | --- | ---: |")
    for row in rows:
        lines.append(f"| {row['category']} | {row['field']} | {row['value']} |")
    lines.append("")

    lines.append("## Quality summaries")
    lines.append("")
    lines.append("| Quality file | Passed | Problems | Warnings |")
    lines.append("| --- | --- | ---: | ---: |")
    for item in report["quality_summaries"]:
        lines.append(
            f"| `{item['quality_file']}` | "
            f"{'yes' if item['passed'] else 'no'} | "
            f"{item['problem_count']} | "
            f"{item['warning_count']} |"
        )
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    if metrics["structural_all_required_checks_passed"]:
        lines.append("The project currently passes the structural quality gate.")
    else:
        lines.append("The project does not currently pass the structural quality gate.")
    lines.append("")
    lines.append(
        "This does not prove scientific validity. It confirms that the current engineering pipeline, reports, and test inventory are internally consistent."
    )
    lines.append("")

    lines.append("## Next actions")
    lines.append("")
    for action in report["next_actions"]:
        lines.append(f"- {action}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: generate_project_status_report.py <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    output_md = Path(sys.argv[1])
    output_json = Path(sys.argv[2])
    output_csv = Path(sys.argv[3])

    report = build_report()
    rows = summary_rows(report)

    write_markdown(output_md, report)
    write_json(output_json, report)
    write_csv(output_csv, rows)

    print(f"Project status markdown written to: {output_md}")
    print(f"Project status JSON written to: {output_json}")
    print(f"Project status CSV written to: {output_csv}")
    print("Project status report completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())