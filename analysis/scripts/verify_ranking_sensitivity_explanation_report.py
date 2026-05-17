from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_MARKDOWN_SECTIONS = [
    "# FieldOps Lab ranking sensitivity explanation report",
    "## Input status",
    "## Overall result",
    "## Scenario explanations",
    "## Conservative interpretation",
]

REQUIRED_CSV_COLUMNS = [
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "profile_id",
    "sensitivity_reason",
    "policy_id",
    "replanning_method_id",
    "recommendation_class",
    "rank",
    "ranking_score",
    "dominant_metric",
    "mean_delta_objective_value",
    "mean_delta_makespan",
    "mean_delta_total_travel_time",
    "mean_delta_total_service_time",
    "mean_delta_total_waiting_time",
    "mean_total_lateness",
    "mean_late_task_count",
    "mean_effect_count",
    "investigation_status",
    "interpretation",
]

VALID_SENSITIVITY_REASONS = {
    "recommended_policy_changes_across_profiles",
    "same_policy_but_recommendation_class_changes_across_profiles",
}

VALID_INVESTIGATION_STATUSES = {
    "requires_metric_explanation",
    "requires_recommendation_class_explanation",
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
        return [dict(row) for row in reader]


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}

    if isinstance(value, int | float):
        return value != 0

    return False


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


def as_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(value)

    if isinstance(value, int | float):
        return float(value)

    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default

    return default


def as_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value)


def validate_input_status(
    report: dict[str, Any],
    problems: list[str],
) -> None:
    input_status = report.get("input_status")

    if not isinstance(input_status, dict):
        problems.append("input_status must be an object.")
        return

    if not as_bool(input_status.get("all_required_inputs_available")):
        problems.append("all_required_inputs_available must be true.")

    for field in [
        "sensitive_scenario_report_path",
        "ranking_sensitivity_source_path",
    ]:
        if not as_text(input_status.get(field)):
            problems.append(f"{field} must not be empty.")

    for field in [
        "sensitive_scenario_report_exists",
        "ranking_sensitivity_source_exists",
    ]:
        if not as_bool(input_status.get(field)):
            problems.append(f"{field} must be true.")

    for field in [
        "sensitive_scenario_count",
        "source_ranking_row_count",
        "source_recommended_row_count",
    ]:
        if as_int(input_status.get(field)) <= 0:
            problems.append(f"{field} must be positive.")


def validate_summary(
    report: dict[str, Any],
    problems: list[str],
) -> None:
    summary = report.get("summary")

    if not isinstance(summary, dict):
        problems.append("summary must be an object.")
        return

    source_sensitive_scenario_count = as_int(
        summary.get("source_sensitive_scenario_count")
    )
    explanation_count = as_int(summary.get("explanation_count"))
    policy_change_count = as_int(summary.get("policy_change_explanation_count"))
    class_change_count = as_int(summary.get("class_change_explanation_count"))

    if source_sensitive_scenario_count <= 0:
        problems.append("source_sensitive_scenario_count must be positive.")

    if explanation_count <= 0:
        problems.append("explanation_count must be positive.")

    if not as_bool(summary.get("all_sensitive_scenarios_have_explanation")):
        problems.append("all_sensitive_scenarios_have_explanation must be true.")

    if explanation_count != source_sensitive_scenario_count:
        problems.append(
            "explanation_count must equal source_sensitive_scenario_count."
        )

    if policy_change_count + class_change_count != explanation_count:
        problems.append(
            "policy_change_explanation_count plus class_change_explanation_count "
            "must equal explanation_count."
        )

    if as_int(summary.get("source_ranking_row_count")) <= 0:
        problems.append("source_ranking_row_count must be positive.")

    if as_int(summary.get("source_recommended_row_count")) <= 0:
        problems.append("source_recommended_row_count must be positive.")


