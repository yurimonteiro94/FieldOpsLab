from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_MARKDOWN_SECTIONS = [
    "# FieldOps Lab ranking-sensitive scenario report",
    "## Input status",
    "## Overall result",
    "## Sensitive scenarios",
    "## Required investigation",
    "## Conservative interpretation",
]

REQUIRED_CSV_COLUMNS = [
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "ranking_profile_count",
    "sensitive_to_ranking_profile",
    "sensitivity_reason",
    "unique_recommended_policy_count",
    "unique_recommendation_class_count",
    "recommended_policies",
    "recommendation_classes",
    "stability_class",
    "investigation_status",
    "interpretation",
    "recommended_profile_policy_pairs",
    "scenario_id",
]

VALID_SENSITIVITY_REASONS = {
    "recommended_policy_changes_across_profiles",
    "same_policy_but_recommendation_class_changes_across_profiles",
    "ranking_summary_marked_as_not_stable",
}

VALID_INVESTIGATION_STATUS = {
    "requires_policy_change_explanation",
    "requires_recommendation_class_explanation",
    "requires_stability_class_explanation",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default

    return default


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}

    return bool(value)


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def split_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def validate_input_status(report: dict[str, Any], problems: list[str]) -> None:
    input_status = report.get("input_status")

    if not isinstance(input_status, dict):
        problems.append("input_status must be an object.")
        return

    if not input_status.get("all_required_inputs_available"):
        problems.append("all_required_inputs_available must be true.")

    if not input_status.get("source_exists"):
        problems.append("source_exists must be true.")

    if not input_status.get("source_has_summary_rows"):
        problems.append("source_has_summary_rows must be true.")

    if not input_status.get("source_has_ranking_rows"):
        problems.append("source_has_ranking_rows must be true.")

    if as_int(input_status.get("source_scenario_summary_count")) <= 0:
        problems.append("source_scenario_summary_count must be positive.")

    if as_int(input_status.get("source_ranking_row_count")) <= 0:
        problems.append("source_ranking_row_count must be positive.")

    if as_int(input_status.get("source_ranking_profile_count")) <= 0:
        problems.append("source_ranking_profile_count must be positive.")


def validate_summary(report: dict[str, Any], problems: list[str]) -> None:
    summary = report.get("summary")

    if not isinstance(summary, dict):
        problems.append("summary must be an object.")
        return

    scenario_summary_count = as_int(summary.get("scenario_summary_count"))
    ranking_row_count = as_int(summary.get("ranking_row_count"))
    ranking_profile_count = as_int(summary.get("ranking_profile_count"))
    sensitive_scenario_count = as_int(summary.get("sensitive_scenario_count"))
    stable_scenario_count = as_int(summary.get("stable_scenario_count"))
    policy_change_count = as_int(summary.get("policy_change_sensitive_scenario_count"))
    class_change_count = as_int(summary.get("class_change_sensitive_scenario_count"))

    if scenario_summary_count <= 0:
        problems.append("scenario_summary_count must be positive.")

    if ranking_row_count <= 0:
        problems.append("ranking_row_count must be positive.")

    if ranking_profile_count <= 0:
        problems.append("ranking_profile_count must be positive.")

    if sensitive_scenario_count < 0:
        problems.append("sensitive_scenario_count must not be negative.")

    if stable_scenario_count < 0:
        problems.append("stable_scenario_count must not be negative.")

    if sensitive_scenario_count + stable_scenario_count != scenario_summary_count:
        problems.append(
            "sensitive_scenario_count plus stable_scenario_count must equal scenario_summary_count."
        )

    if policy_change_count < 0:
        problems.append("policy_change_sensitive_scenario_count must not be negative.")

    if class_change_count < 0:
        problems.append("class_change_sensitive_scenario_count must not be negative.")

    if policy_change_count + class_change_count > sensitive_scenario_count:
        problems.append(
            "policy and class sensitivity counts must not exceed sensitive_scenario_count."
        )

    fragility_status = summary.get("ranking_fragility_status")

    if sensitive_scenario_count > 0:
        if fragility_status != "some_scenarios_sensitive_to_ranking_profile":
            problems.append(
                "ranking_fragility_status must indicate sensitivity when sensitive scenarios exist."
            )
    else:
        if fragility_status != "no_ranking_sensitivity_detected_under_current_profiles":
            problems.append(
                "ranking_fragility_status must indicate no sensitivity when no sensitive scenario exists."
            )


