from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


EXPECTED_BATCH_COUNT = 12


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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")


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
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def text_contains(path: Path, expected: str) -> bool:
    if not path.exists():
        return False

    return expected in path.read_text(encoding="utf-8")


def verify_summary(summary_json: Path, summary_md: Path, summary_csv: Path) -> dict[str, Any]:
    data = load_json(summary_json)
    summary = data.get("summary", {})
    rows = data.get("rows", [])

    if not isinstance(summary, dict):
        summary = {}

    if not isinstance(rows, list):
        rows = []

    problems: list[str] = []
    warnings: list[str] = []

    batch_count = int(summary.get("batch_count", 0) or 0)
    recommendation_count = int(summary.get("recommendation_count", 0) or 0)
    total_completed = int(summary.get("total_completed_experiment_count", 0) or 0)
    weak_or_tied_count = int(summary.get("weak_or_tied_count", 0) or 0)
    tradeoff_count = int(summary.get("tradeoff_count", 0) or 0)
    scientific_status = str(summary.get("scientific_status", ""))
    fuzzy_logic_status = str(summary.get("fuzzy_logic_status", ""))

    if batch_count != EXPECTED_BATCH_COUNT:
        problems.append(
            f"Unexpected batch count. expected={EXPECTED_BATCH_COUNT}; actual={batch_count}"
        )

    if recommendation_count != len(rows):
        problems.append(
            f"Recommendation count does not match row count. recommendation_count={recommendation_count}; rows={len(rows)}"
        )

    if recommendation_count != EXPECTED_BATCH_COUNT:
        problems.append(
            f"Unexpected recommendation count. expected={EXPECTED_BATCH_COUNT}; actual={recommendation_count}"
        )

    if total_completed <= 0:
        problems.append("total_completed_experiment_count must be greater than zero.")

    if total_completed != 108:
        warnings.append(
            f"Expected 108 completed experiments for the current campaign design, got {total_completed}."
        )

    if fuzzy_logic_status != "not_used_in_main_pipeline":
        problems.append(f"Unexpected fuzzy logic status: {fuzzy_logic_status}")

    if scientific_status != "campaign_result_consolidation_only":
        problems.append(f"Unexpected scientific status: {scientific_status}")

    if not summary_md.exists():
        problems.append(f"Summary markdown does not exist: {summary_md}")
    elif not text_contains(summary_md, "# FieldOps Lab campaign result summary"):
        problems.append("Summary markdown does not contain the expected title.")

    csv_rows = csv_row_count(summary_csv)

    if not summary_csv.exists():
        problems.append(f"Summary CSV does not exist: {summary_csv}")
    elif csv_rows != recommendation_count:
        problems.append(
            f"Summary CSV row count mismatch. csv_rows={csv_rows}; recommendation_count={recommendation_count}"
        )

    if weak_or_tied_count > 0:
        warnings.append(
            f"Campaign has {weak_or_tied_count} weak or tied recommendation(s)."
        )

    if tradeoff_count > 0:
        warnings.append(
            f"Campaign has {tradeoff_count} trade-off recommendation(s)."
        )

    row_checks: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            problems.append("Summary row is not an object.")
            continue

        row_problems: list[str] = []
        batch_id = str(row.get("batch_id", ""))
        result_json_path = Path(str(row.get("result_json_path", "")))

        if not batch_id:
            row_problems.append("Missing batch_id.")

        if not result_json_path.exists():
            row_problems.append(f"Result JSON path does not exist: {result_json_path}")

        if str(row.get("recommendation_class", "")) == "missing_recommendation":
            row_problems.append(f"Missing recommendation for batch: {batch_id}")

        problems.extend(row_problems)

        row_checks.append(
            {
                "batch_id": batch_id,
                "recommendation_class": str(row.get("recommendation_class", "")),
                "result_json_path": str(result_json_path),
                "problem_count": len(row_problems),
                "problems": row_problems,
            }
        )

    return {
        "report_type": "fieldops_lab_campaign_result_summary_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "summary_json": str(summary_json),
        "summary_md": str(summary_md),
        "summary_csv": str(summary_csv),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "batch_count": batch_count,
        "recommendation_count": recommendation_count,
        "total_completed_experiment_count": total_completed,
        "weak_or_tied_count": weak_or_tied_count,
        "tradeoff_count": tradeoff_count,
        "csv_row_count": csv_rows,
        "scientific_status": scientific_status,
        "fuzzy_logic_status": fuzzy_logic_status,
        "problems": problems,
        "warnings": warnings,
        "row_checks": row_checks,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign result summary quality check")
    lines.append("")
    lines.append(f"Summary JSON: `{report['summary_json']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {format_number(report['all_required_checks_passed'])} |")
    lines.append(f"| problem_count | {format_number(report['problem_count'])} |")
    lines.append(f"| warning_count | {format_number(report['warning_count'])} |")
    lines.append(f"| batch_count | {format_number(report['batch_count'])} |")
    lines.append(f"| recommendation_count | {format_number(report['recommendation_count'])} |")
    lines.append(
        f"| total_completed_experiment_count | {format_number(report['total_completed_experiment_count'])} |"
    )
    lines.append(f"| weak_or_tied_count | {format_number(report['weak_or_tied_count'])} |")
    lines.append(f"| tradeoff_count | {format_number(report['tradeoff_count'])} |")
    lines.append(f"| csv_row_count | {format_number(report['csv_row_count'])} |")
    lines.append(f"| fuzzy_logic_status | {report['fuzzy_logic_status']} |")
    lines.append(f"| scientific_status | {report['scientific_status']} |")
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
            "The campaign result summary passed the structural quality check. "
            "It is safe to use as a campaign-level consolidation report."
        )
    else:
        lines.append(
            "The campaign result summary failed the structural quality check. "
            "Do not use it until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "This still does not prove scientific validity. It checks consistency of the consolidation layer."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_result_summary.py "
            "<summary_json> <summary_md> <summary_csv> <output_quality_md> <output_quality_json>",
            file=sys.stderr,
        )
        return 2

    summary_json = Path(sys.argv[1])
    summary_md = Path(sys.argv[2])
    summary_csv = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    try:
        report = verify_summary(summary_json, summary_md, summary_csv)
        write_markdown(output_md, report)
        write_json(output_json, report)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign result summary quality report written to: {output_md}")
    print(f"Campaign result summary quality JSON written to: {output_json}")

    if not bool(report["all_required_checks_passed"]):
        print("ERROR: Campaign result summary quality check failed.", file=sys.stderr)
        return 1

    print("Campaign result summary quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())