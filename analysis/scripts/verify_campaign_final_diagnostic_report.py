from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_ROW_FIELDS = [
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "provisional_action",
    "evidence_strength",
    "scientific_use_status",
    "threshold_with_greedy_trigger_class",
]

EXPECTED_MARKDOWN_TEXT = "# FieldOps Lab campaign final diagnostic report"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def format_number(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")

    if value is None:
        return ""

    return str(value)


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def check_report(
    final_json_path: Path,
    final_md_path: Path,
    final_csv_path: Path,
) -> tuple[dict[str, Any], list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []

    data = load_json(final_json_path)
    csv_rows = read_csv_rows(final_csv_path)

    try:
        markdown_text = final_md_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        markdown_text = ""
        problems.append(f"Markdown file not found: {final_md_path}")

    if EXPECTED_MARKDOWN_TEXT not in markdown_text:
        problems.append(f"Expected markdown title not found: {EXPECTED_MARKDOWN_TEXT}")

    report_type = data.get("report_type", "")
    if report_type != "fieldops_lab_campaign_final_diagnostic_report":
        problems.append(
            "Unexpected report_type. "
            f"expected=fieldops_lab_campaign_final_diagnostic_report; actual={report_type}"
        )

    overview = data.get("overview", {})
    if not isinstance(overview, dict):
        problems.append("Missing or invalid overview object.")
        overview = {}

    rows = data.get("rows", [])
    if not isinstance(rows, list):
        problems.append("Missing or invalid rows list.")
        rows = []

    row_dicts = [row for row in rows if isinstance(row, dict)]
    if len(row_dicts) != len(rows):
        problems.append("Rows list contains non-object item(s).")

    overview_row_count = int_value(overview.get("decision_row_count", -1))
    if overview_row_count != len(row_dicts):
        problems.append(
            "Decision row count mismatch. "
            f"overview={overview_row_count}; actual={len(row_dicts)}"
        )

    if len(csv_rows) != len(row_dicts):
        problems.append(
            "CSV row count mismatch. "
            f"csv={len(csv_rows)}; json_rows={len(row_dicts)}"
        )

    for index, row in enumerate(row_dicts, start=1):
        for field in REQUIRED_ROW_FIELDS:
            value = row.get(field, "")
            if value is None or str(value).strip() == "":
                problems.append(f"Row {index} missing required field: {field}")

    source_files = data.get("source_files", [])
    if not isinstance(source_files, list) or len(source_files) < 6:
        problems.append("Expected at least 6 source files in source_files list.")

    semantic_problem_count = int_value(overview.get("semantic_problem_count", 0))
    invalid_evidence_count = int_value(overview.get("invalid_evidence_count", 0))
    low_evidence_count = int_value(overview.get("low_evidence_count", 0))
    service_modeling_review_count = int_value(overview.get("service_modeling_review_count", 0))
    replan_candidate_count = int_value(overview.get("replan_candidate_count", 0))

    if semantic_problem_count > 0:
        problems.append(f"Semantic problems remain in final report: {semantic_problem_count}")

    if invalid_evidence_count > 0:
        problems.append(f"Invalid evidence rows found: {invalid_evidence_count}")

    if low_evidence_count > 0:
        warnings.append(f"Final report contains {low_evidence_count} low-evidence row(s).")

    if service_modeling_review_count > 0:
        warnings.append(
            f"Final report contains {service_modeling_review_count} service-modeling review row(s)."
        )

    if replan_candidate_count == 0:
        warnings.append("Final report contains no replanning candidate rows.")

    quality = {
        "report_type": "fieldops_lab_campaign_final_diagnostic_report_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "final_json_path": str(final_json_path),
        "final_markdown_path": str(final_md_path),
        "final_csv_path": str(final_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "decision_row_count": len(row_dicts),
        "csv_row_count": len(csv_rows),
        "source_file_count": len(source_files) if isinstance(source_files, list) else 0,
        "low_evidence_count": low_evidence_count,
        "service_modeling_review_count": service_modeling_review_count,
        "replan_candidate_count": replan_candidate_count,
        "semantic_problem_count": semantic_problem_count,
        "invalid_evidence_count": invalid_evidence_count,
        "fuzzy_logic_status": overview.get("fuzzy_logic_status", ""),
        "scientific_status": overview.get("scientific_status", ""),
        "general_project_completeness_estimate_percent": overview.get(
            "general_project_completeness_estimate_percent", ""
        ),
        "campaign_pipeline_completeness_estimate_percent": overview.get(
            "campaign_pipeline_completeness_estimate_percent", ""
        ),
        "problems": problems,
        "warnings": warnings,
    }

    return quality, problems, warnings


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_markdown(path: Path, quality: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign final diagnostic report quality check")
    lines.append("")
    lines.append(f"Final JSON: `{quality['final_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| all_required_checks_passed | {format_number(quality['all_required_checks_passed'])} |"
    )
    lines.append(f"| problem_count | {format_number(quality['problem_count'])} |")
    lines.append(f"| warning_count | {format_number(quality['warning_count'])} |")
    lines.append(f"| decision_row_count | {format_number(quality['decision_row_count'])} |")
    lines.append(f"| csv_row_count | {format_number(quality['csv_row_count'])} |")
    lines.append(f"| source_file_count | {format_number(quality['source_file_count'])} |")
    lines.append(f"| low_evidence_count | {format_number(quality['low_evidence_count'])} |")
    lines.append(
        f"| service_modeling_review_count | {format_number(quality['service_modeling_review_count'])} |"
    )
    lines.append(f"| replan_candidate_count | {format_number(quality['replan_candidate_count'])} |")
    lines.append(f"| semantic_problem_count | {format_number(quality['semantic_problem_count'])} |")
    lines.append(f"| invalid_evidence_count | {format_number(quality['invalid_evidence_count'])} |")
    lines.append(f"| fuzzy_logic_status | {quality['fuzzy_logic_status']} |")
    lines.append(f"| scientific_status | {quality['scientific_status']} |")
    lines.append(
        f"| general_project_completeness_estimate_percent | {format_number(quality['general_project_completeness_estimate_percent'])} |"
    )
    lines.append(
        f"| campaign_pipeline_completeness_estimate_percent | {format_number(quality['campaign_pipeline_completeness_estimate_percent'])} |"
    )
    lines.append("")

    lines.append("## Problems")
    lines.append("")

    if quality["problems"]:
        for problem in quality["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Warnings")
    lines.append("")

    if quality["warnings"]:
        for warning in quality["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")

    if quality["all_required_checks_passed"]:
        lines.append(
            "The final diagnostic report passed the structural quality check. "
            "It can be used as a consolidated project artifact for the current campaign."
        )
    else:
        lines.append(
            "The final diagnostic report failed the structural quality check. "
            "Do not use it as a consolidated artifact until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "Passing this check does not prove scientific validity. It confirms that the final diagnostic layer is internally consistent."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_final_diagnostic_report.py "
            "<final_json> <final_md> <final_csv> <quality_md> <quality_json>",
            file=sys.stderr,
        )
        return 2

    final_json_path = Path(sys.argv[1])
    final_md_path = Path(sys.argv[2])
    final_csv_path = Path(sys.argv[3])
    quality_md_path = Path(sys.argv[4])
    quality_json_path = Path(sys.argv[5])

    try:
        quality, problems, _warnings = check_report(
            final_json_path,
            final_md_path,
            final_csv_path,
        )
    except RuntimeError as exc:
        quality = {
            "report_type": "fieldops_lab_campaign_final_diagnostic_report_quality_check",
            "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
            "final_json_path": str(final_json_path),
            "final_markdown_path": str(final_md_path),
            "final_csv_path": str(final_csv_path),
            "all_required_checks_passed": False,
            "problem_count": 1,
            "warning_count": 0,
            "decision_row_count": 0,
            "csv_row_count": 0,
            "source_file_count": 0,
            "low_evidence_count": 0,
            "service_modeling_review_count": 0,
            "replan_candidate_count": 0,
            "semantic_problem_count": 0,
            "invalid_evidence_count": 0,
            "fuzzy_logic_status": "",
            "scientific_status": "",
            "general_project_completeness_estimate_percent": "",
            "campaign_pipeline_completeness_estimate_percent": "",
            "problems": [str(exc)],
            "warnings": [],
        }
        problems = [str(exc)]

    write_markdown(quality_md_path, quality)
    write_json(quality_json_path, quality)

    print(f"Campaign final diagnostic quality report written to: {quality_md_path}")
    print(f"Campaign final diagnostic quality JSON written to: {quality_json_path}")

    if problems:
        print("ERROR: Campaign final diagnostic quality check failed.", file=sys.stderr)
        return 1

    print("Campaign final diagnostic quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())