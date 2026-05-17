from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


MANDATORY_CATEGORIES = {
    "experimental_design",
    "statistical_validation",
    "external_validation",
    "methodological_limitations",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "passed", "pass", "ok"}

    return False


def validate_report(report: dict[str, Any], markdown_text: str, csv_rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []

    if report.get("report_type") != "scientific_validation_plan":
        problems.append("report_type must be scientific_validation_plan.")

    if report.get("validation_stage") != "diagnostic_to_experimental_transition":
        problems.append("validation_stage must be diagnostic_to_experimental_transition.")

    if not as_bool(report.get("structural_inputs_available")):
        problems.append("structural_inputs_available must be true.")

    if not as_bool(report.get("structural_inputs_passed")):
        problems.append("structural_inputs_passed must be true.")

    context = report.get("context")
    if not isinstance(context, dict):
        problems.append("context must be an object.")
        context = {}

    scientific_status = str(context.get("scientific_status", ""))
    if "diagnostic" not in scientific_status:
        warnings.append("scientific_status does not explicitly contain diagnostic.")

    actions = report.get("validation_actions")
    if not isinstance(actions, list):
        problems.append("validation_actions must be a list.")
        actions = []

    if len(actions) < 8:
        problems.append("validation_actions must contain at least 8 actions.")

    action_ids: set[str] = set()
    categories: set[str] = set()

    required_action_fields = {
        "id",
        "priority",
        "category",
        "action",
        "acceptance_criterion",
        "evidence_output",
        "status",
    }

    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            problems.append(f"validation_actions[{index}] must be an object.")
            continue

        for field in required_action_fields:
            value = str(action.get(field, "")).strip()
            if not value:
                problems.append(f"validation_actions[{index}].{field} must not be empty.")

        action_id = str(action.get("id", "")).strip()
        if action_id in action_ids:
            problems.append(f"Duplicate validation action id: {action_id}")
        action_ids.add(action_id)

        category = str(action.get("category", "")).strip()
        if category:
            categories.add(category)

    missing_categories = MANDATORY_CATEGORIES - categories
    if missing_categories:
        problems.append(
            "Validation actions are missing mandatory categories: "
            + ", ".join(sorted(missing_categories))
        )

    if len(csv_rows) != len(actions):
        problems.append(
            f"CSV row count must match validation action count. CSV={len(csv_rows)}, actions={len(actions)}."
        )

    quality_inputs = report.get("quality_inputs")
    if not isinstance(quality_inputs, list) or not quality_inputs:
        problems.append("quality_inputs must be a non-empty list.")
    else:
        for item in quality_inputs:
            if not isinstance(item, dict):
                problems.append("Each quality input must be an object.")
                continue

            if not as_bool(item.get("exists")):
                problems.append(f"Quality input does not exist: {item.get('path', '<unknown>')}")

            if not as_bool(item.get("passed")):
                problems.append(f"Quality input did not pass: {item.get('path', '<unknown>')}")

    risks = report.get("open_scientific_risks")
    if not isinstance(risks, list) or not risks:
        problems.append("open_scientific_risks must be a non-empty list.")

    conclusion = str(report.get("conservative_conclusion", "")).lower()
    if "does not prove scientific validity" not in conclusion:
        problems.append("conservative_conclusion must explicitly state that the plan does not prove scientific validity.")

    if "does not prove scientific validity" not in markdown_text.lower():
        problems.append("Markdown report must explicitly state that the plan does not prove scientific validity.")

    if "## Validation actions" not in markdown_text:
        problems.append("Markdown report must contain a Validation actions section.")

    return problems, warnings


def write_quality_markdown(
    output_path: Path,
    json_path: Path,
    problems: list[str],
    warnings: list[str],
    csv_row_count: int,
    action_count: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# FieldOps Lab scientific validation plan quality check",
        "",
        f"Plan JSON: `{json_path}`",
        "",
        "## Overall result",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| all_required_checks_passed | {'yes' if not problems else 'no'} |",
        f"| problem_count | {len(problems)} |",
        f"| warning_count | {len(warnings)} |",
        f"| action_count | {action_count} |",
        f"| csv_row_count | {csv_row_count} |",
        "",
        "## Problems",
        "",
    ]

    if problems:
        for problem in problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Warnings", ""])

    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Conservative interpretation",
            "",
            "The scientific validation plan passed structural verification."
            if not problems
            else "The scientific validation plan failed structural verification.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_quality_json(
    output_path: Path,
    problems: list[str],
    warnings: list[str],
    csv_row_count: int,
    action_count: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "all_required_checks_passed": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "action_count": action_count,
        "csv_row_count": csv_row_count,
        "problems": problems,
        "warnings": warnings,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: verify_scientific_validation_plan.py "
            "<input_json> <input_markdown> <input_csv> <output_quality_markdown> <output_quality_json>",
            file=sys.stderr,
        )
        return 2

    json_path = Path(sys.argv[1])
    markdown_path = Path(sys.argv[2])
    csv_path = Path(sys.argv[3])
    quality_markdown_path = Path(sys.argv[4])
    quality_json_path = Path(sys.argv[5])

    report = read_json(json_path)
    markdown_text = markdown_path.read_text(encoding="utf-8")
    csv_rows = read_csv_rows(csv_path)

    actions = report.get("validation_actions")
    action_count = len(actions) if isinstance(actions, list) else 0

    problems, warnings = validate_report(report, markdown_text, csv_rows)

    write_quality_markdown(
        quality_markdown_path,
        json_path,
        problems,
        warnings,
        csv_row_count=len(csv_rows),
        action_count=action_count,
    )
    write_quality_json(
        quality_json_path,
        problems,
        warnings,
        csv_row_count=len(csv_rows),
        action_count=action_count,
    )

    print(f"Scientific validation plan quality report written to: {quality_markdown_path}")
    print(f"Scientific validation plan quality JSON written to: {quality_json_path}")

    if problems:
        print("ERROR: Scientific validation plan quality check failed.", file=sys.stderr)
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    print("Scientific validation plan quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())