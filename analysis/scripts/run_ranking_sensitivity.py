from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EPSILON = 0.000001


RANKING_PROFILES: dict[str, dict[str, Any]] = {
    "objective_only": {
        "description": "Replicates the current default ranking. Lower objective delta is better.",
        "weights": {
            "mean_delta_objective_value": 1.0,
        },
    },
    "balanced_operational": {
        "description": "Balances objective value, makespan, travel time, lateness, and small replanning effort.",
        "weights": {
            "mean_delta_objective_value": 1.0,
            "mean_delta_makespan": 0.5,
            "mean_delta_total_travel_time": 0.25,
            "mean_delta_total_lateness": 2.0,
            "mean_delta_late_task_count": 100.0,
            "replanning_applied_rate": 5.0,
        },
    },
    "makespan_priority": {
        "description": "Prioritizes finishing earlier. This profile intentionally penalizes makespan strongly.",
        "weights": {
            "mean_delta_objective_value": 0.25,
            "mean_delta_makespan": 1.5,
            "mean_delta_total_travel_time": 0.10,
            "mean_delta_total_lateness": 2.0,
            "mean_delta_late_task_count": 100.0,
            "replanning_applied_rate": 20.0,
        },
    },
    "conservative_replanning": {
        "description": "Penalizes replanning effort. Useful when operational stability matters.",
        "weights": {
            "mean_delta_objective_value": 1.0,
            "mean_delta_makespan": 0.5,
            "mean_delta_total_travel_time": 0.25,
            "mean_delta_total_lateness": 2.0,
            "mean_delta_late_task_count": 100.0,
            "replanning_request_rate": 10.0,
            "replanning_applied_rate": 30.0,
        },
    },
}


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

    if abs(number - int(number)) < EPSILON:
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


def make_option_id(option: dict[str, Any]) -> str:
    policy_id = as_text(option.get("policy_id"), "unknown_policy")
    method_id = as_text(option.get("replanning_method_id"), "unknown_method")
    execution_mode = as_text(option.get("execution_mode"), "unknown_execution")

    return f"{policy_id} + {method_id} + {execution_mode}"


def experiment_key(experiment: dict[str, Any]) -> tuple[str, str, str, str]:
    policy = get_dict(experiment, "policy")
    replanning_result = get_dict(experiment, "replanning_result")
    execution = get_dict(experiment, "execution")

    scenario_id = as_text(experiment.get("scenario_id"), "unknown_scenario")
    policy_id = as_text(policy.get("policy_id"), "unknown_policy")
    replanning_method_id = as_text(replanning_result.get("method_id"), "unknown_method")
    execution_mode = as_text(execution.get("execution_mode"), "unknown_execution")

    return scenario_id, policy_id, replanning_method_id, execution_mode


def build_option_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    experiments = get_list(data, "experiments")
    groups: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for raw_experiment in experiments:
        if not isinstance(raw_experiment, dict):
            continue

        key = experiment_key(raw_experiment)
        scenario_id, policy_id, replanning_method_id, execution_mode = key

        metrics = get_dict(raw_experiment, "metrics")
        policy = get_dict(raw_experiment, "policy")
        replanning_request = get_dict(raw_experiment, "replanning_request")
        replanning_result = get_dict(raw_experiment, "replanning_result")

        if key not in groups:
            groups[key] = {
                "scenario_id": scenario_id,
                "policy_id": policy_id,
                "replanning_method_id": replanning_method_id,
                "execution_mode": execution_mode,
                "experiment_count": 0.0,
                "sum_delta_objective_value": 0.0,
                "sum_delta_makespan": 0.0,
                "sum_delta_total_travel_time": 0.0,
                "sum_delta_total_waiting_time": 0.0,
                "sum_delta_total_service_time": 0.0,
                "sum_delta_total_lateness": 0.0,
                "sum_delta_late_task_count": 0.0,
                "sum_effect_count": 0.0,
                "policy_should_replan_count": 0.0,
                "replanning_request_count": 0.0,
                "replanning_success_count": 0.0,
                "replanning_applied_count": 0.0,
            }

        group = groups[key]
        group["experiment_count"] += 1.0
        group["sum_delta_objective_value"] += as_number(metrics.get("delta_objective_value"))
        group["sum_delta_makespan"] += as_number(metrics.get("delta_makespan"))
        group["sum_delta_total_travel_time"] += as_number(metrics.get("delta_total_travel_time"))
        group["sum_delta_total_waiting_time"] += as_number(metrics.get("delta_total_waiting_time"))
        group["sum_delta_total_service_time"] += as_number(metrics.get("delta_total_service_time"))
        group["sum_delta_total_lateness"] += as_number(metrics.get("delta_total_lateness"))
        group["sum_delta_late_task_count"] += as_number(metrics.get("delta_late_task_count"))
        group["sum_effect_count"] += as_number(metrics.get("effect_count"))

        if as_bool(policy.get("should_replan")):
            group["policy_should_replan_count"] += 1.0

        if as_bool(replanning_request.get("has_replanning_request")):
            group["replanning_request_count"] += 1.0

        if as_bool(replanning_result.get("is_successful")):
            group["replanning_success_count"] += 1.0

        if as_bool(replanning_result.get("was_applied_to_execution")):
            group["replanning_applied_count"] += 1.0

    options: list[dict[str, Any]] = []

    for group in groups.values():
        count = as_number(group.get("experiment_count"))

        if count <= 0.0:
            continue

        option = {
            "scenario_id": group["scenario_id"],
            "policy_id": group["policy_id"],
            "replanning_method_id": group["replanning_method_id"],
            "execution_mode": group["execution_mode"],
            "experiment_count": count,
            "mean_delta_objective_value": group["sum_delta_objective_value"] / count,
            "mean_delta_makespan": group["sum_delta_makespan"] / count,
            "mean_delta_total_travel_time": group["sum_delta_total_travel_time"] / count,
            "mean_delta_total_waiting_time": group["sum_delta_total_waiting_time"] / count,
            "mean_delta_total_service_time": group["sum_delta_total_service_time"] / count,
            "mean_delta_total_lateness": group["sum_delta_total_lateness"] / count,
            "mean_delta_late_task_count": group["sum_delta_late_task_count"] / count,
            "mean_effect_count": group["sum_effect_count"] / count,
            "policy_should_replan_rate": group["policy_should_replan_count"] / count,
            "replanning_request_rate": group["replanning_request_count"] / count,
            "replanning_success_rate": group["replanning_success_count"] / count,
            "replanning_applied_rate": group["replanning_applied_count"] / count,
        }

        option["option_id"] = make_option_id(option)
        options.append(option)

    return options


