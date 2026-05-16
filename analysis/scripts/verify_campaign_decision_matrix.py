from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "recommendation_class",
    "recommended_policy_id",
    "threshold_with_greedy_trigger_class",
    "provisional_action",
    "evidence_strength",
    "methodological_caution",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def format_number(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def build_quality_report(matrix_json_path: Path, matrix_md_path: Path, matrix_csv_path: Path) -> dict[str, Any]:
    matrix_json = load_json(matrix_json_path)
    rows = matrix_json.get("rows", [])
    overview = matrix_json.get("overview", {})

    if not isinstance(rows, list):
        raise RuntimeError("Decision matrix JSON field 'rows' must be a list.")
    if not isinstance(overview, dict):
        raise RuntimeError("Decision matrix JSON field 'overview' must be an object.")

    csv_rows = read_csv_rows(matrix_csv_path)

    problems: list[str] = []
    warnings: list[str] = []

    if not matrix_md_path.exists():
        problems.append(f"Markdown report not found: {matrix_md_path}")
    else:
        markdown_text = matrix_md_path.read_text(encoding="utf-8")
        if "# FieldOps Lab campaign decision matrix" not in markdown_text:
            problems.append("Markdown report does not contain the expected title.")

    if len(rows) == 0:
        problems.append("Decision matrix has no rows.")

    if len(rows) != len(csv_rows):
        problems.append(f"CSV row count mismatch. json_rows={len(rows)}; csv_rows={len(csv_rows)}")

    overview_count = int(overview.get("matrix_row_count", -1))
    if overview_count != len(rows):
        problems.append(
            f"Overview matrix_row_count mismatch. overview={overview_count}; rows={len(rows)}"
        )

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            problems.append(f"Row {index} is not an object.")
            continue

        for field in REQUIRED_FIELDS:
            if field not in row or str(row[field]).strip() == "":
                problems.append(f"Row {index} missing required field: {field}")

        if row.get("evidence_strength") == "invalid":
            problems.append(f"Row {index} has invalid evidence strength.")

    fuzzy_status = str(overview.get("fuzzy_logic_status", ""))
    if fuzzy_status != "not_used_in_main_pipeline":
        problems.append(f"Unexpected fuzzy_logic_status: {fuzzy_status}")

    low_evidence_count = int(overview.get("low_evidence_count", 0))
    service_review_count = int(overview.get("service_modeling_review_count", 0))
    replan_count = int(overview.get("replan_candidate_count", 0))

    if low_evidence_count > 0:
        warnings.append(
            f"Decision matrix contains {low_evidence_count} low-evidence row(s)."
        )

    if service_review_count > 0:
        warnings.append(
            f"Decision matrix contains {service_review_count} service-modeling review row(s)."
        )

    if replan_count == 0:
        warnings.append("Decision matrix did not identify any replanning candidate.")

    return {
        "report_type": "fieldops_lab_campaign_decision_matrix_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "matrix_json_path": str(matrix_json_path),
        "matrix_markdown_path": str(matrix_md_path),
        "matrix_csv_path": str(matrix_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "row_count": len(rows),
        "csv_row_count": len(csv_rows),
        "low_evidence_count": low_evidence_count,
        "service_modeling_review_count": service_review_count,
        "replan_candidate_count": replan_count,
        "fuzzy_logic_status": fuzzy_status,
        "scientific_status": overview.get("scientific_status", ""),
        "problems": problems,
        "warnings": warnings,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# FieldOps Lab campaign decision matrix quality check")
    lines.append("")
    lines.append(f"Decision matrix JSON: `{report['matrix_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in [
        "all_required_checks_passed",
        "problem_count",
        "warning_count",
        "row_count",
        "csv_row_count",
        "low_evidence_count",
        "service_modeling_review_count",
        "replan_candidate_count",
        "fuzzy_logic_status",
        "scientific_status",
    ]:
        lines.append(f"| {key} | {format_number(report.get(key, ''))} |")

    lines.append("")
    lines.append("## Problems")
    lines.append("")
    if report["problems"]:
        for problem in report["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    if report["all_required_checks_passed"]:
        lines.append(
            "The decision matrix passed the structural quality check. It can be used as a diagnostic consolidation layer."
        )
    else:
        lines.append(
            "The decision matrix failed the structural quality check. Do not use it as evidence until the listed problems are corrected."
        )

    lines.append("")
    lines.append(
        "Warnings are methodological cautions. They do not necessarily indicate execution failure."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_decision_matrix.py "
            "<matrix_json> <matrix_md> <matrix_csv> <quality_md> <quality_json>",
            file=sys.stderr,
        )
        return 2

    try:
        matrix_json = Path(sys.argv[1])
        matrix_md = Path(sys.argv[2])
        matrix_csv = Path(sys.argv[3])
        quality_md = Path(sys.argv[4])
        quality_json = Path(sys.argv[5])

        report = build_quality_report(matrix_json, matrix_md, matrix_csv)
        write_markdown(quality_md, report)
        write_json(quality_json, report)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign decision matrix quality report written to: {quality_md}")
    print(f"Campaign decision matrix quality JSON written to: {quality_json}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Campaign decision matrix quality check failed.", file=sys.stderr)
        return 1

    print("Campaign decision matrix quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())