from __future__ import annotations

import copy
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {
    "light": 1,
    "moderate": 2,
    "severe": 3,
}


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


def normalize_path(path_text: str, reference_file: Path) -> Path:
    path = Path(path_text)

    if path.exists():
        return path

    candidate = reference_file.parent / path

    if candidate.exists():
        return candidate

    return path


def find_perturbation_array_key(plan: dict[str, Any]) -> str:
    preferred_keys = [
        "perturbations",
        "events",
        "planned_perturbations",
        "runtime_perturbations",
    ]

    for key in preferred_keys:
        value = plan.get(key)
        if isinstance(value, list):
            return key

    for key, value in plan.items():
        if not isinstance(value, list):
            continue

        object_count = sum(1 for item in value if isinstance(item, dict))

        if object_count == 0:
            continue

        score = 0

        for item in value:
            if not isinstance(item, dict):
                continue

            lowered_keys = {str(k).lower() for k in item.keys()}

            if "type" in lowered_keys:
                score += 2

            if any("delay" in key for key in lowered_keys):
                score += 2

            if "technician_id" in lowered_keys:
                score += 1

            if "task_id" in lowered_keys:
                score += 1

        if score > 0:
            return key

    raise RuntimeError("Could not identify perturbation array in perturbation plan.")


def get_perturbations(plan: dict[str, Any]) -> list[dict[str, Any]]:
    key = find_perturbation_array_key(plan)
    value = plan.get(key)

    if not isinstance(value, list):
        raise RuntimeError(f"Perturbation array is not a list. key={key}")

    perturbations = []

    for item in value:
        if isinstance(item, dict):
            perturbations.append(item)

    return perturbations


def perturbation_type(perturbation: dict[str, Any]) -> str:
    value = perturbation.get("type", "")
    return str(value).upper()


def is_travel_perturbation(perturbation: dict[str, Any]) -> bool:
    kind = str(perturbation.get("type", "")).upper()

    if "SERVICE" in kind:
        return False

    if "TRAVEL" in kind:
        return True

    keys = {str(key).lower() for key in perturbation.keys()}
    joined_keys = " ".join(keys)

    return (
        "from_location_id" in keys
        and "to_location_id" in keys
        and "service" not in joined_keys
    )
def is_service_perturbation(perturbation: dict[str, Any]) -> bool:
    kind = str(perturbation.get("type", "")).upper()

    if "TRAVEL" in kind:
        return False

    if "SERVICE" in kind:
        return True

    keys = {str(key).lower() for key in perturbation.keys()}
    joined_keys = " ".join(keys)

    return "current_task_id" in keys or "service" in joined_keys
def find_delay_key(perturbation: dict[str, Any]) -> str:
    preferred_keys = [
        "delay_duration",
        "delay_minutes",
        "duration",
        "duration_minutes",
    ]

    for key in preferred_keys:
        if key in perturbation and isinstance(perturbation[key], (int, float)):
            return key

    for key, value in perturbation.items():
        lowered = str(key).lower()

        if "delay" in lowered and isinstance(value, (int, float)):
            return str(key)

    raise RuntimeError(
        "Could not identify numeric delay key in perturbation: "
        f"{sorted(perturbation.keys())}"
    )


def set_delay_value(perturbation: dict[str, Any], delay_minutes: int) -> None:
    key = find_delay_key(perturbation)
    perturbation[key] = delay_minutes


def get_delay_value(perturbation: dict[str, Any]) -> int:
    key = find_delay_key(perturbation)
    return int(perturbation[key])


def update_perturbation_identity(
    perturbation: dict[str, Any],
    perturbation_id: str,
    description: str,
) -> None:
    if "perturbation_id" in perturbation:
        perturbation["perturbation_id"] = perturbation_id
    elif "id" in perturbation:
        perturbation["id"] = perturbation_id
    else:
        perturbation["perturbation_id"] = perturbation_id

    if "description" in perturbation:
        perturbation["description"] = description
    else:
        perturbation["description"] = description


def severity_from_text(text: str) -> str:
    lowered = text.lower()

    for severity in SEVERITY_ORDER:
        if severity in lowered:
            return severity

    return ""


