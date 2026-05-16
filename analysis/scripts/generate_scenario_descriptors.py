import csv
import json
import sys
from pathlib import Path


def as_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def fmt(value):
    value = as_float(value)

    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))

    return f"{value:.2f}"


def markdown_escape(value):
    text = str(value)
    text = text.replace("|", "\\|")
    return text


def metric(experiment, key):
    return as_float(experiment.get("metrics", {}).get(key, 0.0))


def policy_id(experiment):
    return experiment.get("policy", {}).get("policy_id", "")


def replanning_method_id(experiment):
    return experiment.get("replanning_result", {}).get("method_id", "")


def execution_mode(experiment):
    return experiment.get("execution", {}).get("execution_mode", "")


def was_replanning_applied(experiment):
    return bool(experiment.get("replanning_result", {}).get("was_applied_to_execution", False))


def group_experiments_by_scenario(experiments):
    grouped = {}

    for experiment in experiments:
        scenario_id = experiment.get("scenario_id", "")

        if scenario_id not in grouped:
            grouped[scenario_id] = []

        grouped[scenario_id].append(experiment)

    return grouped


def find_no_replanning_baseline(experiments):
    for experiment in experiments:
        if policy_id(experiment) == "no_replanning_policy_v1":
            return experiment

    for experiment in experiments:
        if execution_mode(experiment) == "no_replanning_execution_baseline":
            return experiment

    return None


def find_applied_greedy_replanning(experiments):
    for experiment in experiments:
        if replanning_method_id(experiment) == "greedy_replanning_solver_v1" and was_replanning_applied(experiment):
            return experiment

    for experiment in experiments:
        if execution_mode(experiment) == "replanning_applied_execution":
            return experiment

    return None


def find_recommended_option(recommendations, scenario_id):
    for row in recommendations:
        if row.get("scenario_id", "") == scenario_id:
            return row

    return None


def positive(value):
    return max(0.0, as_float(value))


def classify_impact(score):
    if score < 10:
        return "negligible"

    if score < 40:
        return "low"

    if score < 90:
        return "medium"

    return "high"


def classify_gain(gain):
    if gain <= 0:
        return "none"

    if gain < 30:
        return "small"

    if gain < 80:
        return "medium"

    return "high"


def classify_risk(risk):
    if risk <= 0:
        return "none"

    if risk <= 10:
        return "low"

    if risk <= 30:
        return "medium"

    return "high"


def classify_tradeoff(gain, risk):
    if gain <= 0:
        return "no_replanning_gain"

    if risk <= 0:
        return "dominant_or_nearly_dominant_replanning"

    if risk <= 10:
        return "favorable_tradeoff"

    if risk <= 30:
        return "moderate_tradeoff"

    return "high_risk_tradeoff"


def classify_scenario_descriptor(impact_score, gain, risk):
    impact_class = classify_impact(impact_score)

    if gain <= 0 and impact_class in ("negligible", "low"):
        return "stable_low_disruption"

    if gain <= 0:
        return "baseline_preferred"

    if risk <= 5 and gain >= 30:
        return "reassignment_opportunity"

    if impact_class == "high" and risk <= 30:
        return "high_impact_controlled_tradeoff"

    if impact_class == "high":
        return "high_impact_high_risk_tradeoff"

    if risk <= 30:
        return "moderate_tradeoff"

    return "uncertain_high_risk_tradeoff"


def conservative_action(impact_score, gain, risk):
    impact_class = classify_impact(impact_score)

    if gain <= 0:
        return "keep_current_plan"

    if impact_class in ("negligible", "low") and risk > 10:
        return "keep_current_plan_or_require_manager_review"

    if risk <= 5 and gain >= 30:
        return "replan"

    if risk <= 30 and gain >= 80:
        return "replan_with_makespan_monitoring"

    if risk <= 30:
        return "compare_with_operational_priorities"

    return "require_manager_review"


def compute_no_replanning_impact_score(baseline):
    if baseline is None:
        return 0.0

    delta_objective = positive(metric(baseline, "delta_objective_value"))
    delta_makespan = positive(metric(baseline, "delta_makespan"))
    delta_travel = positive(metric(baseline, "delta_total_travel_time"))
    total_lateness = positive(metric(baseline, "executed_total_lateness"))
    late_tasks = positive(metric(baseline, "executed_late_task_count"))

    return (
        delta_objective
        + 0.50 * delta_makespan
        + 0.25 * delta_travel
        + 2.00 * total_lateness
        + 100.00 * late_tasks
    )