def validate_sensitive_scenarios(report: dict[str, Any], problems: list[str]) -> None:
    summary = report.get("summary", {})
    sensitive_scenarios = report.get("sensitive_scenarios")

    if not isinstance(sensitive_scenarios, list):
        problems.append("sensitive_scenarios must be a list.")
        return

    sensitive_scenario_count = as_int(summary.get("sensitive_scenario_count"))

    if len(sensitive_scenarios) != sensitive_scenario_count:
        problems.append(
            "sensitive_scenarios length must match sensitive_scenario_count."
        )

    policy_change_count = 0
    class_change_count = 0

    for index, row in enumerate(sensitive_scenarios):
        if not isinstance(row, dict):
            problems.append(f"sensitive_scenarios[{index}] must be an object.")
            continue

        prefix = f"sensitive_scenarios[{index}]"

        if not row.get("batch_id"):
            problems.append(f"{prefix}.batch_id must not be empty.")

        if not row.get("scenario_id"):
            problems.append(f"{prefix}.scenario_id must not be empty.")

        if not row.get("scenario_family_id"):
            problems.append(f"{prefix}.scenario_family_id must not be empty.")

        if not row.get("severity_id"):
            problems.append(f"{prefix}.severity_id must not be empty.")

        if as_int(row.get("ranking_profile_count")) <= 0:
            problems.append(f"{prefix}.ranking_profile_count must be positive.")

        if not as_bool(row.get("sensitive_to_ranking_profile")):
            problems.append(f"{prefix}.sensitive_to_ranking_profile must be true.")

        reason = row.get("sensitivity_reason")

        if reason not in VALID_SENSITIVITY_REASONS:
            problems.append(f"{prefix}.sensitivity_reason is invalid.")

        investigation_status = row.get("investigation_status")

        if investigation_status not in VALID_INVESTIGATION_STATUS:
            problems.append(f"{prefix}.investigation_status is invalid.")

        unique_policy_count = as_int(row.get("unique_recommended_policy_count"))
        unique_class_count = as_int(row.get("unique_recommendation_class_count"))

        recommended_policies = as_list(row.get("recommended_policies"))
        recommendation_classes = as_list(row.get("recommendation_classes"))

        if not recommended_policies:
            problems.append(f"{prefix}.recommended_policies must not be empty.")

        if not recommendation_classes:
            problems.append(f"{prefix}.recommendation_classes must not be empty.")

        if reason == "recommended_policy_changes_across_profiles":
            policy_change_count += 1

            if unique_policy_count < 2:
                problems.append(
                    f"{prefix}.unique_recommended_policy_count must be at least 2 for policy-sensitive scenarios."
                )

            if len(recommended_policies) < 2:
                problems.append(
                    f"{prefix}.recommended_policies must contain at least 2 policies for policy-sensitive scenarios."
                )

            if investigation_status != "requires_policy_change_explanation":
                problems.append(
                    f"{prefix}.investigation_status must be requires_policy_change_explanation."
                )

        if reason == "same_policy_but_recommendation_class_changes_across_profiles":
            class_change_count += 1

            if unique_class_count < 2:
                problems.append(
                    f"{prefix}.unique_recommendation_class_count must be at least 2 for class-sensitive scenarios."
                )

            if len(recommendation_classes) < 2:
                problems.append(
                    f"{prefix}.recommendation_classes must contain at least 2 classes for class-sensitive scenarios."
                )

            if investigation_status != "requires_recommendation_class_explanation":
                problems.append(
                    f"{prefix}.investigation_status must be requires_recommendation_class_explanation."
                )

        if reason == "ranking_summary_marked_as_not_stable":
            if investigation_status != "requires_stability_class_explanation":
                problems.append(
                    f"{prefix}.investigation_status must be requires_stability_class_explanation."
                )

        if not row.get("interpretation"):
            problems.append(f"{prefix}.interpretation must not be empty.")

    summary_policy_change_count = as_int(
        summary.get("policy_change_sensitive_scenario_count")
    )
    summary_class_change_count = as_int(
        summary.get("class_change_sensitive_scenario_count")
    )

    if policy_change_count != summary_policy_change_count:
        problems.append(
            "policy_change_sensitive_scenario_count must match sensitive scenario rows."
        )

    if class_change_count != summary_class_change_count:
        problems.append(
            "class_change_sensitive_scenario_count must match sensitive scenario rows."
        )


def validate_markdown(path: Path, problems: list[str]) -> None:
    text = path.read_text(encoding="utf-8")

    for section in REQUIRED_MARKDOWN_SECTIONS:
        if section not in text:
            problems.append(f"Markdown is missing section: {section}")


