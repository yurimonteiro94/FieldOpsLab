from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


EXPECTED_FAMILIES = {
    "travel_delay_only",
    "service_delay_only",
    "combined_delay",
    "reassignment_opportunity",
}

EXPECTED_SEVERITIES = {
    "light",
    "moderate",
    "severe",
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


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


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

        if score > 0:
            return str(key)

    return ""


def get_perturbations(plan: dict[str, Any]) -> list[dict[str, Any]]:
    key = find_perturbation_array_key(plan)

    if not key:
        return []

    value = plan.get(key)

    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, dict)]


def perturbation_type(perturbation: dict[str, Any]) -> str:
    return str(perturbation.get("type", "")).upper()


def is_travel_perturbation(perturbation: dict[str, Any]) -> bool:
    kind = perturbation_type(perturbation)

    if "TRAVEL" in kind:
        return True

    keys = {str(key).lower() for key in perturbation.keys()}

    return "from_location_id" in keys and "to_location_id" in keys


def is_service_perturbation(perturbation: dict[str, Any]) -> bool:
    kind = perturbation_type(perturbation)

    if "SERVICE" in kind:
        return True

    keys = {str(key).lower() for key in perturbation.keys()}

    return "service" in " ".join(keys)


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

    return ""


def get_delay_value(perturbation: dict[str, Any]) -> int:
    key = find_delay_key(perturbation)

    if not key:
        return 0

    try:
        return int(perturbation[key])
    except (TypeError, ValueError):
        return 0


def expected_counts_for_family(family_id: str) -> tuple[int, int]:
    if family_id == "travel_delay_only":
        return 1, 0

    if family_id == "service_delay_only":
        return 0, 1

    if family_id == "combined_delay":
        return 1, 1

    if family_id == "reassignment_opportunity":
        return 1, 0

    return 0, 0


def verify_plan(row: dict[str, Any]) -> dict[str, Any]:
    path = Path(str(row.get("path", "")))
    family_id = str(row.get("scenario_family_id", ""))
    severity_id = str(row.get("severity_id", ""))

    problems: list[str] = []
    warnings: list[str] = []

    exists = path.exists()
    size_bytes = path.stat().st_size if exists else 0

    plan: dict[str, Any] = {}

    if not exists:
        problems.append(f"Plan file does not exist: {path}")
    else:
        try:
            plan = load_json(path)
        except RuntimeError as exc:
            problems.append(str(exc))
            plan = {}

    perturbations = get_perturbations(plan)
    travel_perturbations = [
        item for item in perturbations if is_travel_perturbation(item)
    ]
    service_perturbations = [
        item for item in perturbations if is_service_perturbation(item)
    ]

    expected_travel_count, expected_service_count = expected_counts_for_family(family_id)

    if family_id not in EXPECTED_FAMILIES:
        problems.append(f"Unexpected family: {family_id}")

    if severity_id not in EXPECTED_SEVERITIES:
        problems.append(f"Unexpected severity: {severity_id}")

    if len(travel_perturbations) != expected_travel_count:
        problems.append(
            "Unexpected travel perturbation count. "
            f"expected={expected_travel_count}; actual={len(travel_perturbations)}"
        )

    if len(service_perturbations) != expected_service_count:
        problems.append(
            "Unexpected service perturbation count. "
            f"expected={expected_service_count}; actual={len(service_perturbations)}"
        )

    expected_travel_delay = int(row.get("planned_travel_delay_minutes", 0))
    expected_service_delay = int(row.get("planned_service_delay_minutes", 0))

    actual_travel_delay = sum(get_delay_value(item) for item in travel_perturbations)
    actual_service_delay = sum(get_delay_value(item) for item in service_perturbations)

    if actual_travel_delay != expected_travel_delay:
        problems.append(
            "Unexpected total travel delay. "
            f"expected={expected_travel_delay}; actual={actual_travel_delay}"
        )

    if actual_service_delay != expected_service_delay:
        problems.append(
            "Unexpected total service delay. "
            f"expected={expected_service_delay}; actual={actual_service_delay}"
        )

    if family_id == "reassignment_opportunity" and not bool(
        row.get("creates_reassignment_opportunity", False)
    ):
        warnings.append(
            "Reassignment family is not marked as creating reassignment opportunity in index row."
        )

    semantic_status = str(plan.get("semantic_status", ""))

    if semantic_status != "family_specific_template_based_perturbation_plan":
        problems.append(
            "Unexpected semantic_status in plan. "
            f"expected=family_specific_template_based_perturbation_plan; actual={semantic_status}"
        )

    return {
        "perturbation_plan_id": str(row.get("perturbation_plan_id", "")),
        "path": str(path),
        "exists": exists,
        "size_bytes": size_bytes,
        "scenario_family_id": family_id,
        "severity_id": severity_id,
        "perturbation_count": len(perturbations),
        "travel_perturbation_count": len(travel_perturbations),
        "service_perturbation_count": len(service_perturbations),
        "expected_travel_delay": expected_travel_delay,
        "actual_travel_delay": actual_travel_delay,
        "expected_service_delay": expected_service_delay,
        "actual_service_delay": actual_service_delay,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "problems": problems,
        "warnings": warnings,
    }


