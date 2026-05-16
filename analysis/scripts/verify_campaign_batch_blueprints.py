from __future__ import annotations

import csv
import json
import sys
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
    except FileNotFoundError:
        raise RuntimeError(f"JSON file not found: {path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        raise RuntimeError(f"CSV file not found: {path}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(f"Text file not found: {path}")


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


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def format_number(value: Any) -> str:
    if isinstance(value, bool):
        return yes_no(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")

    if value is None:
        return ""

    return str(value)


def get_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)

    if isinstance(value, dict):
        return value

    return {}


def get_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)

    if isinstance(value, list):
        return value

    return []


def add_problem(problems: list[str], condition: bool, message: str) -> None:
    if not condition:
        problems.append(message)


def validate_blueprint_file(
    blueprint_path: Path,
    index_row: dict[str, Any],
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    result: dict[str, Any] = {
        "batch_id": index_row.get("batch_id", ""),
        "path": str(blueprint_path),
        "exists": blueprint_path.exists(),
        "size_bytes": blueprint_path.stat().st_size if blueprint_path.exists() else 0,
        "problem_count": 0,
        "warning_count": 0,
        "problems": problems,
        "warnings": warnings,
    }

    if not blueprint_path.exists():
        problems.append(f"Blueprint file does not exist: {blueprint_path}")
        result["problem_count"] = len(problems)
        result["warning_count"] = len(warnings)
        return result

    try:
        blueprint = load_json(blueprint_path)
    except RuntimeError as exc:
        problems.append(str(exc))
        result["problem_count"] = len(problems)
        result["warning_count"] = len(warnings)
        return result

    batch = get_dict(blueprint, "batch")
    source_plan = get_dict(blueprint, "source_plan")
    scenario_family = get_dict(blueprint, "scenario_family")
    severity = get_dict(blueprint, "severity")
    quality_gate = get_dict(blueprint, "quality_gate")
    interpretation = get_dict(blueprint, "interpretation")

    policy_options = get_list(blueprint, "policy_options")
    planned_runs = get_list(blueprint, "planned_runs")
    algorithm_runs = get_list(blueprint, "algorithm_runs")

    expected_batch_id = str(index_row.get("batch_id", ""))
    expected_family_id = str(index_row.get("scenario_family_id", ""))
    expected_severity_id = str(index_row.get("severity_id", ""))

    batch_id = str(batch.get("batch_id", ""))
    family_id = str(batch.get("scenario_family_id", ""))
    severity_id = str(batch.get("severity_id", ""))

    add_problem(
        problems,
        blueprint.get("blueprint_type") == "fieldops_lab_campaign_batch_blueprint",
        "Invalid blueprint_type.",
    )
    add_problem(
        problems,
        blueprint.get("executable_status") == "blueprint_not_executable_yet",
        "Blueprint executable_status should be blueprint_not_executable_yet.",
    )
    add_problem(
        problems,
        batch_id == expected_batch_id,
        f"Batch ID mismatch. Expected {expected_batch_id}, found {batch_id}.",
    )
    add_problem(
        problems,
        family_id == expected_family_id,
        f"Scenario family mismatch. Expected {expected_family_id}, found {family_id}.",
    )
    add_problem(
        problems,
        severity_id == expected_severity_id,
        f"Severity mismatch. Expected {expected_severity_id}, found {severity_id}.",
    )
    add_problem(
        problems,
        family_id in EXPECTED_FAMILIES,
        f"Unexpected scenario family: {family_id}.",
    )
    add_problem(
        problems,
        severity_id in EXPECTED_SEVERITIES,
        f"Unexpected severity: {severity_id}.",
    )

    add_problem(
        problems,
        source_plan.get("fuzzy_logic_status") == "not_used_in_main_pipeline",
        "Fuzzy logic should not be used in the main pipeline at this stage.",
    )
    add_problem(
        problems,
        source_plan.get("scientific_status") == "campaign_design_only",
        "Source plan scientific_status should be campaign_design_only.",
    )

    planned_run_count = as_int(batch.get("planned_run_count"))
    policy_option_count = as_int(batch.get("policy_option_count"))
    algorithm_run_count = as_int(batch.get("planned_algorithm_run_count"))

    add_problem(
        problems,
        planned_run_count == len(planned_runs),
        f"planned_run_count mismatch. Batch says {planned_run_count}, file has {len(planned_runs)}.",
    )
    add_problem(
        problems,
        policy_option_count == len(policy_options),
        f"policy_option_count mismatch. Batch says {policy_option_count}, file has {len(policy_options)}.",
    )
    add_problem(
        problems,
        algorithm_run_count == len(algorithm_runs),
        f"planned_algorithm_run_count mismatch. Batch says {algorithm_run_count}, file has {len(algorithm_runs)}.",
    )
    add_problem(
        problems,
        len(planned_runs) == 3,
        f"Each blueprint should currently have 3 planned runs. Found {len(planned_runs)}.",
    )
    add_problem(
        problems,
        len(policy_options) == 3,
        f"Each blueprint should currently have 3 policy options. Found {len(policy_options)}.",
    )
    add_problem(
        problems,
        len(algorithm_runs) == 9,
        f"Each blueprint should currently have 9 algorithm runs. Found {len(algorithm_runs)}.",
    )
    add_problem(
        problems,
        len(algorithm_runs) == len(planned_runs) * len(policy_options),
        "Algorithm run count should equal planned_run_count * policy_option_count.",
    )

    planned_run_ids = [
        str(run.get("planned_run_id", ""))
        for run in planned_runs
        if isinstance(run, dict)
    ]
    policy_option_ids = [
        str(option.get("policy_option_id", ""))
        for option in policy_options
        if isinstance(option, dict)
    ]
    algorithm_run_ids = [
        str(run.get("algorithm_run_id", ""))
        for run in algorithm_runs
        if isinstance(run, dict)
    ]

    add_problem(
        problems,
        len(planned_run_ids) == len(set(planned_run_ids)),
        "Duplicate planned_run_id values detected.",
    )
    add_problem(
        problems,
        len(policy_option_ids) == len(set(policy_option_ids)),
        "Duplicate policy_option_id values detected.",
    )
    add_problem(
        problems,
        len(algorithm_run_ids) == len(set(algorithm_run_ids)),
        "Duplicate algorithm_run_id values detected.",
    )

    planned_run_id_set = set(planned_run_ids)
    policy_option_id_set = set(policy_option_ids)

    for run in planned_runs:
        if not isinstance(run, dict):
            problems.append("A planned run is not a JSON object.")
            continue

        add_problem(
            problems,
            run.get("scenario_family_id") == family_id,
            f"Planned run {run.get('planned_run_id', '')} has wrong scenario_family_id.",
        )
        add_problem(
            problems,
            run.get("severity_id") == severity_id,
            f"Planned run {run.get('planned_run_id', '')} has wrong severity_id.",
        )
        add_problem(
            problems,
            run.get("status") == "planned_not_executed",
            f"Planned run {run.get('planned_run_id', '')} should have status planned_not_executed.",
        )

    for run in algorithm_runs:
        if not isinstance(run, dict):
            problems.append("An algorithm run is not a JSON object.")
            continue

        planned_run_id = str(run.get("planned_run_id", ""))
        policy_option_id = str(run.get("policy_option_id", ""))

        add_problem(
            problems,
            planned_run_id in planned_run_id_set,
            f"Algorithm run {run.get('algorithm_run_id', '')} references unknown planned_run_id {planned_run_id}.",
        )
        add_problem(
            problems,
            policy_option_id in policy_option_id_set,
            f"Algorithm run {run.get('algorithm_run_id', '')} references unknown policy_option_id {policy_option_id}.",
        )
        add_problem(
            problems,
            run.get("execution_status") == "planned_not_executed",
            f"Algorithm run {run.get('algorithm_run_id', '')} should have execution_status planned_not_executed.",
        )
        add_problem(
            problems,
            run.get("configuration_status") == "blueprint_not_executable_yet",
            f"Algorithm run {run.get('algorithm_run_id', '')} should have configuration_status blueprint_not_executable_yet.",
        )

    add_problem(
        problems,
        quality_gate.get("planned_run_count_matches_replications") is True,
        "Quality gate planned_run_count_matches_replications should be true.",
    )
    add_problem(
        problems,
        quality_gate.get("algorithm_run_count_matches_policy_options") is True,
        "Quality gate algorithm_run_count_matches_policy_options should be true.",
    )
    add_problem(
        problems,
        interpretation.get("status") == "planning_blueprint_only",
        "Interpretation status should be planning_blueprint_only.",
    )

    result["blueprint_type"] = blueprint.get("blueprint_type", "")
    result["executable_status"] = blueprint.get("executable_status", "")
    result["scenario_family_id"] = family_id
    result["severity_id"] = severity_id
    result["planned_run_count"] = len(planned_runs)
    result["policy_option_count"] = len(policy_options)
    result["planned_algorithm_run_count"] = len(algorithm_runs)
    result["problem_count"] = len(problems)
    result["warning_count"] = len(warnings)

    return result


def validate_campaign_blueprints(
    index_json_path: Path,
    index_markdown_path: Path,
    index_csv_path: Path,
    blueprint_dir: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    index_payload = load_json(index_json_path)
    csv_rows = load_csv_rows(index_csv_path)
    markdown_text = read_text(index_markdown_path)

    campaign = get_dict(index_payload, "campaign")
    blueprints = get_list(index_payload, "blueprints")
    source_plan = get_dict(index_payload, "source_plan")

    add_problem(
        problems,
        index_payload.get("index_type") == "fieldops_lab_campaign_batch_blueprint_index",
        "Invalid index_type.",
    )
    add_problem(
        problems,
        "# FieldOps Lab campaign batch blueprint index" in markdown_text,
        "Expected markdown title was not found.",
    )
    add_problem(
        problems,
        blueprint_dir.exists() and blueprint_dir.is_dir(),
        f"Blueprint directory does not exist: {blueprint_dir}",
    )
    add_problem(
        problems,
        source_plan.get("fuzzy_logic_status") == "not_used_in_main_pipeline",
        "Fuzzy logic should not be used in the main pipeline.",
    )
    add_problem(
        problems,
        source_plan.get("scientific_status") == "campaign_design_only",
        "Source scientific_status should be campaign_design_only.",
    )

    blueprint_count = as_int(campaign.get("blueprint_count"))
    total_planned_run_count = as_int(campaign.get("total_planned_run_count"))
    total_planned_algorithm_run_count = as_int(campaign.get("total_planned_algorithm_run_count"))

    add_problem(
        problems,
        blueprint_count == 12,
        f"Expected 12 blueprints. Found {blueprint_count}.",
    )
    add_problem(
        problems,
        total_planned_run_count == 36,
        f"Expected 36 planned runs. Found {total_planned_run_count}.",
    )
    add_problem(
        problems,
        total_planned_algorithm_run_count == 108,
        f"Expected 108 planned algorithm runs. Found {total_planned_algorithm_run_count}.",
    )
    add_problem(
        problems,
        len(blueprints) == blueprint_count,
        f"Index blueprint list count mismatch. Campaign says {blueprint_count}, list has {len(blueprints)}.",
    )
    add_problem(
        problems,
        len(csv_rows) == blueprint_count,
        f"CSV row count mismatch. Expected {blueprint_count}, found {len(csv_rows)}.",
    )
    add_problem(
        problems,
        campaign.get("executable_status") == "blueprint_not_executable_yet",
        "Campaign executable_status should be blueprint_not_executable_yet.",
    )

    expected_pairs = {
        (family, severity)
        for family in EXPECTED_FAMILIES
        for severity in EXPECTED_SEVERITIES
    }

    found_pairs: set[tuple[str, str]] = set()
    batch_ids: list[str] = []
    blueprint_checks: list[dict[str, Any]] = []

    for item in blueprints:
        if not isinstance(item, dict):
            problems.append("A blueprint index row is not a JSON object.")
            continue

        batch_id = str(item.get("batch_id", ""))
        family_id = str(item.get("scenario_family_id", ""))
        severity_id = str(item.get("severity_id", ""))
        blueprint_path = Path(str(item.get("blueprint_path", "")))

        batch_ids.append(batch_id)
        found_pairs.add((family_id, severity_id))

        add_problem(
            problems,
            batch_id != "",
            "Blueprint index row has empty batch_id.",
        )
        add_problem(
            problems,
            family_id in EXPECTED_FAMILIES,
            f"Unexpected family in index: {family_id}.",
        )
        add_problem(
            problems,
            severity_id in EXPECTED_SEVERITIES,
            f"Unexpected severity in index: {severity_id}.",
        )
        add_problem(
            problems,
            as_int(item.get("replication_count")) == 3,
            f"Index row {batch_id} should have replication_count 3.",
        )
        add_problem(
            problems,
            as_int(item.get("planned_run_count")) == 3,
            f"Index row {batch_id} should have planned_run_count 3.",
        )
        add_problem(
            problems,
            as_int(item.get("policy_option_count")) == 3,
            f"Index row {batch_id} should have policy_option_count 3.",
        )
        add_problem(
            problems,
            as_int(item.get("planned_algorithm_run_count")) == 9,
            f"Index row {batch_id} should have planned_algorithm_run_count 9.",
        )
        add_problem(
            problems,
            item.get("executable_status") == "blueprint_not_executable_yet",
            f"Index row {batch_id} should have executable_status blueprint_not_executable_yet.",
        )
        add_problem(
            problems,
            item.get("interpretation_status") == "planning_blueprint_only",
            f"Index row {batch_id} should have interpretation_status planning_blueprint_only.",
        )

        blueprint_checks.append(validate_blueprint_file(blueprint_path, item))

    add_problem(
        problems,
        len(batch_ids) == len(set(batch_ids)),
        "Duplicate batch IDs detected in blueprint index.",
    )
    add_problem(
        problems,
        found_pairs == expected_pairs,
        "Blueprint family/severity coverage does not match the expected 4 x 3 campaign design.",
    )

    for check in blueprint_checks:
        for problem in check["problems"]:
            problems.append(f"{check['batch_id']}: {problem}")

        for warning in check["warnings"]:
            warnings.append(f"{check['batch_id']}: {warning}")

    all_required_checks_passed = len(problems) == 0

    return {
        "report_type": "fieldops_lab_campaign_batch_blueprint_quality_check",
        "index_json_path": str(index_json_path),
        "index_markdown_path": str(index_markdown_path),
        "index_csv_path": str(index_csv_path),
        "blueprint_dir": str(blueprint_dir),
        "all_required_checks_passed": all_required_checks_passed,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "blueprint_count": len(blueprint_checks),
        "campaign_values": {
            "blueprint_count": blueprint_count,
            "total_planned_run_count": total_planned_run_count,
            "total_planned_algorithm_run_count": total_planned_algorithm_run_count,
            "executable_status": campaign.get("executable_status", ""),
            "fuzzy_logic_status": source_plan.get("fuzzy_logic_status", ""),
            "scientific_status": source_plan.get("scientific_status", ""),
        },
        "blueprint_checks": blueprint_checks,
        "problems": problems,
        "warnings": warnings,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    campaign_values = report["campaign_values"]

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign batch blueprint quality check")
    lines.append("")
    lines.append(f"Index JSON: `{report['index_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {yes_no(bool(report['all_required_checks_passed']))} |")
    lines.append(f"| problem_count | {format_number(report['problem_count'])} |")
    lines.append(f"| warning_count | {format_number(report['warning_count'])} |")
    lines.append(f"| blueprint_count | {format_number(report['blueprint_count'])} |")
    lines.append(f"| blueprint_dir | `{report['blueprint_dir']}` |")
    lines.append("")

    lines.append("## Campaign values")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| blueprint_count | {format_number(campaign_values['blueprint_count'])} |")
    lines.append(f"| total_planned_run_count | {format_number(campaign_values['total_planned_run_count'])} |")
    lines.append(f"| total_planned_algorithm_run_count | {format_number(campaign_values['total_planned_algorithm_run_count'])} |")
    lines.append(f"| executable_status | {campaign_values['executable_status']} |")
    lines.append(f"| fuzzy_logic_status | {campaign_values['fuzzy_logic_status']} |")
    lines.append(f"| scientific_status | {campaign_values['scientific_status']} |")
    lines.append("")

    lines.append("## Blueprint checks")
    lines.append("")
    lines.append("| Batch | Exists | Size bytes | Planned runs | Policy options | Algorithm runs | Problems |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")

    for check in report["blueprint_checks"]:
        problem_text = "none" if not check["problems"] else "; ".join(check["problems"])
        lines.append(
            "| "
            f"{check['batch_id']} | "
            f"{yes_no(bool(check['exists']))} | "
            f"{format_number(check['size_bytes'])} | "
            f"{format_number(check.get('planned_run_count', 0))} | "
            f"{format_number(check.get('policy_option_count', 0))} | "
            f"{format_number(check.get('planned_algorithm_run_count', 0))} | "
            f"{problem_text} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    if report["problems"]:
        for problem in report["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")

    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if report["all_required_checks_passed"]:
        lines.append(
            "The campaign batch blueprints passed the structural quality check. "
            "They are coherent enough to be used as input for the next implementation step."
        )
        lines.append("")
        lines.append(
            "They are still not executable experiment configs. The next step should convert these blueprints into concrete batch configuration JSON files or build a generator for those configs."
        )
    else:
        lines.append(
            "The campaign batch blueprints did not pass the structural quality check. "
            "Do not use them as a basis for executable configs until the listed problems are corrected."
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 7:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_batch_blueprints.py "
            "<index_json> <index_md> <index_csv> <blueprint_dir> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    index_json_path = Path(sys.argv[1])
    index_markdown_path = Path(sys.argv[2])
    index_csv_path = Path(sys.argv[3])
    blueprint_dir = Path(sys.argv[4])
    output_md = Path(sys.argv[5])
    output_json = Path(sys.argv[6])

    try:
        report = validate_campaign_blueprints(
            index_json_path,
            index_markdown_path,
            index_csv_path,
            blueprint_dir,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_markdown(output_md, report)
    write_json(output_json, report)

    print(f"Campaign batch blueprint quality report written to: {output_md}")
    print(f"Campaign batch blueprint quality JSON written to: {output_json}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Campaign batch blueprint quality check failed.", file=sys.stderr)
        return 1

    print("Campaign batch blueprint quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())