def family_from_planned_run(row: dict[str, Any]) -> str:
    for key in ["scenario_family_id", "family_id", "family"]:
        value = row.get(key)

        if isinstance(value, str) and value:
            return value

    planned_run_id = str(row.get("planned_run_id", ""))

    for family in [
        "travel_delay_only",
        "service_delay_only",
        "combined_delay",
        "reassignment_opportunity",
    ]:
        if family in planned_run_id:
            return family

    return ""


def severity_from_planned_run(row: dict[str, Any]) -> str:
    for key in ["severity_id", "severity"]:
        value = row.get(key)

        if isinstance(value, str) and value:
            return value

    return severity_from_text(str(row.get("planned_run_id", "")))


def extract_planned_runs(campaign_plan: dict[str, Any]) -> list[dict[str, Any]]:
    value = campaign_plan.get("planned_runs")

    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    for key, candidate in campaign_plan.items():
        if not isinstance(candidate, list):
            continue

        dict_items = [item for item in candidate if isinstance(item, dict)]

        if not dict_items:
            continue

        first = dict_items[0]

        if "planned_run_id" in first or "scenario_family_id" in first:
            return dict_items

    raise RuntimeError("Could not find planned runs inside campaign plan JSON.")


def collect_sample_perturbation_templates(
    sample_batch_config: dict[str, Any],
    sample_batch_config_path: Path,
) -> dict[str, dict[str, Any]]:
    experiments = sample_batch_config.get("experiments")

    if not isinstance(experiments, list):
        raise RuntimeError("Sample batch config does not contain an experiments array.")

    templates: dict[str, dict[str, Any]] = {}

    for experiment in experiments:
        if not isinstance(experiment, dict):
            continue

        plan_path_text = str(experiment.get("perturbation_plan_path", ""))

        if not plan_path_text:
            continue

        plan_path = normalize_path(plan_path_text, sample_batch_config_path)

        if not plan_path.exists():
            raise RuntimeError(f"Perturbation plan path not found: {plan_path}")

        plan = load_json(plan_path)
        scenario_id = str(experiment.get("scenario_id", ""))
        plan_id = str(plan.get("perturbation_plan_id", plan_path.stem))
        severity = severity_from_text(scenario_id + " " + plan_id + " " + plan_path.name)

        if severity:
            templates[f"severity:{severity}"] = plan

        if "reassignment" in scenario_id.lower() or "reassignment" in plan_id.lower():
            templates["family:reassignment_opportunity"] = plan

    required_severities = ["light", "moderate", "severe"]

    missing = [
        severity
        for severity in required_severities
        if f"severity:{severity}" not in templates
    ]

    if missing:
        raise RuntimeError(f"Missing sample perturbation templates for severities: {missing}")

    return templates


def choose_template_plan(
    templates: dict[str, dict[str, Any]],
    family_id: str,
    severity_id: str,
) -> dict[str, Any]:
    if family_id == "reassignment_opportunity":
        reassignment_plan = templates.get("family:reassignment_opportunity")

        if reassignment_plan is not None:
            return reassignment_plan

    return templates[f"severity:{severity_id}"]


def find_required_template_perturbation(
    template_plan: dict[str, Any],
    wants_travel: bool,
) -> dict[str, Any]:
    perturbations = get_perturbations(template_plan)

    for perturbation in perturbations:
        if wants_travel and is_travel_perturbation(perturbation):
            return perturbation

        if not wants_travel and is_service_perturbation(perturbation):
            return perturbation

    kind = "travel" if wants_travel else "service"

    raise RuntimeError(f"Could not find {kind} perturbation in template plan.")


