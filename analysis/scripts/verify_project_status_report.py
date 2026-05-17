from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data


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


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def build_quality_report(
    status_json_path: Path,
    status_md_path: Path,
    status_csv_path: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    for path in [status_json_path, status_md_path, status_csv_path]:
        if not path.exists():
            problems.append(f"Required project status file missing: {path}")
        elif path.stat().st_size == 0:
            problems.append(f"Required project status file is empty: {path}")

    status = load_json(status_json_path) if status_json_path.exists() else {}
    metrics = status.get("summary_metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
        problems.append("summary_metrics must be an object.")

    quality_summaries = status.get("quality_summaries", [])
    if not isinstance(quality_summaries, list):
        quality_summaries = []
        problems.append("quality_summaries must be a list.")

    required_positive_metrics = [
        "analysis_script_count",
        "python_test_count",
        "cpp_test_source_count",
        "pipeline_step_count",
        "final_diagnostic_row_count",
        "ranking_row_count",
        "scenario_summary_count",
    ]

    for key in required_positive_metrics:
        if int_value(metrics.get(key, 0)) <= 0:
            problems.append(f"{key} must be positive.")

    if int_value(metrics.get("pipeline_failed_step_count", 0)) != 0:
        problems.append("pipeline_failed_step_count must be 0.")

    if int_value(metrics.get("script_without_direct_python_test_count", 0)) != 0:
        problems.append("script_without_direct_python_test_count must be 0.")

    if int_value(metrics.get("script_needing_test_review_count", 0)) != 0:
        problems.append("script_needing_test_review_count must be 0.")

    if not bool_value(metrics.get("structural_all_required_checks_passed", False)):
        problems.append("structural_all_required_checks_passed must be true.")

    if not quality_summaries:
        problems.append("quality_summaries must not be empty.")

    for item in quality_summaries:
        if not isinstance(item, dict):
            problems.append("Each quality summary must be an object.")
            continue

        quality_file = item.get("quality_file", "<unknown>")

        if not bool_value(item.get("exists", False)):
            problems.append(f"Quality file does not exist: {quality_file}")

        if not bool_value(item.get("passed", False)):
            problems.append(f"Quality file did not pass: {quality_file}")

        if int_value(item.get("problem_count", 0)) != 0:
            problems.append(f"Quality file has problems: {quality_file}")

    methodological_warning_count = int_value(
        metrics.get("methodological_warning_count", 0)
    )
    if methodological_warning_count > 0:
        warnings.append("Project still has methodological warning(s).")

    csv_row_count = count_csv_rows(status_csv_path)
    if csv_row_count <= 0:
        problems.append("Project status CSV must contain at least one data row.")

    expected_csv_row_count = 16
    if csv_row_count != expected_csv_row_count:
        problems.append(
            f"Project status CSV row count must be {expected_csv_row_count}, found {csv_row_count}."
        )

    return {
        "report_type": "fieldops_lab_project_status_quality_check",
        "status_json": str(status_json_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "csv_row_count": csv_row_count,
        "problems": problems,
        "warnings": warnings,
        "summary_metrics": metrics,
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []

    lines.append("# FieldOps Lab project status quality check")
    lines.append("")
    lines.append(f"Status JSON: `{report['status_json']}`")
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| all_required_checks_passed | {'yes' if report['all_required_checks_passed'] else 'no'} |"
    )
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    lines.append(f"| csv_row_count | {report['csv_row_count']} |")
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
        lines.append("The project status report passed structural verification.")
    else:
        lines.append("The project status report failed structural verification.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: verify_project_status_report.py <status_json> <status_md> <status_csv> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    status_json_path = Path(sys.argv[1])
    status_md_path = Path(sys.argv[2])
    status_csv_path = Path(sys.argv[3])
    output_md_path = Path(sys.argv[4])
    output_json_path = Path(sys.argv[5])

    report = build_quality_report(
        status_json_path=status_json_path,
        status_md_path=status_md_path,
        status_csv_path=status_csv_path,
    )

    write_markdown(output_md_path, report)
    write_json(output_json_path, report)

    print(f"Project status quality report written to: {output_md_path}")
    print(f"Project status quality JSON written to: {output_json_path}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Project status quality check failed.", file=sys.stderr)
        for problem in report["problems"]:
            print(f"ERROR: {problem}", file=sys.stderr)
        for warning in report["warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)
        return 1

    print("Project status quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())