from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


RANKING_PROFILES = {
    "objective_only": {
        "description": "Uses only objective delta. This matches the current preliminary ranking.",
        "weights": {
            "mean_delta_objective_value": 1.0,
        },
    },
    "balanced_operational": {
        "description": "Balances objective, makespan, travel time, lateness, and replanning effort.",
        "weights": {
            "mean_delta_objective_value": 1.0,
            "mean_delta_makespan": 0.4,
            "mean_delta_total_travel_time": 0.2,
            "mean_total_lateness": 2.0,
            "replanning_applied_count": 1.0,
        },
    },
    "makespan_priority": {
        "description": "Penalizes makespan strongly and is useful when finishing later is operationally expensive.",
        "weights": {
            "mean_delta_objective_value": 0.5,
            "mean_delta_makespan": 1.0,
            "mean_delta_total_travel_time": 0.1,
            "mean_total_lateness": 2.0,
        },
    },
    "conservative_replanning": {
        "description": "Penalizes replanning effort and favors stability unless benefits are clear.",
        "weights": {
            "mean_delta_objective_value": 1.0,
            "mean_delta_makespan": 0.3,
            "mean_delta_total_travel_time": 0.2,
            "replanning_applied_count": 8.0,
            "replanning_request_count": 2.0,
        },
    },
}


CSV_FIELDS = [
    "scenario_id",
    "batch_id",
    "scenario_family_id",
    "severity_id",
    "profile_id",
    "rank",
    "ranking_score",
    "policy_id",
    "replanning_method_id",
    "execution_mode",
    "experiment_count",
    "mean_delta_objective_value",
    "mean_delta_makespan",
    "mean_delta_total_travel_time",
    "mean_total_lateness",
    "replanning_request_count",
    "replanning_applied_count",
    "is_recommended",
    "recommendation_class",
]


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def str_value(value: Any) -> str:
    return "" if value is None else str(value)


def float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_id(value: Any) -> str:
    return str_value(value).strip()


def infer_family_and_severity(batch_id: str, scenario_id: str) -> tuple[str, str]:
    family_tokens = [
        "combined_delay",
        "reassignment_opportunity",
        "service_delay_only",
        "travel_delay_only",
    ]

    severity_tokens = ["light", "moderate", "severe"]

    batch_text = str(batch_id)
    scenario_text = str(scenario_id)

    def find_token(text: str, tokens: list[str]) -> str:
        for token in tokens:
            if token in text:
                return token
        return ""

    # Prefer batch_id because result rows may contain scenario_id values inherited
    # from earlier templates. The batch_id is the safer source for campaign family.
    family = find_token(batch_text, family_tokens)
    if not family:
        family = find_token(scenario_text, family_tokens)

    severity = find_token(batch_text, severity_tokens)
    if not severity:
        severity = find_token(scenario_text, severity_tokens)

    return family, severity
def discover_result_files(result_dir: Path) -> list[Path]:
    if not result_dir.exists():
        raise RuntimeError(f"Result directory does not exist: {result_dir}")

    paths = sorted(result_dir.glob("*_result.json"))

    if not paths:
        raise RuntimeError(f"No campaign result JSON files found in: {result_dir}")

    return paths


def ranking_rows_from_result(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)

    batch = data.get("batch", {})
    rankings = data.get("rankings", {})

    if not isinstance(batch, dict):
        batch = {}

    if not isinstance(rankings, dict):
        rankings = {}

    batch_id = normalize_id(batch.get("batch_id", path.stem.replace("_result", "")))
    rows = as_list(rankings.get("rows"))

    output: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        scenario_id = normalize_id(row.get("scenario_id", ""))
        family, severity = infer_family_and_severity(batch_id, scenario_id)

        output.append(
            {
                "result_path": str(path),
                "batch_id": batch_id,
                "scenario_id": scenario_id,
                "scenario_family_id": family,
                "severity_id": severity,
                "policy_id": normalize_id(row.get("policy_id", "")),
                "replanning_method_id": normalize_id(row.get("replanning_method_id", "")),
                "execution_mode": normalize_id(row.get("execution_mode", "")),
                "experiment_count": int_value(row.get("experiment_count", 0)),
                "mean_delta_objective_value": float_value(row.get("mean_delta_objective_value", 0.0)),
                "mean_delta_makespan": float_value(row.get("mean_delta_makespan", 0.0)),
                "mean_delta_total_travel_time": float_value(row.get("mean_delta_total_travel_time", 0.0)),
                "mean_delta_total_service_time": float_value(row.get("mean_delta_total_service_time", 0.0)),
                "mean_delta_total_waiting_time": float_value(row.get("mean_delta_total_waiting_time", 0.0)),
                "mean_total_lateness": float_value(row.get("mean_total_lateness", 0.0)),
                "mean_late_task_count": float_value(row.get("mean_late_task_count", 0.0)),
                "mean_effect_count": float_value(row.get("mean_effect_count", 0.0)),
                "policy_should_replan_count": int_value(row.get("policy_should_replan_count", 0)),
                "replanning_request_count": int_value(row.get("replanning_request_count", 0)),
                "replanning_success_count": int_value(row.get("replanning_success_count", 0)),
                "replanning_applied_count": int_value(row.get("replanning_applied_count", 0)),
            }
        )

    return output


