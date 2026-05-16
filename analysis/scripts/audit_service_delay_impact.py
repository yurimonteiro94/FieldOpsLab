from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SEVERITIES = ("light", "moderate", "severe")


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


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


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def discover_result_files(result_dir: Path) -> list[Path]:
    if not result_dir.exists():
        raise RuntimeError(f"Result directory does not exist: {result_dir}")

    if not result_dir.is_dir():
        raise RuntimeError(f"Result path is not a directory: {result_dir}")

    paths = sorted(result_dir.glob("*_result.json"))

    if not paths:
        raise RuntimeError(f"No campaign batch result JSON files found in: {result_dir}")

    return paths


def parse_family_and_severity(batch_id: str) -> tuple[str, str]:
    normalized = batch_id

    if normalized.startswith("campaign_"):
        normalized = normalized[len("campaign_") :]

    if normalized.endswith("_batch"):
        normalized = normalized[: -len("_batch")]

    for severity in SEVERITIES:
        suffix = f"_{severity}"

        if normalized.endswith(suffix):
            family = normalized[: -len(suffix)]
            return family, severity

    return normalized, ""


def safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def metric(experiment: dict[str, Any], key: str) -> float:
    metrics = safe_dict(experiment.get("metrics"))

    value = metrics.get(key, 0)

    if isinstance(value, (int, float)):
        return float(value)

    return 0.0


