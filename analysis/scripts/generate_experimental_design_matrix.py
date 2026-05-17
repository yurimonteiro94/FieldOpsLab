from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class InstanceSizeLevel:
    level_id: str
    customer_count: int
    technician_count: int
    time_horizon_minutes: int
    description: str


@dataclass(frozen=True)
class DemandDensityLevel:
    level_id: str
    demand_density_score: int
    geographic_spread: str
    description: str


@dataclass(frozen=True)
class DelayFamily:
    family_id: str
    uses_travel_delay: bool
    uses_service_delay: bool
    creates_reassignment_opportunity: bool
    description: str


@dataclass(frozen=True)
class DelaySeverity:
    severity_id: str
    nominal_delay_minutes: int
    severity_score: int
    description: str


@dataclass(frozen=True)
class PolicyCandidate:
    policy_id: str
    policy_family: str
    implementation_status: str
    description: str


INSTANCE_SIZE_LEVELS = [
    InstanceSizeLevel(
        level_id="small",
        customer_count=10,
        technician_count=2,
        time_horizon_minutes=480,
        description="Small diagnostic instance for fast validation and manual inspection.",
    ),
    InstanceSizeLevel(
        level_id="medium",
        customer_count=25,
        technician_count=4,
        time_horizon_minutes=480,
        description="Medium instance for realistic operational comparison.",
    ),
    InstanceSizeLevel(
        level_id="large",
        customer_count=50,
        technician_count=8,
        time_horizon_minutes=480,
        description="Large instance for stress testing and scalability checks.",
    ),
]

DEMAND_DENSITY_LEVELS = [
    DemandDensityLevel(
        level_id="sparse",
        demand_density_score=1,
        geographic_spread="wide",
        description="Low density demand, with larger travel separation between tasks.",
    ),
    DemandDensityLevel(
        level_id="moderate",
        demand_density_score=2,
        geographic_spread="balanced",
        description="Moderate density demand, used as the central experimental condition.",
    ),
    DemandDensityLevel(
        level_id="dense",
        demand_density_score=3,
        geographic_spread="compact",
        description="High density demand, with stronger reassignment and sequencing opportunities.",
    ),
]

DELAY_FAMILIES = [
    DelayFamily(
        family_id="travel_delay_only",
        uses_travel_delay=True,
        uses_service_delay=False,
        creates_reassignment_opportunity=False,
        description="Only travel time is perturbed.",
    ),
    DelayFamily(
        family_id="service_delay_only",
        uses_travel_delay=False,
        uses_service_delay=True,
        creates_reassignment_opportunity=False,
        description="Only service time is perturbed.",
    ),
    DelayFamily(
        family_id="combined_delay",
        uses_travel_delay=True,
        uses_service_delay=True,
        creates_reassignment_opportunity=False,
        description="Travel and service times are perturbed together.",
    ),
    DelayFamily(
        family_id="reassignment_opportunity",
        uses_travel_delay=True,
        uses_service_delay=True,
        creates_reassignment_opportunity=True,
        description="Perturbation creates a possible benefit for reassignment or resequencing.",
    ),
]

DELAY_SEVERITIES = [
    DelaySeverity(
        severity_id="light",
        nominal_delay_minutes=15,
        severity_score=1,
        description="Small disruption, useful to test whether replanning is unnecessary.",
    ),
    DelaySeverity(
        severity_id="moderate",
        nominal_delay_minutes=35,
        severity_score=2,
        description="Medium disruption, useful to test trade-offs between keeping and changing the plan.",
    ),
    DelaySeverity(
        severity_id="severe",
        nominal_delay_minutes=60,
        severity_score=3,
        description="Large disruption, useful to test whether replanning becomes necessary.",
    ),
]

POLICY_CANDIDATES = [
    PolicyCandidate(
        policy_id="no_replanning_policy_v1",
        policy_family="baseline",
        implementation_status="implemented",
        description="Baseline policy that keeps the original plan after perturbations.",
    ),
    PolicyCandidate(
        policy_id="threshold_delay_replanning_policy_v1",
        policy_family="trigger_based_replanning",
        implementation_status="implemented",
        description="Policy that triggers replanning when disruption severity crosses a threshold.",
    ),
]

RANDOM_SEEDS = [101, 202, 303]

