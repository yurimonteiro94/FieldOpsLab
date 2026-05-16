from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


MATRIX_FIELDS = [
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "recommendation_class",
    "recommended_policy_id",
    "recommended_replanning_method_id",
    "has_clear_winner",
    "mean_delta_objective_value",
    "mean_delta_makespan",
    "mean_delta_total_travel_time",
    "semantic_status",
    "semantic_problem_count",
    "semantic_warning_count",
    "service_effect_class",
    "service_warning_count",
    "threshold_with_greedy_trigger_class",
    "threshold_without_solver_trigger_class",
    "threshold_should_replan_count",
    "threshold_request_count",
    "threshold_applied_count",
    "provisional_action",
    "evidence_strength",
    "methodological_caution",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def format_number(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"yes", "true", "1", "y", "sim"}


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def first_present(row: dict[str, Any], keys: list[str], default: Any = "") -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return default


def normalize_id(value: Any) -> str:
    return str(value).strip()


def recursively_find_row_lists(data: Any) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []

    if isinstance(data, list):
        object_items = [item for item in data if isinstance(item, dict)]
        if object_items:
            found.append(object_items)
        for item in data:
            found.extend(recursively_find_row_lists(item))

    if isinstance(data, dict):
        for value in data.values():
            found.extend(recursively_find_row_lists(value))

    return found


def score_row_list(rows: list[dict[str, Any]], required_any: list[str], required_batch: bool = True) -> int:
    if not rows:
        return -1

    score = 0
    for row in rows:
        keys = set(row.keys())
        if required_batch and ("batch_id" in keys or "batch" in keys):
            score += 2
        for key in required_any:
            if key in keys:
                score += 3

    return score


def pick_rows(data: dict[str, Any], required_any: list[str], label: str) -> list[dict[str, Any]]:
    candidates = recursively_find_row_lists(data)
    candidates = [rows for rows in candidates if rows]

    if not candidates:
        raise RuntimeError(f"No row lists found while reading {label}.")

    best = max(candidates, key=lambda rows: score_row_list(rows, required_any))
    if score_row_list(best, required_any) <= 0:
        raise RuntimeError(f"Could not identify expected rows in {label}.")

    return best


def normalize_result_summary_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_rows = pick_rows(
        data,
        [
            "recommendation_class",
            "recommended_policy_id",
            "recommended_replanning_method_id",
            "mean_delta_objective_value",
        ],
        "campaign result summary",
    )

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        batch_id = normalize_id(first_present(row, ["batch_id", "batch"], ""))
        if not batch_id:
            continue

        rows.append(
            {
                "batch_id": batch_id,
                "scenario_family_id": normalize_id(
                    first_present(row, ["scenario_family_id", "family", "family_id"], "")
                ),
                "severity_id": normalize_id(first_present(row, ["severity_id", "severity"], "")),
                "recommendation_class": normalize_id(first_present(row, ["recommendation_class"], "")),
                "recommended_policy_id": normalize_id(
                    first_present(row, ["recommended_policy_id", "policy", "policy_id"], "")
                ),
                "recommended_replanning_method_id": normalize_id(
                    first_present(
                        row,
                        [
                            "recommended_replanning_method_id",
                            "replanning_method_id",
                            "method",
                            "recommended_method",
                        ],
                        "",
                    )
                ),
                "has_clear_winner": bool_value(
                    first_present(row, ["has_clear_winner", "clear_winner"], False)
                ),
                "mean_delta_objective_value": float_value(
                    first_present(row, ["mean_delta_objective_value", "delta_objective"], 0.0)
                ),
                "mean_delta_makespan": float_value(
                    first_present(row, ["mean_delta_makespan", "delta_makespan"], 0.0)
                ),
                "mean_delta_total_travel_time": float_value(
                    first_present(row, ["mean_delta_total_travel_time", "delta_travel"], 0.0)
                ),
            }
        )

    if not rows:
        raise RuntimeError("No campaign recommendation rows could be normalized.")

    return rows


def normalize_semantic_rows(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_rows = pick_rows(
        data,
        [
            "semantic_problem_count",
            "semantic_warning_count",
            "baseline_travel_delta",
            "baseline_service_delta",
        ],
        "campaign semantic inspection",
    )

    by_batch: dict[str, dict[str, Any]] = {}
    for row in raw_rows:
        batch_id = normalize_id(first_present(row, ["batch_id", "batch"], ""))
        if not batch_id:
            continue

        problem_count = int_value(
            first_present(row, ["semantic_problem_count", "problem_count", "problems"], 0)
        )
        warning_count = int_value(
            first_present(row, ["semantic_warning_count", "warning_count", "warnings"], 0)
        )

        by_batch[batch_id] = {
            "semantic_status": "ok" if problem_count == 0 else "problem",
            "semantic_problem_count": problem_count,
            "semantic_warning_count": warning_count,
            "baseline_travel_delta": float_value(
                first_present(row, ["baseline_travel_delta", "baseline_delta_travel"], 0.0)
            ),
            "baseline_service_delta": float_value(
                first_present(row, ["baseline_service_delta", "baseline_delta_service"], 0.0)
            ),
        }

    return by_batch


def normalize_service_rows(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_rows = pick_rows(data, ["service_effect_class", "service_warning_count"], "service delay audit")

    by_batch: dict[str, dict[str, Any]] = {}
    for row in raw_rows:
        batch_id = normalize_id(first_present(row, ["batch_id", "batch"], ""))
        if not batch_id:
            continue

        by_batch[batch_id] = {
            "service_effect_class": normalize_id(first_present(row, ["service_effect_class"], "")),
            "service_warning_count": int_value(
                first_present(row, ["service_warning_count", "warning_count", "warnings"], 0)
            ),
        }

    return by_batch


def normalize_trigger_rows(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_rows = pick_rows(
        data,
        [
            "trigger_behavior_class",
            "option",
            "policy_should_replan_count",
            "replanning_request_count",
            "replanning_applied_count",
        ],
        "policy trigger behavior audit",
    )

    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "threshold_should_replan_count": 0,
            "threshold_request_count": 0,
            "threshold_applied_count": 0,
            "threshold_with_greedy_trigger_class": "",
            "threshold_without_solver_trigger_class": "",
        }
    )

    for row in raw_rows:
        batch_id = normalize_id(first_present(row, ["batch_id", "batch"], ""))
        if not batch_id:
            continue

        option_id = normalize_id(first_present(row, ["option_id", "option"], ""))
        trigger_class = normalize_id(first_present(row, ["trigger_class", "trigger_behavior_class"], ""))

        if "threshold" not in option_id:
            continue

        grouped[batch_id]["threshold_should_replan_count"] += int_value(
            first_present(row, ["policy_should_replan_count", "should_replan_count"], 0)
        )
        grouped[batch_id]["threshold_request_count"] += int_value(
            first_present(row, ["replanning_request_count", "request_count"], 0)
        )
        grouped[batch_id]["threshold_applied_count"] += int_value(
            first_present(row, ["replanning_applied_count", "applied_count"], 0)
        )

        if option_id == "threshold_with_greedy_replanning":
            grouped[batch_id]["threshold_with_greedy_trigger_class"] = trigger_class
        elif option_id == "threshold_without_solver":
            grouped[batch_id]["threshold_without_solver_trigger_class"] = trigger_class

    return dict(grouped)


def classify_provisional_action(row: dict[str, Any]) -> tuple[str, str, str]:
    recommendation_class = str(row["recommendation_class"])
    policy_id = str(row["recommended_policy_id"])
    severity = str(row["severity_id"])
    semantic_problem_count = int_value(row["semantic_problem_count"])
    service_effect_class = str(row["service_effect_class"])
    service_warning_count = int_value(row["service_warning_count"])
    has_clear_winner = bool_value(row["has_clear_winner"])
    delta_makespan = float_value(row["mean_delta_makespan"])
    trigger_with_greedy = str(row["threshold_with_greedy_trigger_class"])

    cautions: list[str] = []

    if semantic_problem_count > 0:
        return (
            "do_not_interpret_until_semantics_are_fixed",
            "invalid",
            "semantic problems detected",
        )

    if service_warning_count > 0 or service_effect_class == "visible_but_neutral_and_kept_plan":
        cautions.append("service delay visible but weak under current objective/makespan")

    if not has_clear_winner:
        cautions.append("weak or tied recommendation")

    if delta_makespan > 0 and "replanning" in policy_id:
        cautions.append("replanning improves objective but increases makespan")

    if "triggered_and_applied" not in trigger_with_greedy and severity in {"moderate", "severe"}:
        if "no_replanning" not in policy_id:
            cautions.append("recommended replanning without expected trigger evidence")

    if recommendation_class == "weak_or_tied":
        if service_effect_class == "visible_but_neutral_and_kept_plan":
            return (
                "review_service_delay_modeling_before_concluding",
                "low",
                "; ".join(cautions) if cautions else "service-delay modeling caution",
            )

        if severity == "light":
            return (
                "keep_current_plan_candidate",
                "low",
                "; ".join(cautions) if cautions else "light scenario with weak/tied evidence",
            )

        return (
            "inconclusive_requires_richer_ranking_or_more_instances",
            "low",
            "; ".join(cautions) if cautions else "weak/tied recommendation",
        )

    if recommendation_class == "replanning_tradeoff":
        if delta_makespan > 0:
            return (
                "replan_candidate_with_makespan_monitoring",
                "medium",
                "; ".join(cautions) if cautions else "trade-off recommendation",
            )

        return (
            "replan_candidate",
            "medium",
            "; ".join(cautions) if cautions else "clear replanning candidate",
        )

    if "no_replanning" in policy_id:
        return (
            "keep_current_plan_candidate",
            "low" if not has_clear_winner else "medium",
            "; ".join(cautions) if cautions else "no-replanning candidate",
        )

    return (
        "manual_review_required",
        "low",
        "; ".join(cautions) if cautions else "unclassified recommendation pattern",
    )


def build_matrix(
    result_rows: list[dict[str, Any]],
    semantic_by_batch: dict[str, dict[str, Any]],
    service_by_batch: dict[str, dict[str, Any]],
    trigger_by_batch: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []

    for result_row in result_rows:
        batch_id = str(result_row["batch_id"])
        semantic = semantic_by_batch.get(batch_id, {})
        service = service_by_batch.get(batch_id, {})
        trigger = trigger_by_batch.get(batch_id, {})

        row = {
            **result_row,
            "semantic_status": semantic.get("semantic_status", "missing"),
            "semantic_problem_count": int_value(semantic.get("semantic_problem_count", 0)),
            "semantic_warning_count": int_value(semantic.get("semantic_warning_count", 0)),
            "service_effect_class": normalize_id(service.get("service_effect_class", "")),
            "service_warning_count": int_value(service.get("service_warning_count", 0)),
            "threshold_with_greedy_trigger_class": normalize_id(
                trigger.get("threshold_with_greedy_trigger_class", "")
            ),
            "threshold_without_solver_trigger_class": normalize_id(
                trigger.get("threshold_without_solver_trigger_class", "")
            ),
            "threshold_should_replan_count": int_value(
                trigger.get("threshold_should_replan_count", 0)
            ),
            "threshold_request_count": int_value(trigger.get("threshold_request_count", 0)),
            "threshold_applied_count": int_value(trigger.get("threshold_applied_count", 0)),
        }

        action, strength, caution = classify_provisional_action(row)
        row["provisional_action"] = action
        row["evidence_strength"] = strength
        row["methodological_caution"] = caution

        matrix.append(row)

    matrix.sort(key=lambda item: (str(item["scenario_family_id"]), str(item["severity_id"])))
    return matrix


def build_overview(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts = Counter(str(row["provisional_action"]) for row in matrix)
    strength_counts = Counter(str(row["evidence_strength"]) for row in matrix)
    family_counts = Counter(str(row["scenario_family_id"]) for row in matrix)
    recommendation_counts = Counter(str(row["recommendation_class"]) for row in matrix)

    return {
        "matrix_row_count": len(matrix),
        "family_count": len(family_counts),
        "provisional_action_counts": dict(sorted(action_counts.items())),
        "evidence_strength_counts": dict(sorted(strength_counts.items())),
        "recommendation_class_counts": dict(sorted(recommendation_counts.items())),
        "low_evidence_count": strength_counts.get("low", 0),
        "medium_evidence_count": strength_counts.get("medium", 0),
        "invalid_evidence_count": strength_counts.get("invalid", 0),
        "service_modeling_review_count": action_counts.get(
            "review_service_delay_modeling_before_concluding", 0
        ),
        "replan_candidate_count": sum(
            count for action, count in action_counts.items() if action.startswith("replan")
        ),
        "keep_current_plan_candidate_count": action_counts.get("keep_current_plan_candidate", 0),
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "scientific_status": "decision_matrix_diagnostic_only",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in MATRIX_FIELDS})


def write_markdown(path: Path, overview: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# FieldOps Lab campaign decision matrix")
    lines.append("")
    lines.append(
        "This report consolidates campaign recommendations, semantic checks, service-delay diagnostics, and policy-trigger behavior into one decision-support table."
    )
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in [
        "matrix_row_count",
        "family_count",
        "low_evidence_count",
        "medium_evidence_count",
        "invalid_evidence_count",
        "service_modeling_review_count",
        "replan_candidate_count",
        "keep_current_plan_candidate_count",
        "fuzzy_logic_status",
        "scientific_status",
    ]:
        lines.append(f"| {key} | {format_number(overview.get(key, ''))} |")

    lines.append("")
    lines.append("## Provisional actions")
    lines.append("")
    lines.append("| Action | Count |")
    lines.append("| --- | ---: |")
    for action, count in overview["provisional_action_counts"].items():
        lines.append(f"| {action} | {count} |")

    lines.append("")
    lines.append("## Evidence strength")
    lines.append("")
    lines.append("| Evidence strength | Count |")
    lines.append("| --- | ---: |")
    for strength, count in overview["evidence_strength_counts"].items():
        lines.append(f"| {strength} | {count} |")

    lines.append("")
    lines.append("## Decision matrix")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Recommendation | Trigger with greedy | Service class | Action | Evidence | Caution |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['recommendation_class']} | "
            f"{row['threshold_with_greedy_trigger_class']} | "
            f"{row['service_effect_class']} | "
            f"{row['provisional_action']} | "
            f"{row['evidence_strength']} | "
            f"{row['methodological_caution']} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This matrix is a diagnostic decision-support layer. It does not prove the final research method yet."
    )
    lines.append("")
    lines.append(
        "Rows marked as low evidence, weak/tied, or service-modeling review should not be used as final policy conclusions without broader instances, stronger ranking criteria, and additional validation."
    )
    lines.append("")
    lines.append(
        "Fuzzy logic remains outside the main pipeline. These descriptors could later feed fuzzy logic, statistical rules, or a deterministic decision framework, but they are not fuzzy rules here."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 8:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_decision_matrix.py "
            "<campaign_result_summary_json> <semantic_inspection_json> "
            "<service_delay_audit_json> <policy_trigger_audit_json> "
            "<output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    try:
        result_summary_path = Path(sys.argv[1])
        semantic_path = Path(sys.argv[2])
        service_path = Path(sys.argv[3])
        trigger_path = Path(sys.argv[4])
        output_md = Path(sys.argv[5])
        output_json = Path(sys.argv[6])
        output_csv = Path(sys.argv[7])

        result_summary = load_json(result_summary_path)
        semantic_inspection = load_json(semantic_path)
        service_audit = load_json(service_path)
        trigger_audit = load_json(trigger_path)

        result_rows = normalize_result_summary_rows(result_summary)
        semantic_by_batch = normalize_semantic_rows(semantic_inspection)
        service_by_batch = normalize_service_rows(service_audit)
        trigger_by_batch = normalize_trigger_rows(trigger_audit)

        matrix = build_matrix(result_rows, semantic_by_batch, service_by_batch, trigger_by_batch)
        overview = build_overview(matrix)

        payload = {
            "report_type": "fieldops_lab_campaign_decision_matrix",
            "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
            "inputs": {
                "campaign_result_summary_json": str(result_summary_path),
                "semantic_inspection_json": str(semantic_path),
                "service_delay_audit_json": str(service_path),
                "policy_trigger_audit_json": str(trigger_path),
            },
            "overview": overview,
            "rows": matrix,
            "interpretation": {
                "status": "diagnostic_decision_support_only",
                "warning": "This matrix consolidates evidence but does not prove final scientific validity.",
                "fuzzy_logic_status": "not_used_in_main_pipeline",
            },
        }

        write_markdown(output_md, overview, matrix)
        write_json(output_json, payload)
        write_csv(output_csv, matrix)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign decision matrix markdown written to: {output_md}")
    print(f"Campaign decision matrix JSON written to: {output_json}")
    print(f"Campaign decision matrix CSV written to: {output_csv}")
    print(f"Decision rows: {len(matrix)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())