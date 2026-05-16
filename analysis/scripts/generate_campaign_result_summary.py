from __future__ import annotations

import csv
import json
import sys
from collections import Counter
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


def classify_recommendation(recommendation: dict[str, Any]) -> str:
    has_clear_winner = bool(recommendation.get("has_clear_winner", False))
    delta_objective = float(recommendation.get("mean_delta_objective_value", 0.0) or 0.0)
    delta_makespan = float(recommendation.get("mean_delta_makespan", 0.0) or 0.0)
    applied_count = int(recommendation.get("replanning_applied_count", 0) or 0)

    if not has_clear_winner:
        return "weak_or_tied"

    if delta_objective < 0 and delta_makespan <= 0 and applied_count > 0:
        return "strong_replanning_improvement"

    if delta_objective < 0 and delta_makespan > 0 and applied_count > 0:
        return "replanning_tradeoff"

    if applied_count == 0:
        return "keep_plan_or_no_replanning"

    if delta_objective >= 0 and applied_count > 0:
        return "replanning_not_beneficial"

    return "needs_review"


def build_result_rows(execution_index: dict[str, Any]) -> list[dict[str, Any]]:
    execution_rows = execution_index.get("rows", [])

    if not isinstance(execution_rows, list):
        raise RuntimeError("Execution index rows must be a list.")

    rows: list[dict[str, Any]] = []

    for execution_row in execution_rows:
        if not isinstance(execution_row, dict):
            raise RuntimeError("Execution index row must be an object.")

        result_path = Path(str(execution_row.get("result_json_output_path", "")))

        if not result_path.exists():
            raise RuntimeError(f"Campaign batch result JSON not found: {result_path}")

        result = load_json(result_path)

        batch = result.get("batch", {})
        rankings = result.get("rankings", {})
        recommendations = result.get("recommendations", {})

        if not isinstance(batch, dict):
            batch = {}

        if not isinstance(rankings, dict):
            rankings = {}

        if not isinstance(recommendations, dict):
            recommendations = {}

        batch_id = str(batch.get("batch_id", execution_row.get("batch_id", result_path.stem)))
        family_id, severity_id = parse_batch_identity(batch_id)

        recommendation_rows = recommendations.get("rows", [])

        if not isinstance(recommendation_rows, list):
            recommendation_rows = []

        if not recommendation_rows:
            rows.append(
                {
                    "batch_id": batch_id,
                    "scenario_family_id": family_id,
                    "severity_id": severity_id,
                    "scenario_id": "",
                    "recommended_policy_id": "",
                    "recommended_replanning_method_id": "",
                    "recommended_execution_mode": "",
                    "recommendation_class": "missing_recommendation",
                    "has_clear_winner": False,
                    "best_score": 0.0,
                    "second_best_score": 0.0,
                    "score_margin_to_second": 0.0,
                    "mean_delta_objective_value": 0.0,
                    "mean_delta_makespan": 0.0,
                    "mean_delta_total_travel_time": 0.0,
                    "mean_total_lateness": 0.0,
                    "mean_late_task_count": 0.0,
                    "replanning_request_count": 0,
                    "replanning_success_count": 0,
                    "replanning_applied_count": 0,
                    "experiment_count": int(batch.get("completed_experiment_count", 0) or 0),
                    "ranking_row_count": int(rankings.get("row_count", 0) or 0),
                    "result_json_path": str(result_path),
                }
            )

            continue

        for recommendation in recommendation_rows:
            if not isinstance(recommendation, dict):
                continue

            rows.append(
                {
                    "batch_id": batch_id,
                    "scenario_family_id": family_id,
                    "severity_id": severity_id,
                    "scenario_id": str(recommendation.get("scenario_id", "")),
                    "recommended_policy_id": str(recommendation.get("recommended_policy_id", "")),
                    "recommended_replanning_method_id": str(
                        recommendation.get("recommended_replanning_method_id", "")
                    ),
                    "recommended_execution_mode": str(
                        recommendation.get("recommended_execution_mode", "")
                    ),
                    "recommendation_class": classify_recommendation(recommendation),
                    "has_clear_winner": bool(recommendation.get("has_clear_winner", False)),
                    "best_score": float(recommendation.get("best_score", 0.0) or 0.0),
                    "second_best_score": float(recommendation.get("second_best_score", 0.0) or 0.0),
                    "score_margin_to_second": float(
                        recommendation.get("score_margin_to_second", 0.0) or 0.0
                    ),
                    "mean_delta_objective_value": float(
                        recommendation.get("mean_delta_objective_value", 0.0) or 0.0
                    ),
                    "mean_delta_makespan": float(
                        recommendation.get("mean_delta_makespan", 0.0) or 0.0
                    ),
                    "mean_delta_total_travel_time": float(
                        recommendation.get("mean_delta_total_travel_time", 0.0) or 0.0
                    ),
                    "mean_total_lateness": float(
                        recommendation.get("mean_total_lateness", 0.0) or 0.0
                    ),
                    "mean_late_task_count": float(
                        recommendation.get("mean_late_task_count", 0.0) or 0.0
                    ),
                    "replanning_request_count": int(
                        recommendation.get("replanning_request_count", 0) or 0
                    ),
                    "replanning_success_count": int(
                        recommendation.get("replanning_success_count", 0) or 0
                    ),
                    "replanning_applied_count": int(
                        recommendation.get("replanning_applied_count", 0) or 0
                    ),
                    "experiment_count": int(recommendation.get("experiment_count", 0) or 0),
                    "ranking_row_count": int(rankings.get("row_count", 0) or 0),
                    "result_json_path": str(result_path),
                }
            )

    rows.sort(
        key=lambda row: (
            str(row["scenario_family_id"]),
            SEVERITY_IDS.index(str(row["severity_id"]))
            if str(row["severity_id"]) in SEVERITY_IDS
            else 999,
            str(row["batch_id"]),
        )
    )

    return rows