REQUIRED_ROW_FIELDS = [
    "experiment_id",
    "scenario_id",
    "instance_size_level",
    "customer_count",
    "technician_count",
    "time_horizon_minutes",
    "demand_density_level",
    "demand_density_score",
    "geographic_spread",
    "delay_family_id",
    "uses_travel_delay",
    "uses_service_delay",
    "creates_reassignment_opportunity",
    "severity_id",
    "nominal_delay_minutes",
    "severity_score",
    "policy_id",
    "policy_family",
    "policy_implementation_status",
    "replication_id",
    "random_seed",
    "planned_outputs",
    "scientific_purpose",
    "status",
]


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def build_scenario_id(
    instance_size: InstanceSizeLevel,
    demand_density: DemandDensityLevel,
    delay_family: DelayFamily,
    severity: DelaySeverity,
) -> str:
    return (
        f"size_{instance_size.level_id}"
        f"_density_{demand_density.level_id}"
        f"_delay_{delay_family.family_id}"
        f"_severity_{severity.severity_id}"
    )


def build_experiment_id(
    scenario_id: str,
    policy: PolicyCandidate,
    replication_id: int,
) -> str:
    return f"{scenario_id}_policy_{policy.policy_id}_replication_{replication_id:02d}"


def build_scientific_purpose(
    instance_size: InstanceSizeLevel,
    demand_density: DemandDensityLevel,
    delay_family: DelayFamily,
    severity: DelaySeverity,
) -> str:
    return (
        f"Evaluate policy behavior for {instance_size.level_id} instances, "
        f"{demand_density.level_id} demand density, "
        f"{delay_family.family_id} perturbations, "
        f"and {severity.severity_id} delay severity."
    )


