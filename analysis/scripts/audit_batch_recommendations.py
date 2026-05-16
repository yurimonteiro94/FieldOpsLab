from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input JSON root must be an object.")

    return data


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(content)


def get_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)

    if isinstance(value, dict):
        return value

    return {}


def get_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)

    if isinstance(value, list):
        return value

    return []


def as_text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value

    return default


def as_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default

    if isinstance(value, int) or isinstance(value, float):
        return float(value)

    return default


def as_bool(value: Any) -> bool:
    return value is True


def format_number(value: Any) -> str:
    number = as_number(value)

    if number == int(number):
        return str(int(number))

    return f"{number:.2f}"


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines: list[str] = []

    lines.append("| " + " | ".join(escape_cell(header) for header in headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for row in rows:
        lines.append("| " + " | ".join(escape_cell(value) for value in row) + " |")

    return lines


def get_weight_summary(ranking_config: dict[str, Any]) -> tuple[int, list[str]]:
    weight_keys = [
        "objective_value_weight",
        "makespan_weight",
        "late_task_count_weight",
        "total_lateness_weight",
        "total_service_time_weight",
        "total_travel_time_weight",
        "total_waiting_time_weight",
        "effect_count_weight",
        "policy_should_replan_count_weight",
        "replanning_request_count_weight",
        "replanning_success_count_weight",
        "replanning_applied_count_weight",
    ]

    active_weights: list[str] = []

    for key in weight_keys:
        value = as_number(ranking_config.get(key))

        if value != 0.0:
            active_weights.append(f"{key}={format_number(value)}")

    return len(active_weights), active_weights


def classify_recommendation(row: dict[str, Any]) -> tuple[str, str]:
    scenario_id = as_text(row.get("scenario_id"), "unknown_scenario")
    has_clear_winner = as_bool(row.get("has_clear_winner"))
    margin = as_number(row.get("score_margin_to_second"))
    delta_objective = as_number(row.get("mean_delta_objective_value"))
    delta_makespan = as_number(row.get("mean_delta_makespan"))
    delta_travel = as_number(row.get("mean_delta_total_travel_time"))
    replanning_applied = as_number(row.get("replanning_applied_count"))
    replanning_success = as_number(row.get("replanning_success_count"))

    if not has_clear_winner or margin == 0.0:
        return (
            "weak",
            f"{scenario_id} has no clear winner. The best and second-best scores are tied or too close.",
        )

    if replanning_applied > 0.0 and replanning_success <= 0.0:
        return (
            "invalid",
            f"{scenario_id} says replanning was applied, but no successful replanning was counted.",
        )

    if delta_objective < 0.0 and delta_makespan > 0.0 and delta_travel < 0.0:
        return (
            "tradeoff",
            f"{scenario_id} improves objective and travel time, but increases makespan.",
        )

    if delta_objective < 0.0 and delta_makespan <= 0.0:
        return (
            "strong",
            f"{scenario_id} improves the objective without increasing makespan.",
        )

    if delta_objective < 0.0:
        return (
            "moderate",
            f"{scenario_id} improves the objective, but needs additional metric checks.",
        )

    return (
        "weak",
        f"{scenario_id} does not show an objective improvement over the planned solution.",
    )


def build_audit_rows(recommendations: dict[str, Any]) -> list[list[Any]]:
    raw_rows = get_list(recommendations, "rows")
    rows: list[list[Any]] = []

    sorted_rows = sorted(
        [row for row in raw_rows if isinstance(row, dict)],
        key=lambda row: as_text(row.get("scenario_id")),
    )

    for row in sorted_rows:
        classification, reason = classify_recommendation(row)

        rows.append(
            [
                as_text(row.get("scenario_id"), "unknown_scenario"),
                classification,
                as_text(row.get("recommended_policy_id"), "unknown_policy"),
                as_text(row.get("recommended_replanning_method_id"), "unknown_method"),
                as_text(row.get("recommended_execution_mode"), "unknown_execution_mode"),
                format_number(row.get("best_score")),
                format_number(row.get("second_best_score")),
                format_number(row.get("score_margin_to_second")),
                format_number(row.get("mean_delta_objective_value")),
                format_number(row.get("mean_delta_makespan")),
                format_number(row.get("mean_delta_total_travel_time")),
                reason,
            ]
        )

    return rows


def build_global_findings(data: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    batch = get_dict(data, "batch")
    outputs = get_dict(data, "outputs")
    rankings = get_dict(data, "rankings")
    ranking_config = get_dict(rankings, "ranking_config")
    recommendations = get_dict(data, "recommendations")

    configured_count = as_number(batch.get("configured_experiment_count"))
    completed_count = as_number(batch.get("completed_experiment_count"))
    completion_percent = as_number(batch.get("completion_percent"))

    if configured_count > 0.0 and completed_count == configured_count and completion_percent == 100.0:
        findings.append("The batch execution is complete. All configured experiments were completed.")
    else:
        findings.append("The batch execution is incomplete. Do not use this result as a finished comparison.")

    expected_output_flags = [
        "overview_csv_was_written",
        "summary_csv_was_written",
        "aggregate_csv_was_written",
        "ranking_csv_was_written",
        "recommendation_csv_was_written",
        "result_json_was_written",
    ]

    missing_outputs = [key for key in expected_output_flags if not as_bool(outputs.get(key))]

    if missing_outputs:
        findings.append("Some expected output files were not written: " + ", ".join(missing_outputs) + ".")
    else:
        findings.append("All expected output files were reported as written.")

    active_weight_count, active_weights = get_weight_summary(ranking_config)

    if active_weight_count == 0:
        findings.append("The ranking configuration has no active weights. This is not valid for decision support.")
    elif active_weight_count == 1 and active_weights[0].startswith("objective_value_weight="):
        findings.append(
            "The ranking is objective-only. This is acceptable for a first validation, "
            "but weak for research conclusions because it ignores makespan, lateness, travel time, "
            "waiting time, and replanning effort."
        )
    else:
        findings.append("The ranking uses multiple active weights: " + ", ".join(active_weights) + ".")

    recommendation_rows = get_list(recommendations, "rows")

    weak_count = 0
    tradeoff_count = 0
    strong_count = 0
    invalid_count = 0

    for row in recommendation_rows:
        if not isinstance(row, dict):
            continue

        classification, _ = classify_recommendation(row)

        if classification == "weak":
            weak_count += 1
        elif classification == "tradeoff":
            tradeoff_count += 1
        elif classification == "strong":
            strong_count += 1
        elif classification == "invalid":
            invalid_count += 1

    findings.append(f"Recommendation audit summary: strong={strong_count}, tradeoff={tradeoff_count}, weak={weak_count}, invalid={invalid_count}.")

    if tradeoff_count > 0:
        findings.append(
            "There are trade-off recommendations. These should not be described as absolute improvements."
        )

    if weak_count > 0:
        findings.append(
            "There are weak recommendations. These need either better ranking criteria, more replications, or richer scenarios."
        )

    if invalid_count > 0:
        findings.append(
            "There are invalid recommendations. The experiment pipeline should be checked before continuing."
        )

    return findings


def generate_audit_report(data: dict[str, Any]) -> str:
    batch = get_dict(data, "batch")
    recommendations = get_dict(data, "recommendations")
    rankings = get_dict(data, "rankings")
    ranking_config = get_dict(rankings, "ranking_config")

    batch_id = as_text(batch.get("batch_id"), "unknown_batch")
    ranking_config_id = as_text(ranking_config.get("ranking_config_id"), "unknown_ranking_config")

    lines: list[str] = []

    lines.append("# FieldOps Lab recommendation audit")
    lines.append("")
    lines.append(f"Batch ID: `{batch_id}`")
    lines.append("")
    lines.append(f"Ranking config ID: `{ranking_config_id}`")
    lines.append("")
    lines.append("## Global findings")
    lines.append("")

    for finding in build_global_findings(data):
        lines.append(f"- {finding}")

    lines.append("")
    lines.append("## Scenario audit")
    lines.append("")

    audit_rows = build_audit_rows(recommendations)

    if audit_rows:
        lines.extend(
            markdown_table(
                [
                    "Scenario",
                    "Audit class",
                    "Policy",
                    "Method",
                    "Execution",
                    "Best score",
                    "Second score",
                    "Margin",
                    "Delta objective",
                    "Delta makespan",
                    "Delta travel",
                    "Reason",
                ],
                audit_rows,
            )
        )
    else:
        lines.append("No recommendation rows were found.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This audit should be used as a safety layer before making claims from the batch. "
        "A recommendation classified as tradeoff may still be useful, but it must be explained as a compromise, "
        "not as an unconditional improvement."
    )
    lines.append("")
    lines.append(
        "At the current stage, the result is good for validating the pipeline. "
        "It is not yet enough to support a final research conclusion because the experiment set is small, "
        "the scenarios are handcrafted, and the ranking is still objective-only."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: py -3 audit_batch_recommendations.py <input_result_json> <output_audit_md>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        data = read_json(input_path)
        report = generate_audit_report(data)
        write_text(output_path, report)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Batch recommendation audit written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())