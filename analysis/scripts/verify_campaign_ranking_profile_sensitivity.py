from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_PROFILES = {
    "objective_only",
    "balanced_operational",
    "makespan_priority",
    "conservative_replanning",
}


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


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


def int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def read_csv_row_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return sum(1 for _ in csv.DictReader(file))
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc


def infer_expected_family_and_severity(batch_id: str) -> tuple[str, str]:
    family_tokens = [
        "combined_delay",
        "reassignment_opportunity",
        "service_delay_only",
        "travel_delay_only",
    ]

    severity_tokens = ["light", "moderate", "severe"]

    family = ""
    severity = ""

    for token in family_tokens:
        if token in batch_id:
            family = token
            break

    for token in severity_tokens:
        if token in batch_id:
            severity = token
            break

    return family, severity


def build_report(json_path: Path, markdown_path: Path, csv_path: Path) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    data = load_json(json_path)
    csv_row_count = read_csv_row_count(csv_path)

    if not markdown_path.exists():
        problems.append(f"Markdown report not found: {markdown_path}")
    elif markdown_path.stat().st_size <= 0:
        problems.append(f"Markdown report is empty: {markdown_path}")

    profile_count = int_value(data.get("ranking_profile_count", 0))
    ranking_row_count = int_value(data.get("ranking_row_count", 0))
    recommendation_count = int_value(data.get("recommendation_count", 0))
    scenario_summary_count = int_value(data.get("scenario_summary_count", 0))
    result_file_count = int_value(data.get("result_file_count", 0))

    profiles = data.get("ranking_profiles", {})
    profile_ids = set(profiles.keys()) if isinstance(profiles, dict) else set()

    missing_profiles = sorted(REQUIRED_PROFILES - profile_ids)

    if missing_profiles:
        problems.append(f"Missing required ranking profiles: {missing_profiles}")

    if profile_count != len(REQUIRED_PROFILES):
        problems.append(
            f"Unexpected ranking profile count. expected={len(REQUIRED_PROFILES)}; actual={profile_count}"
        )

    if result_file_count <= 0:
        problems.append("result_file_count must be positive.")

    if scenario_summary_count <= 0:
        problems.append("scenario_summary_count must be positive.")

    if recommendation_count != scenario_summary_count * profile_count:
        problems.append(
            "Unexpected recommendation count. "
            f"expected={scenario_summary_count * profile_count}; actual={recommendation_count}"
        )

    if ranking_row_count != csv_row_count:
        problems.append(
            f"CSV row count mismatch. json={ranking_row_count}; csv={csv_row_count}"
        )

    if ranking_row_count <= recommendation_count:
        problems.append(
            "ranking_row_count must be greater than recommendation_count because each scenario should have multiple options."
        )

    stability_counts = data.get("stability_counts", {})
    if not isinstance(stability_counts, dict):
        problems.append("stability_counts must be an object.")
        stability_counts = {}

    sensitive_count = int_value(stability_counts.get("sensitive_to_ranking_profile", 0))

    if sensitive_count > 0:
        warnings.append(
            f"Ranking sensitivity found in {sensitive_count} scenario(s)."
        )

    rows = data.get("rows", [])
    if not isinstance(rows, list):
        problems.append("rows must be a list.")
        rows = []

    missing_score_count = 0
    missing_recommended_count = 0

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            problems.append(f"Row {index} is not an object.")
            continue

        if "ranking_score" not in row:
            missing_score_count += 1

        if "is_recommended" not in row:
            missing_recommended_count += 1

    if missing_score_count > 0:
        problems.append(f"{missing_score_count} row(s) missing ranking_score.")

    if missing_recommended_count > 0:
        problems.append(f"{missing_recommended_count} row(s) missing is_recommended.")

    summary_rows = data.get("summary_rows", [])
    if not isinstance(summary_rows, list):
        problems.append("summary_rows must be a list.")
        summary_rows = []

    for index, row in enumerate(summary_rows, start=1):
        if not isinstance(row, dict):
            problems.append(f"Summary row {index} is not an object.")
            continue

        batch_id = str(row.get("batch_id", ""))
        actual_family = str(row.get("scenario_family_id", ""))
        actual_severity = str(row.get("severity_id", ""))

        expected_family, expected_severity = infer_expected_family_and_severity(batch_id)

        if expected_family and actual_family != expected_family:
            problems.append(
                "Summary row family mismatch. "
                f"row={index}; batch_id={batch_id}; expected={expected_family}; actual={actual_family}"
            )

        if expected_severity and actual_severity != expected_severity:
            problems.append(
                "Summary row severity mismatch. "
                f"row={index}; batch_id={batch_id}; expected={expected_severity}; actual={actual_severity}"
            )

    return {
        "report_type": "fieldops_lab_campaign_ranking_profile_sensitivity_quality_check",
        "generated_at_local": now_text(),
        "sensitivity_json_path": str(json_path),
        "sensitivity_markdown_path": str(markdown_path),
        "sensitivity_csv_path": str(csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "result_file_count": result_file_count,
        "ranking_profile_count": profile_count,
        "scenario_summary_count": scenario_summary_count,
        "recommendation_count": recommendation_count,
        "ranking_row_count": ranking_row_count,
        "csv_row_count": csv_row_count,
        "sensitive_to_ranking_profile_count": sensitive_count,
        "problems": problems,
        "warnings": warnings,
        "interpretation": {
            "status": "ranking_profile_sensitivity_quality_check",
            "warning": "This check validates structure and consistency, not final scientific validity.",
        },
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign ranking profile sensitivity quality check")
    lines.append("")
    lines.append(f"Sensitivity JSON: `{report['sensitivity_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {'yes' if report['all_required_checks_passed'] else 'no'} |")
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    lines.append(f"| result_file_count | {report['result_file_count']} |")
    lines.append(f"| ranking_profile_count | {report['ranking_profile_count']} |")
    lines.append(f"| scenario_summary_count | {report['scenario_summary_count']} |")
    lines.append(f"| recommendation_count | {report['recommendation_count']} |")
    lines.append(f"| ranking_row_count | {report['ranking_row_count']} |")
    lines.append(f"| csv_row_count | {report['csv_row_count']} |")
    lines.append(f"| sensitive_to_ranking_profile_count | {report['sensitive_to_ranking_profile_count']} |")
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
            "The ranking profile sensitivity report passed the structural quality check. It can be used as a diagnostic layer."
        )
    else:
        lines.append(
            "The ranking profile sensitivity report failed the structural quality check. Do not use it until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "This does not prove which ranking profile is scientifically correct. It only shows how sensitive current recommendations are to alternative ranking assumptions."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_ranking_profile_sensitivity.py "
            "<sensitivity_json> <sensitivity_md> <sensitivity_csv> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    sensitivity_json = Path(sys.argv[1])
    sensitivity_md = Path(sys.argv[2])
    sensitivity_csv = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    try:
        report = build_report(sensitivity_json, sensitivity_md, sensitivity_csv)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_markdown(output_md, report)
    write_json(output_json, report)

    print(f"Campaign ranking profile sensitivity quality report written to: {output_md}")
    print(f"Campaign ranking profile sensitivity quality JSON written to: {output_json}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Campaign ranking profile sensitivity quality check failed.", file=sys.stderr)
        return 1

    print("Campaign ranking profile sensitivity quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())