def build_row(
    instance_size: InstanceSizeLevel,
    demand_density: DemandDensityLevel,
    delay_family: DelayFamily,
    severity: DelaySeverity,
    policy: PolicyCandidate,
    replication_id: int,
    random_seed: int,
) -> dict[str, Any]:
    scenario_id = build_scenario_id(
        instance_size=instance_size,
        demand_density=demand_density,
        delay_family=delay_family,
        severity=severity,
    )

    return {
        "experiment_id": build_experiment_id(
            scenario_id=scenario_id,
            policy=policy,
            replication_id=replication_id,
        ),
        "scenario_id": scenario_id,
        "instance_size_level": instance_size.level_id,
        "customer_count": instance_size.customer_count,
        "technician_count": instance_size.technician_count,
        "time_horizon_minutes": instance_size.time_horizon_minutes,
        "demand_density_level": demand_density.level_id,
        "demand_density_score": demand_density.demand_density_score,
        "geographic_spread": demand_density.geographic_spread,
        "delay_family_id": delay_family.family_id,
        "uses_travel_delay": bool_text(delay_family.uses_travel_delay),
        "uses_service_delay": bool_text(delay_family.uses_service_delay),
        "creates_reassignment_opportunity": bool_text(
            delay_family.creates_reassignment_opportunity
        ),
        "severity_id": severity.severity_id,
        "nominal_delay_minutes": severity.nominal_delay_minutes,
        "severity_score": severity.severity_score,
        "policy_id": policy.policy_id,
        "policy_family": policy.policy_family,
        "policy_implementation_status": policy.implementation_status,
        "replication_id": replication_id,
        "random_seed": random_seed,
        "planned_outputs": (
            "scenario_result_json; scenario_result_csv; "
            "policy_metric_summary; statistical_comparison_input"
        ),
        "scientific_purpose": build_scientific_purpose(
            instance_size=instance_size,
            demand_density=demand_density,
            delay_family=delay_family,
            severity=severity,
        ),
        "status": "planned",
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for (
        instance_size,
        demand_density,
        delay_family,
        severity,
        policy,
        seed,
    ) in product(
        INSTANCE_SIZE_LEVELS,
        DEMAND_DENSITY_LEVELS,
        DELAY_FAMILIES,
        DELAY_SEVERITIES,
        POLICY_CANDIDATES,
        RANDOM_SEEDS,
    ):
        replication_id = RANDOM_SEEDS.index(seed) + 1
        rows.append(
            build_row(
                instance_size=instance_size,
                demand_density=demand_density,
                delay_family=delay_family,
                severity=severity,
                policy=policy,
                replication_id=replication_id,
                random_seed=seed,
            )
        )

    return rows


def build_factor_summary() -> dict[str, Any]:
    return {
        "instance_size_levels": [asdict(item) for item in INSTANCE_SIZE_LEVELS],
        "demand_density_levels": [asdict(item) for item in DEMAND_DENSITY_LEVELS],
        "delay_families": [asdict(item) for item in DELAY_FAMILIES],
        "delay_severities": [asdict(item) for item in DELAY_SEVERITIES],
        "policy_candidates": [asdict(item) for item in POLICY_CANDIDATES],
        "random_seeds": RANDOM_SEEDS,
    }


def build_report() -> dict[str, Any]:
    rows = build_rows()
    scenario_ids = sorted({row["scenario_id"] for row in rows})

    return {
        "report_type": "experimental_design_matrix",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "scientific_stage": "experimental_design",
        "acceptance_goal": (
            "Define a broader experimental design with controlled factors for "
            "instance size, demand density, delay type, delay severity, policy, "
            "and random seed."
        ),
        "factor_summary": build_factor_summary(),
        "summary": {
            "experiment_count": len(rows),
            "scenario_count": len(scenario_ids),
            "instance_size_level_count": len(INSTANCE_SIZE_LEVELS),
            "demand_density_level_count": len(DEMAND_DENSITY_LEVELS),
            "delay_family_count": len(DELAY_FAMILIES),
            "severity_count": len(DELAY_SEVERITIES),
            "policy_count": len(POLICY_CANDIDATES),
            "replication_count": len(RANDOM_SEEDS),
            "all_experiments_reproducible_from_explicit_factors": True,
        },
        "rows": rows,
        "conservative_interpretation": (
            "This matrix defines a reproducible experimental design. It does not "
            "prove scientific validity by itself. It prepares the project for "
            "replicated experiments and later statistical comparison."
        ),
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, report: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REQUIRED_ROW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in REQUIRED_ROW_FIELDS})


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    ensure_parent(path)

    summary = report["summary"]
    factor_summary = report["factor_summary"]
    rows = report["rows"]

    lines: list[str] = []
    lines.append("# FieldOps Lab experimental design matrix")
    lines.append("")
    lines.append(
        "This report defines the first broad experimental design matrix for the scientific validation phase."
    )
    lines.append("")
    lines.append(
        "It converts the current diagnostic state into planned, reproducible experiments."
    )
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Field", "Value"],
            [
                ["scientific_stage", report["scientific_stage"]],
                ["experiment_count", summary["experiment_count"]],
                ["scenario_count", summary["scenario_count"]],
                ["instance_size_level_count", summary["instance_size_level_count"]],
                ["demand_density_level_count", summary["demand_density_level_count"]],
                ["delay_family_count", summary["delay_family_count"]],
                ["severity_count", summary["severity_count"]],
                ["policy_count", summary["policy_count"]],
                ["replication_count", summary["replication_count"]],
                [
                    "all_experiments_reproducible_from_explicit_factors",
                    bool_text(
                        summary["all_experiments_reproducible_from_explicit_factors"]
                    ),
                ],
            ],
        )
    )

    lines.append("")
    lines.append("## Controlled factors")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Factor", "Levels"],
            [
                [
                    "instance_size",
                    "; ".join(
                        item["level_id"]
                        for item in factor_summary["instance_size_levels"]
                    ),
                ],
                [
                    "demand_density",
                    "; ".join(
                        item["level_id"]
                        for item in factor_summary["demand_density_levels"]
                    ),
                ],
                [
                    "delay_family",
                    "; ".join(item["family_id"] for item in factor_summary["delay_families"]),
                ],
                [
                    "delay_severity",
                    "; ".join(
                        item["severity_id"]
                        for item in factor_summary["delay_severities"]
                    ),
                ],
                [
                    "policy",
                    "; ".join(
                        item["policy_id"] for item in factor_summary["policy_candidates"]
                    ),
                ],
                ["random_seed", "; ".join(str(seed) for seed in factor_summary["random_seeds"])],
            ],
        )
    )

    lines.append("")
    lines.append("## Sample planned experiments")
    lines.append("")
    sample_rows = rows[:12]
    lines.extend(
        markdown_table(
            [
                "Experiment",
                "Size",
                "Density",
                "Delay family",
                "Severity",
                "Policy",
                "Seed",
            ],
            [
                [
                    row["experiment_id"],
                    row["instance_size_level"],
                    row["demand_density_level"],
                    row["delay_family_id"],
                    row["severity_id"],
                    row["policy_id"],
                    row["random_seed"],
                ]
                for row in sample_rows
            ],
        )
    )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(report["conservative_interpretation"])
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: generate_experimental_design_matrix.py "
            "<output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    output_md = Path(sys.argv[1])
    output_json = Path(sys.argv[2])
    output_csv = Path(sys.argv[3])

    report = build_report()
    rows = report["rows"]

    write_markdown(output_md, report)
    write_json(output_json, report)
    write_csv(output_csv, rows)

    print(f"Experimental design matrix markdown written to: {output_md}")
    print(f"Experimental design matrix JSON written to: {output_json}")
    print(f"Experimental design matrix CSV written to: {output_csv}")
    print("Experimental design matrix completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())