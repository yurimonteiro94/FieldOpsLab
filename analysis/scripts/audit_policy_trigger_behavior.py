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


def safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def discover_result_files(result_dir: Path) -> list[Path]:
    if not result_dir.exists():
        raise RuntimeError(f"Result directory does not exist: {result_dir}")

    if not result_dir.is_dir():
        raise RuntimeError(f"Result path is not a directory: {result_dir}")

    paths = sorted(result_dir.glob("*_result.json"))

    if not paths:
        raise RuntimeError(f"No campaign result files found in: {result_dir}")

    return paths


def parse_family_and_severity(batch_id: str) -> tuple[str, str]:
    value = batch_id

    if value.startswith("campaign_"):
        value = value[len("campaign_") :]

    if value.endswith("_batch"):
        value = value[: -len("_batch")]

    for severity in SEVERITIES:
        suffix = f"_{severity}"

        if value.endswith(suffix):
            return value[: -len(suffix)], severity

    return value, ""


def metric(experiment: dict[str, Any], key: str) -> float:
    metrics = safe_dict(experiment.get("metrics"))
    value = metrics.get(key, 0)

    if isinstance(value, (int, float)):
        return float(value)

    return 0.0


def option_label(experiment: dict[str, Any]) -> str:
    policy = safe_dict(experiment.get("policy"))
    replanning = safe_dict(experiment.get("replanning_result"))

    policy_id = str(policy.get("policy_id", ""))
    method_id = str(replanning.get("method_id", ""))

    if policy_id == "no_replanning_policy_v1":
        return "no_replanning_baseline"

    if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "replanning_not_implemented_v1":
        return "threshold_without_solver"

    if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "greedy_replanning_solver_v1":
        return "threshold_with_greedy_replanning"

    return f"{policy_id}+{method_id}"


def summarize_group(experiments: list[dict[str, Any]]) -> dict[str, Any]:
    if not experiments:
        return {
            "experiment_count": 0,
            "policy_should_replan_count": 0,
            "replanning_request_count": 0,
            "replanning_success_count": 0,
            "replanning_applied_count": 0,
            "mean_delta_objective": 0.0,
            "mean_delta_makespan": 0.0,
            "mean_delta_travel": 0.0,
            "mean_delta_service": 0.0,
            "mean_delta_lateness": 0.0,
        }

    count = len(experiments)

    return {
        "experiment_count": count,
        "policy_should_replan_count": sum(
            1
            for experiment in experiments
            if bool(safe_dict(experiment.get("policy")).get("should_replan", False))
        ),
        "replanning_request_count": sum(
            1
            for experiment in experiments
            if bool(safe_dict(experiment.get("replanning_request")).get("has_replanning_request", False))
        ),
        "replanning_success_count": sum(
            1
            for experiment in experiments
            if bool(safe_dict(experiment.get("replanning_result")).get("is_successful", False))
        ),
        "replanning_applied_count": sum(
            1
            for experiment in experiments
            if bool(safe_dict(experiment.get("replanning_result")).get("was_applied_to_execution", False))
        ),
        "mean_delta_objective": sum(metric(experiment, "delta_objective_value") for experiment in experiments) / count,
        "mean_delta_makespan": sum(metric(experiment, "delta_makespan") for experiment in experiments) / count,
        "mean_delta_travel": sum(metric(experiment, "delta_total_travel_time") for experiment in experiments) / count,
        "mean_delta_service": sum(metric(experiment, "delta_total_service_time") for experiment in experiments) / count,
        "mean_delta_lateness": sum(metric(experiment, "delta_total_lateness") for experiment in experiments) / count,
    }


def classify_trigger_behavior(
    family: str,
    severity: str,
    option: str,
    summary: dict[str, Any],
) -> tuple[str, list[str]]:
    warnings: list[str] = []

    should_count = int(summary["policy_should_replan_count"])
    experiment_count = int(summary["experiment_count"])
    service_delta = float(summary["mean_delta_service"])
    travel_delta = float(summary["mean_delta_travel"])

    if option == "no_replanning_baseline":
        return "baseline_policy", warnings

    if option not in ("threshold_without_solver", "threshold_with_greedy_replanning"):
        return "unknown_policy_option", warnings

    if experiment_count == 0:
        return "missing_option", ["Policy option has no experiments."]

    if family == "service_delay_only" and severity in ("moderate", "severe"):
        if service_delta > 0 and should_count == 0:
            warnings.append(
                "Threshold policy did not request replanning for a moderate/severe service-only delay."
            )
            return "service_delay_not_triggering_threshold", warnings

    if family == "combined_delay" and severity in ("moderate", "severe"):
        if travel_delta > 0 and should_count > 0:
            return "combined_delay_triggers_threshold", warnings

        warnings.append(
            "Combined delay did not trigger replanning despite moderate/severe disruption."
        )
        return "combined_delay_not_triggering_threshold", warnings

    if family in ("travel_delay_only", "reassignment_opportunity") and severity in ("moderate", "severe"):
        if travel_delta > 0 and should_count > 0:
            return "travel_delay_triggers_threshold", warnings

        warnings.append(
            "Travel-related moderate/severe delay did not trigger replanning."
        )
        return "travel_delay_not_triggering_threshold", warnings

    if should_count == 0:
        return "no_trigger", warnings

    return "triggered", warnings