def validate_profile_explanation(
    profile: Any,
    scenario_index: int,
    profile_index: int,
    problems: list[str],
) -> None:
    prefix = f"explanations[{scenario_index}].profile_explanations[{profile_index}]"

    if not isinstance(profile, dict):
        problems.append(f"{prefix} must be an object.")
        return

    for field in [
        "profile_id",
        "policy_id",
        "recommendation_key",
        "recommendation_class",
        "dominant_metric",
    ]:
        if not as_text(profile.get(field)):
            problems.append(f"{prefix}.{field} must not be empty.")

    if as_int(profile.get("rank")) <= 0:
        problems.append(f"{prefix}.rank must be positive.")

    as_float(profile.get("ranking_score"))

    metrics = profile.get("metrics")

    if not isinstance(metrics, dict):
        problems.append(f"{prefix}.metrics must be an object.")
        return

    required_metric_fields = [
        "mean_delta_objective_value",
        "mean_delta_makespan",
        "mean_delta_total_travel_time",
        "mean_delta_total_service_time",
        "mean_delta_total_waiting_time",
        "mean_total_lateness",
        "mean_late_task_count",
        "mean_effect_count",
    ]

    for field in required_metric_fields:
        if field not in metrics:
            problems.append(f"{prefix}.metrics.{field} is missing.")
        else:
            as_float(metrics.get(field))


def validate_explanations(
    report: dict[str, Any],
    problems: list[str],
) -> None:
    explanations = report.get("explanations")

    if not isinstance(explanations, list):
        problems.append("explanations must be a list.")
        return

    if not explanations:
        problems.append("explanations must not be empty.")
        return

    for index, explanation in enumerate(explanations):
        prefix = f"explanations[{index}]"

        if not isinstance(explanation, dict):
            problems.append(f"{prefix} must be an object.")
            continue

        for field in [
            "batch_id",
            "scenario_id",
            "scenario_family_id",
            "severity_id",
            "sensitivity_reason",
            "investigation_status",
            "interpretation",
        ]:
            if not as_text(explanation.get(field)):
                problems.append(f"{prefix}.{field} must not be empty.")

        if not as_bool(explanation.get("sensitive_to_ranking_profile")):
            problems.append(f"{prefix}.sensitive_to_ranking_profile must be true.")

        sensitivity_reason = as_text(explanation.get("sensitivity_reason"))
        investigation_status = as_text(explanation.get("investigation_status"))

        if sensitivity_reason not in VALID_SENSITIVITY_REASONS:
            problems.append(f"{prefix}.sensitivity_reason is invalid.")

        if investigation_status not in VALID_INVESTIGATION_STATUSES:
            problems.append(f"{prefix}.investigation_status is invalid.")

        recommended_policy_count = as_int(explanation.get("recommended_policy_count"))
        recommendation_class_count = as_int(
            explanation.get("recommendation_class_count")
        )

        if sensitivity_reason == "recommended_policy_changes_across_profiles":
            if recommended_policy_count < 2:
                problems.append(
                    f"{prefix}.recommended_policy_count must be at least 2 "
                    "for policy-change sensitivity."
                )

        if (
            sensitivity_reason
            == "same_policy_but_recommendation_class_changes_across_profiles"
        ):
            if recommendation_class_count < 2:
                problems.append(
                    f"{prefix}.recommendation_class_count must be at least 2 "
                    "for recommendation-class sensitivity."
                )

        if not isinstance(explanation.get("recommended_policies"), list) or not explanation.get(
            "recommended_policies"
        ):
            problems.append(f"{prefix}.recommended_policies must not be empty.")

        if not isinstance(explanation.get("recommendation_classes"), list) or not explanation.get(
            "recommendation_classes"
        ):
            problems.append(f"{prefix}.recommendation_classes must not be empty.")

        profile_explanations = explanation.get("profile_explanations")

        if not isinstance(profile_explanations, list):
            problems.append(f"{prefix}.profile_explanations must be a list.")
            continue

        if not profile_explanations:
            problems.append(f"{prefix}.profile_explanations must not be empty.")
            continue

        for profile_index, profile in enumerate(profile_explanations):
            validate_profile_explanation(
                profile=profile,
                scenario_index=index,
                profile_index=profile_index,
                problems=problems,
            )


