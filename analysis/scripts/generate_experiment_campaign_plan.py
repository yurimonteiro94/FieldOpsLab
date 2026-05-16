from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SEVERITY_LEVELS = [
    {
        "severity_id": "light",
        "nominal_delay_minutes": 10,
        "description": "Small disruption. Usually useful to test whether replanning is unnecessary.",
    },
    {
        "severity_id": "moderate",
        "nominal_delay_minutes": 50,
        "description": "Medium disruption. Useful to test trade-offs between keeping the plan and replanning.",
    },
    {
        "severity_id": "severe",
        "nominal_delay_minutes": 90,
        "description": "Large disruption. Useful to test robustness, risk, and operational recovery.",
    },
]

SCENARIO_FAMILIES = [
    {
        "family_id": "travel_delay_only",
        "description": "Only travel time is perturbed.",
        "uses_travel_delay": True,
        "uses_service_delay": False,
        "creates_reassignment_opportunity": False,
    },
    {
        "family_id": "service_delay_only",
        "description": "Only service time is perturbed.",
        "uses_travel_delay": False,
        "uses_service_delay": True,
        "creates_reassignment_opportunity": False,
    },
    {
        "family_id": "combined_delay",
        "description": "Travel and service times are both perturbed.",
        "uses_travel_delay": True,
        "uses_service_delay": True,
        "creates_reassignment_opportunity": False,
    },
    {
        "family_id": "reassignment_opportunity",
        "description": "A disruption creates a possible benefit from reassigning remaining work.",
        "uses_travel_delay": True,
        "uses_service_delay": False,
        "creates_reassignment_opportunity": True,
    },
]

POLICY_OPTIONS = [
    {
        "policy_option_id": "no_replanning_baseline",
        "policy_id": "no_replanning_policy_v1",
        "replanning_method_id": "replanning_not_implemented_v1",
        "description": "Baseline option. The original plan is kept.",
    },
    {
        "policy_option_id": "threshold_without_solver",
        "policy_id": "threshold_delay_replanning_policy_v1",
        "replanning_method_id": "replanning_not_implemented_v1",
        "description": "Decision policy may request replanning, but no solver is applied. Useful as a control option.",
    },
    {
        "policy_option_id": "threshold_with_greedy_replanning",
        "policy_id": "threshold_delay_replanning_policy_v1",
        "replanning_method_id": "greedy_replanning_solver_v1",
        "description": "Decision policy may request replanning and applies the current greedy replanning solver.",
    },
]

RANKING_PROFILES = [
    {
        "ranking_profile_id": "objective_only",
        "description": "Preliminary ranking. Optimizes objective delta only.",
        "status": "baseline_only",
    },
    {
        "ranking_profile_id": "balanced_operational",
        "description": "Balances objective, makespan, travel time, lateness, and replanning effort.",
        "status": "recommended_for_sensitivity_analysis",
    },
    {
        "ranking_profile_id": "makespan_priority",
        "description": "Prioritizes finishing earlier and penalizes makespan strongly.",
        "status": "recommended_for_sensitivity_analysis",
    },
    {
        "ranking_profile_id": "conservative_replanning",
        "description": "Penalizes unnecessary replanning and favors operational stability.",
        "status": "recommended_for_sensitivity_analysis",
    },
]

DEFAULT_REPLICATION_COUNT = 3


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


def estimate_descriptor(family_id: str, severity_id: str) -> str:
    if severity_id == "light":
        return "stable_low_disruption"

    if family_id == "reassignment_opportunity":
        return "reassignment_opportunity"

    if severity_id == "severe" and family_id == "combined_delay":
        return "high_impact_controlled_tradeoff"

    if severity_id == "severe":
        return "high_impact_delay"

    return "moderate_tradeoff"


def estimate_conservative_action(family_id: str, severity_id: str) -> str:
    if severity_id == "light":
        return "keep_current_plan_or_validate"

    if family_id == "reassignment_opportunity":
        return "test_replanning_opportunity"

    if severity_id == "severe":
        return "compare_policies_with_risk_monitoring"

    return "compare_policies_before_recommending"


