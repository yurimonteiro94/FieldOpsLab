from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EPSILON = 0.000001


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


def clamp(value: float) -> float:
    if value < 0.0:
        return 0.0

    if value > 1.0:
        return 1.0

    return value


def left_shoulder(x: float, full_until: float, zero_at: float) -> float:
    if x <= full_until:
        return 1.0

    if x >= zero_at:
        return 0.0

    denominator = zero_at - full_until

    if abs(denominator) < EPSILON:
        return 0.0

    return clamp((zero_at - x) / denominator)


def triangular(x: float, left: float, peak: float, right: float) -> float:
    if x <= left or x >= right:
        return 0.0

    if abs(x - peak) < EPSILON:
        return 1.0

    if x < peak:
        denominator = peak - left

        if abs(denominator) < EPSILON:
            return 0.0

        return clamp((x - left) / denominator)

    denominator = right - peak

    if abs(denominator) < EPSILON:
        return 0.0

    return clamp((right - x) / denominator)


def right_shoulder(x: float, zero_until: float, full_at: float) -> float:
    if x <= zero_until:
        return 0.0

    if x >= full_at:
        return 1.0

    denominator = full_at - zero_until

    if abs(denominator) < EPSILON:
        return 0.0

    return clamp((x - zero_until) / denominator)


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


def experiment_key(experiment: dict[str, Any]) -> tuple[str, str, str, str]:
    policy = get_dict(experiment, "policy")
    replanning_result = get_dict(experiment, "replanning_result")
    execution = get_dict(experiment, "execution")

    scenario_id = as_text(experiment.get("scenario_id"), "unknown_scenario")
    policy_id = as_text(policy.get("policy_id"), "unknown_policy")
    method_id = as_text(replanning_result.get("method_id"), "unknown_method")
    execution_mode = as_text(execution.get("execution_mode"), "unknown_execution")

    return scenario_id, policy_id, method_id, execution_mode


def make_option_id(option: dict[str, Any]) -> str:
    return (
        as_text(option.get("policy_id"), "unknown_policy")
        + " + "
        + as_text(option.get("replanning_method_id"), "unknown_method")
        + " + "
        + as_text(option.get("execution_mode"), "unknown_execution")
    )