def calculate_score(option: dict[str, Any], weights: dict[str, float]) -> float:
    score = 0.0

    for metric_name, weight in weights.items():
        score += as_number(option.get(metric_name)) * weight

    return score


def rank_options_for_profile(
    options: list[dict[str, Any]],
    profile: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    weights = profile.get("weights")

    if not isinstance(weights, dict):
        raise ValueError("Ranking profile weights must be an object.")

    clean_weights: dict[str, float] = {}

    for key, value in weights.items():
        clean_weights[str(key)] = as_number(value)

    by_scenario: dict[str, list[dict[str, Any]]] = {}

    for option in options:
        scenario_id = as_text(option.get("scenario_id"), "unknown_scenario")
        scored_option = dict(option)
        scored_option["ranking_score"] = calculate_score(scored_option, clean_weights)

        by_scenario.setdefault(scenario_id, []).append(scored_option)

    for scenario_id in by_scenario:
        by_scenario[scenario_id].sort(
            key=lambda row: (
                as_number(row.get("ranking_score")),
                as_number(row.get("mean_delta_makespan")),
                as_number(row.get("mean_delta_total_travel_time")),
                as_text(row.get("policy_id")),
                as_text(row.get("replanning_method_id")),
                as_text(row.get("execution_mode")),
            )
        )

    return by_scenario


def build_profile_recommendations(options: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}

    for profile_id, profile in RANKING_PROFILES.items():
        ranked_by_scenario = rank_options_for_profile(options, profile)
        profile_rows: dict[str, dict[str, Any]] = {}

        for scenario_id, ranked_options in ranked_by_scenario.items():
            if not ranked_options:
                continue

            best = ranked_options[0]
            second = ranked_options[1] if len(ranked_options) > 1 else None

            best_score = as_number(best.get("ranking_score"))
            second_score = as_number(second.get("ranking_score")) if second is not None else best_score
            margin = second_score - best_score

            row = dict(best)
            row["profile_id"] = profile_id
            row["second_best_score"] = second_score
            row["score_margin_to_second"] = margin
            row["has_clear_winner"] = margin > EPSILON

            profile_rows[scenario_id] = row

        result[profile_id] = profile_rows

    return result


def build_profile_table() -> list[str]:
    rows: list[list[Any]] = []

    for profile_id, profile in RANKING_PROFILES.items():
        weights = profile.get("weights")
        description = as_text(profile.get("description"))

        if isinstance(weights, dict):
            weight_text = ", ".join(f"{key}={format_number(value)}" for key, value in weights.items())
        else:
            weight_text = ""

        rows.append([profile_id, description, weight_text])

    return markdown_table(["Profile", "Description", "Weights"], rows)


def build_recommendation_tables(
    profile_recommendations: dict[str, dict[str, dict[str, Any]]]
) -> list[str]:
    lines: list[str] = []

    for profile_id, scenario_rows in profile_recommendations.items():
        lines.append(f"### {profile_id}")
        lines.append("")

        rows: list[list[Any]] = []

        for scenario_id in sorted(scenario_rows.keys()):
            row = scenario_rows[scenario_id]

            rows.append(
                [
                    scenario_id,
                    as_text(row.get("option_id")),
                    format_number(row.get("ranking_score")),
                    format_number(row.get("second_best_score")),
                    format_number(row.get("score_margin_to_second")),
                    "yes" if as_bool(row.get("has_clear_winner")) else "no",
                    format_number(row.get("mean_delta_objective_value")),
                    format_number(row.get("mean_delta_makespan")),
                    format_number(row.get("mean_delta_total_travel_time")),
                    format_number(row.get("replanning_applied_rate")),
                ]
            )

        lines.extend(
            markdown_table(
                [
                    "Scenario",
                    "Recommended option",
                    "Score",
                    "Second score",
                    "Margin",
                    "Clear winner",
                    "Delta objective",
                    "Delta makespan",
                    "Delta travel",
                    "Replanning applied rate",
                ],
                rows,
            )
        )

        lines.append("")

    return lines


def build_stability_table(
    profile_recommendations: dict[str, dict[str, dict[str, Any]]]
) -> list[str]:
    scenario_ids: set[str] = set()

    for profile_rows in profile_recommendations.values():
        scenario_ids.update(profile_rows.keys())

    rows: list[list[Any]] = []

    for scenario_id in sorted(scenario_ids):
        option_by_profile: dict[str, str] = {}

        for profile_id in RANKING_PROFILES.keys():
            row = profile_recommendations.get(profile_id, {}).get(scenario_id)
            option_by_profile[profile_id] = as_text(row.get("option_id")) if isinstance(row, dict) else ""

        unique_options = set(option_by_profile.values())
        unique_options.discard("")

        if len(unique_options) == 1:
            stability = "stable"
        elif len(unique_options) == 0:
            stability = "missing"
        else:
            stability = "sensitive"

        rows.append(
            [
                scenario_id,
                stability,
                option_by_profile.get("objective_only", ""),
                option_by_profile.get("balanced_operational", ""),
                option_by_profile.get("makespan_priority", ""),
                option_by_profile.get("conservative_replanning", ""),
            ]
        )

    return markdown_table(
        [
            "Scenario",
            "Stability",
            "Objective only",
            "Balanced operational",
            "Makespan priority",
            "Conservative replanning",
        ],
        rows,
    )


def build_interpretation(
    profile_recommendations: dict[str, dict[str, dict[str, Any]]]
) -> list[str]:
    lines: list[str] = []

    scenario_ids: set[str] = set()

    for profile_rows in profile_recommendations.values():
        scenario_ids.update(profile_rows.keys())

    sensitive_count = 0
    stable_count = 0

    for scenario_id in scenario_ids:
        unique_options: set[str] = set()

        for profile_id in RANKING_PROFILES.keys():
            row = profile_recommendations.get(profile_id, {}).get(scenario_id)

            if isinstance(row, dict):
                option_id = as_text(row.get("option_id"))

                if option_id:
                    unique_options.add(option_id)

        if len(unique_options) <= 1:
            stable_count += 1
        else:
            sensitive_count += 1

    lines.append(f"- Stable scenarios: {stable_count}.")
    lines.append(f"- Sensitive scenarios: {sensitive_count}.")

    if sensitive_count > 0:
        lines.append(
            "- Some recommendations change when the ranking weights change. "
            "These cases should not be treated as final policy conclusions yet."
        )

    if stable_count > 0:
        lines.append(
            "- Stable recommendations are more promising, but still require more replications and broader scenarios."
        )

    lines.append(
        "- This script is a step toward decision support. It is not fuzzy logic yet, but it prepares the ground for fuzzy rules by showing how scenario recommendations react to different priorities."
    )

    return lines


def generate_report(data: dict[str, Any]) -> str:
    batch = get_dict(data, "batch")
    batch_id = as_text(batch.get("batch_id"), "unknown_batch")
    batch_name = as_text(batch.get("name"), "unknown_batch_name")

    options = build_option_rows(data)
    profile_recommendations = build_profile_recommendations(options)

    lines: list[str] = []

    lines.append("# FieldOps Lab ranking sensitivity report")
    lines.append("")
    lines.append(f"Batch ID: `{batch_id}`")
    lines.append("")
    lines.append(f"Batch name: {batch_name}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This report tests whether the recommended policy changes when the ranking weights change. "
        "If the recommendation changes across profiles, the conclusion is sensitive to the decision criteria."
    )
    lines.append("")
    lines.append("## Ranking profiles")
    lines.append("")
    lines.extend(build_profile_table())
    lines.append("")
    lines.append("## Recommendations by profile")
    lines.append("")
    lines.extend(build_recommendation_tables(profile_recommendations))
    lines.append("## Stability across profiles")
    lines.append("")
    lines.extend(build_stability_table(profile_recommendations))
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.extend(build_interpretation(profile_recommendations))

    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: py -3 run_ranking_sensitivity.py <input_result_json> <output_report_md>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        data = read_json(input_path)
        report = generate_report(data)
        write_text(output_path, report)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Ranking sensitivity report written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())