def build_planned_rows(replication_count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for family in SCENARIO_FAMILIES:
        family_id = str(family["family_id"])

        for severity in SEVERITY_LEVELS:
            severity_id = str(severity["severity_id"])

            for replication_id in range(1, replication_count + 1):
                planned_run_id = (
                    f"planned_{family_id}_{severity_id}_rep{replication_id:03d}"
                )

                nominal_delay = int(severity["nominal_delay_minutes"])

                if bool(family["uses_travel_delay"]):
                    planned_travel_delay_minutes = nominal_delay
                else:
                    planned_travel_delay_minutes = 0

                if bool(family["uses_service_delay"]):
                    planned_service_delay_minutes = max(5, int(round(nominal_delay * 0.7)))
                else:
                    planned_service_delay_minutes = 0

                rows.append(
                    {
                        "planned_run_id": planned_run_id,
                        "scenario_family_id": family_id,
                        "severity_id": severity_id,
                        "replication_id": replication_id,
                        "planned_travel_delay_minutes": planned_travel_delay_minutes,
                        "planned_service_delay_minutes": planned_service_delay_minutes,
                        "creates_reassignment_opportunity": bool(
                            family["creates_reassignment_opportunity"]
                        ),
                        "expected_descriptor": estimate_descriptor(family_id, severity_id),
                        "conservative_action": estimate_conservative_action(
                            family_id, severity_id
                        ),
                        "planned_policy_option_count": len(POLICY_OPTIONS),
                        "planned_algorithm_run_count": len(POLICY_OPTIONS),
                        "status": "planned_not_executed",
                    }
                )

    return rows


def build_plan(rows: list[dict[str, Any]], replication_count: int) -> dict[str, Any]:
    total_algorithm_runs = sum(int(row["planned_algorithm_run_count"]) for row in rows)

    return {
        "plan_type": "fieldops_lab_experiment_campaign_plan",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "design_status": "planning_only",
        "replication_count_per_condition": replication_count,
        "scenario_family_count": len(SCENARIO_FAMILIES),
        "severity_level_count": len(SEVERITY_LEVELS),
        "policy_option_count": len(POLICY_OPTIONS),
        "ranking_profile_count": len(RANKING_PROFILES),
        "planned_condition_count": len(SCENARIO_FAMILIES) * len(SEVERITY_LEVELS),
        "planned_run_count": len(rows),
        "planned_algorithm_run_count": total_algorithm_runs,
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "scientific_status": "campaign_design_only",
        "warning": (
            "This is a campaign design plan. It does not execute experiments and does not prove scientific validity by itself."
        ),
    }


def write_json(
    output_path: Path,
    plan: dict[str, Any],
    rows: list[dict[str, Any]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "plan": plan,
        "severity_levels": SEVERITY_LEVELS,
        "scenario_families": SCENARIO_FAMILIES,
        "policy_options": POLICY_OPTIONS,
        "ranking_profiles": RANKING_PROFILES,
        "planned_runs": rows,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_csv(output_path: Path, rows: list[dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "planned_run_id",
        "scenario_family_id",
        "severity_id",
        "replication_id",
        "planned_travel_delay_minutes",
        "planned_service_delay_minutes",
        "creates_reassignment_opportunity",
        "expected_descriptor",
        "conservative_action",
        "planned_policy_option_count",
        "planned_algorithm_run_count",
        "status",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(
    output_path: Path,
    plan: dict[str, Any],
    rows: list[dict[str, Any]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    descriptor_counts: dict[str, int] = {}
    for row in rows:
        descriptor = str(row["expected_descriptor"])
        descriptor_counts[descriptor] = descriptor_counts.get(descriptor, 0) + 1

    lines: list[str] = []

    lines.append("# FieldOps Lab experiment campaign plan")
    lines.append("")
    lines.append("This file defines a planned experimental campaign. It is not an execution result.")
    lines.append("")

    lines.append("## Campaign design overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in [
        "design_status",
        "replication_count_per_condition",
        "scenario_family_count",
        "severity_level_count",
        "policy_option_count",
        "ranking_profile_count",
        "planned_condition_count",
        "planned_run_count",
        "planned_algorithm_run_count",
        "fuzzy_logic_status",
        "scientific_status",
    ]:
        lines.append(f"| {key} | {format_number(plan.get(key, ''))} |")
    lines.append("")

    lines.append("## Scenario families")
    lines.append("")
    lines.append("| Family | Travel delay | Service delay | Reassignment opportunity | Description |")
    lines.append("| --- | --- | --- | --- | --- |")
    for family in SCENARIO_FAMILIES:
        lines.append(
            "| "
            f"{family['family_id']} | "
            f"{format_number(family['uses_travel_delay'])} | "
            f"{format_number(family['uses_service_delay'])} | "
            f"{format_number(family['creates_reassignment_opportunity'])} | "
            f"{family['description']} |"
        )
    lines.append("")

    lines.append("## Severity levels")
    lines.append("")
    lines.append("| Severity | Nominal delay minutes | Description |")
    lines.append("| --- | ---: | --- |")
    for severity in SEVERITY_LEVELS:
        lines.append(
            "| "
            f"{severity['severity_id']} | "
            f"{severity['nominal_delay_minutes']} | "
            f"{severity['description']} |"
        )
    lines.append("")

    lines.append("## Policy options")
    lines.append("")
    lines.append("| Option | Policy | Method | Description |")
    lines.append("| --- | --- | --- | --- |")
    for option in POLICY_OPTIONS:
        lines.append(
            "| "
            f"{option['policy_option_id']} | "
            f"{option['policy_id']} | "
            f"{option['replanning_method_id']} | "
            f"{option['description']} |"
        )
    lines.append("")

    lines.append("## Ranking profiles to test later")
    lines.append("")
    lines.append("| Profile | Status | Description |")
    lines.append("| --- | --- | --- |")
    for profile in RANKING_PROFILES:
        lines.append(
            "| "
            f"{profile['ranking_profile_id']} | "
            f"{profile['status']} | "
            f"{profile['description']} |"
        )
    lines.append("")

    lines.append("## Expected descriptor distribution")
    lines.append("")
    lines.append("| Descriptor | Planned run count |")
    lines.append("| --- | ---: |")
    for descriptor in sorted(descriptor_counts):
        lines.append(f"| {descriptor} | {descriptor_counts[descriptor]} |")
    lines.append("")

    lines.append("## Planned runs")
    lines.append("")
    lines.append(
        "| Planned run | Family | Severity | Replication | Travel delay | Service delay | Descriptor | Conservative action |"
    )
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- | --- |")
    for row in rows:
        lines.append(
            "| "
            f"{row['planned_run_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['replication_id']} | "
            f"{row['planned_travel_delay_minutes']} | "
            f"{row['planned_service_delay_minutes']} | "
            f"{row['expected_descriptor']} | "
            f"{row['conservative_action']} |"
        )
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This plan is a bridge between the current handcrafted validation batch and a broader experimental campaign. "
        "It should be used to guide the next implementation step, which is generating or loading concrete batch configuration files from this design."
    )
    lines.append("")
    lines.append(
        "Fuzzy logic is intentionally not part of the main pipeline here. The campaign first needs broader controlled evidence, sensitivity analysis, and quality checks."
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) not in (4, 5):
        print(
            "Usage: py -3 analysis\\scripts\\generate_experiment_campaign_plan.py "
            "<output_md> <output_json> <output_csv> [replication_count]",
            file=sys.stderr,
        )
        return 2

    output_md = Path(sys.argv[1])
    output_json = Path(sys.argv[2])
    output_csv = Path(sys.argv[3])

    replication_count = DEFAULT_REPLICATION_COUNT
    if len(sys.argv) == 5:
        try:
            replication_count = int(sys.argv[4])
        except ValueError:
            print("ERROR: replication_count must be an integer.", file=sys.stderr)
            return 2

    if replication_count <= 0:
        print("ERROR: replication_count must be greater than zero.", file=sys.stderr)
        return 2

    rows = build_planned_rows(replication_count)
    plan = build_plan(rows, replication_count)

    write_markdown(output_md, plan, rows)
    write_json(output_json, plan, rows)
    write_csv(output_csv, rows)

    print(f"Experiment campaign plan markdown written to: {output_md}")
    print(f"Experiment campaign plan JSON written to: {output_json}")
    print(f"Experiment campaign plan CSV written to: {output_csv}")
    print(f"Planned runs: {plan['planned_run_count']}")
    print(f"Planned algorithm runs: {plan['planned_algorithm_run_count']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())