def build_option_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    experiments = get_list(data, "experiments")
    groups: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for raw_experiment in experiments:
        if not isinstance(raw_experiment, dict):
            continue

        key = experiment_key(raw_experiment)
        scenario_id, policy_id, method_id, execution_mode = key

        metrics = get_dict(raw_experiment, "metrics")
        policy = get_dict(raw_experiment, "policy")
        replanning_request = get_dict(raw_experiment, "replanning_request")
        replanning_result = get_dict(raw_experiment, "replanning_result")

        if key not in groups:
            groups[key] = {
                "scenario_id": scenario_id,
                "policy_id": policy_id,
                "replanning_method_id": method_id,
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


def group_options_by_scenario(options: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_scenario: dict[str, list[dict[str, Any]]] = {}

    for option in options:
        scenario_id = as_text(option.get("scenario_id"), "unknown_scenario")
        by_scenario.setdefault(scenario_id, []).append(option)

    return by_scenario


def select_no_replanning_option(options: list[dict[str, Any]]) -> dict[str, Any] | None:
    for option in options:
        if as_text(option.get("policy_id")) == "no_replanning_policy_v1":
            return option

    for option in options:
        if as_text(option.get("execution_mode")) == "no_replanning_execution_baseline":
            return option

    return None


def select_greedy_replanning_option(options: list[dict[str, Any]]) -> dict[str, Any] | None:
    for option in options:
        method_id = as_text(option.get("replanning_method_id"))
        execution_mode = as_text(option.get("execution_mode"))

        if method_id == "greedy_replanning_solver_v1" and execution_mode == "replanning_applied_execution":
            return option

    for option in options:
        method_id = as_text(option.get("replanning_method_id"))

        if method_id == "greedy_replanning_solver_v1":
            return option

    return None


def build_fuzzy_memberships(features: dict[str, float]) -> dict[str, dict[str, float]]:
    impact = features["no_replanning_impact_score"]
    gain = features["objective_gain_if_replan"]
    risk = features["makespan_risk_if_replan"]
    travel_gain = features["travel_gain_if_replan"]

    return {
        "no_replanning_impact": {
            "low": left_shoulder(impact, 15.0, 60.0),
            "medium": triangular(impact, 30.0, 90.0, 150.0),
            "high": right_shoulder(impact, 100.0, 180.0),
        },
        "objective_gain_if_replan": {
            "low": left_shoulder(gain, 10.0, 40.0),
            "medium": triangular(gain, 20.0, 70.0, 120.0),
            "high": right_shoulder(gain, 80.0, 140.0),
        },
        "makespan_risk_if_replan": {
            "low": left_shoulder(risk, 10.0, 30.0),
            "medium": triangular(risk, 15.0, 40.0, 70.0),
            "high": right_shoulder(risk, 50.0, 90.0),
        },
        "travel_gain_if_replan": {
            "low": left_shoulder(travel_gain, 10.0, 40.0),
            "medium": triangular(travel_gain, 20.0, 70.0, 120.0),
            "high": right_shoulder(travel_gain, 80.0, 140.0),
        },
    }


def calculate_rule_strengths(memberships: dict[str, dict[str, float]]) -> dict[str, float]:
    impact = memberships["no_replanning_impact"]
    gain = memberships["objective_gain_if_replan"]
    risk = memberships["makespan_risk_if_replan"]
    travel_gain = memberships["travel_gain_if_replan"]

    do_not_replan = max(
        min(impact["low"], gain["low"]),
        min(gain["low"], risk["high"]),
        min(impact["low"], risk["low"]),
    )

    replan = max(
        min(gain["high"], risk["low"]),
        min(gain["high"], risk["medium"]) * 0.80,
        min(gain["medium"], risk["low"]) * 0.70,
        min(gain["medium"], travel_gain["high"], risk["low"]) * 0.80,
    )

    conditional_replan = max(
        min(gain["high"], risk["high"]),
        min(gain["high"], risk["medium"]),
        min(gain["medium"], risk["medium"]),
        min(impact["high"], risk["high"]),
        min(travel_gain["high"], risk["medium"]),
    )

    return {
        "do_not_replan": do_not_replan,
        "replan": replan,
        "conditional_replan": conditional_replan,
    }


def choose_fuzzy_decision(rule_strengths: dict[str, float]) -> str:
    do_not_replan = as_number(rule_strengths.get("do_not_replan"))
    replan = as_number(rule_strengths.get("replan"))
    conditional_replan = as_number(rule_strengths.get("conditional_replan"))

    strongest = max(do_not_replan, replan, conditional_replan)

    if strongest < 0.25:
        return "UNCERTAIN_KEEP_CURRENT_PLAN"

    if conditional_replan >= replan and conditional_replan >= do_not_replan:
        return "CONDITIONAL_REPLAN"

    if replan >= do_not_replan:
        return "REPLAN"

    return "DO_NOT_REPLAN"


def build_features(
    no_replanning_option: dict[str, Any],
    greedy_replanning_option: dict[str, Any],
) -> dict[str, float]:
    baseline_delta_objective = as_number(no_replanning_option.get("mean_delta_objective_value"))
    baseline_delta_makespan = as_number(no_replanning_option.get("mean_delta_makespan"))
    baseline_delta_travel = as_number(no_replanning_option.get("mean_delta_total_travel_time"))

    greedy_delta_objective = as_number(greedy_replanning_option.get("mean_delta_objective_value"))
    greedy_delta_makespan = as_number(greedy_replanning_option.get("mean_delta_makespan"))
    greedy_delta_travel = as_number(greedy_replanning_option.get("mean_delta_total_travel_time"))

    no_replanning_impact_score = (
        max(0.0, baseline_delta_objective)
        + 0.5 * max(0.0, baseline_delta_makespan)
        + 0.25 * max(0.0, baseline_delta_travel)
    )

    objective_gain_if_replan = baseline_delta_objective - greedy_delta_objective
    travel_gain_if_replan = baseline_delta_travel - greedy_delta_travel
    makespan_risk_if_replan = max(0.0, greedy_delta_makespan - baseline_delta_makespan)

    return {
        "baseline_delta_objective": baseline_delta_objective,
        "baseline_delta_makespan": baseline_delta_makespan,
        "baseline_delta_travel": baseline_delta_travel,
        "greedy_delta_objective": greedy_delta_objective,
        "greedy_delta_makespan": greedy_delta_makespan,
        "greedy_delta_travel": greedy_delta_travel,
        "no_replanning_impact_score": no_replanning_impact_score,
        "objective_gain_if_replan": objective_gain_if_replan,
        "travel_gain_if_replan": travel_gain_if_replan,
        "makespan_risk_if_replan": makespan_risk_if_replan,
    }


def build_decision_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    options = build_option_rows(data)
    by_scenario = group_options_by_scenario(options)
    rows: list[dict[str, Any]] = []

    for scenario_id in sorted(by_scenario.keys()):
        scenario_options = by_scenario[scenario_id]

        no_replanning_option = select_no_replanning_option(scenario_options)
        greedy_replanning_option = select_greedy_replanning_option(scenario_options)

        if no_replanning_option is None or greedy_replanning_option is None:
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "status": "missing_comparison_option",
                    "decision": "UNAVAILABLE",
                }
            )
            continue

        features = build_features(no_replanning_option, greedy_replanning_option)
        memberships = build_fuzzy_memberships(features)
        rule_strengths = calculate_rule_strengths(memberships)
        decision = choose_fuzzy_decision(rule_strengths)

        row = {
            "scenario_id": scenario_id,
            "status": "ok",
            "no_replanning_option_id": as_text(no_replanning_option.get("option_id")),
            "greedy_replanning_option_id": as_text(greedy_replanning_option.get("option_id")),
            "decision": decision,
            "features": features,
            "memberships": memberships,
            "rule_strengths": rule_strengths,
        }

        rows.append(row)

    return rows