def build_summary(execution_index: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    class_counts = Counter(str(row["recommendation_class"]) for row in rows)
    policy_counts = Counter(str(row["recommended_policy_id"]) for row in rows)
    method_counts = Counter(str(row["recommended_replanning_method_id"]) for row in rows)
    family_counts = Counter(str(row["scenario_family_id"]) for row in rows)
    severity_counts = Counter(str(row["severity_id"]) for row in rows)

    clear_winner_count = sum(1 for row in rows if bool(row["has_clear_winner"]))
    tradeoff_count = class_counts.get("replanning_tradeoff", 0)
    weak_or_tied_count = class_counts.get("weak_or_tied", 0)

    total_experiments = int(execution_index.get("total_completed_experiment_count", 0) or 0)

    return {
        "summary_type": "fieldops_lab_campaign_result_summary",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "batch_count": int(execution_index.get("batch_count", 0) or 0),
        "recommendation_count": len(rows),
        "total_completed_experiment_count": total_experiments,
        "clear_winner_count": clear_winner_count,
        "weak_or_tied_count": weak_or_tied_count,
        "tradeoff_count": tradeoff_count,
        "recommendation_class_counts": dict(sorted(class_counts.items())),
        "recommended_policy_counts": dict(sorted(policy_counts.items())),
        "recommended_method_counts": dict(sorted(method_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "scientific_status": "campaign_result_consolidation_only",
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "warning": (
            "This summary consolidates campaign execution outputs. "
            "It still does not prove scientific validity because the campaign uses "
            "template-based perturbations and the ranking remains preliminary."
        ),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "scenario_id",
        "recommended_policy_id",
        "recommended_replanning_method_id",
        "recommended_execution_mode",
        "recommendation_class",
        "has_clear_winner",
        "best_score",
        "second_best_score",
        "score_margin_to_second",
        "mean_delta_objective_value",
        "mean_delta_makespan",
        "mean_delta_total_travel_time",
        "mean_total_lateness",
        "mean_late_task_count",
        "replanning_request_count",
        "replanning_success_count",
        "replanning_applied_count",
        "experiment_count",
        "ranking_row_count",
        "result_json_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign result summary")
    lines.append("")
    lines.append("This report consolidates recommendations from the executed campaign batches.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| batch_count | {format_number(summary['batch_count'])} |")
    lines.append(f"| recommendation_count | {format_number(summary['recommendation_count'])} |")
    lines.append(
        f"| total_completed_experiment_count | {format_number(summary['total_completed_experiment_count'])} |"
    )
    lines.append(f"| clear_winner_count | {format_number(summary['clear_winner_count'])} |")
    lines.append(f"| weak_or_tied_count | {format_number(summary['weak_or_tied_count'])} |")
    lines.append(f"| tradeoff_count | {format_number(summary['tradeoff_count'])} |")
    lines.append(f"| fuzzy_logic_status | {summary['fuzzy_logic_status']} |")
    lines.append(f"| scientific_status | {summary['scientific_status']} |")
    lines.append("")
    lines.append("## Recommendation classes")
    lines.append("")
    lines.append("| Class | Count |")
    lines.append("| --- | ---: |")

    for class_name, count in summary["recommendation_class_counts"].items():
        lines.append(f"| {class_name} | {format_number(count)} |")

    lines.append("")
    lines.append("## Recommended policies")
    lines.append("")
    lines.append("| Policy | Count |")
    lines.append("| --- | ---: |")

    for policy_id, count in summary["recommended_policy_counts"].items():
        lines.append(f"| {policy_id} | {format_number(count)} |")

    lines.append("")
    lines.append("## Recommendations by batch")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Recommendation class | Policy | Method | Clear winner | Delta objective | Delta makespan | Delta travel |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['recommendation_class']} | "
            f"{row['recommended_policy_id']} | "
            f"{row['recommended_replanning_method_id']} | "
            f"{format_number(row['has_clear_winner'])} | "
            f"{format_number(row['mean_delta_objective_value'])} | "
            f"{format_number(row['mean_delta_makespan'])} | "
            f"{format_number(row['mean_delta_total_travel_time'])} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This report is useful because it finally summarizes the whole executable campaign, "
        "not only one handcrafted sample batch."
    )
    lines.append("")
    lines.append(
        "However, this is still not a final scientific conclusion. The current campaign is still "
        "template-based, uses a small base instance, and depends on preliminary ranking criteria. "
        "The next step is to inspect whether the recommendations are meaningful by family and severity."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_result_summary.py "
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
        rows = build_result_rows(execution_index)
        summary = build_summary(execution_index, rows)

        payload = {
            "summary": summary,
            "rows": rows,
        }

        write_markdown(output_md, summary, rows)
        write_json(output_json, payload)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign result summary markdown written to: {output_md}")
    print(f"Campaign result summary JSON written to: {output_json}")
    print(f"Campaign result summary CSV written to: {output_csv}")
    print(f"Recommendation rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())