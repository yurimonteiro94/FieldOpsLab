from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Plan JSON not found: {path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"Plan JSON root must be an object: {path}")

    return data


def require_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)

    if not isinstance(value, dict):
        raise RuntimeError(f"Expected key '{key}' to be an object.")

    return value


def require_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)

    if not isinstance(value, list):
        raise RuntimeError(f"Expected key '{key}' to be a list.")

    return value


def as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default

    return default


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


def sanitize_id(value: str) -> str:
    result = []

    for char in value:
        if char.isalnum() or char in ("_", "-"):
            result.append(char)
        else:
            result.append("_")

    cleaned = "".join(result).strip("_")

    if not cleaned:
        return "unnamed"

    return cleaned


def build_lookup(items: list[Any], key: str) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    for item in items:
        if not isinstance(item, dict):
            continue

        item_id = item.get(key)

        if isinstance(item_id, str) and item_id:
            lookup[item_id] = item

    return lookup


def clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in output_dir.glob("*_blueprint.json"):
        if path.is_file:
            path.unlink()


def group_planned_runs(planned_runs: list[Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for item in planned_runs:
        if not isinstance(item, dict):
            continue

        family_id = str(item.get("scenario_family_id", ""))
        severity_id = str(item.get("severity_id", ""))

        key = (family_id, severity_id)

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(item)

    for runs in grouped.values():
        runs.sort(
            key=lambda run: (
                as_int(run.get("replication_id")),
                str(run.get("planned_run_id", "")),
            )
        )

    return grouped


def build_algorithm_runs(
    planned_runs: list[dict[str, Any]],
    policy_options: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    algorithm_runs: list[dict[str, Any]] = []

    for planned_run in planned_runs:
        planned_run_id = str(planned_run.get("planned_run_id", ""))

        for policy_option in policy_options:
            policy_option_id = str(policy_option.get("policy_option_id", ""))

            algorithm_run_id = f"{planned_run_id}__{policy_option_id}"

            algorithm_runs.append(
                {
                    "algorithm_run_id": algorithm_run_id,
                    "planned_run_id": planned_run_id,
                    "policy_option_id": policy_option_id,
                    "scenario_family_id": planned_run.get("scenario_family_id", ""),
                    "severity_id": planned_run.get("severity_id", ""),
                    "replication_id": planned_run.get("replication_id", 0),
                    "planned_travel_delay_minutes": planned_run.get("planned_travel_delay_minutes", 0),
                    "planned_service_delay_minutes": planned_run.get("planned_service_delay_minutes", 0),
                    "creates_reassignment_opportunity": planned_run.get(
                        "creates_reassignment_opportunity",
                        False,
                    ),
                    "expected_descriptor": planned_run.get("expected_descriptor", ""),
                    "conservative_action": planned_run.get("conservative_action", ""),
                    "policy_id": policy_option.get("policy_id", ""),
                    "replanning_method_id": policy_option.get("replanning_method_id", ""),
                    "execution_status": "planned_not_executed",
                    "configuration_status": "blueprint_not_executable_yet",
                }
            )

    return algorithm_runs


def build_blueprint(
    plan: dict[str, Any],
    source_plan_path: Path,
    family: dict[str, Any],
    severity: dict[str, Any],
    planned_runs: list[dict[str, Any]],
    policy_options: list[dict[str, Any]],
) -> dict[str, Any]:
    family_id = str(family.get("family_id", "unknown_family"))
    severity_id = str(severity.get("severity_id", "unknown_severity"))

    batch_id = f"campaign_{sanitize_id(family_id)}_{sanitize_id(severity_id)}_batch_blueprint"

    algorithm_runs = build_algorithm_runs(planned_runs, policy_options)

    replication_ids = sorted(
        {
            as_int(planned_run.get("replication_id"))
            for planned_run in planned_runs
        }
    )

    return {
        "blueprint_type": "fieldops_lab_campaign_batch_blueprint",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "executable_status": "blueprint_not_executable_yet",
        "source_plan": {
            "path": str(source_plan_path),
            "design_status": plan.get("design_status", ""),
            "fuzzy_logic_status": plan.get("fuzzy_logic_status", ""),
            "scientific_status": plan.get("scientific_status", ""),
        },
        "batch": {
            "batch_id": batch_id,
            "scenario_family_id": family_id,
            "severity_id": severity_id,
            "name": f"{family_id} / {severity_id}",
            "description": (
                "Planned campaign batch blueprint. "
                "This file organizes planned runs, but it is not an executable FieldOps Lab batch config yet."
            ),
            "replication_count": len(replication_ids),
            "planned_run_count": len(planned_runs),
            "policy_option_count": len(policy_options),
            "planned_algorithm_run_count": len(algorithm_runs),
        },
        "scenario_family": family,
        "severity": severity,
        "policy_options": policy_options,
        "planned_runs": planned_runs,
        "algorithm_runs": algorithm_runs,
        "quality_gate": {
            "planned_run_count_matches_replications": len(planned_runs) == len(replication_ids),
            "algorithm_run_count_matches_policy_options": len(algorithm_runs) == len(planned_runs) * len(policy_options),
        },
        "interpretation": {
            "status": "planning_blueprint_only",
            "warning": (
                "This blueprint is not yet executable. "
                "It should be used as an intermediate layer before generating concrete experiment JSON configs."
            ),
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "blueprint_path",
        "scenario_family_id",
        "severity_id",
        "replication_count",
        "planned_run_count",
        "policy_option_count",
        "planned_algorithm_run_count",
        "executable_status",
        "interpretation_status",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_index_json(
    path: Path,
    source_plan_path: Path,
    plan: dict[str, Any],
    index_rows: list[dict[str, Any]],
) -> None:
    total_planned_runs = sum(as_int(row.get("planned_run_count")) for row in index_rows)
    total_algorithm_runs = sum(as_int(row.get("planned_algorithm_run_count")) for row in index_rows)

    payload = {
        "index_type": "fieldops_lab_campaign_batch_blueprint_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "source_plan": {
            "path": str(source_plan_path),
            "design_status": plan.get("design_status", ""),
            "fuzzy_logic_status": plan.get("fuzzy_logic_status", ""),
            "scientific_status": plan.get("scientific_status", ""),
        },
        "campaign": {
            "blueprint_count": len(index_rows),
            "total_planned_run_count": total_planned_runs,
            "total_planned_algorithm_run_count": total_algorithm_runs,
            "executable_status": "blueprint_not_executable_yet",
        },
        "blueprints": index_rows,
        "interpretation": {
            "status": "planning_blueprint_index_only",
            "warning": (
                "This index organizes blueprint files. "
                "It does not execute experiments and does not prove scientific validity."
            ),
        },
    }

    write_json(path, payload)


def write_index_markdown(
    path: Path,
    source_plan_path: Path,
    plan: dict[str, Any],
    index_rows: list[dict[str, Any]],
) -> None:
    total_planned_runs = sum(as_int(row.get("planned_run_count")) for row in index_rows)
    total_algorithm_runs = sum(as_int(row.get("planned_algorithm_run_count")) for row in index_rows)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign batch blueprint index")
    lines.append("")
    lines.append("This report indexes campaign batch blueprints generated from the experiment campaign plan.")
    lines.append("")
    lines.append("## Source plan")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| source_plan_path | `{source_plan_path}` |")
    lines.append(f"| design_status | {plan.get('design_status', '')} |")
    lines.append(f"| fuzzy_logic_status | {plan.get('fuzzy_logic_status', '')} |")
    lines.append(f"| scientific_status | {plan.get('scientific_status', '')} |")
    lines.append("")

    lines.append("## Blueprint overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| blueprint_count | {format_number(len(index_rows))} |")
    lines.append(f"| total_planned_run_count | {format_number(total_planned_runs)} |")
    lines.append(f"| total_planned_algorithm_run_count | {format_number(total_algorithm_runs)} |")
    lines.append("| executable_status | blueprint_not_executable_yet |")
    lines.append("")

    lines.append("## Blueprints")
    lines.append("")
    lines.append(
        "| Batch | Family | Severity | Replications | Planned runs | Algorithm runs | Status |"
    )
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- |")

    for row in index_rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{format_number(row['replication_count'])} | "
            f"{format_number(row['planned_run_count'])} | "
            f"{format_number(row['planned_algorithm_run_count'])} | "
            f"{row['executable_status']} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "These blueprints are an intermediate planning layer. They organize future batches, but they are not executable experiment configs yet."
    )
    lines.append("")
    lines.append(
        "This is intentional. The project should first preserve a clean separation between campaign design, blueprint organization, executable configs, execution results, and scientific interpretation."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_batch_blueprints.py "
            "<plan_json> <output_blueprint_dir> <output_index_md> <output_index_json> <output_index_csv>",
            file=sys.stderr,
        )
        return 2

    plan_json_path = Path(sys.argv[1])
    output_blueprint_dir = Path(sys.argv[2])
    output_index_md = Path(sys.argv[3])
    output_index_json = Path(sys.argv[4])
    output_index_csv = Path(sys.argv[5])

    try:
        payload = load_json(plan_json_path)

        plan = require_dict(payload, "plan")
        scenario_families = require_list(payload, "scenario_families")
        severity_levels = require_list(payload, "severity_levels")
        policy_options_raw = require_list(payload, "policy_options")
        planned_runs_raw = require_list(payload, "planned_runs")

        policy_options = [
            item for item in policy_options_raw
            if isinstance(item, dict)
        ]

        planned_runs = [
            item for item in planned_runs_raw
            if isinstance(item, dict)
        ]

        family_lookup = build_lookup(scenario_families, "family_id")
        severity_lookup = build_lookup(severity_levels, "severity_id")

        grouped_runs = group_planned_runs(planned_runs)

        clean_output_dir(output_blueprint_dir)

        index_rows: list[dict[str, Any]] = []

        for key in sorted(grouped_runs.keys()):
            family_id, severity_id = key
            family = family_lookup.get(family_id, {"family_id": family_id})
            severity = severity_lookup.get(severity_id, {"severity_id": severity_id})
            group_runs = grouped_runs[key]

            blueprint = build_blueprint(
                plan,
                plan_json_path,
                family,
                severity,
                group_runs,
                policy_options,
            )

            batch = blueprint["batch"]
            batch_id = str(batch["batch_id"])
            blueprint_path = output_blueprint_dir / f"{batch_id}_blueprint.json"

            write_json(blueprint_path, blueprint)

            index_rows.append(
                {
                    "batch_id": batch_id,
                    "blueprint_path": str(blueprint_path),
                    "scenario_family_id": family_id,
                    "severity_id": severity_id,
                    "replication_count": batch.get("replication_count", 0),
                    "planned_run_count": batch.get("planned_run_count", 0),
                    "policy_option_count": batch.get("policy_option_count", 0),
                    "planned_algorithm_run_count": batch.get("planned_algorithm_run_count", 0),
                    "executable_status": blueprint.get("executable_status", ""),
                    "interpretation_status": blueprint.get("interpretation", {}).get("status", ""),
                }
            )

        write_index_markdown(output_index_md, plan_json_path, plan, index_rows)
        write_index_json(output_index_json, plan_json_path, plan, index_rows)
        write_csv(output_index_csv, index_rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign batch blueprints written to: {output_blueprint_dir}")
    print(f"Campaign batch blueprint index markdown written to: {output_index_md}")
    print(f"Campaign batch blueprint index JSON written to: {output_index_json}")
    print(f"Campaign batch blueprint index CSV written to: {output_index_csv}")
    print(f"Blueprint count: {len(index_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())