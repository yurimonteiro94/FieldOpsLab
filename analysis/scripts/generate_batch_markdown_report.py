from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("The input JSON root must be an object.")

    return data


def format_number(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, bool):
        return "yes" if value else "no"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    return str(value)


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def get_nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data

    for key in keys:
        if not isinstance(current, dict):
            return default
        if key not in current:
            return default
        current = current[key]

    return current


def make_markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines: list[str] = []

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        formatted = [format_number(value).replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(formatted) + " |")

    return lines


def collect_active_weights(ranking_config: dict[str, Any]) -> list[tuple[str, Any]]:
    active_weights: list[tuple[str, Any]] = []

    for key in sorted(ranking_config.keys()):
        if not key.endswith("_weight"):
            continue

        value = ranking_config.get(key)

        if isinstance(value, (int, float)) and float(value) != 0.0:
            active_weights.append((key, value))

    return active_weights


def collect_output_rows(outputs: dict[str, Any]) -> list[list[Any]]:
    output_pairs = [
        ("overview_csv_output_path", "overview_csv_was_written"),
        ("summary_csv_output_path", "summary_csv_was_written"),
        ("aggregate_csv_output_path", "aggregate_csv_was_written"),
        ("ranking_csv_output_path", "ranking_csv_was_written"),
        ("recommendation_csv_output_path", "recommendation_csv_was_written"),
        ("result_json_output_path", "result_json_was_written"),
    ]

    rows: list[list[Any]] = []

    for path_key, written_key in output_pairs:
        path_value = outputs.get(path_key, "")
        written_value = outputs.get(written_key, False)
        rows.append([path_key, path_value, yes_no(written_value)])

    return rows


def collect_recommendation_rows(recommendations: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []

    for row in recommendations.get("rows", []):
        if not isinstance(row, dict):
            continue

        rows.append(
            [
                row.get("scenario_id", ""),
                row.get("recommended_policy_id", ""),
                row.get("recommended_replanning_method_id", ""),
                row.get("recommended_execution_mode", ""),
                row.get("best_score", ""),
                row.get("second_best_score", ""),
                row.get("score_margin_to_second", ""),
                yes_no(row.get("has_clear_winner", False)),
                row.get("mean_delta_objective_value", ""),
                row.get("mean_delta_makespan", ""),
                row.get("mean_delta_total_travel_time", ""),
            ]
        )

    return rows


def collect_tradeoff_warnings(recommendations: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    for row in recommendations.get("rows", []):
        if not isinstance(row, dict):
            continue

        scenario_id = row.get("scenario_id", "")
        delta_objective = float(row.get("mean_delta_objective_value", 0.0) or 0.0)
        delta_makespan = float(row.get("mean_delta_makespan", 0.0) or 0.0)
        delta_travel = float(row.get("mean_delta_total_travel_time", 0.0) or 0.0)

        if delta_objective < 0 and delta_makespan > 0:
            warnings.append(
                f"- {scenario_id}: objective improves by {format_number(abs(delta_objective))}, "
                f"but makespan increases by {format_number(delta_makespan)}."
            )

        if delta_travel < 0 and delta_makespan > 0:
            warnings.append(
                f"- {scenario_id}: travel time improves by {format_number(abs(delta_travel))}, "
                f"but makespan still increases by {format_number(delta_makespan)}."
            )

    return warnings


def generate_report(data: dict[str, Any]) -> str:
    batch = get_nested(data, "batch", default={})
    rankings = get_nested(data, "rankings", default={})
    ranking_config = get_nested(data, "rankings", "ranking_config", default={})
    recommendations = get_nested(data, "recommendations", default={})
    outputs = get_nested(data, "outputs", default={})

    if not isinstance(batch, dict):
        batch = {}

    if not isinstance(rankings, dict):
        rankings = {}

    if not isinstance(ranking_config, dict):
        ranking_config = {}

    if not isinstance(recommendations, dict):
        recommendations = {}

    if not isinstance(outputs, dict):
        outputs = {}

    batch_name = batch.get("name", "")
    batch_description = batch.get("description", "")

    lines: list[str] = []

    lines.append("# FieldOps Lab batch report")
    lines.append("")
    lines.append(f"## {batch_name or 'Unnamed batch'}")
    lines.append("")
    lines.append("This report was generated automatically from the batch result JSON.")
    lines.append("")

    lines.append("## Batch overview")
    lines.append("")
    lines.extend(
        make_markdown_table(
            ["Field", "Value"],
            [
                ["batch_id", batch.get("batch_id", "")],
                ["configured_experiment_count", batch.get("configured_experiment_count", "")],
                ["completed_experiment_count", batch.get("completed_experiment_count", "")],
                ["completion_percent", batch.get("completion_percent", "")],
                ["is_complete", yes_no(batch.get("is_complete", False))],
                ["experiment_count", batch.get("experiment_count", "")],
            ],
        )
    )
    lines.append("")

    lines.append("## Description")
    lines.append("")
    lines.append(str(batch_description or "No description provided."))
    lines.append("")

    lines.append("## Ranking configuration")
    lines.append("")
    lines.append(f"Ranking config ID: `{ranking_config.get('ranking_config_id', '')}`")
    lines.append("")
    lines.append(
        f"Score definition: {rankings.get('ranking_score_definition', 'No ranking score definition provided.')}"
    )
    lines.append("")

    active_weights = collect_active_weights(ranking_config)

    if active_weights:
        lines.extend(
            make_markdown_table(
                ["Active weight", "Value"],
                [[key, value] for key, value in active_weights],
            )
        )
    else:
        lines.append("No active ranking weights were found.")

    lines.append("")

    active_weight_names = [name for name, _ in active_weights]

    if active_weight_names == ["objective_value_weight"]:
        lines.append(
            "**Important limitation:** this ranking is currently objective-only. "
            "It does not penalize makespan, lateness, travel time, waiting time, or replanning effort."
        )
        lines.append("")

    lines.append("## Recommendations")
    lines.append("")

    recommendation_rows = collect_recommendation_rows(recommendations)

    if recommendation_rows:
        lines.extend(
            make_markdown_table(
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
                recommendation_rows,
            )
        )
    else:
        lines.append("No recommendations were found in the batch result.")

    lines.append("")

    lines.append("## Trade-off warnings")
    lines.append("")

    tradeoff_warnings = collect_tradeoff_warnings(recommendations)

    if tradeoff_warnings:
        lines.extend(tradeoff_warnings)
    else:
        lines.append("No trade-off warnings were detected.")

    lines.append("")

    lines.append("## Generated files")
    lines.append("")

    output_rows = collect_output_rows(outputs)

    if output_rows:
        lines.extend(
            make_markdown_table(
                ["Output", "Path", "Written"],
                output_rows,
            )
        )
    else:
        lines.append("No generated output file information was found.")

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
        "The ranking configuration is still limited, the sample size is small, "
        "and the current scenarios are handcrafted examples rather than a broad experimental campaign."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: py -3 analysis\\scripts\\generate_batch_markdown_report.py "
            "<batch_result_json> <output_markdown_path>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = load_json(input_path)
    report = generate_report(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"Markdown batch report written to: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())