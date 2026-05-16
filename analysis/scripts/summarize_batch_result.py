from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("The result JSON root must be an object.")

    return data


def as_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default

    if isinstance(value, int | float):
        return float(value)

    return default


def as_text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value

    return default


def format_number(value: Any) -> str:
    number = as_number(value)

    if number == int(number):
        return str(int(number))

    return f"{number:.2f}"


def format_bool(value: Any) -> str:
    if value is True:
        return "yes"

    if value is False:
        return "no"

    return "unknown"


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


def summarize_ranking_config(ranking_config: dict[str, Any]) -> list[str]:
    lines: list[str] = []

    ranking_config_id = as_text(
        ranking_config.get("ranking_config_id"),
        "unknown_ranking_config",
    )

    lines.append(f"Ranking config: {ranking_config_id}")

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
    ignored_weights: list[str] = []

    for key in weight_keys:
        value = as_number(ranking_config.get(key))

        if value != 0.0:
            active_weights.append(f"{key}={format_number(value)}")
        else:
            ignored_weights.append(key)

    if active_weights:
        lines.append("Active weights: " + ", ".join(active_weights))
    else:
        lines.append("Active weights: none")

    if len(active_weights) == 1 and active_weights[0].startswith("objective_value_weight="):
        lines.append(
            "Important note: this ranking is currently objective-only. "
            "It does not penalize makespan, lateness, travel time, waiting time, "
            "or replanning effort."
        )

    return lines


def summarize_recommendations(recommendations: dict[str, Any]) -> tuple[list[str], list[str]]:
    rows = get_list(recommendations, "rows")

    lines: list[str] = []
    warnings: list[str] = []

    if not rows:
        return ["No recommendations found."], warnings

    lines.append("Recommendations by scenario:")

    sorted_rows = sorted(
        rows,
        key=lambda row: as_text(row.get("scenario_id")) if isinstance(row, dict) else "",
    )

    for row in sorted_rows:
        if not isinstance(row, dict):
            continue

        scenario_id = as_text(row.get("scenario_id"), "unknown_scenario")
        policy_id = as_text(row.get("recommended_policy_id"), "unknown_policy")
        method_id = as_text(row.get("recommended_replanning_method_id"), "unknown_method")
        execution_mode = as_text(row.get("recommended_execution_mode"), "unknown_execution_mode")

        best_score = row.get("best_score")
        second_best_score = row.get("second_best_score")
        score_margin = row.get("score_margin_to_second")
        has_clear_winner = row.get("has_clear_winner")

        delta_objective = as_number(row.get("mean_delta_objective_value"))
        delta_makespan = as_number(row.get("mean_delta_makespan"))
        delta_lateness = as_number(row.get("mean_total_lateness"))
        delta_travel = as_number(row.get("mean_delta_total_travel_time"))
        replanning_success_count = as_number(row.get("replanning_success_count"))

        clear_winner_text = "clear winner" if has_clear_winner is True else "tie or weak winner"

        lines.append(
            f"- {scenario_id}: {policy_id} + {method_id} "
            f"({execution_mode}) | score={format_number(best_score)} | "
            f"second={format_number(second_best_score)} | "
            f"margin={format_number(score_margin)} | {clear_winner_text}"
        )

        if delta_objective < 0.0 and delta_makespan > 0.0:
            warnings.append(
                f"{scenario_id}: the recommended option improves objective value by "
                f"{format_number(abs(delta_objective))}, but increases makespan by "
                f"{format_number(delta_makespan)}."
            )

        if delta_lateness > 0.0:
            warnings.append(
                f"{scenario_id}: the recommended option has positive lateness "
                f"({format_number(delta_lateness)})."
            )

        if execution_mode == "replanning_applied_execution" and replanning_success_count <= 0.0:
            warnings.append(
                f"{scenario_id}: execution says replanning was applied, but "
                f"replanning_success_count is {format_number(replanning_success_count)}."
            )

        if delta_travel < 0.0 and delta_makespan > 0.0:
            warnings.append(
                f"{scenario_id}: travel time improves by {format_number(abs(delta_travel))}, "
                f"but makespan still increases by {format_number(delta_makespan)}. "
                f"This is a trade-off, not an absolute improvement."
            )

    return lines, warnings


def summarize_result(data: dict[str, Any]) -> str:
    batch = get_dict(data, "batch")
    rankings = get_dict(data, "rankings")
    ranking_config = get_dict(rankings, "ranking_config")
    recommendations = get_dict(data, "recommendations")
    outputs = get_dict(data, "outputs")

    lines: list[str] = []

    lines.append("FieldOps Lab batch result summary")
    lines.append("=" * 38)
    lines.append(f"Batch ID: {as_text(batch.get('batch_id'), 'unknown_batch')}")
    lines.append(f"Name: {as_text(batch.get('name'), 'unnamed batch')}")
    lines.append(f"Configured experiments: {format_number(batch.get('configured_experiment_count'))}")
    lines.append(f"Completed experiments: {format_number(batch.get('completed_experiment_count'))}")
    lines.append(f"Completion: {format_number(batch.get('completion_percent'))}%")
    lines.append(f"Is complete: {format_bool(batch.get('is_complete'))}")
    lines.append("")

    lines.extend(summarize_ranking_config(ranking_config))
    lines.append("")

    score_definition = as_text(rankings.get("ranking_score_definition"))

    if score_definition:
        lines.append(f"Score definition: {score_definition}")
        lines.append("")

    recommendation_lines, warning_lines = summarize_recommendations(recommendations)
    lines.extend(recommendation_lines)
    lines.append("")

    if warning_lines:
        lines.append("Trade-off warnings:")
        for warning in warning_lines:
            lines.append(f"- {warning}")
    else:
        lines.append("Trade-off warnings: none")

    lines.append("")
    lines.append("Generated output files:")

    output_keys = [
        "overview_csv_output_path",
        "summary_csv_output_path",
        "aggregate_csv_output_path",
        "ranking_csv_output_path",
        "recommendation_csv_output_path",
        "result_json_output_path",
    ]

    for key in output_keys:
        value = as_text(outputs.get(key))
        was_written = outputs.get(key.replace("_output_path", "_was_written"))

        if value:
            lines.append(f"- {key}: {value} | written={format_bool(was_written)}")

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python summarize_batch_result.py <batch_result_json_path>",
            file=sys.stderr,
        )
        return 2

    result_path = Path(sys.argv[1])

    try:
        data = read_json(result_path)
        summary = summarize_result(data)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())