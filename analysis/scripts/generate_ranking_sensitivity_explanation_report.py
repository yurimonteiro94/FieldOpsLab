from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SENSITIVE_SCENARIO_REPORT_PATH = (
    PROJECT_ROOT / "analysis" / "reports" / "ranking_sensitive_scenario_report.json"
)

RANKING_SENSITIVITY_SOURCE_PATH = (
    PROJECT_ROOT / "analysis" / "reports" / "campaign_ranking_profile_sensitivity.json"
)


METRIC_FIELDS = [
    "mean_delta_objective_value",
    "mean_delta_makespan",
    "mean_delta_total_travel_time",
    "mean_delta_total_service_time",
    "mean_delta_total_waiting_time",
    "mean_total_lateness",
    "mean_late_task_count",
    "mean_effect_count",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


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


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}

    if isinstance(value, int | float):
        return value != 0

    return False


def as_list_of_text(value: Any) -> list[str]:
    if isinstance(value, list):
        return sorted({as_text(item) for item in value if as_text(item)})

    if isinstance(value, str):
        return sorted(
            {
                item.strip()
                for item in value.replace(",", ";").split(";")
                if item.strip()
            }
        )

    return []


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def resolve_output_path(raw_path: str) -> Path:
    path = Path(raw_path)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def collect_recommended_rows(
    ranking_rows: list[dict[str, Any]],
    batch_id: str,
) -> list[dict[str, Any]]:
    recommended_rows: list[dict[str, Any]] = []

    for row in ranking_rows:
        if as_text(row.get("batch_id")) != batch_id:
            continue

        if not as_bool(row.get("is_recommended")):
            continue

        recommended_rows.append(row)

    recommended_rows.sort(
        key=lambda row: (
            as_text(row.get("profile_id")),
            as_int(row.get("rank")),
            as_text(row.get("policy_id")),
            as_text(row.get("replanning_method_id")),
        )
    )

    return recommended_rows


def metric_snapshot(row: dict[str, Any]) -> dict[str, float]:
    return {field: as_float(row.get(field)) for field in METRIC_FIELDS}


def dominant_metric(metrics: dict[str, float]) -> str:
    if not metrics:
        return ""

    return max(metrics.items(), key=lambda item: abs(item[1]))[0]


def recommendation_key(row: dict[str, Any]) -> str:
    policy_id = as_text(row.get("policy_id"))
    method_id = as_text(row.get("replanning_method_id"))

    if method_id:
        return f"{policy_id}+{method_id}"

    return policy_id


