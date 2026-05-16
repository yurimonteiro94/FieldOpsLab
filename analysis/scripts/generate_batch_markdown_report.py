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


def escape_markdown_cell(value: Any) -> str:
    text = str(value)
    text = text.replace("|", "\\|")
    text = text.replace("\n", " ")
    return text


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines: list[str] = []

    lines.append("| " + " | ".join(escape_markdown_cell(header) for header in headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for row in rows:
        lines.append("| " + " | ".join(escape_markdown_cell(value) for value in row) + " |")

    return lines


def active_weight_rows(ranking_config: dict[str, Any]) -> list[list[Any]]:
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

    rows: list[list[Any]] = []

    for key in weight_keys:
        value = as_number(ranking_config.get(key))

        if value != 0.0:
            rows.append([key, format_number(value)])

    return rows


def recommendation_rows(recommendations: dict[str, Any]) -> list[list[Any]]:
    rows = get_list(recommendations, "rows")
    table_rows: list[list[Any]] = []

    sorted_rows = sorted(
        [row for row in rows if isinstance(row, dict)],
        key=lambda row: as_text(row.get("scenario_id")),
    )

    for row in sorted_rows:
        table_rows.append(
            [
                as_text(row.get("scenario_id"), "unknown_scenario"),
                as_text(row.get("recommended_policy_id"), "unknown_policy"),
                as_text(row.get("recommended_replanning_method_id"), "unknown_method"),
                as_text(row.get("recommended_execution_mode"), "unknown_execution_mode"),
                format_number(row.get("best_score")),
                format_number(row.get("second_best_score")),
                format_number(row.get("score_margin_to_second")),
                format_bool(row.get("has_clear_winner")),
                format_number(row.get("mean_delta_objective_value")),
                format_number(row.get("mean_delta_makespan")),
                format_number(row.get("mean_delta_total_travel_time")),
            ]
        )

    return table_rows


def output_rows(outputs: dict[str, Any]) -> list[list[Any]]:
    keys = [
        ("overview_csv_output_path", "overview_csv_was_written"),
        ("summary_csv_output_path", "summary_csv_was_written"),
        ("aggregate_csv_output_path", "aggregate_csv_was_written"),
        ("ranking_csv_output_path", "ranking_csv_was_written"),
        ("recommendation_csv_output_path", "recommendation_csv_was_written"),
        ("result_json_output_path", "result_json_was_written"),
    ]

    rows: list[list[Any]] = []

    for path_key, flag_key in keys:
        path_value = as_text(outputs.get(path_key))

        if path_value:
            rows.append([path_key, path_value, format_bool(outputs.get(flag_key))])

    return rows


def collect_tradeoff_warnings(recommendations: dict[str, Any]) -> list[str]:
    rows = get_list(recommendations, "rows")
    warnings: list[str] = []

    sorted_rows = sorted(
        [row for row in rows if isinstance(row, dict)],
        key=lambda row: as_text(row.get("scenario_id")),
    )

    for row in sorted_rows:
        scenario_id = as_text(row.get("scenario_id"), "unknown_scenario")
        execution_mode = as_text(row.get("recommended_execution_mode"))

        delta_objective = as_number(row.get("mean_delta_objective_value"))
        delta_makespan = as_number(row.get("mean_delta_makespan"))
        delta_travel = as_number(row.get("mean_delta_total_travel_time"))
        delta_lateness = as_number(row.get("mean_total_lateness"))
        replanning_success_count = as_number(row.get("replanning_success_count"))

        if delta_objective < 0.0 and delta_makespan > 0.0:
            warnings.append(
                f"{scenario_id}: objective improves by {format_number(abs(delta_objective))}, "
                f"but makespan increases by {format_number(delta_makespan)}."
            )

        if delta_travel < 0.0 and delta_makespan > 0.0:
            warnings.append(
                f"{scenario_id}: travel time improves by {format_number(abs(delta_travel))}, "
                f"but makespan still increases by {format_number(delta_makespan)}."
            )

        if delta_lateness > 0.0:
            warnings.append(
                f"{scenario_id}: the recommended option has positive lateness "
                f"of {format_number(delta_lateness)}."
            )

        if execution_mode == "replanning_applied_execution" and replanning_success_count <= 0.0:
            warnings.append(
                f"{scenario_id}: replanning appears to be applied, but success count is "
                f"{format_number(replanning_success_count)}."
            )

    return warnings


def generate_markdown_report(data: dict[str, Any]) -> str:
    batch = get_dict(data, "batch")
    rankings = get_dict(data, "rankings")
    ranking_config = get_dict(rankings, "ranking_config")
    recommendations = get_dict(data, "recommendations")
    outputs = get_dict(data, "outputs")

    lines: list[str] = []

    batch_id = as_text(batch.get("batch_id"), "unknown_batch")
    batch_name = as_text(batch.get("name"), "Unnamed batch")

    lines.append(f"# FieldOps Lab batch report")
    lines.append("")
    lines.append(f"## {batch_name}")
    lines.append("")
    lines.append("This report was generated automatically from the batch result JSON.")
    lines.append("")
    lines.append("## Batch overview")
    lines.append("")

    lines.extend(
        markdown_table(
            ["Field", "Value"],
            [
                ["batch_id", batch_id],
                ["configured_experiment_count", format_number(batch.get("configured_experiment_count"))],
                ["completed_experiment_count", format_number(batch.get("completed_experiment_count"))],
                ["completion_percent", format_number(batch.get("completion_percent"))],
                ["is_complete", format_bool(batch.get("is_complete"))],
                ["experiment_count", format_number(batch.get("experiment_count"))],
            ],
        )
    )

    description = as_text(batch.get("description"))

    if description:
        lines.append("")
        lines.append("## Description")
        lines.append("")
        lines.append(description)

    lines.append("")
    lines.append("## Ranking configuration")
    lines.append("")

    lines.append(f"Ranking config ID: `{as_text(ranking_config.get('ranking_config_id'), 'unknown_ranking_config')}`")
    lines.append("")

    score_definition = as_text(rankings.get("ranking_score_definition"))

    if score_definition:
        lines.append(f"Score definition: {score_definition}")
        lines.append("")

    weight_rows = active_weight_rows(ranking_config)

    if weight_rows:
        lines.extend(markdown_table(["Active weight", "Value"], weight_rows))
    else:
        lines.append("No active ranking weights were found.")

    if len(weight_rows) == 1 and weight_rows[0][0] == "objective_value_weight":
        lines.append("")
        lines.append(
            "**Important limitation:** this ranking is currently objective-only. "
            "It does not penalize makespan, lateness, travel time, waiting time, "
            "or replanning effort."
        )

    lines.append("")
    lines.append("## Recommendations")
    lines.append("")

    rec_rows = recommendation_rows(recommendations)

    if rec_rows:
        lines.extend(
            markdown_table(
                [
                    "Scenario",
                    "Policy",
                    "Replanning method",
                    "Execution mode",
                    "Best score",
                    "Second score",
                    "Margin",
                    "Clear winner",
                    "Delta objective",
                    "Delta makespan",
                    "Delta travel",
                ],
                rec_rows,
            )
        )
    else:
        lines.append("No recommendations were found.")

    lines.append("")
    lines.append("## Trade-off warnings")
    lines.append("")

    warnings = collect_tradeoff_warnings(recommendations)

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("No trade-off warnings were found.")

    lines.append("")
    lines.append("## Generated files")
    lines.append("")

    out_rows = output_rows(outputs)

    if out_rows:
        lines.extend(markdown_table(["Output", "Path", "Written"], out_rows))
    else:
        lines.append("No generated output paths were found.")

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The current batch is useful as a controlled validation example. "
        "It shows that the system can execute baseline policies, trigger replanning decisions, "
        "apply a greedy replanning method, rank alternatives, recommend options, and export results."
    )
    lines.append("")
    lines.append(
        "However, this is not yet enough for a research conclusion. "
        "The ranking configuration is still objective-only, the sample size is small, "
        "and the current scenarios are handcrafted examples rather than a broad experimental campaign."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: py -3 generate_batch_markdown_report.py <input_result_json> <output_report_md>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        data = read_json(input_path)
        markdown = generate_markdown_report(data)
        write_text(output_path, markdown)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Markdown batch report written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())