def validate_csv(
    path: Path,
    report: dict[str, Any],
    problems: list[str],
) -> list[dict[str, str]]:
    rows = read_csv_rows(path)

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []

    missing_columns = [
        column for column in REQUIRED_CSV_COLUMNS if column not in fieldnames
    ]

    if missing_columns:
        problems.append(f"CSV is missing required columns: {missing_columns}")

    sensitive_scenarios = report.get("sensitive_scenarios", [])

    if isinstance(sensitive_scenarios, list) and len(rows) != len(sensitive_scenarios):
        problems.append("CSV row count must match sensitive_scenarios length.")

    for index, row in enumerate(rows):
        prefix = f"csv_rows[{index}]"

        if not row.get("batch_id"):
            problems.append(f"{prefix}.batch_id must not be empty.")

        if row.get("sensitive_to_ranking_profile", "").strip().lower() not in {
            "true",
            "yes",
            "1",
        }:
            problems.append(f"{prefix}.sensitive_to_ranking_profile must be true.")

        reason = row.get("sensitivity_reason", "")

        if reason not in VALID_SENSITIVITY_REASONS:
            problems.append(f"{prefix}.sensitivity_reason is invalid.")

        if not split_csv_list(row.get("recommended_policies", "")):
            problems.append(f"{prefix}.recommended_policies must not be empty.")

        if not split_csv_list(row.get("recommendation_classes", "")):
            problems.append(f"{prefix}.recommendation_classes must not be empty.")

    return rows


def build_quality_report(
    report_json_path: Path,
    csv_rows: list[dict[str, str]],
    problems: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "report_type": "ranking_sensitive_scenario_quality_check",
        "ranking_sensitive_scenario_report_json": str(report_json_path),
        "all_required_checks_passed": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "csv_row_count": len(csv_rows),
        "problems": problems,
        "warnings": warnings,
        "interpretation": (
            "The ranking-sensitive scenario report passed structural verification."
            if not problems
            else "The ranking-sensitive scenario report failed structural verification."
        ),
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")

    return "\n".join(lines)


def write_quality_markdown(path: Path, quality_report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab ranking-sensitive scenario quality check")
    lines.append("")
    lines.append(
        f"Scenario report JSON: `{quality_report['ranking_sensitive_scenario_report_json']}`"
    )
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append(
        markdown_table(
            ["Field", "Value"],
            [
                [
                    "all_required_checks_passed",
                    "yes" if quality_report["all_required_checks_passed"] else "no",
                ],
                ["problem_count", quality_report["problem_count"]],
                ["warning_count", quality_report["warning_count"]],
                ["csv_row_count", quality_report["csv_row_count"]],
            ],
        )
    )
    lines.append("")

    lines.append("## Problems")
    lines.append("")

    if quality_report["problems"]:
        for problem in quality_report["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Warnings")
    lines.append("")

    if quality_report["warnings"]:
        for warning in quality_report["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(quality_report["interpretation"])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_quality_json(path: Path, quality_report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(quality_report, file, indent=2, ensure_ascii=False)
        file.write("\n")


def parse_args(argv: list[str]) -> tuple[Path, Path, Path, Path, Path]:
    if len(argv) != 6:
        raise ValueError(
            "Usage: verify_ranking_sensitive_scenario_report.py "
            "<input_json> <input_md> <input_csv> <quality_md> <quality_json>"
        )

    return (
        Path(argv[1]),
        Path(argv[2]),
        Path(argv[3]),
        Path(argv[4]),
        Path(argv[5]),
    )


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    try:
        input_json, input_md, input_csv, quality_md, quality_json = parse_args(argv)

        problems: list[str] = []
        warnings: list[str] = []

        report = read_json(input_json)

        if report.get("report_type") != "ranking_sensitive_scenario_report":
            problems.append("report_type must be ranking_sensitive_scenario_report.")

        validate_input_status(report, problems)
        validate_summary(report, problems)
        validate_sensitive_scenarios(report, problems)
        validate_markdown(input_md, problems)
        csv_rows = validate_csv(input_csv, report, problems)

        quality_report = build_quality_report(
            input_json,
            csv_rows,
            problems,
            warnings,
        )

        write_quality_markdown(quality_md, quality_report)
        write_quality_json(quality_json, quality_report)

        print(f"Ranking-sensitive scenario quality report written to: {quality_md}")
        print(f"Ranking-sensitive scenario quality JSON written to: {quality_json}")

        if problems:
            for problem in problems:
                print(f"ERROR: {problem}", file=sys.stderr)

            print("ERROR: Ranking-sensitive scenario quality check failed.", file=sys.stderr)
            return 1

        print("Ranking-sensitive scenario quality check passed.")
        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())