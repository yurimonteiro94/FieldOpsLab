from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Input JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    text = normalize_text(value).lower()
    return text in {"true", "yes", "1", "y"}


def first_present(data: dict[str, Any], keys: list[str], default: Any = "") -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def pick_rows(data: dict[str, Any], required_keys: list[str], label: str) -> list[dict[str, Any]]:
    direct_rows = data.get("rows")
    if isinstance(direct_rows, list):
        rows = [row for row in direct_rows if isinstance(row, dict)]
        if rows:
            return rows

    candidates: list[list[dict[str, Any]]] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                visit(nested)
            return

        if isinstance(value, list):
            rows = [item for item in value if isinstance(item, dict)]
            if not rows:
                return

            score = 0
            for key in required_keys:
                if any(key in row for row in rows):
                    score += 1

            if score > 0:
                candidates.append(rows)

    visit(data)

    if not candidates:
        raise RuntimeError(f"Could not find row list in {label}.")

    candidates.sort(
        key=lambda rows: (
            sum(1 for key in required_keys if any(key in row for row in rows)),
            len(rows),
        ),
        reverse=True,
    )

    return candidates[0]


def normalize_decision_rows(matrix_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = pick_rows(
        matrix_data,
        [
            "batch_id",
            "scenario_family_id",
            "severity_id",
            "provisional_action",
            "evidence_strength",
        ],
        "campaign decision matrix",
    )

    normalized_rows: list[dict[str, Any]] = []

    for row in rows:
        batch_id = normalize_text(first_present(row, ["batch_id", "batch"], ""))
        if not batch_id:
            continue

        action = normalize_text(first_present(row, ["provisional_action", "action"], ""))
        evidence = normalize_text(first_present(row, ["evidence_strength", "evidence"], ""))
        recommendation_class = normalize_text(first_present(row, ["recommendation_class"], ""))
        service_class = normalize_text(first_present(row, ["service_effect_class"], ""))
        trigger_class = normalize_text(first_present(row, ["threshold_with_greedy_trigger_class"], ""))
        caution = normalize_text(first_present(row, ["methodological_caution"], ""))

        scientific_use_status = classify_scientific_use_status(
            action=action,
            evidence=evidence,
            recommendation_class=recommendation_class,
            service_class=service_class,
        )

        normalized_rows.append(
            {
                "batch_id": batch_id,
                "scenario_family_id": normalize_text(
                    first_present(row, ["scenario_family_id", "family"], "")
                ),
                "severity_id": normalize_text(first_present(row, ["severity_id", "severity"], "")),
                "recommendation_class": recommendation_class,
                "recommended_policy_id": normalize_text(first_present(row, ["recommended_policy_id"], "")),
                "recommended_replanning_method_id": normalize_text(
                    first_present(row, ["recommended_replanning_method_id"], "")
                ),
                "has_clear_winner": bool_value(first_present(row, ["has_clear_winner"], False)),
                "mean_delta_objective_value": float_value(
                    first_present(row, ["mean_delta_objective_value", "mean_delta_objective"], 0.0)
                ),
                "mean_delta_makespan": float_value(
                    first_present(row, ["mean_delta_makespan"], 0.0)
                ),
                "mean_delta_total_travel_time": float_value(
                    first_present(row, ["mean_delta_total_travel_time", "mean_delta_travel"], 0.0)
                ),
                "semantic_status": normalize_text(first_present(row, ["semantic_status"], "")),
                "semantic_problem_count": int_value(first_present(row, ["semantic_problem_count"], 0)),
                "semantic_warning_count": int_value(first_present(row, ["semantic_warning_count"], 0)),
                "service_effect_class": service_class,
                "service_warning_count": int_value(first_present(row, ["service_warning_count"], 0)),
                "threshold_with_greedy_trigger_class": trigger_class,
                "threshold_without_solver_trigger_class": normalize_text(
                    first_present(row, ["threshold_without_solver_trigger_class"], "")
                ),
                "threshold_should_replan_count": int_value(
                    first_present(row, ["threshold_should_replan_count"], 0)
                ),
                "threshold_request_count": int_value(
                    first_present(row, ["threshold_request_count"], 0)
                ),
                "threshold_applied_count": int_value(
                    first_present(row, ["threshold_applied_count"], 0)
                ),
                "provisional_action": action,
                "evidence_strength": evidence,
                "methodological_caution": caution,
                "scientific_use_status": scientific_use_status,
            }
        )

    normalized_rows.sort(
        key=lambda item: (
            item["scenario_family_id"],
            severity_order(item["severity_id"]),
            item["batch_id"],
        )
    )

    return normalized_rows


def severity_order(severity: str) -> int:
    order = {
        "light": 1,
        "moderate": 2,
        "severe": 3,
    }
    return order.get(severity, 99)


def classify_scientific_use_status(
    action: str,
    evidence: str,
    recommendation_class: str,
    service_class: str,
) -> str:
    if evidence == "invalid":
        return "do_not_use"

    if "service" in action or service_class == "visible_but_neutral_and_kept_plan":
        return "diagnostic_only_requires_modeling_review"

    if recommendation_class == "weak_or_tied":
        return "diagnostic_only_low_evidence"

    if evidence == "medium" and action.startswith("replan_candidate"):
        return "preliminary_pattern_candidate"

    if action == "keep_current_plan_candidate":
        return "preliminary_stability_candidate"

    return "diagnostic_only"


def count_rows(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(Counter(normalize_text(row.get(key, "")) for row in rows))


def build_overview(rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_count = len({row["scenario_family_id"] for row in rows})
    severity_count = len({row["severity_id"] for row in rows})

    action_counts = Counter(row["provisional_action"] for row in rows)
    evidence_counts = Counter(row["evidence_strength"] for row in rows)
    scientific_use_counts = Counter(row["scientific_use_status"] for row in rows)
    recommendation_counts = Counter(row["recommendation_class"] for row in rows)

    semantic_problem_count = sum(int_value(row["semantic_problem_count"]) for row in rows)
    semantic_warning_count = sum(int_value(row["semantic_warning_count"]) for row in rows)
    service_warning_count = sum(int_value(row["service_warning_count"]) for row in rows)

    return {
        "decision_row_count": len(rows),
        "family_count": family_count,
        "severity_count": severity_count,
        "replan_candidate_count": sum(
            count for action, count in action_counts.items() if action.startswith("replan_candidate")
        ),
        "keep_current_plan_candidate_count": action_counts.get("keep_current_plan_candidate", 0),
        "service_modeling_review_count": action_counts.get(
            "review_service_delay_modeling_before_concluding", 0
        ),
        "low_evidence_count": evidence_counts.get("low", 0),
        "medium_evidence_count": evidence_counts.get("medium", 0),
        "invalid_evidence_count": evidence_counts.get("invalid", 0),
        "weak_or_tied_count": recommendation_counts.get("weak_or_tied", 0),
        "replanning_tradeoff_count": recommendation_counts.get("replanning_tradeoff", 0),
        "semantic_problem_count": semantic_problem_count,
        "semantic_warning_count": semantic_warning_count,
        "service_warning_count": service_warning_count,
        "action_counts": dict(action_counts),
        "evidence_counts": dict(evidence_counts),
        "scientific_use_counts": dict(scientific_use_counts),
        "recommendation_class_counts": dict(recommendation_counts),
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "scientific_status": "final_diagnostic_report_only",
        "general_project_completeness_estimate_percent": 30,
        "campaign_pipeline_completeness_estimate_percent": 90,
    }


def build_source_summary(paths: dict[str, Path], loaded: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for label, path in paths.items():
        data = loaded[label]
        rows.append(
            {
                "label": label,
                "path": str(path),
                "exists": path.exists(),
                "top_level_keys": len(data.keys()),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )

    return rows


def build_payload(
    paths: dict[str, Path],
    loaded: dict[str, dict[str, Any]],
    decision_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    overview = build_overview(decision_rows)

    return {
        "report_type": "fieldops_lab_campaign_final_diagnostic_report",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "source_files": build_source_summary(paths, loaded),
        "overview": overview,
        "rows": decision_rows,
        "interpretation": {
            "status": "diagnostic_consolidation",
            "warning": (
                "This report consolidates campaign diagnostics. It is not a final "
                "scientific conclusion and should not be used as proof without broader "
                "instances, stronger ranking criteria, and statistical validation."
            ),
            "fuzzy_logic_status": "not_used_in_main_pipeline",
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "provisional_action",
        "evidence_strength",
        "scientific_use_status",
        "recommendation_class",
        "recommended_policy_id",
        "recommended_replanning_method_id",
        "has_clear_winner",
        "mean_delta_objective_value",
        "mean_delta_makespan",
        "mean_delta_total_travel_time",
        "semantic_status",
        "semantic_problem_count",
        "service_effect_class",
        "service_warning_count",
        "threshold_with_greedy_trigger_class",
        "threshold_without_solver_trigger_class",
        "threshold_should_replan_count",
        "threshold_request_count",
        "threshold_applied_count",
        "methodological_caution",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    overview = payload["overview"]
    rows = payload["rows"]
    source_files = payload["source_files"]

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign final diagnostic report")
    lines.append("")
    lines.append("This report consolidates the executed campaign, result summary, semantic inspection, service-delay audit, policy-trigger audit, and campaign decision matrix.")
    lines.append("")
    lines.append("## Overall status")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| decision_row_count | {format_number(overview['decision_row_count'])} |")
    lines.append(f"| family_count | {format_number(overview['family_count'])} |")
    lines.append(f"| severity_count | {format_number(overview['severity_count'])} |")
    lines.append(f"| replan_candidate_count | {format_number(overview['replan_candidate_count'])} |")
    lines.append(f"| keep_current_plan_candidate_count | {format_number(overview['keep_current_plan_candidate_count'])} |")
    lines.append(f"| service_modeling_review_count | {format_number(overview['service_modeling_review_count'])} |")
    lines.append(f"| low_evidence_count | {format_number(overview['low_evidence_count'])} |")
    lines.append(f"| medium_evidence_count | {format_number(overview['medium_evidence_count'])} |")
    lines.append(f"| semantic_problem_count | {format_number(overview['semantic_problem_count'])} |")
    lines.append(f"| service_warning_count | {format_number(overview['service_warning_count'])} |")
    lines.append(f"| fuzzy_logic_status | {overview['fuzzy_logic_status']} |")
    lines.append(f"| scientific_status | {overview['scientific_status']} |")
    lines.append(f"| general_project_completeness_estimate_percent | {format_number(overview['general_project_completeness_estimate_percent'])} |")
    lines.append(f"| campaign_pipeline_completeness_estimate_percent | {format_number(overview['campaign_pipeline_completeness_estimate_percent'])} |")
    lines.append("")

    lines.append("## Source files")
    lines.append("")
    lines.append("| Label | Path | Size bytes |")
    lines.append("| --- | --- | ---: |")

    for source in source_files:
        lines.append(
            f"| {source['label']} | `{source['path']}` | {format_number(source['size_bytes'])} |"
        )

    lines.append("")

    lines.append("## Provisional action counts")
    lines.append("")
    lines.append("| Action | Count |")
    lines.append("| --- | ---: |")

    for action, count in sorted(overview["action_counts"].items()):
        lines.append(f"| {action} | {format_number(count)} |")

    lines.append("")

    lines.append("## Scientific use status")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("| --- | ---: |")

    for status, count in sorted(overview["scientific_use_counts"].items()):
        lines.append(f"| {status} | {format_number(count)} |")

    lines.append("")

    lines.append("## Final diagnostic table")
    lines.append("")
    lines.append("| Batch | Family | Severity | Action | Evidence | Scientific use | Trigger | Service class | Caution |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['provisional_action']} | "
            f"{row['evidence_strength']} | "
            f"{row['scientific_use_status']} | "
            f"{row['threshold_with_greedy_trigger_class']} | "
            f"{row['service_effect_class']} | "
            f"{row['methodological_caution']} |"
        )

    lines.append("")

    lines.append("## What this report supports")
    lines.append("")
    lines.append("- It supports a demonstrable campaign-level diagnostic pipeline.")
    lines.append("- It supports preliminary pattern identification by scenario family and severity.")
    lines.append("- It supports identifying weak points in the current model, especially service-delay effects and objective-only ranking.")
    lines.append("")

    lines.append("## What this report does not support yet")
    lines.append("")
    lines.append("- It does not prove a final research conclusion.")
    lines.append("- It does not validate the method statistically.")
    lines.append("- It does not replace broader instances, richer policies, better ranking criteria, or real-company validation.")
    lines.append("")

    lines.append("## Recommended next implementation priorities")
    lines.append("")
    lines.append("1. Integrate this final diagnostic report into the full campaign pipeline.")
    lines.append("2. Replace objective-only ranking with an operational ranking profile.")
    lines.append("3. Add at least one stronger replanning policy or method for comparison.")
    lines.append("4. Add larger or more varied instances before making scientific claims.")
    lines.append("5. Add statistical analysis after enough independent results exist.")
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "The current project has a working end-to-end experimental campaign pipeline. "
        "It is strong as an engineering milestone and still preliminary as scientific evidence."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 9:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_final_diagnostic_report.py "
            "<campaign_execution_index_json> "
            "<campaign_result_summary_json> "
            "<campaign_result_semantic_inspection_json> "
            "<service_delay_impact_audit_json> "
            "<policy_trigger_behavior_audit_json> "
            "<campaign_decision_matrix_json> "
            "<output_md> "
            "<output_json> "
            "<output_csv>",
            file=sys.stderr,
        )
        return 2

    paths = {
        "campaign_execution_index": Path(sys.argv[1]),
        "campaign_result_summary": Path(sys.argv[2]),
        "campaign_result_semantic_inspection": Path(sys.argv[3]),
        "service_delay_impact_audit": Path(sys.argv[4]),
        "policy_trigger_behavior_audit": Path(sys.argv[5]),
        "campaign_decision_matrix": Path(sys.argv[6]),
    }

    output_md = Path(sys.argv[7])
    output_json = Path(sys.argv[8])
    output_csv = Path(sys.argv[9]) if len(sys.argv) > 9 else None

    try:
        loaded = {label: load_json(path) for label, path in paths.items()}

        decision_rows = normalize_decision_rows(loaded["campaign_decision_matrix"])
        if not decision_rows:
            raise RuntimeError("No decision rows found in campaign decision matrix.")

        payload = build_payload(paths, loaded, decision_rows)

        write_markdown(output_md, payload)
        write_json(output_json, payload)

        if output_csv is not None:
            write_csv(output_csv, decision_rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign final diagnostic markdown written to: {output_md}")
    print(f"Campaign final diagnostic JSON written to: {output_json}")

    if output_csv is not None:
        print(f"Campaign final diagnostic CSV written to: {output_csv}")

    print(f"Decision rows: {len(decision_rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())