def build_descriptor_rows(data):
    experiments = data.get("experiments", [])
    recommendations = data.get("recommendations", {}).get("rows", [])
    grouped = group_experiments_by_scenario(experiments)

    rows = []

    for scenario_id in sorted(grouped.keys()):
        scenario_experiments = grouped[scenario_id]

        baseline = find_no_replanning_baseline(scenario_experiments)
        greedy = find_applied_greedy_replanning(scenario_experiments)
        recommendation = find_recommended_option(recommendations, scenario_id)

        baseline_delta_objective = metric(baseline, "delta_objective_value") if baseline else 0.0
        baseline_delta_makespan = metric(baseline, "delta_makespan") if baseline else 0.0
        baseline_delta_travel = metric(baseline, "delta_total_travel_time") if baseline else 0.0
        baseline_late_tasks = metric(baseline, "executed_late_task_count") if baseline else 0.0
        baseline_total_lateness = metric(baseline, "executed_total_lateness") if baseline else 0.0

        if greedy is not None:
            candidate_delta_objective = metric(greedy, "delta_objective_value")
            candidate_delta_makespan = metric(greedy, "delta_makespan")
            candidate_delta_travel = metric(greedy, "delta_total_travel_time")
            candidate_policy = policy_id(greedy)
            candidate_method = replanning_method_id(greedy)
            candidate_execution = execution_mode(greedy)
        elif recommendation is not None:
            candidate_delta_objective = as_float(recommendation.get("mean_delta_objective_value", 0.0))
            candidate_delta_makespan = as_float(recommendation.get("mean_delta_makespan", 0.0))
            candidate_delta_travel = as_float(recommendation.get("mean_delta_total_travel_time", 0.0))
            candidate_policy = recommendation.get("recommended_policy_id", "")
            candidate_method = recommendation.get("recommended_replanning_method_id", "")
            candidate_execution = recommendation.get("recommended_execution_mode", "")
        else:
            candidate_delta_objective = baseline_delta_objective
            candidate_delta_makespan = baseline_delta_makespan
            candidate_delta_travel = baseline_delta_travel
            candidate_policy = ""
            candidate_method = ""
            candidate_execution = ""

        impact_score = compute_no_replanning_impact_score(baseline)

        objective_gain = baseline_delta_objective - candidate_delta_objective
        travel_gain = baseline_delta_travel - candidate_delta_travel
        makespan_risk = max(0.0, candidate_delta_makespan - baseline_delta_makespan)

        impact_class = classify_impact(impact_score)
        gain_class = classify_gain(objective_gain)
        risk_class = classify_risk(makespan_risk)
        tradeoff_class = classify_tradeoff(objective_gain, makespan_risk)
        scenario_descriptor = classify_scenario_descriptor(impact_score, objective_gain, makespan_risk)
        action = conservative_action(impact_score, objective_gain, makespan_risk)

        row = {
            "scenario_id": scenario_id,
            "experiment_count": len(scenario_experiments),
            "baseline_delta_objective": baseline_delta_objective,
            "baseline_delta_makespan": baseline_delta_makespan,
            "baseline_delta_travel": baseline_delta_travel,
            "baseline_late_tasks": baseline_late_tasks,
            "baseline_total_lateness": baseline_total_lateness,
            "candidate_policy": candidate_policy,
            "candidate_method": candidate_method,
            "candidate_execution": candidate_execution,
            "candidate_delta_objective": candidate_delta_objective,
            "candidate_delta_makespan": candidate_delta_makespan,
            "candidate_delta_travel": candidate_delta_travel,
            "no_replanning_impact_score": impact_score,
            "objective_gain_if_candidate": objective_gain,
            "travel_gain_if_candidate": travel_gain,
            "makespan_risk_if_candidate": makespan_risk,
            "impact_class": impact_class,
            "gain_class": gain_class,
            "risk_class": risk_class,
            "tradeoff_class": tradeoff_class,
            "scenario_descriptor": scenario_descriptor,
            "conservative_action": action,
        }

        rows.append(row)

    return rows


