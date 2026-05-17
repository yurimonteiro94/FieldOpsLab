from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_ROW_FIELDS = [
    "batch_id",
    "ranking_stability_class",
    "ranking_unique_policy_count",
    "ranking_profile_recommendations",
]

REQUIRED_SUMMARY_FIELDS = [
    "ranking_profile_count",
    "scenario_summary_count",
    "recommendation_count",
    "ranking_row_count",
    "sensitive_to_ranking_profile_count",
]


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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    try:
        text = str(value).strip()
        if not text:
            return default

        return int(float(text))
    except (TypeError, ValueError):
        return default


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def pick_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ["rows", "decision_rows", "final_rows", "diagnostic_rows"]:
        rows = data.get(key)

        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]

    return []


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def build_report(
    final_json_path: Path,
    final_md_path: Path,
    final_csv_path: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    final_data = load_json(final_json_path)
    json_rows = pick_rows(final_data)
    csv_rows = load_csv_rows(final_csv_path)

    try:
        markdown_text = final_md_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Markdown file not found: {final_md_path}") from exc

    sensitivity = final_data.get("ranking_profile_sensitivity")

    if not isinstance(sensitivity, dict):
        problems.append("Missing top-level ranking_profile_sensitivity object.")
        sensitivity = {}

    for field in REQUIRED_SUMMARY_FIELDS:
        if field not in sensitivity:
            problems.append(f"Missing ranking sensitivity summary field: {field}")

    ranking_profile_count = int_value(sensitivity.get("ranking_profile_count", 0))
    scenario_summary_count = int_value(sensitivity.get("scenario_summary_count", 0))
    recommendation_count = int_value(sensitivity.get("recommendation_count", 0))
    ranking_row_count = int_value(sensitivity.get("ranking_row_count", 0))
    sensitive_count = int_value(sensitivity.get("sensitive_to_ranking_profile_count", 0))

    if ranking_profile_count <= 0:
        problems.append("ranking_profile_count must be positive.")

    if scenario_summary_count != len(json_rows):
        problems.append(
            "scenario_summary_count must match final diagnostic row count. "
            f"scenario_summary_count={scenario_summary_count}; row_count={len(json_rows)}"
        )

    if recommendation_count < scenario_summary_count:
        warnings.append(
            "recommendation_count is smaller than scenario_summary_count. "
            f"recommendation_count={recommendation_count}; scenario_summary_count={scenario_summary_count}"
        )

    if ranking_row_count < recommendation_count:
        warnings.append(
            "ranking_row_count is smaller than recommendation_count. "
            f"ranking_row_count={ranking_row_count}; recommendation_count={recommendation_count}"
        )

    if "Ranking profile sensitivity integration" not in markdown_text:
        problems.append("Markdown report is missing the ranking profile sensitivity integration section.")

    if "Ranking stability counts" not in markdown_text:
        problems.append("Markdown report is missing the ranking stability counts section.")

    if "Ranking sensitivity by final diagnostic row" not in markdown_text:
        problems.append("Markdown report is missing the row-level ranking sensitivity section.")

    if len(csv_rows) != len(json_rows):
        problems.append(
            f"CSV row count differs from JSON row count. csv_row_count={len(csv_rows)}; json_row_count={len(json_rows)}"
        )

    missing_json_field_count = 0
    empty_stability_count = 0
    empty_unique_policy_count = 0

    for index, row in enumerate(json_rows, start=1):
        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                missing_json_field_count += 1
                problems.append(f"JSON row {index} missing required field: {field}")

        if not normalize_text(row.get("ranking_stability_class", "")):
            empty_stability_count += 1
            problems.append(f"JSON row {index} has empty ranking_stability_class.")

        if int_value(row.get("ranking_unique_policy_count", 0)) <= 0:
            empty_unique_policy_count += 1
            problems.append(f"JSON row {index} has invalid ranking_unique_policy_count.")

    missing_csv_field_count = 0

    if csv_rows:
        csv_fields = set(csv_rows[0].keys())

        for field in REQUIRED_ROW_FIELDS:
            if field not in csv_fields:
                missing_csv_field_count += 1
                problems.append(f"CSV is missing required field: {field}")
    else:
        problems.append("CSV has no rows.")

    stability_counts: dict[str, int] = {}

    for row in json_rows:
        stability = normalize_text(row.get("ranking_stability_class", "")) or "missing"
        stability_counts[stability] = stability_counts.get(stability, 0) + 1

    if sensitive_count < 0:
        problems.append("sensitive_to_ranking_profile_count cannot be negative.")

    if sensitive_count > len(json_rows):
        problems.append(
            "sensitive_to_ranking_profile_count cannot exceed row count. "
            f"sensitive_count={sensitive_count}; row_count={len(json_rows)}"
        )

    return {
        "report_type": "fieldops_lab_final_diagnostic_ranking_integration_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "final_json_path": str(final_json_path),
        "final_markdown_path": str(final_md_path),
        "final_csv_path": str(final_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "json_row_count": len(json_rows),
        "csv_row_count": len(csv_rows),
        "ranking_profile_count": ranking_profile_count,
        "scenario_summary_count": scenario_summary_count,
        "recommendation_count": recommendation_count,
        "ranking_row_count": ranking_row_count,
        "sensitive_to_ranking_profile_count": sensitive_count,
        "stability_counts": stability_counts,
        "missing_json_field_count": missing_json_field_count,
        "missing_csv_field_count": missing_csv_field_count,
        "empty_stability_count": empty_stability_count,
        "empty_unique_policy_count": empty_unique_policy_count,
        "problems": problems,
        "warnings": warnings,
        "interpretation": {
            "status": "final_diagnostic_ranking_integration_quality_check",
            "warning": "This verifies integration consistency. It does not prove the scientific correctness of any ranking profile.",
        },
    }


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []

    lines.append("# FieldOps Lab final diagnostic ranking integration quality check")
    lines.append("")
    lines.append(f"Final JSON: `{report['final_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {yes_no(bool(report['all_required_checks_passed']))} |")
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    lines.append(f"| json_row_count | {report['json_row_count']} |")
    lines.append(f"| csv_row_count | {report['csv_row_count']} |")
    lines.append(f"| ranking_profile_count | {report['ranking_profile_count']} |")
    lines.append(f"| scenario_summary_count | {report['scenario_summary_count']} |")
    lines.append(f"| recommendation_count | {report['recommendation_count']} |")
    lines.append(f"| ranking_row_count | {report['ranking_row_count']} |")
    lines.append(f"| sensitive_to_ranking_profile_count | {report['sensitive_to_ranking_profile_count']} |")
    lines.append("")

    lines.append("## Stability counts")
    lines.append("")
    lines.append("| Stability class | Count |")
    lines.append("| --- | ---: |")

    stability_counts = report.get("stability_counts", {})
    if isinstance(stability_counts, dict) and stability_counts:
        for stability, count in sorted(stability_counts.items()):
            lines.append(f"| {stability} | {count} |")
    else:
        lines.append("| None | 0 |")

    lines.append("")

    lines.append("## Problems")
    lines.append("")

    problems = report.get("problems", [])
    if problems:
        for problem in problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Warnings")
    lines.append("")

    warnings = report.get("warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if report["all_required_checks_passed"]:
        lines.append(
            "The final diagnostic report contains and exposes ranking sensitivity information consistently in JSON, Markdown, and CSV."
        )
    else:
        lines.append(
            "The final diagnostic report ranking integration failed. Do not rely on ranking-sensitivity conclusions until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "This still does not prove the scientific correctness of any ranking profile. It only verifies that the integration layer is present and internally consistent."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_final_diagnostic_ranking_integration.py "
            "<final_json> <final_md> <final_csv> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    final_json_path = Path(sys.argv[1])
    final_md_path = Path(sys.argv[2])
    final_csv_path = Path(sys.argv[3])
    output_md_path = Path(sys.argv[4])
    output_json_path = Path(sys.argv[5])

    try:
        report = build_report(final_json_path, final_md_path, final_csv_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_markdown(output_md_path, report)
    write_json(output_json_path, report)

    print(f"Final diagnostic ranking integration quality report written to: {output_md_path}")
    print(f"Final diagnostic ranking integration quality JSON written to: {output_json_path}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Final diagnostic ranking integration quality check failed.", file=sys.stderr)
        return 1

    print("Final diagnostic ranking integration quality check passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())