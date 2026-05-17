from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPORT_TYPE = "fieldops_lab_test_inventory_report"
QUALITY_REPORT_TYPE = "fieldops_lab_test_inventory_quality_check"


REQUIRED_ROW_FIELDS = [
    "script_path",
    "script_name",
    "script_stem",
    "is_patch_script",
    "direct_python_test_count",
    "related_python_test_count",
    "generic_python_test_count",
    "status",
]


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_quality_report(
    inventory_json_path: Path,
    inventory_md_path: Path,
    inventory_csv_path: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    if not inventory_json_path.exists():
        problems.append(f"Inventory JSON missing: {inventory_json_path}")
        data: dict[str, Any] = {}
    else:
        try:
            data = load_json(inventory_json_path)
        except json.JSONDecodeError as error:
            data = {}
            problems.append(f"Inventory JSON is invalid: {error}")

    if not inventory_md_path.exists():
        problems.append(f"Inventory markdown missing: {inventory_md_path}")
        markdown_text = ""
    else:
        markdown_text = inventory_md_path.read_text(encoding="utf-8")

    if not inventory_csv_path.exists():
        problems.append(f"Inventory CSV missing: {inventory_csv_path}")
        csv_rows: list[dict[str, str]] = []
    else:
        try:
            csv_rows = read_csv_rows(inventory_csv_path)
        except csv.Error as error:
            csv_rows = []
            problems.append(f"Inventory CSV is invalid: {error}")

    if data:
        if data.get("report_type") != REPORT_TYPE:
            problems.append("Inventory JSON has wrong or missing report_type.")

        rows = data.get("rows")
        if not isinstance(rows, list):
            problems.append("Inventory JSON missing rows list.")
            rows = []

        overview = data.get("overview")
        if not isinstance(overview, dict):
            problems.append("Inventory JSON missing overview object.")
            overview = {}

        expected_row_count = int_value(overview.get("row_count", 0))
        if expected_row_count != len(rows):
            problems.append(
                f"Overview row_count={expected_row_count}, but JSON has {len(rows)} row(s)."
            )

        if len(csv_rows) != len(rows):
            problems.append(
                f"CSV row count {len(csv_rows)} does not match JSON row count {len(rows)}."
            )

        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                problems.append(f"Row {index} is not an object.")
                continue

            for field in REQUIRED_ROW_FIELDS:
                if field not in row:
                    problems.append(f"Row {index} missing required field: {field}")

            script_path = str(row.get("script_path", "")).strip()
            status = str(row.get("status", "")).strip()

            if not script_path:
                problems.append(f"Row {index} has empty script_path.")

            if not status:
                problems.append(f"Row {index} has empty status.")

            if bool(row.get("is_patch_script", False)):
                problems.append(f"Temporary patch script found in inventory: {script_path}")

        reported_problem_count = int_value(data.get("problem_count", 0))
        actual_problem_count_from_source = len(data.get("problems", []))
        if reported_problem_count != actual_problem_count_from_source:
            problems.append(
                "Inventory problem_count does not match length of source problems list."
            )

        reported_warning_count = int_value(data.get("warning_count", 0))
        actual_warning_count_from_source = len(data.get("warnings", []))
        if reported_warning_count != actual_warning_count_from_source:
            problems.append(
                "Inventory warning_count does not match length of source warnings list."
            )

        if reported_warning_count > 0:
            warnings.append(f"Inventory contains {reported_warning_count} structural warning(s).")

    if markdown_text and "# FieldOps Lab test inventory report" not in markdown_text:
        problems.append("Inventory markdown title is missing.")

    report = {
        "report_type": QUALITY_REPORT_TYPE,
        "generated_at_local": now_text(),
        "inventory_json_path": str(inventory_json_path),
        "inventory_markdown_path": str(inventory_md_path),
        "inventory_csv_path": str(inventory_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "row_count": len(data.get("rows", [])) if data else 0,
        "csv_row_count": len(csv_rows),
        "analysis_script_count": int_value(
            data.get("overview", {}).get("analysis_script_count", 0)
        )
        if data
        else 0,
        "python_test_count": int_value(data.get("overview", {}).get("python_test_count", 0))
        if data
        else 0,
        "cpp_test_source_count": int_value(
            data.get("overview", {}).get("cpp_test_source_count", 0)
        )
        if data
        else 0,
        "script_without_direct_python_test_count": int_value(
            data.get("overview", {}).get("script_without_direct_python_test_count", 0)
        )
        if data
        else 0,
        "script_needing_test_review_count": int_value(
            data.get("overview", {}).get("script_needing_test_review_count", 0)
        )
        if data
        else 0,
        "problems": problems,
        "warnings": warnings,
        "interpretation": {
            "status": "test_inventory_quality_check",
            "scientific_status": "test_structure_quality_check_only",
        },
    }

    return report


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# FieldOps Lab test inventory quality check")
    lines.append("")
    lines.append(f"Inventory JSON: `{report['inventory_json_path']}`")
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
        "analysis_script_count",
        "python_test_count",
        "cpp_test_source_count",
        "script_without_direct_python_test_count",
        "script_needing_test_review_count",
    ]:
        value = report[key]
        if isinstance(value, bool):
            value = "yes" if value else "no"
        lines.append(f"| {key} | {value} |")
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
            "The test inventory passed the structural quality check. It can be used to guide future test hardening."
        )
    else:
        lines.append(
            "The test inventory failed the structural quality check. Fix the listed problems before relying on it."
        )
    lines.append("")
    lines.append(
        "Warnings indicate test coverage review opportunities, not necessarily execution failures."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_test_inventory_report.py "
            "<inventory_json> <inventory_md> <inventory_csv> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    inventory_json_path = Path(sys.argv[1])
    inventory_md_path = Path(sys.argv[2])
    inventory_csv_path = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    report = build_quality_report(
        inventory_json_path,
        inventory_md_path,
        inventory_csv_path,
    )

    write_markdown(output_md, report)
    write_json(output_json, report)

    print(f"Test inventory quality report written to: {output_md}")
    print(f"Test inventory quality JSON written to: {output_json}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Test inventory quality check failed.", file=sys.stderr)
        return 1

    print("Test inventory quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())