def write_csv(rows, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "scenario_id",
        "experiment_count",
        "baseline_delta_objective",
        "baseline_delta_makespan",
        "baseline_delta_travel",
        "baseline_late_tasks",
        "baseline_total_lateness",
        "candidate_policy",
        "candidate_method",
        "candidate_execution",
        "candidate_delta_objective",
        "candidate_delta_makespan",
        "candidate_delta_travel",
        "no_replanning_impact_score",
        "objective_gain_if_candidate",
        "travel_gain_if_candidate",
        "makespan_risk_if_candidate",
        "impact_class",
        "gain_class",
        "risk_class",
        "tradeoff_class",
        "scenario_descriptor",
        "conservative_action",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def descriptor_counts(rows):
    counts = {}

    for row in rows:
        key = row["scenario_descriptor"]

        if key not in counts:
            counts[key] = 0

        counts[key] += 1

    return counts


def write_markdown(data, rows, output_path, csv_output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    batch = data.get("batch", {})
    ranking_config = data.get("rankings", {}).get("ranking_config", {})

    lines = []

    lines.append("# FieldOps Lab scenario descriptor report")
    lines.append("")
    lines.append(f"Batch ID: `{markdown_escape(batch.get('batch_id', ''))}`")
    lines.append("")
    lines.append(f"Batch name: {markdown_escape(batch.get('name', ''))}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This report creates scenario descriptors from the batch result. "
        "It does not use fuzzy rules. The goal is to describe the operational situation before choosing any final decision model."
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- The no-replanning baseline is used to estimate the operational impact of keeping the original plan.")
    lines.append("- The applied greedy replanning option is used as the current candidate when available.")
    lines.append("- The descriptor compares candidate gain against makespan risk.")
    lines.append("- The result is a conservative scenario classification, not a final scientific conclusion.")
    lines.append("")
    lines.append("## Batch overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| configured_experiment_count | {fmt(batch.get('configured_experiment_count', 0))} |")
    lines.append(f"| completed_experiment_count | {fmt(batch.get('completed_experiment_count', 0))} |")
    lines.append(f"| completion_percent | {fmt(batch.get('completion_percent', 0))} |")
    lines.append(f"| ranking_config_id | `{markdown_escape(ranking_config.get('ranking_config_id', ''))}` |")
    lines.append("")
    lines.append("## Descriptor summary")
    lines.append("")
    lines.append("| Descriptor | Count |")
    lines.append("| --- | --- |")

    for key, count in sorted(descriptor_counts(rows).items()):
        lines.append(f"| {markdown_escape(key)} | {count} |")

    lines.append("")
    lines.append("## Scenario descriptors")
    lines.append("")
    lines.append(
        "| Scenario | Impact score | Impact | Gain | Risk | Descriptor | Conservative action | "
        "Objective gain | Travel gain | Makespan risk | Candidate |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for row in rows:
        candidate = (
            f"{row['candidate_policy']} + "
            f"{row['candidate_method']} + "
            f"{row['candidate_execution']}"
        )

        lines.append(
            "| "
            f"{markdown_escape(row['scenario_id'])} | "
            f"{fmt(row['no_replanning_impact_score'])} | "
            f"{markdown_escape(row['impact_class'])} | "
            f"{markdown_escape(row['gain_class'])} | "
            f"{markdown_escape(row['risk_class'])} | "
            f"{markdown_escape(row['scenario_descriptor'])} | "
            f"{markdown_escape(row['conservative_action'])} | "
            f"{fmt(row['objective_gain_if_candidate'])} | "
            f"{fmt(row['travel_gain_if_candidate'])} | "
            f"{fmt(row['makespan_risk_if_candidate'])} | "
            f"{markdown_escape(candidate)} |"
        )

    lines.append("")
    lines.append("## Detailed values")
    lines.append("")

    for row in rows:
        lines.append(f"### {markdown_escape(row['scenario_id'])}")
        lines.append("")
        lines.append("| Feature | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| baseline_delta_objective | {fmt(row['baseline_delta_objective'])} |")
        lines.append(f"| baseline_delta_makespan | {fmt(row['baseline_delta_makespan'])} |")
        lines.append(f"| baseline_delta_travel | {fmt(row['baseline_delta_travel'])} |")
        lines.append(f"| candidate_delta_objective | {fmt(row['candidate_delta_objective'])} |")
        lines.append(f"| candidate_delta_makespan | {fmt(row['candidate_delta_makespan'])} |")
        lines.append(f"| candidate_delta_travel | {fmt(row['candidate_delta_travel'])} |")
        lines.append(f"| no_replanning_impact_score | {fmt(row['no_replanning_impact_score'])} |")
        lines.append(f"| objective_gain_if_candidate | {fmt(row['objective_gain_if_candidate'])} |")
        lines.append(f"| travel_gain_if_candidate | {fmt(row['travel_gain_if_candidate'])} |")
        lines.append(f"| makespan_risk_if_candidate | {fmt(row['makespan_risk_if_candidate'])} |")
        lines.append(f"| tradeoff_class | {markdown_escape(row['tradeoff_class'])} |")
        lines.append(f"| scenario_descriptor | {markdown_escape(row['scenario_descriptor'])} |")
        lines.append(f"| conservative_action | {markdown_escape(row['conservative_action'])} |")
        lines.append("")

    lines.append("## CSV output")
    lines.append("")
    lines.append(f"CSV file: `{markdown_escape(csv_output_path)}`")
    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This layer is intentionally independent from fuzzy logic. "
        "The descriptors can later feed a fuzzy controller, a weighted ranking, a statistical model, or a rule-based decision method."
    )
    lines.append("")
    lines.append(
        "At this stage, the safest scientific interpretation is that the project can already describe different operational situations, "
        "but the conclusions still need broader scenarios, more replications, and stronger validation."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: py -3 generate_scenario_descriptors.py "
            "<batch_result_json> <output_markdown> <output_csv>"
        )
        return 1

    input_json_path = Path(sys.argv[1])
    output_markdown_path = sys.argv[2]
    output_csv_path = sys.argv[3]

    if not input_json_path.exists():
        print(f"Input JSON not found: {input_json_path}")
        return 1

    with input_json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    rows = build_descriptor_rows(data)

    write_csv(rows, output_csv_path)
    write_markdown(data, rows, output_markdown_path, output_csv_path)

    print(f"Scenario descriptor report written to: {output_markdown_path}")
    print(f"Scenario descriptor CSV written to: {output_csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())