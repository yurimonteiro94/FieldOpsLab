from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


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


def read_csv_row_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return sum(1 for _ in reader)
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def validate(
    audit_json_path: Path,
    audit_md_path: Path,
    audit_csv_path: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    audit = load_json(audit_json_path)

    if audit.get("report_type") != "fieldops_lab_service_delay_impact_audit":
        problems.append("Invalid report_type in audit JSON.")

    summary = audit.get("summary", {})
    rows = audit.get("rows", [])

    if not isinstance(summary, dict):
        problems.append("summary must be an object.")
        summary = {}

    if not isinstance(rows, list):
        problems.append("rows must be an array.")
        rows = []

    batch_count = int(summary.get("batch_count", 0)) if isinstance(summary.get("batch_count", 0), int) else 0

    if batch_count != len(rows):
        problems.append(f"batch_count mismatch. summary={batch_count}; rows={len(rows)}")

    csv_row_count = read_csv_row_count(audit_csv_path)

    if csv_row_count != len(rows):
        problems.append(f"CSV row count mismatch. csv={csv_row_count}; rows={len(rows)}")

    if not audit_md_path.exists():
        problems.append(f"Markdown audit file does not exist: {audit_md_path}")
    else:
        text = audit_md_path.read_text(encoding="utf-8")

        expected_texts = [
            "# FieldOps Lab service delay impact audit",
            "## Batch diagnostics",
            "## Conservative interpretation",
        ]

        for expected in expected_texts:
            if expected not in text:
                problems.append(f"Expected text not found in markdown: {expected}")

    service_only_count = sum(
        1
        for row in rows
        if isinstance(row, dict) and row.get("family") == "service_delay_only"
    )

    combined_count = sum(
        1
        for row in rows
        if isinstance(row, dict) and row.get("family") == "combined_delay"
    )

    if service_only_count == 0:
        problems.append("No service_delay_only batches found in audit rows.")

    if combined_count == 0:
        problems.append("No combined_delay batches found in audit rows.")

    visible_but_neutral_count = int(summary.get("visible_but_neutral_and_kept_plan_count", 0))

    if visible_but_neutral_count > 0:
        warnings.append(
            f"Service delay is visible but neutral under current objective/makespan in {visible_but_neutral_count} batch(es)."
        )

    warning_count = int(summary.get("warning_count", 0))

    if warning_count > 0:
        warnings.append(f"Audit contains {warning_count} methodological warning(s).")

    return {
        "report_type": "fieldops_lab_service_delay_impact_audit_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "audit_json_path": str(audit_json_path),
        "audit_md_path": str(audit_md_path),
        "audit_csv_path": str(audit_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "batch_count": len(rows),
        "csv_row_count": csv_row_count,
        "service_only_batch_count": service_only_count,
        "combined_delay_batch_count": combined_count,
        "visible_but_neutral_and_kept_plan_count": visible_but_neutral_count,
        "problems": problems,
        "warnings": warnings,
        "summary": summary,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_markdown(path: Path, quality: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab service delay impact audit quality check")
    lines.append("")
    lines.append(f"Audit JSON: `{quality['audit_json_path']}`")
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")

    for key in [
        "all_required_checks_passed",
        "problem_count",
        "warning_count",
        "batch_count",
        "csv_row_count",
        "service_only_batch_count",
        "combined_delay_batch_count",
        "visible_but_neutral_and_kept_plan_count",
    ]:
        lines.append(f"| {key} | {format_number(quality.get(key))} |")

    lines.append("")

    lines.append("## Problems")
    lines.append("")

    problems = quality.get("problems", [])

    if problems:
        for problem in problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Warnings")
    lines.append("")

    warnings = quality.get("warnings", [])

    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")

    if quality["all_required_checks_passed"]:
        lines.append(
            "The service-delay impact audit passed the structural quality check. Any warnings should be treated as methodological findings, not as execution failures."
        )
    else:
        lines.append(
            "The service-delay impact audit failed the structural quality check. Fix the listed problems before using the audit."
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_service_delay_impact_audit.py "
            "<audit_json> <audit_md> <audit_csv> <quality_md> <quality_json>",
            file=sys.stderr,
        )
        return 2

    audit_json_path = Path(sys.argv[1])
    audit_md_path = Path(sys.argv[2])
    audit_csv_path = Path(sys.argv[3])
    quality_md_path = Path(sys.argv[4])
    quality_json_path = Path(sys.argv[5])

    try:
        quality = validate(audit_json_path, audit_md_path, audit_csv_path)

        write_markdown(quality_md_path, quality)
        write_json(quality_json_path, quality)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Service delay impact audit quality report written to: {quality_md_path}")
    print(f"Service delay impact audit quality JSON written to: {quality_json_path}")

    if not quality["all_required_checks_passed"]:
        print("ERROR: Service delay impact audit quality check failed.", file=sys.stderr)
        return 1

    print("Service delay impact audit quality check passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())