def build_profile_explanations(
    recommended_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []

    for row in recommended_rows:
        metrics = metric_snapshot(row)

        explanations.append(
            {
                "profile_id": as_text(row.get("profile_id")),
                "policy_id": as_text(row.get("policy_id")),
                "replanning_method_id": as_text(row.get("replanning_method_id")),
                "recommendation_key": recommendation_key(row),
                "recommendation_class": as_text(row.get("recommendation_class")),
                "rank": as_int(row.get("rank")),
                "ranking_score": as_float(row.get("ranking_score")),
                "dominant_metric": dominant_metric(metrics),
                "metrics": metrics,
            }
        )

    return explanations


def summarize_metric_ranges(
    profile_explanations: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    ranges: dict[str, dict[str, float]] = {}

    for field in METRIC_FIELDS:
        values = [
            as_float(profile.get("metrics", {}).get(field))
            for profile in profile_explanations
            if isinstance(profile.get("metrics"), dict)
        ]

        if not values:
            continue

        ranges[field] = {
            "minimum": min(values),
            "maximum": max(values),
            "spread": max(values) - min(values),
        }

    return ranges


def classify_sensitivity_reason(
    recommended_policy_count: int,
    recommendation_class_count: int,
) -> str:
    if recommended_policy_count >= 2:
        return "recommended_policy_changes_across_profiles"

    if recommendation_class_count >= 2:
        return "same_policy_but_recommendation_class_changes_across_profiles"

    return "not_sensitive_under_current_profile_summary"


def investigation_status_for_reason(reason: str) -> str:
    if reason == "recommended_policy_changes_across_profiles":
        return "requires_metric_explanation"

    if reason == "same_policy_but_recommendation_class_changes_across_profiles":
        return "requires_recommendation_class_explanation"

    return "no_sensitivity_explanation_required"


def interpretation_for_reason(reason: str) -> str:
    if reason == "recommended_policy_changes_across_profiles":
        return (
            "The recommended policy changes under different ranking profiles. "
            "This is a strong ranking sensitivity signal and needs metric-level "
            "explanation before it can support a robust scientific recommendation."
        )

    if reason == "same_policy_but_recommendation_class_changes_across_profiles":
        return (
            "The recommended policy remains the same, but the recommendation class "
            "changes under different ranking profiles. This means the policy choice "
            "looks stable, but the strength or quality of the recommendation is fragile."
        )

    return (
        "No ranking sensitivity explanation was required for this scenario under "
        "the current profile summary."
    )


def build_input_status(
    sensitive_report: dict[str, Any],
    ranking_source: dict[str, Any],
) -> dict[str, Any]:
    sensitive_scenarios = sensitive_report.get("sensitive_scenarios", [])
    ranking_rows = ranking_source.get("rows", [])

    if not isinstance(sensitive_scenarios, list):
        sensitive_scenarios = []

    if not isinstance(ranking_rows, list):
        ranking_rows = []

    return {
        "all_required_inputs_available": (
            SENSITIVE_SCENARIO_REPORT_PATH.exists()
            and RANKING_SENSITIVITY_SOURCE_PATH.exists()
            and bool(sensitive_scenarios)
            and bool(ranking_rows)
        ),
        "sensitive_scenario_report_path": str(
            SENSITIVE_SCENARIO_REPORT_PATH.relative_to(PROJECT_ROOT)
        ),
        "ranking_sensitivity_source_path": str(
            RANKING_SENSITIVITY_SOURCE_PATH.relative_to(PROJECT_ROOT)
        ),
        "sensitive_scenario_report_exists": SENSITIVE_SCENARIO_REPORT_PATH.exists(),
        "ranking_sensitivity_source_exists": RANKING_SENSITIVITY_SOURCE_PATH.exists(),
        "sensitive_scenario_count": len(sensitive_scenarios),
        "source_ranking_row_count": len(ranking_rows),
        "source_recommended_row_count": sum(
            1 for row in ranking_rows if isinstance(row, dict) and as_bool(row.get("is_recommended"))
        ),
    }


def build_explanations(
    sensitive_report: dict[str, Any],
    ranking_source: dict[str, Any],
) -> list[dict[str, Any]]:
    raw_sensitive_scenarios = sensitive_report.get("sensitive_scenarios", [])
    raw_ranking_rows = ranking_source.get("rows", [])

    if not isinstance(raw_sensitive_scenarios, list):
        raw_sensitive_scenarios = []

    if not isinstance(raw_ranking_rows, list):
        raw_ranking_rows = []

    ranking_rows = [
        row for row in raw_ranking_rows if isinstance(row, dict)
    ]

    explanations: list[dict[str, Any]] = []

    for scenario in raw_sensitive_scenarios:
        if not isinstance(scenario, dict):
            continue

        batch_id = as_text(scenario.get("batch_id"))
        recommended_rows = collect_recommended_rows(ranking_rows, batch_id)
        profile_explanations = build_profile_explanations(recommended_rows)

        recommended_policies = sorted(
            {
                as_text(profile.get("policy_id"))
                for profile in profile_explanations
                if as_text(profile.get("policy_id"))
            }
        )
        recommendation_classes = sorted(
            {
                as_text(profile.get("recommendation_class"))
                for profile in profile_explanations
                if as_text(profile.get("recommendation_class"))
            }
        )

        recommended_policy_count = len(recommended_policies)
        recommendation_class_count = len(recommendation_classes)
        sensitivity_reason = classify_sensitivity_reason(
            recommended_policy_count=recommended_policy_count,
            recommendation_class_count=recommendation_class_count,
        )

        explanations.append(
            {
                "batch_id": batch_id,
                "scenario_id": as_text(scenario.get("scenario_id")),
                "scenario_family_id": as_text(scenario.get("scenario_family_id")),
                "severity_id": as_text(scenario.get("severity_id")),
                "ranking_profile_count": as_int(
                    scenario.get("ranking_profile_count"),
                    default=len(profile_explanations),
                ),
                "sensitive_to_ranking_profile": (
                    sensitivity_reason
                    != "not_sensitive_under_current_profile_summary"
                ),
                "sensitivity_reason": sensitivity_reason,
                "recommended_policy_count": recommended_policy_count,
                "recommendation_class_count": recommendation_class_count,
                "recommended_policies": recommended_policies,
                "recommendation_classes": recommendation_classes,
                "profile_explanations": profile_explanations,
                "metric_ranges": summarize_metric_ranges(profile_explanations),
                "investigation_status": investigation_status_for_reason(
                    sensitivity_reason
                ),
                "interpretation": interpretation_for_reason(sensitivity_reason),
            }
        )

    explanations.sort(
        key=lambda row: (
            row["scenario_family_id"],
            row["severity_id"],
            row["batch_id"],
        )
    )

    return explanations


def build_report(
    sensitive_report: dict[str, Any],
    ranking_source: dict[str, Any],
) -> dict[str, Any]:
    explanations = build_explanations(
        sensitive_report=sensitive_report,
        ranking_source=ranking_source,
    )
    input_status = build_input_status(
        sensitive_report=sensitive_report,
        ranking_source=ranking_source,
    )

    explanation_count = len(explanations)
    source_sensitive_scenario_count = input_status["sensitive_scenario_count"]

    policy_change_count = sum(
        1
        for item in explanations
        if item["sensitivity_reason"] == "recommended_policy_changes_across_profiles"
    )
    class_change_count = sum(
        1
        for item in explanations
        if item["sensitivity_reason"]
        == "same_policy_but_recommendation_class_changes_across_profiles"
    )

    return {
        "report_type": "ranking_sensitivity_explanation_report",
        "generated_at_local": datetime.now().isoformat(timespec="seconds"),
        "input_status": input_status,
        "summary": {
            "source_sensitive_scenario_count": source_sensitive_scenario_count,
            "explanation_count": explanation_count,
            "policy_change_explanation_count": policy_change_count,
            "class_change_explanation_count": class_change_count,
            "all_sensitive_scenarios_have_explanation": (
                explanation_count == source_sensitive_scenario_count
                and explanation_count > 0
            ),
            "source_ranking_row_count": input_status["source_ranking_row_count"],
            "source_recommended_row_count": input_status[
                "source_recommended_row_count"
            ],
        },
        "explanations": explanations,
        "conservative_interpretation": (
            "This report explains why the current diagnostic campaign marks some "
            "scenarios as ranking-sensitive. It still does not prove statistical "
            "significance or scientific generalization."
        ),
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_csv(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
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

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for explanation in report["explanations"]:
            for profile in explanation["profile_explanations"]:
                metrics = profile["metrics"]

                row = {
                    "batch_id": explanation["batch_id"],
                    "scenario_family_id": explanation["scenario_family_id"],
                    "severity_id": explanation["severity_id"],
                    "profile_id": profile["profile_id"],
                    "sensitivity_reason": explanation["sensitivity_reason"],
                    "policy_id": profile["policy_id"],
                    "replanning_method_id": profile["replanning_method_id"],
                    "recommendation_class": profile["recommendation_class"],
                    "rank": profile["rank"],
                    "ranking_score": profile["ranking_score"],
                    "dominant_metric": profile["dominant_metric"],
                    "investigation_status": explanation["investigation_status"],
                    "interpretation": explanation["interpretation"],
                }

                for field in METRIC_FIELDS:
                    row[field] = metrics.get(field, 0.0)

                writer.writerow(row)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in rows:
        lines.append("| " + " | ".join(as_text(value) for value in row) + " |")

    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    input_status = report["input_status"]
    summary = report["summary"]
    explanations = report["explanations"]

    lines: list[str] = []

    lines.append("# FieldOps Lab ranking sensitivity explanation report")
    lines.append("")
    lines.append(
        "This report explains the scenarios previously marked as sensitive to "
        "ranking profile choice."
    )
    lines.append("")
    lines.append(
        "It separates policy changes from weaker sensitivity cases where the policy "
        "stays the same but the recommendation class changes."
    )
    lines.append("")

    lines.append("## Input status")
    lines.append("")
    lines.append(
        markdown_table(
            ["Field", "Value"],
            [
                [
                    "all_required_inputs_available",
                    "yes" if input_status["all_required_inputs_available"] else "no",
                ],
                [
                    "sensitive_scenario_report_path",
                    input_status["sensitive_scenario_report_path"],
                ],
                [
                    "ranking_sensitivity_source_path",
                    input_status["ranking_sensitivity_source_path"],
                ],
                [
                    "sensitive_scenario_report_exists",
                    "yes"
                    if input_status["sensitive_scenario_report_exists"]
                    else "no",
                ],
                [
                    "ranking_sensitivity_source_exists",
                    "yes"
                    if input_status["ranking_sensitivity_source_exists"]
                    else "no",
                ],
                [
                    "sensitive_scenario_count",
                    input_status["sensitive_scenario_count"],
                ],
                [
                    "source_ranking_row_count",
                    input_status["source_ranking_row_count"],
                ],
                [
                    "source_recommended_row_count",
                    input_status["source_recommended_row_count"],
                ],
            ],
        )
    )
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append(
        markdown_table(
            ["Field", "Value"],
            [
                [
                    "source_sensitive_scenario_count",
                    summary["source_sensitive_scenario_count"],
                ],
                ["explanation_count", summary["explanation_count"]],
                [
                    "policy_change_explanation_count",
                    summary["policy_change_explanation_count"],
                ],
                [
                    "class_change_explanation_count",
                    summary["class_change_explanation_count"],
                ],
                [
                    "all_sensitive_scenarios_have_explanation",
                    "yes"
                    if summary["all_sensitive_scenarios_have_explanation"]
                    else "no",
                ],
                ["source_ranking_row_count", summary["source_ranking_row_count"]],
                [
                    "source_recommended_row_count",
                    summary["source_recommended_row_count"],
                ],
            ],
        )
    )
    lines.append("")

    lines.append("## Scenario explanations")
    lines.append("")

    for explanation in explanations:
        lines.append(f"### `{explanation['batch_id']}`")
        lines.append("")
        lines.append(f"- Scenario family: `{explanation['scenario_family_id']}`")
        lines.append(f"- Severity: `{explanation['severity_id']}`")
        lines.append(f"- Sensitivity reason: `{explanation['sensitivity_reason']}`")
        lines.append(
            f"- Recommended policies: `{'; '.join(explanation['recommended_policies'])}`"
        )
        lines.append(
            f"- Recommendation classes: `{'; '.join(explanation['recommendation_classes'])}`"
        )
        lines.append(f"- Investigation status: `{explanation['investigation_status']}`")
        lines.append(f"- Interpretation: {explanation['interpretation']}")
        lines.append("")

        lines.append(
            markdown_table(
                [
                    "Profile",
                    "Policy",
                    "Class",
                    "Rank",
                    "Score",
                    "Dominant metric",
                    "Objective delta",
                    "Makespan delta",
                    "Service delta",
                    "Waiting delta",
                ],
                [
                    [
                        profile["profile_id"],
                        profile["policy_id"],
                        profile["recommendation_class"],
                        profile["rank"],
                        profile["ranking_score"],
                        profile["dominant_metric"],
                        profile["metrics"]["mean_delta_objective_value"],
                        profile["metrics"]["mean_delta_makespan"],
                        profile["metrics"]["mean_delta_total_service_time"],
                        profile["metrics"]["mean_delta_total_waiting_time"],
                    ]
                    for profile in explanation["profile_explanations"]
                ],
            )
        )
        lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(report["conservative_interpretation"])
    lines.append("")
    lines.append(
        "The next scientific step is to use this explanation as input for broader "
        "replicated experiments and statistical comparisons."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[Path, Path, Path]:
    if len(argv) != 4:
        raise ValueError(
            "Usage: generate_ranking_sensitivity_explanation_report.py "
            "<output_md> <output_json> <output_csv>"
        )

    return (
        resolve_output_path(argv[1]),
        resolve_output_path(argv[2]),
        resolve_output_path(argv[3]),
    )


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    try:
        output_md, output_json, output_csv = parse_args(argv)

        sensitive_report = read_json(SENSITIVE_SCENARIO_REPORT_PATH)
        ranking_source = read_json(RANKING_SENSITIVITY_SOURCE_PATH)

        report = build_report(
            sensitive_report=sensitive_report,
            ranking_source=ranking_source,
        )

        write_markdown(output_md, report)
        write_json(output_json, report)
        write_csv(output_csv, report)

        print(
            "Ranking sensitivity explanation markdown written to: "
            f"{relative_or_absolute(output_md)}"
        )
        print(
            "Ranking sensitivity explanation JSON written to: "
            f"{relative_or_absolute(output_json)}"
        )
        print(
            "Ranking sensitivity explanation CSV written to: "
            f"{relative_or_absolute(output_csv)}"
        )
        print("Ranking sensitivity explanation report completed successfully.")

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())