def strongest_label(membership: dict[str, float]) -> str:
    if not membership:
        return "unknown"

    return max(membership.keys(), key=lambda key: membership[key])


def build_decision_table(rows: list[dict[str, Any]]) -> list[str]:
    table_rows: list[list[Any]] = []

    for row in rows:
        features = row.get("features")
        memberships = row.get("memberships")
        rule_strengths = row.get("rule_strengths")

        if not isinstance(features, dict) or not isinstance(memberships, dict) or not isinstance(rule_strengths, dict):
            table_rows.append(
                [
                    as_text(row.get("scenario_id")),
                    as_text(row.get("decision")),
                    "unavailable",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            continue

        impact_membership = memberships.get("no_replanning_impact")
        gain_membership = memberships.get("objective_gain_if_replan")
        risk_membership = memberships.get("makespan_risk_if_replan")

        if not isinstance(impact_membership, dict):
            impact_membership = {}

        if not isinstance(gain_membership, dict):
            gain_membership = {}

        if not isinstance(risk_membership, dict):
            risk_membership = {}

        table_rows.append(
            [
                as_text(row.get("scenario_id")),
                as_text(row.get("decision")),
                strongest_label(impact_membership),
                strongest_label(gain_membership),
                strongest_label(risk_membership),
                format_number(features.get("objective_gain_if_replan")),
                format_number(features.get("makespan_risk_if_replan")),
                format_number(rule_strengths.get("do_not_replan")),
                format_number(rule_strengths.get("replan")),
                format_number(rule_strengths.get("conditional_replan")),
            ]
        )

    return markdown_table(
        [
            "Scenario",
            "Fuzzy decision",
            "Impact label",
            "Gain label",
            "Risk label",
            "Objective gain",
            "Makespan risk",
            "Do not replan strength",
            "Replan strength",
            "Conditional strength",
        ],
        table_rows,
    )


def build_detail_sections(rows: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []

    for row in rows:
        scenario_id = as_text(row.get("scenario_id"))
        lines.append(f"### {scenario_id}")
        lines.append("")

        features = row.get("features")
        memberships = row.get("memberships")
        rule_strengths = row.get("rule_strengths")

        if not isinstance(features, dict) or not isinstance(memberships, dict) or not isinstance(rule_strengths, dict):
            lines.append("This scenario could not be evaluated because a comparison option is missing.")
            lines.append("")
            continue

        feature_rows = [
            ["baseline_delta_objective", format_number(features.get("baseline_delta_objective"))],
            ["baseline_delta_makespan", format_number(features.get("baseline_delta_makespan"))],
            ["baseline_delta_travel", format_number(features.get("baseline_delta_travel"))],
            ["greedy_delta_objective", format_number(features.get("greedy_delta_objective"))],
            ["greedy_delta_makespan", format_number(features.get("greedy_delta_makespan"))],
            ["greedy_delta_travel", format_number(features.get("greedy_delta_travel"))],
            ["no_replanning_impact_score", format_number(features.get("no_replanning_impact_score"))],
            ["objective_gain_if_replan", format_number(features.get("objective_gain_if_replan"))],
            ["travel_gain_if_replan", format_number(features.get("travel_gain_if_replan"))],
            ["makespan_risk_if_replan", format_number(features.get("makespan_risk_if_replan"))],
        ]

        lines.extend(markdown_table(["Feature", "Value"], feature_rows))
        lines.append("")

        membership_rows: list[list[Any]] = []

        for group_name, group_value in memberships.items():
            if not isinstance(group_value, dict):
                continue

            membership_rows.append(
                [
                    group_name,
                    format_number(group_value.get("low")),
                    format_number(group_value.get("medium")),
                    format_number(group_value.get("high")),
                    strongest_label(group_value),
                ]
            )

        lines.extend(markdown_table(["Membership group", "Low", "Medium", "High", "Strongest label"], membership_rows))
        lines.append("")

        rule_rows = [
            ["do_not_replan", format_number(rule_strengths.get("do_not_replan"))],
            ["replan", format_number(rule_strengths.get("replan"))],
            ["conditional_replan", format_number(rule_strengths.get("conditional_replan"))],
        ]

        lines.extend(markdown_table(["Rule", "Strength"], rule_rows))
        lines.append("")
        lines.append(f"Decision: `{as_text(row.get('decision'))}`")
        lines.append("")

    return lines


def build_interpretation(rows: list[dict[str, Any]]) -> list[str]:
    decision_counts: dict[str, int] = {}

    for row in rows:
        decision = as_text(row.get("decision"), "UNKNOWN")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    lines: list[str] = []

    for decision in sorted(decision_counts.keys()):
        lines.append(f"- {decision}: {decision_counts[decision]} scenario(s).")

    lines.append(
        "- This is a fuzzy decision prototype, not the final fuzzy controller. "
        "It is useful for checking whether the current experimental outputs can be translated into linguistic decision rules."
    )
    lines.append(
        "- The rules are intentionally conservative. A scenario with good objective gain but meaningful makespan risk may become CONDITIONAL_REPLAN instead of a simple REPLAN."
    )
    lines.append(
        "- The next scientific step is to calibrate these membership functions and rule weights using broader experiments, not only this handcrafted sample batch."
    )

    return lines


def generate_report(data: dict[str, Any]) -> str:
    batch = get_dict(data, "batch")
    batch_id = as_text(batch.get("batch_id"), "unknown_batch")
    batch_name = as_text(batch.get("name"), "unknown_batch_name")

    rows = build_decision_rows(data)

    lines: list[str] = []

    lines.append("# FieldOps Lab fuzzy decision prototype report")
    lines.append("")
    lines.append(f"Batch ID: `{batch_id}`")
    lines.append("")
    lines.append(f"Batch name: {batch_name}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This report converts batch results into fuzzy-style linguistic variables and preliminary decision rules. "
        "It is an analysis prototype, not the final fuzzy decision module."
    )
    lines.append("")
    lines.append("## Fuzzy inputs")
    lines.append("")
    lines.append("- no_replanning_impact_score: estimated operational damage when the current plan is kept.")
    lines.append("- objective_gain_if_replan: objective improvement obtained by using the greedy replanning option instead of the no-replanning baseline.")
    lines.append("- travel_gain_if_replan: travel-time improvement obtained by using the greedy replanning option.")
    lines.append("- makespan_risk_if_replan: additional makespan caused by using the greedy replanning option.")
    lines.append("")
    lines.append("## Decision summary")
    lines.append("")
    lines.extend(build_decision_table(rows))
    lines.append("")
    lines.append("## Scenario details")
    lines.append("")
    lines.extend(build_detail_sections(rows))
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.extend(build_interpretation(rows))

    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: py -3 generate_fuzzy_decision_report.py <input_result_json> <output_report_md>",
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

    print(f"Fuzzy decision prototype report written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())