def build_rows(result_path: Path, result: dict[str, Any]) -> list[dict[str, Any]]:
    batch = safe_dict(result.get("batch"))
    batch_id = str(batch.get("batch_id", result_path.stem.replace("_result", "")))
    family, severity = parse_family_and_severity(batch_id)

    experiments = [
        item
        for item in safe_list(result.get("experiments"))
        if isinstance(item, dict)
    ]

    grouped: dict[str, list[dict[str, Any]]] = {}

    for experiment in experiments:
        grouped.setdefault(option_label(experiment), []).append(experiment)

    rows: list[dict[str, Any]] = []

    for option in sorted(grouped.keys()):
        summary = summarize_group(grouped[option])
        trigger_class, warnings = classify_trigger_behavior(family, severity, option, summary)

        row = {
            "batch_id": batch_id,
            "family": family,
            "severity": severity,
            "option": option,
            "experiment_count": summary["experiment_count"],
            "policy_should_replan_count": summary["policy_should_replan_count"],
            "replanning_request_count": summary["replanning_request_count"],
            "replanning_success_count": summary["replanning_success_count"],
            "replanning_applied_count": summary["replanning_applied_count"],
            "mean_delta_objective": summary["mean_delta_objective"],
            "mean_delta_makespan": summary["mean_delta_makespan"],
            "mean_delta_travel": summary["mean_delta_travel"],
            "mean_delta_service": summary["mean_delta_service"],
            "mean_delta_lateness": summary["mean_delta_lateness"],
            "trigger_behavior_class": trigger_class,
            "warning_count": len(warnings),
            "warnings": "; ".join(warnings),
            "result_path": str(result_path),
        }

        rows.append(row)

    return rows


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    threshold_rows = [
        row
        for row in rows
        if row["option"] in ("threshold_without_solver", "threshold_with_greedy_replanning")
    ]

    service_not_triggering = [
        row
        for row in rows
        if row["trigger_behavior_class"] == "service_delay_not_triggering_threshold"
    ]

    triggered_rows = [
        row
        for row in threshold_rows
        if int(row["policy_should_replan_count"]) > 0
    ]

    warning_count = sum(int(row["warning_count"]) for row in rows)

    return {
        "row_count": len(rows),
        "threshold_row_count": len(threshold_rows),
        "triggered_threshold_row_count": len(triggered_rows),
        "service_delay_not_triggering_threshold_count": len(service_not_triggering),
        "warning_count": warning_count,
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "scientific_status": "policy_trigger_behavior_diagnostic_only",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "family",
        "severity",
        "option",
        "experiment_count",
        "policy_should_replan_count",
        "replanning_request_count",
        "replanning_success_count",
        "replanning_applied_count",
        "mean_delta_objective",
        "mean_delta_makespan",
        "mean_delta_travel",
        "mean_delta_service",
        "mean_delta_lateness",
        "trigger_behavior_class",
        "warning_count",
        "warnings",
        "result_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab policy trigger behavior audit")
    lines.append("")
    lines.append("This report checks whether each policy option actually requests replanning under each campaign scenario.")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")

    for key, value in summary.items():
        lines.append(f"| {key} | {format_number(value)} |")

    lines.append("")

    lines.append("## Trigger behavior by option")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Option | Experiments | Should replan | Requests | Applied | Travel delta | Service delta | Trigger class | Warnings |"
    )
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['family']} | "
            f"{row['severity']} | "
            f"{row['option']} | "
            f"{format_number(row['experiment_count'])} | "
            f"{format_number(row['policy_should_replan_count'])} | "
            f"{format_number(row['replanning_request_count'])} | "
            f"{format_number(row['replanning_applied_count'])} | "
            f"{format_number(row['mean_delta_travel'])} | "
            f"{format_number(row['mean_delta_service'])} | "
            f"{row['trigger_behavior_class']} | "
            f"{format_number(row['warning_count'])} |"
        )

    lines.append("")

    warnings = [row for row in rows if int(row["warning_count"]) > 0]

    lines.append("## Warnings")
    lines.append("")

    if warnings:
        for row in warnings:
            lines.append(f"- {row['batch_id']} / {row['option']}: {row['warnings']}")
    else:
        lines.append("- None.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "If travel-related delays trigger replanning but service-only delays do not, then the current threshold policy is primarily travel-delay-driven."
    )
    lines.append("")
    lines.append(
        "That may be acceptable as a first policy, but it should be explicitly documented. If service delays are operationally relevant, the policy should later include service-delay thresholds or downstream schedule impact."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\audit_policy_trigger_behavior.py "
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

        rows: list[dict[str, Any]] = []

        for result_path in result_paths:
            rows.extend(build_rows(result_path, load_json(result_path)))

        rows.sort(
            key=lambda row: (
                str(row["family"]),
                str(row["severity"]),
                str(row["batch_id"]),
                str(row["option"]),
            )
        )

        summary = build_summary(rows)

        payload = {
            "report_type": "fieldops_lab_policy_trigger_behavior_audit",
            "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
            "summary": summary,
            "rows": rows,
            "interpretation": {
                "status": "diagnostic_only",
                "warning": "This audit checks policy-trigger behavior. It does not prove final scientific validity.",
            },
        }

        write_markdown(output_md, summary, rows)
        write_json(output_json, payload)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Policy trigger behavior audit markdown written to: {output_md}")
    print(f"Policy trigger behavior audit JSON written to: {output_json}")
    print(f"Policy trigger behavior audit CSV written to: {output_csv}")
    print(f"Audited rows: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())