def planned_delay(row: dict[str, Any], key: str, default: int) -> int:
    value = row.get(key, default)

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_plan_from_group(
    family_id: str,
    severity_id: str,
    rows: list[dict[str, Any]],
    templates: dict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    if not rows:
        raise RuntimeError(f"Cannot build perturbation plan for empty group: {family_id}/{severity_id}")

    first_row = rows[0]

    travel_delay = planned_delay(first_row, "planned_travel_delay_minutes", 0)
    service_delay = planned_delay(first_row, "planned_service_delay_minutes", 0)

    wants_travel = travel_delay > 0
    wants_service = service_delay > 0

    template_plan = choose_template_plan(templates, family_id, severity_id)
    perturbation_array_key = find_perturbation_array_key(template_plan)

    generated_plan = copy.deepcopy(template_plan)
    generated_perturbations: list[dict[str, Any]] = []

    plan_id = f"campaign_{family_id}_{severity_id}_perturbation_plan"
    plan_name = f"Campaign perturbation plan: {family_id} / {severity_id}"

    if wants_travel:
        travel_template = find_required_template_perturbation(
            template_plan,
            wants_travel=True,
        )
        travel_perturbation = copy.deepcopy(travel_template)
        set_delay_value(travel_perturbation, travel_delay)
        update_perturbation_identity(
            travel_perturbation,
            f"{plan_id}_travel_delay",
            (
                "Campaign travel-delay perturbation generated from template. "
                f"family={family_id}; severity={severity_id}; delay={travel_delay}."
            ),
        )
        generated_perturbations.append(travel_perturbation)

    if wants_service:
        service_template = find_required_template_perturbation(
            template_plan,
            wants_travel=False,
        )
        service_perturbation = copy.deepcopy(service_template)
        set_delay_value(service_perturbation, service_delay)
        update_perturbation_identity(
            service_perturbation,
            f"{plan_id}_service_delay",
            (
                "Campaign service-delay perturbation generated from template. "
                f"family={family_id}; severity={severity_id}; delay={service_delay}."
            ),
        )
        generated_perturbations.append(service_perturbation)

    generated_plan["perturbation_plan_id"] = plan_id
    generated_plan["name"] = plan_name
    generated_plan["description"] = (
        "Family-specific campaign perturbation plan generated from the current "
        "sample perturbation templates. This is more semantically faithful than "
        "reusing one generic sample plan for every campaign batch."
    )
    generated_plan["scenario_family_id"] = family_id
    generated_plan["severity_id"] = severity_id
    generated_plan["planned_run_count"] = len(rows)
    generated_plan["generated_at_local"] = datetime.now().replace(microsecond=0).isoformat()
    generated_plan["semantic_status"] = "family_specific_template_based_perturbation_plan"
    generated_plan["scientific_status"] = "candidate_campaign_semantics"
    generated_plan[perturbation_array_key] = generated_perturbations

    metadata = {
        "perturbation_plan_id": plan_id,
        "scenario_family_id": family_id,
        "severity_id": severity_id,
        "planned_run_count": len(rows),
        "perturbation_count": len(generated_perturbations),
        "travel_perturbation_count": sum(
            1 for item in generated_perturbations if is_travel_perturbation(item)
        ),
        "service_perturbation_count": sum(
            1 for item in generated_perturbations if is_service_perturbation(item)
        ),
        "planned_travel_delay_minutes": travel_delay,
        "planned_service_delay_minutes": service_delay,
        "creates_reassignment_opportunity": bool(
            first_row.get("creates_reassignment_opportunity", False)
        ),
        "semantic_status": generated_plan["semantic_status"],
        "scientific_status": generated_plan["scientific_status"],
    }

    file_name = f"{plan_id}.json"

    return file_name, generated_plan, metadata


def group_planned_runs(
    planned_runs: list[dict[str, Any]]
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for row in planned_runs:
        family_id = family_from_planned_run(row)
        severity_id = severity_from_planned_run(row)

        if not family_id or not severity_id:
            raise RuntimeError(f"Could not identify family/severity for planned run: {row}")

        key = (family_id, severity_id)
        groups.setdefault(key, []).append(row)

    return groups


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "perturbation_plan_id",
        "path",
        "scenario_family_id",
        "severity_id",
        "planned_run_count",
        "perturbation_count",
        "travel_perturbation_count",
        "service_perturbation_count",
        "planned_travel_delay_minutes",
        "planned_service_delay_minutes",
        "creates_reassignment_opportunity",
        "semantic_status",
        "scientific_status",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(
    path: Path,
    output_plan_dir: Path,
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    total_plans = len(rows)
    total_perturbations = sum(int(row["perturbation_count"]) for row in rows)
    total_travel = sum(int(row["travel_perturbation_count"]) for row in rows)
    total_service = sum(int(row["service_perturbation_count"]) for row in rows)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign perturbation plan index")
    lines.append("")
    lines.append("This report indexes family-specific perturbation plans generated for the campaign.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| output_plan_dir | `{output_plan_dir}` |")
    lines.append(f"| generated_perturbation_plan_count | {total_plans} |")
    lines.append(f"| generated_perturbation_count | {total_perturbations} |")
    lines.append(f"| travel_perturbation_count | {total_travel} |")
    lines.append(f"| service_perturbation_count | {total_service} |")
    lines.append("| semantic_status | family_specific_template_based_perturbation_plan |")
    lines.append("| scientific_status | candidate_campaign_semantics |")
    lines.append("")
    lines.append("## Generated plans")
    lines.append("")
    lines.append("| Plan | Family | Severity | Travel delay | Service delay | Perturbations | Path |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- |")

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            str(row["scenario_family_id"]),
            SEVERITY_ORDER.get(str(row["severity_id"]), 99),
        ),
    )

    for row in sorted_rows:
        lines.append(
            "| "
            f"{row['perturbation_plan_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{format_number(row['planned_travel_delay_minutes'])} | "
            f"{format_number(row['planned_service_delay_minutes'])} | "
            f"{format_number(row['perturbation_count'])} | "
            f"`{row['path']}` |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "These files improve the campaign structure because each scenario family now has "
        "a dedicated perturbation plan instead of blindly reusing the same sample plan."
    )
    lines.append("")
    lines.append(
        "They are still template-based. This is acceptable as the next development step, "
        "but final scientific experiments should later calibrate perturbations against "
        "realistic or literature-backed distributions."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index_json(
    path: Path,
    source_sample_config: Path,
    source_campaign_plan: Path,
    output_plan_dir: Path,
    rows: list[dict[str, Any]],
) -> None:
    payload = {
        "index_type": "fieldops_lab_campaign_perturbation_plan_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "source_sample_config": str(source_sample_config),
        "source_campaign_plan": str(source_campaign_plan),
        "output_plan_dir": str(output_plan_dir),
        "generated_perturbation_plan_count": len(rows),
        "generated_perturbation_count": sum(int(row["perturbation_count"]) for row in rows),
        "travel_perturbation_count": sum(int(row["travel_perturbation_count"]) for row in rows),
        "service_perturbation_count": sum(int(row["service_perturbation_count"]) for row in rows),
        "semantic_status": "family_specific_template_based_perturbation_plan",
        "scientific_status": "candidate_campaign_semantics",
        "fuzzy_logic_status": "not_used_in_main_pipeline",
        "plans": rows,
        "interpretation": {
            "status": "perturbation_plan_generation_only",
            "warning": (
                "These plans are family-specific and executable candidates, but they are "
                "still generated from sample templates. They are not final scientific evidence."
            ),
        },
    }

    write_json(path, payload)


def main() -> int:
    if len(sys.argv) != 7:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_perturbation_plans.py "
            "<sample_batch_config> <campaign_plan_json> <output_plan_dir> "
            "<output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    sample_batch_config_path = Path(sys.argv[1])
    campaign_plan_path = Path(sys.argv[2])
    output_plan_dir = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])
    output_csv = Path(sys.argv[6])

    try:
        sample_batch_config = load_json(sample_batch_config_path)
        campaign_plan = load_json(campaign_plan_path)

        templates = collect_sample_perturbation_templates(
            sample_batch_config,
            sample_batch_config_path,
        )

        planned_runs = extract_planned_runs(campaign_plan)
        groups = group_planned_runs(planned_runs)

        output_plan_dir.mkdir(parents=True, exist_ok=True)

        rows: list[dict[str, Any]] = []

        for family_id, severity_id in sorted(
            groups.keys(),
            key=lambda item: (item[0], SEVERITY_ORDER.get(item[1], 99)),
        ):
            file_name, plan, metadata = build_plan_from_group(
                family_id,
                severity_id,
                groups[(family_id, severity_id)],
                templates,
            )

            plan_path = output_plan_dir / file_name
            write_json(plan_path, plan)

            metadata["path"] = str(plan_path)
            rows.append(metadata)

        write_markdown(output_md, output_plan_dir, rows)
        write_index_json(
            output_json,
            sample_batch_config_path,
            campaign_plan_path,
            output_plan_dir,
            rows,
        )
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign perturbation plans written to: {output_plan_dir}")
    print(f"Campaign perturbation plan index markdown written to: {output_md}")
    print(f"Campaign perturbation plan index JSON written to: {output_json}")
    print(f"Campaign perturbation plan index CSV written to: {output_csv}")
    print(f"Generated perturbation plans: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())