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


def csv_row_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return sum(1 for _ in reader)
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def validate(audit_json: Path, audit_md: Path, audit_csv: Path) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    data = load_json(audit_json)

    if data.get("report_type") != "fieldops_lab_policy_trigger_behavior_audit":
        problems.append("Invalid report_type in audit JSON.")

    summary = data.get("summary", {})
    rows = data.get("rows", [])

    if not isinstance(summary, dict):
        problems.append("summary must be an object.")
        summary = {}

    if not isinstance(rows, list):
        problems.append("rows must be an array.")
        rows = []

    expected_row_count = int(summary.get("row_count", 0)) if isinstance(summary.get("row_count", 0), int) else 0

    if expected_row_count != len(rows):
        problems.append(f"row_count mismatch. summary={expected_row_count}; rows={len(rows)}")

    actual_csv_rows = csv_row_count(audit_csv)

    if actual_csv_rows != len(rows):
        problems.append(f"CSV row count mismatch. csv={actual_csv_rows}; rows={len(rows)}")

    if not audit_md.exists():
        problems.append(f"Markdown file does not exist: {audit_md}")
    else:
        text = audit_md.read_text(encoding="utf-8")

        for expected in [
            "# FieldOps Lab policy trigger behavior audit",
            "## Trigger behavior by option",
            "## Conservative interpretation",
        ]:
            if expected not in text:
                problems.append(f"Expected text not found in markdown: {expected}")

    threshold_row_count = int(summary.get("threshold_row_count", 0))
    triggered_threshold_row_count = int(summary.get("triggered_threshold_row_count", 0))
    service_not_triggering_count = int(summary.get("service_delay_not_triggering_threshold_count", 0))
    warning_count = int(summary.get("warning_count", 0))

    if threshold_row_count <= 0:
        problems.append("No threshold policy rows were found.")

    if triggered_threshold_row_count <= 0:
        problems.append("No threshold policy ever triggered replanning.")

    if service_not_triggering_count > 0:
        warnings.append(
            f"Service-only moderate/severe threshold rows did not trigger replanning in {service_not_triggering_count} case(s)."
        )

    if warning_count > 0:
        warnings.append(f"Audit contains {warning_count} methodological warning(s).")

    return {
        "report_type": "fieldops_lab_policy_trigger_behavior_audit_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "audit_json_path": str(audit_json),
        "audit_md_path": str(audit_md),
        "audit_csv_path": str(audit_csv),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "row_count": len(rows),
        "csv_row_count": actual_csv_rows,
        "threshold_row_count": threshold_row_count,
        "triggered_threshold_row_count": triggered_threshold_row_count,
        "service_delay_not_triggering_threshold_count": service_not_triggering_count,
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

    lines.append("# FieldOps Lab policy trigger behavior audit quality check")
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
        "row_count",
        "csv_row_count",
        "threshold_row_count",
        "triggered_threshold_row_count",
        "service_delay_not_triggering_threshold_count",
    ]:
        lines.append(f"| {key} | {format_number(quality.get(key))} |")

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
            "The policy trigger behavior audit passed the structural quality check. Warnings should be interpreted as modeling findings, not execution failures."
        )
    else:
        lines.append(
            "The policy trigger behavior audit failed the structural quality check. Fix the listed problems before using the audit."
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_policy_trigger_behavior_audit.py "
            "<audit_json> <audit_md> <audit_csv> <quality_md> <quality_json>",
            file=sys.stderr,
        )
        return 2

    audit_json = Path(sys.argv[1])
    audit_md = Path(sys.argv[2])
    audit_csv = Path(sys.argv[3])
    quality_md = Path(sys.argv[4])
    quality_json = Path(sys.argv[5])

    try:
        quality = validate(audit_json, audit_md, audit_csv)

        write_markdown(quality_md, quality)
        write_json(quality_json, quality)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Policy trigger behavior audit quality report written to: {quality_md}")
    print(f"Policy trigger behavior audit quality JSON written to: {quality_json}")

    if not quality["all_required_checks_passed"]:
        print("ERROR: Policy trigger behavior audit quality check failed.", file=sys.stderr)
        return 1

    print("Policy trigger behavior audit quality check passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())