def compute_score(row: dict[str, Any], weights: dict[str, float]) -> float:
    score = 0.0

    for key, weight in weights.items():
        score += float_value(row.get(key, 0.0)) * weight

    return score


def classify_recommendation(best: dict[str, Any], second: dict[str, Any] | None) -> str:
    if second is None:
        return "single_option"

    best_score = float_value(best["ranking_score"])
    second_score = float_value(second["ranking_score"])
    margin = second_score - best_score

    if abs(margin) < 1.0:
        return "weak_or_tied"

    if best.get("replanning_applied_count", 0) > 0 and float_value(best.get("mean_delta_makespan", 0.0)) > 0:
        return "replanning_tradeoff"

    if best.get("replanning_applied_count", 0) > 0:
        return "replanning_candidate"

    return "keep_plan_candidate"


def build_profile_rows(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profile_rows: list[dict[str, Any]] = []

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in base_rows:
        grouped[row["batch_id"]].append(row)

    for profile_id, profile in RANKING_PROFILES.items():
        weights = profile["weights"]

        for batch_id, rows in grouped.items():
            scored_rows: list[dict[str, Any]] = []

            for row in rows:
                scored = dict(row)
                scored["profile_id"] = profile_id
                scored["ranking_score"] = compute_score(row, weights)
                scored_rows.append(scored)

            scored_rows.sort(
                key=lambda item: (
                    float_value(item["ranking_score"]),
                    float_value(item["mean_delta_makespan"]),
                    float_value(item["mean_delta_total_travel_time"]),
                    str_value(item["policy_id"]),
                    str_value(item["replanning_method_id"]),
                    str_value(item["execution_mode"]),
                )
            )

            best = scored_rows[0] if scored_rows else None
            second = scored_rows[1] if len(scored_rows) > 1 else None

            for index, row in enumerate(scored_rows, start=1):
                row["rank"] = index
                row["is_recommended"] = index == 1
                row["recommendation_class"] = (
                    classify_recommendation(row, second) if index == 1 else ""
                )
                profile_rows.append(row)

    return profile_rows


def build_recommendation_summary(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommendations = [row for row in profile_rows if row.get("is_recommended")]

    by_batch: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in recommendations:
        by_batch[row["batch_id"]].append(row)

    summary_rows: list[dict[str, Any]] = []

    for batch_id, rows in sorted(by_batch.items()):
        policy_counter = Counter(row["policy_id"] for row in rows)
        class_counter = Counter(row["recommendation_class"] for row in rows)

        recommended_pairs = sorted(
            {
                f"{row['profile_id']}={row['policy_id']}+{row['replanning_method_id']}"
                for row in rows
            }
        )

        unique_policy_count = len(policy_counter)
        unique_class_count = len(class_counter)

        if unique_policy_count == 1 and unique_class_count == 1:
            stability_class = "stable_across_profiles"
        elif unique_policy_count == 1:
            stability_class = "same_policy_different_class"
        else:
            stability_class = "sensitive_to_ranking_profile"

        first = rows[0]

        summary_rows.append(
            {
                "batch_id": batch_id,
                "scenario_id": first["scenario_id"],
                "scenario_family_id": first["scenario_family_id"],
                "severity_id": first["severity_id"],
                "profile_count": len(rows),
                "unique_recommended_policy_count": unique_policy_count,
                "unique_recommendation_class_count": unique_class_count,
                "stability_class": stability_class,
                "recommended_profile_policy_pairs": "; ".join(recommended_pairs),
            }
        )

    return summary_rows


def build_payload(profile_rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]], result_files: list[Path]) -> dict[str, Any]:
    recommendations = [row for row in profile_rows if row.get("is_recommended")]

    stability_counter = Counter(row["stability_class"] for row in summary_rows)
    profile_counter = Counter(row["profile_id"] for row in recommendations)
    policy_counter = Counter(row["policy_id"] for row in recommendations)
    class_counter = Counter(row["recommendation_class"] for row in recommendations)

    return {
        "report_type": "fieldops_lab_campaign_ranking_profile_sensitivity",
        "generated_at_local": now_text(),
        "result_file_count": len(result_files),
        "ranking_profile_count": len(RANKING_PROFILES),
        "ranking_profiles": RANKING_PROFILES,
        "ranking_row_count": len(profile_rows),
        "recommendation_count": len(recommendations),
        "scenario_summary_count": len(summary_rows),
        "stability_counts": dict(sorted(stability_counter.items())),
        "recommended_policy_counts": dict(sorted(policy_counter.items())),
        "recommendation_class_counts": dict(sorted(class_counter.items())),
        "recommendation_count_by_profile": dict(sorted(profile_counter.items())),
        "summary_rows": summary_rows,
        "rows": profile_rows,
        "interpretation": {
            "fuzzy_logic_status": "not_used_in_main_pipeline",
            "scientific_status": "ranking_profile_sensitivity_diagnostic_only",
            "warning": "This report recalculates alternative ranking profiles from existing aggregate result rows. It is diagnostic and does not replace final statistical validation.",
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign ranking profile sensitivity")
    lines.append("")
    lines.append("This report recalculates campaign recommendations using alternative ranking profiles.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| result_file_count | {payload['result_file_count']} |")
    lines.append(f"| ranking_profile_count | {payload['ranking_profile_count']} |")
    lines.append(f"| ranking_row_count | {payload['ranking_row_count']} |")
    lines.append(f"| recommendation_count | {payload['recommendation_count']} |")
    lines.append(f"| scenario_summary_count | {payload['scenario_summary_count']} |")
    lines.append("| fuzzy_logic_status | not_used_in_main_pipeline |")
    lines.append("| scientific_status | ranking_profile_sensitivity_diagnostic_only |")
    lines.append("")

    lines.append("## Ranking profiles")
    lines.append("")
    lines.append("| Profile | Description |")
    lines.append("| --- | --- |")

    for profile_id, profile in payload["ranking_profiles"].items():
        lines.append(f"| {profile_id} | {profile['description']} |")

    lines.append("")
    lines.append("## Stability counts")
    lines.append("")
    lines.append("| Stability class | Count |")
    lines.append("| --- | ---: |")

    for key, value in payload["stability_counts"].items():
        lines.append(f"| {key} | {value} |")

    lines.append("")
    lines.append("## Recommended policies")
    lines.append("")
    lines.append("| Policy | Count |")
    lines.append("| --- | ---: |")

    for key, value in payload["recommended_policy_counts"].items():
        lines.append(f"| {key} | {value} |")

    lines.append("")
    lines.append("## Scenario sensitivity summary")
    lines.append("")
    lines.append("| Batch | Family | Severity | Stability | Unique policies | Profile recommendations |")
    lines.append("| --- | --- | --- | --- | ---: | --- |")

    for row in payload["summary_rows"]:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['stability_class']} | "
            f"{row['unique_recommended_policy_count']} | "
            f"{row['recommended_profile_policy_pairs']} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "If a scenario is stable across profiles, the current recommendation is less sensitive to the ranking formula."
    )
    lines.append("")
    lines.append(
        "If a scenario is sensitive to ranking profile, it should not be used as a final policy conclusion until ranking criteria are justified and tested on broader instances."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_ranking_profile_sensitivity.py "
            "<campaign_result_dir> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    result_dir = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        result_files = discover_result_files(result_dir)

        base_rows: list[dict[str, Any]] = []
        for path in result_files:
            base_rows.extend(ranking_rows_from_result(path))

        if not base_rows:
            raise RuntimeError("No ranking rows were found in campaign result files.")

        profile_rows = build_profile_rows(base_rows)
        summary_rows = build_recommendation_summary(profile_rows)
        payload = build_payload(profile_rows, summary_rows, result_files)

        write_markdown(output_md, payload)
        write_json(output_json, payload)
        write_csv(output_csv, profile_rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign ranking profile sensitivity markdown written to: {output_md}")
    print(f"Campaign ranking profile sensitivity JSON written to: {output_json}")
    print(f"Campaign ranking profile sensitivity CSV written to: {output_csv}")
    print(f"Ranking rows: {len(profile_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())