def validate_markdown(path: Path, problems: list[str]) -> None:
    text = path.read_text(encoding="utf-8")

    for section in REQUIRED_MARKDOWN_SECTIONS:
        if section not in text:
            problems.append(f"Markdown is missing section: {section}")


def validate_csv(path: Path, problems: list[str]) -> None:
    rows = read_csv_rows(path)

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []

    missing = [
        column for column in REQUIRED_CSV_COLUMNS if column not in fieldnames
    ]

    if missing:
        problems.append(f"CSV is missing required columns: {missing}")

    if not rows:
        problems.append("CSV must contain at least one data row.")
        return

    for index, row in enumerate(rows):
        prefix = f"csv_rows[{index}]"

        for field in [
            "batch_id",
            "scenario_family_id",
            "severity_id",
            "profile_id",
            "sensitivity_reason",
            "policy_id",
            "recommendation_class",
            "dominant_metric",
            "investigation_status",
            "interpretation",
        ]:
            if not as_text(row.get(field)):
                problems.append(f"{prefix}.{field} must not be empty.")

        if as_text(row.get("sensitivity_reason")) not in VALID_SENSITIVITY_REASONS:
            problems.append(f"{prefix}.sensitivity_reason is invalid.")

        if as_text(row.get("investigation_status")) not in VALID_INVESTIGATION_STATUSES:
            problems.append(f"{prefix}.investigation_status is invalid.")


def write_quality_json(
    path: Path,
    problems: list[str],
    warnings: list[str],
    csv_row_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "report_type": "ranking_sensitivity_explanation_quality_check",
        "all_required_checks_passed": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "csv_row_count": csv_row_count,
        "problems": problems,
        "warnings": warnings,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_quality_markdown(
    path: Path,
    input_json: Path,
    problems: list[str],
    warnings: list[str],
    csv_row_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab ranking sensitivity explanation quality check")
    lines.append("")
    lines.append(f"Explanation report JSON: `{input_json}`")
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| all_required_checks_passed | {'yes' if not problems else 'no'} |"
    )
    lines.append(f"| problem_count | {len(problems)} |")
    lines.append(f"| warning_count | {len(warnings)} |")
    lines.append(f"| csv_row_count | {csv_row_count} |")
    lines.append("")

    lines.append("## Problems")
    lines.append("")
    if problems:
        for problem in problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    if problems:
        lines.append(
            "The ranking sensitivity explanation report failed structural verification."
        )
    else:
        lines.append(
            "The ranking sensitivity explanation report passed structural verification."
        )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[Path, Path, Path, Path, Path]:
    if len(argv) != 6:
        raise ValueError(
            "Usage: verify_ranking_sensitivity_explanation_report.py "
            "<input_json> <input_md> <input_csv> <output_quality_md> "
            "<output_quality_json>"
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
        input_json, input_md, input_csv, output_md, output_json = parse_args(argv)

        problems: list[str] = []
        warnings: list[str] = []

        report = read_json(input_json)

        if report.get("report_type") != "ranking_sensitivity_explanation_report":
            problems.append(
                "report_type must be ranking_sensitivity_explanation_report."
            )

        validate_input_status(report, problems)
        validate_summary(report, problems)
        validate_explanations(report, problems)
        validate_markdown(input_md, problems)
        validate_csv(input_csv, problems)

        csv_row_count = len(read_csv_rows(input_csv)) if input_csv.exists() else 0

        write_quality_markdown(
            path=output_md,
            input_json=input_json,
            problems=problems,
            warnings=warnings,
            csv_row_count=csv_row_count,
        )
        write_quality_json(
            path=output_json,
            problems=problems,
            warnings=warnings,
            csv_row_count=csv_row_count,
        )

        print(f"Ranking sensitivity explanation quality report written to: {output_md}")
        print(f"Ranking sensitivity explanation quality JSON written to: {output_json}")

        if problems:
            for problem in problems:
                print(f"ERROR: {problem}", file=sys.stderr)

            print(
                "ERROR: Ranking sensitivity explanation quality check failed.",
                file=sys.stderr,
            )
            return 1

        print("Ranking sensitivity explanation quality check passed.")
        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())