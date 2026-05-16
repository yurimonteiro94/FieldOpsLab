from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


FAMILY_IDS = [
    "travel_delay_only",
    "service_delay_only",
    "combined_delay",
    "reassignment_opportunity",
]

SEVERITY_IDS = [
    "light",
    "moderate",
    "severe",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")


def format_number(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))

        return f"{value:.4f}".rstrip("0").rstrip(".")

    if value is None:
        return ""

    return str(value)


def parse_batch_identity(batch_id: str) -> tuple[str, str]:
    for family_id in FAMILY_IDS:
        prefix = f"campaign_{family_id}_"

        if not batch_id.startswith(prefix):
            continue

        rest = batch_id[len(prefix):]

        for severity_id in SEVERITY_IDS:
            if rest == f"{severity_id}_batch":
                return family_id, severity_id

    return "unknown", "unknown"


def result_paths_from_execution_index(execution_index: dict[str, Any]) -> list[Path]:
    rows = execution_index.get("rows", [])

    if not isinstance(rows, list):
        raise RuntimeError("Execution index rows must be a list.")

    paths: list[Path] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        path_text = str(row.get("result_json_output_path", ""))

        if path_text:
            paths.append(Path(path_text))

    if not paths:
        raise RuntimeError("No result JSON paths found in campaign execution index.")

    return paths


def mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def metric(experiment: dict[str, Any], key: str) -> float:
    metrics = experiment.get("metrics", {})

    if not isinstance(metrics, dict):
        return 0.0

    value = metrics.get(key, 0.0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def policy_value(experiment: dict[str, Any], key: str, default: Any = "") -> Any:
    policy = experiment.get("policy", {})

    if not isinstance(policy, dict):
        return default

    return policy.get(key, default)


def replanning_result_value(experiment: dict[str, Any], key: str, default: Any = "") -> Any:
    result = experiment.get("replanning_result", {})

    if not isinstance(result, dict):
        return default

    return result.get(key, default)


def group_experiments_by_option(experiments: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for experiment in experiments:
        if not isinstance(experiment, dict):
            continue

        policy_id = str(policy_value(experiment, "policy_id", ""))
        method_id = str(replanning_result_value(experiment, "method_id", ""))
        execution = experiment.get("execution", {})

        if isinstance(execution, dict):
            execution_mode = str(execution.get("execution_mode", ""))
        else:
            execution_mode = ""

        option_key = f"{policy_id} + {method_id} + {execution_mode}"
        grouped[option_key].append(experiment)

    return grouped


def summarize_experiment_group(experiments: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment_count": len(experiments),
        "mean_delta_objective_value": mean(
            [metric(experiment, "delta_objective_value") for experiment in experiments]
        ),
        "mean_delta_makespan": mean(
            [metric(experiment, "delta_makespan") for experiment in experiments]
        ),
        "mean_delta_total_travel_time": mean(
            [metric(experiment, "delta_total_travel_time") for experiment in experiments]
        ),
        "mean_delta_total_service_time": mean(
            [metric(experiment, "delta_total_service_time") for experiment in experiments]
        ),
        "mean_delta_total_waiting_time": mean(
            [metric(experiment, "delta_total_waiting_time") for experiment in experiments]
        ),
        "mean_effect_count": mean(
            [metric(experiment, "effect_count") for experiment in experiments]
        ),
        "policy_should_replan_count": sum(
            1 for experiment in experiments if bool(policy_value(experiment, "should_replan", False))
        ),
        "replanning_success_count": sum(
            1
            for experiment in experiments
            if bool(replanning_result_value(experiment, "is_successful", False))
        ),
        "replanning_applied_count": sum(
            1
            for experiment in experiments
            if bool(replanning_result_value(experiment, "was_applied_to_execution", False))
        ),
    }


def find_baseline_summary(option_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for option_key, summary in option_summaries.items():
        if option_key.startswith("no_replanning_policy_v1 +"):
            return summary

    return {}


def inspect_result(path: Path) -> dict[str, Any]:
    result = load_json(path)

    batch = result.get("batch", {})
    experiments = result.get("experiments", [])

    if not isinstance(batch, dict):
        batch = {}

    if not isinstance(experiments, list):
        experiments = []

    batch_id = str(batch.get("batch_id", path.stem))
    family_id, severity_id = parse_batch_identity(batch_id)

    typed_experiments = [item for item in experiments if isinstance(item, dict)]
    grouped = group_experiments_by_option(typed_experiments)

    option_summaries = {
        option_key: summarize_experiment_group(group)
        for option_key, group in sorted(grouped.items())
    }

    baseline = find_baseline_summary(option_summaries)

    problems: list[str] = []
    warnings: list[str] = []

    baseline_travel = float(baseline.get("mean_delta_total_travel_time", 0.0) or 0.0)
    baseline_service = float(baseline.get("mean_delta_total_service_time", 0.0) or 0.0)
    baseline_effect_count = float(baseline.get("mean_effect_count", 0.0) or 0.0)

    if family_id == "travel_delay_only":
        if baseline_travel <= 0:
            problems.append("Travel-delay-only batch has no positive baseline travel-time impact.")

        if baseline_service != 0:
            warnings.append("Travel-delay-only batch also changes service time.")

    elif family_id == "service_delay_only":
        if baseline_service <= 0:
            problems.append("Service-delay-only batch has no positive baseline service-time impact.")

        if baseline_travel != 0:
            warnings.append("Service-delay-only batch also changes travel time.")

    elif family_id == "combined_delay":
        if baseline_travel <= 0:
            problems.append("Combined-delay batch has no positive baseline travel-time impact.")

        if baseline_service <= 0:
            problems.append("Combined-delay batch has no positive baseline service-time impact.")

    elif family_id == "reassignment_opportunity":
        if baseline_travel <= 0:
            problems.append("Reassignment-opportunity batch has no positive baseline travel-time impact.")

    else:
        problems.append(f"Unknown campaign family inferred from batch_id: {batch_id}")

    if baseline_effect_count <= 0:
        problems.append("Baseline has zero applied effects.")

    return {
        "batch_id": batch_id,
        "scenario_family_id": family_id,
        "severity_id": severity_id,
        "result_json_path": str(path),
        "experiment_count": len(typed_experiments),
        "option_count": len(option_summaries),
        "baseline_mean_delta_objective_value": baseline.get("mean_delta_objective_value", 0.0),
        "baseline_mean_delta_makespan": baseline.get("mean_delta_makespan", 0.0),
        "baseline_mean_delta_total_travel_time": baseline_travel,
        "baseline_mean_delta_total_service_time": baseline_service,
        "baseline_mean_effect_count": baseline_effect_count,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "problems": problems,
        "warnings": warnings,
        "option_summaries": option_summaries,
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    for row in rows:
        batch_id = str(row["batch_id"])

        for problem in row["problems"]:
            problems.append(f"{batch_id}: {problem}")

        for warning in row["warnings"]:
            warnings.append(f"{batch_id}: {warning}")

    return {
        "report_type": "fieldops_lab_campaign_result_semantic_inspection",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "batch_count": len(rows),
        "semantic_problem_count": len(problems),
        "semantic_warning_count": len(warnings),
        "all_semantic_checks_passed": len(problems) == 0,
        "problems": problems,
        "warnings": warnings,
        "rows": rows,
        "interpretation": {
            "status": "semantic_diagnostic_only",
            "warning": (
                "This diagnostic checks whether campaign result patterns match the intended "
                "scenario families. It is stricter than structural validation."
            ),
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "experiment_count",
        "option_count",
        "baseline_mean_delta_objective_value",
        "baseline_mean_delta_makespan",
        "baseline_mean_delta_total_travel_time",
        "baseline_mean_delta_total_service_time",
        "baseline_mean_effect_count",
        "problem_count",
        "warning_count",
        "result_json_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign result semantic inspection")
    lines.append("")
    lines.append("This report checks whether executed campaign results match the intended scenario families.")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_semantic_checks_passed | {format_number(report['all_semantic_checks_passed'])} |")
    lines.append(f"| semantic_problem_count | {format_number(report['semantic_problem_count'])} |")
    lines.append(f"| semantic_warning_count | {format_number(report['semantic_warning_count'])} |")
    lines.append(f"| batch_count | {format_number(report['batch_count'])} |")
    lines.append("")
    lines.append("## Batch semantic checks")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Baseline travel delta | Baseline service delta | Baseline effect count | Problems | Warnings |"
    )
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")

    for row in report["rows"]:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{format_number(row['baseline_mean_delta_total_travel_time'])} | "
            f"{format_number(row['baseline_mean_delta_total_service_time'])} | "
            f"{format_number(row['baseline_mean_effect_count'])} | "
            f"{format_number(row['problem_count'])} | "
            f"{format_number(row['warning_count'])} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    if report["problems"]:
        for problem in report["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")

    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if report["all_semantic_checks_passed"]:
        lines.append(
            "The campaign results passed this semantic diagnostic. "
            "The executed perturbation families appear to produce the expected first-order metric effects."
        )
    else:
        lines.append(
            "The campaign results did not pass this semantic diagnostic. "
            "Do not use the campaign summary as evidence until these semantic problems are reviewed."
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\inspect_campaign_result_semantics.py "
            "<campaign_execution_index_json> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    execution_index_path = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        execution_index = load_json(execution_index_path)
        result_paths = result_paths_from_execution_index(execution_index)
        rows = [inspect_result(path) for path in result_paths]
        rows.sort(
            key=lambda row: (
                str(row["scenario_family_id"]),
                SEVERITY_IDS.index(str(row["severity_id"]))
                if str(row["severity_id"]) in SEVERITY_IDS
                else 999,
                str(row["batch_id"]),
            )
        )

        report = build_report(rows)

        write_markdown(output_md, report)
        write_json(output_json, report)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign result semantic inspection markdown written to: {output_md}")
    print(f"Campaign result semantic inspection JSON written to: {output_json}")
    print(f"Campaign result semantic inspection CSV written to: {output_csv}")

    if report["all_semantic_checks_passed"]:
        print("Campaign result semantic inspection passed.")
    else:
        print("WARNING: Campaign result semantic inspection found semantic issues.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())