def mean(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def option_key(experiment: dict[str, Any]) -> str:
    policy = safe_dict(experiment.get("policy"))
    replanning_result = safe_dict(experiment.get("replanning_result"))

    policy_id = str(policy.get("policy_id", ""))
    method_id = str(replanning_result.get("method_id", ""))

    if policy_id == "no_replanning_policy_v1":
        return "no_replanning_baseline"

    if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "greedy_replanning_solver_v1":
        return "threshold_with_greedy_replanning"

    if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "replanning_not_implemented_v1":
        return "threshold_without_solver"

    return f"{policy_id}+{method_id}"


def summarize_option(experiments: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "delta_objective_value",
        "delta_makespan",
        "delta_total_travel_time",
        "delta_total_service_time",
        "delta_total_waiting_time",
        "delta_total_lateness",
        "delta_late_task_count",
        "effect_count",
        "executed_objective_value",
        "executed_makespan",
        "executed_total_travel_time",
        "executed_total_service_time",
        "executed_total_waiting_time",
        "executed_total_lateness",
    ]

    row: dict[str, Any] = {
        "experiment_count": len(experiments),
    }

    for key in keys:
        row[f"mean_{key}"] = mean([metric(experiment, key) for experiment in experiments])

    row["policy_should_replan_count"] = sum(
        1
        for experiment in experiments
        if bool(safe_dict(experiment.get("policy")).get("should_replan", False))
    )

    row["replanning_success_count"] = sum(
        1
        for experiment in experiments
        if bool(safe_dict(experiment.get("replanning_result")).get("is_successful", False))
    )

    row["replanning_applied_count"] = sum(
        1
        for experiment in experiments
        if bool(safe_dict(experiment.get("replanning_result")).get("was_applied_to_execution", False))
    )

    return row


def group_options(experiments: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for experiment in experiments:
        grouped.setdefault(option_key(experiment), []).append(experiment)

    return {
        key: summarize_option(items)
        for key, items in sorted(grouped.items())
    }


def get_first_recommendation(result: dict[str, Any]) -> dict[str, Any]:
    recommendations = safe_dict(result.get("recommendations"))
    rows = safe_list(recommendations.get("rows"))

    for row in rows:
        if isinstance(row, dict):
            return row

    return {}


def classify_service_effect(
    family: str,
    baseline: dict[str, Any],
    recommendation: dict[str, Any],
) -> tuple[str, list[str]]:
    warnings: list[str] = []

    service_delta = float(baseline.get("mean_delta_total_service_time", 0.0))
    objective_delta = float(baseline.get("mean_delta_objective_value", 0.0))
    makespan_delta = float(baseline.get("mean_delta_makespan", 0.0))
    lateness_delta = float(baseline.get("mean_delta_total_lateness", 0.0))

    recommended_policy = str(recommendation.get("recommended_policy_id", ""))

    service_related = family in ("service_delay_only", "combined_delay")

    if not service_related:
        return "not_service_related", warnings

    if service_delta <= 0:
        warnings.append("Service-related family has no visible service-time delta.")
        return "service_delay_not_visible", warnings

    if objective_delta == 0 and makespan_delta == 0 and lateness_delta == 0:
        warnings.append(
            "Service delay is visible in service time, but neutral in objective, makespan, and lateness under current metrics."
        )

        if recommended_policy == "no_replanning_policy_v1":
            return "visible_but_neutral_and_kept_plan", warnings

        return "visible_but_neutral", warnings

    if recommended_policy == "no_replanning_policy_v1":
        warnings.append(
            "Service delay affects operational metrics, but the final recommendation still keeps the current plan."
        )
        return "visible_with_metric_effect_but_kept_plan", warnings

    return "visible_with_metric_effect", warnings


def build_row(result_path: Path, result: dict[str, Any]) -> dict[str, Any]:
    batch = safe_dict(result.get("batch"))
    batch_id = str(batch.get("batch_id", result_path.stem.replace("_result", "")))
    family, severity = parse_family_and_severity(batch_id)

    experiments = [
        item
        for item in safe_list(result.get("experiments"))
        if isinstance(item, dict)
    ]

    options = group_options(experiments)

    baseline = options.get("no_replanning_baseline", {})
    greedy = options.get("threshold_with_greedy_replanning", {})
    recommendation = get_first_recommendation(result)

    service_effect_class, warnings = classify_service_effect(family, baseline, recommendation)

    row = {
        "batch_id": batch_id,
        "family": family,
        "severity": severity,
        "result_path": str(result_path),
        "completed_experiment_count": int(batch.get("completed_experiment_count", 0)),
        "is_complete": bool(batch.get("is_complete", False)),
        "option_count": len(options),
        "recommended_policy_id": str(recommendation.get("recommended_policy_id", "")),
        "recommended_method_id": str(recommendation.get("recommended_replanning_method_id", "")),
        "has_clear_winner": bool(recommendation.get("has_clear_winner", False)),
        "baseline_delta_objective": float(baseline.get("mean_delta_objective_value", 0.0)),
        "baseline_delta_makespan": float(baseline.get("mean_delta_makespan", 0.0)),
        "baseline_delta_travel": float(baseline.get("mean_delta_total_travel_time", 0.0)),
        "baseline_delta_service": float(baseline.get("mean_delta_total_service_time", 0.0)),
        "baseline_delta_waiting": float(baseline.get("mean_delta_total_waiting_time", 0.0)),
        "baseline_delta_lateness": float(baseline.get("mean_delta_total_lateness", 0.0)),
        "greedy_delta_objective": float(greedy.get("mean_delta_objective_value", 0.0)),
        "greedy_delta_makespan": float(greedy.get("mean_delta_makespan", 0.0)),
        "greedy_delta_travel": float(greedy.get("mean_delta_total_travel_time", 0.0)),
        "greedy_delta_service": float(greedy.get("mean_delta_total_service_time", 0.0)),
        "greedy_delta_waiting": float(greedy.get("mean_delta_total_waiting_time", 0.0)),
        "greedy_delta_lateness": float(greedy.get("mean_delta_total_lateness", 0.0)),
        "service_effect_class": service_effect_class,
        "warning_count": len(warnings),
        "warnings": "; ".join(warnings),
    }

    return row


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    service_related = [
        row
        for row in rows
        if row["family"] in ("service_delay_only", "combined_delay")
    ]

    visible_but_neutral = [
        row
        for row in rows
        if row["service_effect_class"] == "visible_but_neutral_and_kept_plan"
    ]

    warning_count = sum(int(row["warning_count"]) for row in rows)

    return {
        "batch_count": len(rows),
        "service_related_batch_count": len(service_related),
        "service_only_batch_count": sum(1 for row in rows if row["family"] == "service_delay_only"),
        "combined_delay_batch_count": sum(1 for row in rows if row["family"] == "combined_delay"),
        "visible_but_neutral_and_kept_plan_count": len(visible_but_neutral),
        "warning_count": warning_count,
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "scientific_status": "service_delay_impact_diagnostic_only",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "family",
        "severity",
        "completed_experiment_count",
        "is_complete",
        "option_count",
        "recommended_policy_id",
        "recommended_method_id",
        "has_clear_winner",
        "baseline_delta_objective",
        "baseline_delta_makespan",
        "baseline_delta_travel",
        "baseline_delta_service",
        "baseline_delta_waiting",
        "baseline_delta_lateness",
        "greedy_delta_objective",
        "greedy_delta_makespan",
        "greedy_delta_travel",
        "greedy_delta_service",
        "greedy_delta_waiting",
        "greedy_delta_lateness",
        "service_effect_class",
        "warning_count",
        "warnings",
        "result_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab service delay impact audit")
    lines.append("")
    lines.append("This report audits whether service-delay scenarios visibly affect the executed campaign metrics and final recommendations.")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")

    for key, value in summary.items():
        lines.append(f"| {key} | {format_number(value)} |")

    lines.append("")

    lines.append("## Batch diagnostics")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Recommended policy | Clear winner | Baseline service | Baseline objective | Baseline makespan | Greedy service | Greedy objective | Greedy makespan | Service effect class | Warnings |"
    )
    lines.append("| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['family']} | "
            f"{row['severity']} | "
            f"{row['recommended_policy_id']} | "
            f"{yes_no(row['has_clear_winner'])} | "
            f"{format_number(row['baseline_delta_service'])} | "
            f"{format_number(row['baseline_delta_objective'])} | "
            f"{format_number(row['baseline_delta_makespan'])} | "
            f"{format_number(row['greedy_delta_service'])} | "
            f"{format_number(row['greedy_delta_objective'])} | "
            f"{format_number(row['greedy_delta_makespan'])} | "
            f"{row['service_effect_class']} | "
            f"{format_number(row['warning_count'])} |"
        )

    lines.append("")

    warnings = [row for row in rows if int(row["warning_count"]) > 0]

    lines.append("## Warnings")
    lines.append("")

    if warnings:
        for row in warnings:
            lines.append(f"- {row['batch_id']}: {row['warnings']}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This audit does not prove that the service-delay model is wrong. It checks whether service delays are visible in the current metrics and whether the current ranking reacts to them."
    )
    lines.append("")
    lines.append(
        "If service delays increase service time but do not affect objective, makespan, lateness, or recommendations, then the next modeling question is whether the objective function should penalize service-time disruptions or whether the current behavior is operationally acceptable."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\audit_service_delay_impact.py "
            "<campaign_result_dir> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    result_dir = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        result_paths = discover_result_files(result_dir)

        rows = [
            build_row(path, load_json(path))
            for path in result_paths
        ]

        rows.sort(key=lambda row: (str(row["family"]), str(row["severity"]), str(row["batch_id"])))

        summary = build_summary(rows)

        payload = {
            "report_type": "fieldops_lab_service_delay_impact_audit",
            "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
            "summary": summary,
            "rows": rows,
            "interpretation": {
                "status": "diagnostic_only",
                "warning": "This audit checks metric behavior. It does not prove final scientific validity.",
            },
        }

        write_markdown(output_md, summary, rows)
        write_json(output_json, payload)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Service delay impact audit markdown written to: {output_md}")
    print(f"Service delay impact audit JSON written to: {output_json}")
    print(f"Service delay impact audit CSV written to: {output_csv}")
    print(f"Audited batches: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())