def build_quality_report(index: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = index.get("plans")

    if not isinstance(rows, list):
        raise RuntimeError("Index JSON does not contain a plans array.")

    plan_rows = [row for row in rows if isinstance(row, dict)]
    checks = [verify_plan(row) for row in plan_rows]

    problems: list[str] = []
    warnings: list[str] = []

    expected_count = len(EXPECTED_FAMILIES) * len(EXPECTED_SEVERITIES)

    if len(checks) != expected_count:
        problems.append(
            f"Unexpected plan count. expected={expected_count}; actual={len(checks)}"
        )

    observed_pairs = {
        (check["scenario_family_id"], check["severity_id"])
        for check in checks
    }

    for family_id in EXPECTED_FAMILIES:
        for severity_id in EXPECTED_SEVERITIES:
            if (family_id, severity_id) not in observed_pairs:
                problems.append(f"Missing plan for family={family_id}; severity={severity_id}")

    for check in checks:
        problems.extend(str(problem) for problem in check["problems"])
        warnings.extend(str(warning) for warning in check["warnings"])

    quality = {
        "report_type": "fieldops_lab_campaign_perturbation_plan_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "checked_plan_count": len(checks),
        "expected_plan_count": expected_count,
        "generated_perturbation_plan_count": index.get(
            "generated_perturbation_plan_count",
            0,
        ),
        "generated_perturbation_count": index.get(
            "generated_perturbation_count",
            0,
        ),
        "semantic_status": index.get("semantic_status", ""),
        "scientific_status": index.get("scientific_status", ""),
        "fuzzy_logic_status": index.get("fuzzy_logic_status", ""),
        "problems": problems,
        "warnings": warnings,
        "plan_checks": checks,
    }

    return quality, checks


def write_markdown(path: Path, index_json_path: Path, quality: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign perturbation plan quality check")
    lines.append("")
    lines.append(f"Index JSON: `{index_json_path}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {yes_no(quality['all_required_checks_passed'])} |")
    lines.append(f"| problem_count | {format_number(quality['problem_count'])} |")
    lines.append(f"| warning_count | {format_number(quality['warning_count'])} |")
    lines.append(f"| checked_plan_count | {format_number(quality['checked_plan_count'])} |")
    lines.append(f"| expected_plan_count | {format_number(quality['expected_plan_count'])} |")
    lines.append(f"| generated_perturbation_count | {format_number(quality['generated_perturbation_count'])} |")
    lines.append(f"| semantic_status | {quality['semantic_status']} |")
    lines.append(f"| fuzzy_logic_status | {quality['fuzzy_logic_status']} |")
    lines.append("")
    lines.append("## Plan checks")
    lines.append("")
    lines.append("| Plan | Family | Severity | Exists | Travel delay | Service delay | Problems |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | --- |")

    for check in checks:
        problem_text = "none" if not check["problems"] else "; ".join(check["problems"])

        lines.append(
            "| "
            f"{check['perturbation_plan_id']} | "
            f"{check['scenario_family_id']} | "
            f"{check['severity_id']} | "
            f"{yes_no(check['exists'])} | "
            f"{format_number(check['actual_travel_delay'])} | "
            f"{format_number(check['actual_service_delay'])} | "
            f"{problem_text} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    if quality["problems"]:
        for problem in quality["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")

    if quality["warnings"]:
        for warning in quality["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if quality["all_required_checks_passed"]:
        lines.append(
            "The campaign perturbation plans passed the structural quality check. "
            "They are coherent enough to be connected to executable batch configs."
        )
    else:
        lines.append(
            "The campaign perturbation plans failed the quality check. "
            "Do not connect them to executable batch configs until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "Passing this check does not prove scientific validity. It only confirms that "
        "the generated perturbation plans match the intended family and severity structure."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, checks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "perturbation_plan_id",
        "path",
        "exists",
        "size_bytes",
        "scenario_family_id",
        "severity_id",
        "perturbation_count",
        "travel_perturbation_count",
        "service_perturbation_count",
        "expected_travel_delay",
        "actual_travel_delay",
        "expected_service_delay",
        "actual_service_delay",
        "problem_count",
        "warning_count",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for check in checks:
            writer.writerow({field: check.get(field, "") for field in fieldnames})


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_perturbation_plans.py "
            "<index_json> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    index_json_path = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        index = load_json(index_json_path)
        quality, checks = build_quality_report(index)

        write_markdown(output_md, index_json_path, quality, checks)
        write_json(output_json, quality)
        write_csv(output_csv, checks)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign perturbation plan quality report written to: {output_md}")
    print(f"Campaign perturbation plan quality JSON written to: {output_json}")
    print(f"Campaign perturbation plan quality CSV written to: {output_csv}")

    if not quality["all_required_checks_passed"]:
        print("ERROR: Campaign perturbation plan quality check failed.", file=sys.stderr)
        return 1

    print("Campaign perturbation plan quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())