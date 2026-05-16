from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_PLAN_KEYS = [
    "plan_type",
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
]

REQUIRED_RUN_KEYS = [
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


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(f"Text file not found: {path}")


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        raise RuntimeError(f"CSV file not found: {path}")


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


def add_problem(problems: list[str], message: str) -> None:
    problems.append(message)


def add_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def require_list(payload: dict[str, Any], key: str, problems: list[str]) -> list[Any]:
    value = payload.get(key)

    if not isinstance(value, list):
        add_problem(problems, f"Expected JSON key '{key}' to be a list.")
        return []

    return value


def require_dict(payload: dict[str, Any], key: str, problems: list[str]) -> dict[str, Any]:
    value = payload.get(key)

    if not isinstance(value, dict):
        add_problem(problems, f"Expected JSON key '{key}' to be an object.")
        return {}

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


def check_required_plan_keys(plan: dict[str, Any], problems: list[str]) -> None:
    for key in REQUIRED_PLAN_KEYS:
        if key not in plan:
            add_problem(problems, f"Plan is missing required key: {key}")


def check_basic_files(
    markdown_text: str,
    csv_rows: list[dict[str, str]],
    problems: list[str],
) -> None:
    if "# FieldOps Lab experiment campaign plan" not in markdown_text:
        add_problem(
            problems,
            "Markdown plan does not contain the expected title.",
        )

    if not csv_rows:
        add_problem(problems, "Campaign plan CSV has no data rows.")
        return

    csv_fields = set(csv_rows[0].keys())

    for key in REQUIRED_RUN_KEYS:
        if key not in csv_fields:
            add_problem(problems, f"Campaign plan CSV is missing column: {key}")


def check_plan_counts(
    plan: dict[str, Any],
    scenario_families: list[Any],
    severity_levels: list[Any],
    policy_options: list[Any],
    ranking_profiles: list[Any],
    planned_runs: list[Any],
    csv_rows: list[dict[str, str]],
    problems: list[str],
) -> None:
    replication_count = as_int(plan.get("replication_count_per_condition"))
    scenario_family_count = len(scenario_families)
    severity_level_count = len(severity_levels)
    policy_option_count = len(policy_options)
    ranking_profile_count = len(ranking_profiles)
    planned_condition_count = scenario_family_count * severity_level_count
    planned_run_count = len(planned_runs)
    planned_algorithm_run_count = planned_run_count * policy_option_count

    expected_values = {
        "scenario_family_count": scenario_family_count,
        "severity_level_count": severity_level_count,
        "policy_option_count": policy_option_count,
        "ranking_profile_count": ranking_profile_count,
        "planned_condition_count": planned_condition_count,
        "planned_run_count": planned_run_count,
        "planned_algorithm_run_count": planned_algorithm_run_count,
    }

    if replication_count <= 0:
        add_problem(problems, "replication_count_per_condition must be greater than zero.")

    for key, expected_value in expected_values.items():
        actual_value = as_int(plan.get(key))

        if actual_value != expected_value:
            add_problem(
                problems,
                f"Plan count mismatch for {key}. Expected {expected_value}, found {actual_value}.",
            )

    if len(csv_rows) != planned_run_count:
        add_problem(
            problems,
            f"CSV row count mismatch. Expected {planned_run_count}, found {len(csv_rows)}.",
        )


def check_plan_status(plan: dict[str, Any], problems: list[str], warnings: list[str]) -> None:
    plan_type = str(plan.get("plan_type", ""))
    design_status = str(plan.get("design_status", ""))
    fuzzy_logic_status = str(plan.get("fuzzy_logic_status", ""))
    scientific_status = str(plan.get("scientific_status", ""))

    if plan_type != "fieldops_lab_experiment_campaign_plan":
        add_problem(
            problems,
            f"Unexpected plan_type. Expected fieldops_lab_experiment_campaign_plan, found {plan_type}.",
        )

    if design_status != "planning_only":
        add_problem(
            problems,
            f"Unexpected design_status. Expected planning_only, found {design_status}.",
        )

    if fuzzy_logic_status != "not_used_in_main_pipeline":
        add_problem(
            problems,
            f"Unexpected fuzzy_logic_status. Expected not_used_in_main_pipeline, found {fuzzy_logic_status}.",
        )

    if scientific_status != "campaign_design_only":
        add_warning(
            warnings,
            f"Unexpected scientific_status for a planning file: {scientific_status}.",
        )


def extract_ids(items: list[Any], key: str, problems: list[str]) -> list[str]:
    ids: list[str] = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            add_problem(problems, f"Item {index} in list for {key} is not an object.")
            continue

        value = item.get(key)

        if not isinstance(value, str) or not value.strip():
            add_problem(problems, f"Item {index} is missing non-empty id key: {key}")
            continue

        ids.append(value)

    return ids


def check_policy_options(policy_options: list[Any], problems: list[str]) -> None:
    seen: set[str] = set()

    for index, item in enumerate(policy_options):
        if not isinstance(item, dict):
            add_problem(problems, f"Policy option {index} is not an object.")
            continue

        option_id = str(item.get("policy_option_id", ""))
        policy_id = str(item.get("policy_id", ""))
        method_id = str(item.get("replanning_method_id", ""))

        if not option_id:
            add_problem(problems, f"Policy option {index} has empty policy_option_id.")

        if option_id in seen:
            add_problem(problems, f"Duplicate policy_option_id found: {option_id}")

        seen.add(option_id)

        if not policy_id:
            add_problem(problems, f"Policy option {option_id} has empty policy_id.")

        if not method_id:
            add_problem(problems, f"Policy option {option_id} has empty replanning_method_id.")


def check_planned_runs(
    planned_runs: list[Any],
    csv_rows: list[dict[str, str]],
    scenario_family_ids: list[str],
    severity_ids: list[str],
    policy_option_count: int,
    replication_count: int,
    problems: list[str],
    warnings: list[str],
) -> None:
    seen_run_ids: set[str] = set()
    coverage: dict[tuple[str, str, int], int] = {}

    for index, item in enumerate(planned_runs):
        if not isinstance(item, dict):
            add_problem(problems, f"Planned run {index} is not an object.")
            continue

        for key in REQUIRED_RUN_KEYS:
            if key not in item:
                add_problem(problems, f"Planned run {index} is missing key: {key}")

        planned_run_id = str(item.get("planned_run_id", ""))
        family_id = str(item.get("scenario_family_id", ""))
        severity_id = str(item.get("severity_id", ""))
        replication_id = as_int(item.get("replication_id"))
        travel_delay = as_int(item.get("planned_travel_delay_minutes"))
        service_delay = as_int(item.get("planned_service_delay_minutes"))
        option_count = as_int(item.get("planned_policy_option_count"))
        algorithm_run_count = as_int(item.get("planned_algorithm_run_count"))
        status = str(item.get("status", ""))

        if not planned_run_id:
            add_problem(problems, f"Planned run {index} has empty planned_run_id.")

        if planned_run_id in seen_run_ids:
            add_problem(problems, f"Duplicate planned_run_id found: {planned_run_id}")

        seen_run_ids.add(planned_run_id)

        if family_id not in scenario_family_ids:
            add_problem(
                problems,
                f"Planned run {planned_run_id} uses unknown scenario_family_id: {family_id}",
            )

        if severity_id not in severity_ids:
            add_problem(
                problems,
                f"Planned run {planned_run_id} uses unknown severity_id: {severity_id}",
            )

        if replication_id < 1 or replication_id > replication_count:
            add_problem(
                problems,
                f"Planned run {planned_run_id} has invalid replication_id: {replication_id}",
            )

        if travel_delay < 0:
            add_problem(
                problems,
                f"Planned run {planned_run_id} has negative travel delay: {travel_delay}",
            )

        if service_delay < 0:
            add_problem(
                problems,
                f"Planned run {planned_run_id} has negative service delay: {service_delay}",
            )

        if travel_delay == 0 and service_delay == 0:
            add_warning(
                warnings,
                f"Planned run {planned_run_id} has no travel or service delay.",
            )

        if option_count != policy_option_count:
            add_problem(
                problems,
                f"Planned run {planned_run_id} has policy option count {option_count}, expected {policy_option_count}.",
            )

        if algorithm_run_count != policy_option_count:
            add_problem(
                problems,
                f"Planned run {planned_run_id} has algorithm run count {algorithm_run_count}, expected {policy_option_count}.",
            )

        if status != "planned_not_executed":
            add_problem(
                problems,
                f"Planned run {planned_run_id} has unexpected status: {status}",
            )

        coverage_key = (family_id, severity_id, replication_id)
        coverage[coverage_key] = coverage.get(coverage_key, 0) + 1

    for family_id in scenario_family_ids:
        for severity_id in severity_ids:
            for replication_id in range(1, replication_count + 1):
                key = (family_id, severity_id, replication_id)
                count = coverage.get(key, 0)

                if count != 1:
                    add_problem(
                        problems,
                        "Coverage mismatch. "
                        f"family={family_id}, severity={severity_id}, replication={replication_id}, count={count}.",
                    )

    csv_run_ids = {row.get("planned_run_id", "") for row in csv_rows}
    json_run_ids = seen_run_ids

    if csv_run_ids != json_run_ids:
        missing_in_csv = sorted(json_run_ids - csv_run_ids)
        missing_in_json = sorted(csv_run_ids - json_run_ids)

        if missing_in_csv:
            add_problem(problems, f"Runs missing in CSV: {missing_in_csv}")

        if missing_in_json:
            add_problem(problems, f"Runs missing in JSON: {missing_in_json}")


def build_report_payload(
    plan_json_path: Path,
    plan_md_path: Path,
    plan_csv_path: Path,
    plan: dict[str, Any],
    problems: list[str],
    warnings: list[str],
    planned_runs: list[Any],
    csv_rows: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "report_type": "fieldops_lab_experiment_campaign_plan_quality_check",
        "plan_json_path": str(plan_json_path),
        "plan_markdown_path": str(plan_md_path),
        "plan_csv_path": str(plan_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "planned_run_count": len(planned_runs),
        "csv_row_count": len(csv_rows),
        "planned_algorithm_run_count": as_int(plan.get("planned_algorithm_run_count")),
        "fuzzy_logic_status": plan.get("fuzzy_logic_status", ""),
        "scientific_status": plan.get("scientific_status", ""),
        "problems": problems,
        "warnings": warnings,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab experiment campaign plan quality check")
    lines.append("")
    lines.append(f"Plan JSON: `{payload['plan_json_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in [
        "all_required_checks_passed",
        "problem_count",
        "warning_count",
        "planned_run_count",
        "csv_row_count",
        "planned_algorithm_run_count",
        "fuzzy_logic_status",
        "scientific_status",
    ]:
        lines.append(f"| {key} | {format_number(payload.get(key, ''))} |")
    lines.append("")

    lines.append("## Problems")
    lines.append("")
    if payload["problems"]:
        for problem in payload["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if payload["warnings"]:
        for warning in payload["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    if payload["all_required_checks_passed"]:
        lines.append(
            "The campaign plan passed the structural quality check. This means the plan is coherent enough to be used as input for the next implementation step."
        )
        lines.append("")
        lines.append(
            "This still does not execute experiments or prove scientific validity. It only reduces the risk of using a malformed campaign design."
        )
    else:
        lines.append(
            "The campaign plan failed the structural quality check. Do not use it to generate concrete experiments until the listed problems are corrected."
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_experiment_campaign_plan.py "
            "<plan_json> <plan_md> <plan_csv> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    plan_json_path = Path(sys.argv[1])
    plan_md_path = Path(sys.argv[2])
    plan_csv_path = Path(sys.argv[3])
    output_md_path = Path(sys.argv[4])
    output_json_path = Path(sys.argv[5])

    problems: list[str] = []
    warnings: list[str] = []

    try:
        payload = load_json(plan_json_path)
        markdown_text = load_text(plan_md_path)
        csv_rows = load_csv_rows(plan_csv_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    plan = require_dict(payload, "plan", problems)
    scenario_families = require_list(payload, "scenario_families", problems)
    severity_levels = require_list(payload, "severity_levels", problems)
    policy_options = require_list(payload, "policy_options", problems)
    ranking_profiles = require_list(payload, "ranking_profiles", problems)
    planned_runs = require_list(payload, "planned_runs", problems)

    check_required_plan_keys(plan, problems)
    check_basic_files(markdown_text, csv_rows, problems)
    check_plan_counts(
        plan,
        scenario_families,
        severity_levels,
        policy_options,
        ranking_profiles,
        planned_runs,
        csv_rows,
        problems,
    )
    check_plan_status(plan, problems, warnings)
    check_policy_options(policy_options, problems)

    scenario_family_ids = extract_ids(scenario_families, "family_id", problems)
    severity_ids = extract_ids(severity_levels, "severity_id", problems)
    replication_count = as_int(plan.get("replication_count_per_condition"))
    policy_option_count = len(policy_options)

    check_planned_runs(
        planned_runs,
        csv_rows,
        scenario_family_ids,
        severity_ids,
        policy_option_count,
        replication_count,
        problems,
        warnings,
    )

    report_payload = build_report_payload(
        plan_json_path,
        plan_md_path,
        plan_csv_path,
        plan,
        problems,
        warnings,
        planned_runs,
        csv_rows,
    )

    write_markdown(output_md_path, report_payload)
    write_json(output_json_path, report_payload)

    print(f"Experiment campaign plan quality report written to: {output_md_path}")
    print(f"Experiment campaign plan quality JSON written to: {output_json_path}")

    if problems:
        print("ERROR: Experiment campaign plan quality check failed.", file=sys.stderr)
        return 1

    print("Experiment campaign plan quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())