from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1"}
    return False


def expected_product_count(report: dict[str, Any]) -> int:
    factors = report.get("factor_summary", {})
    return (
        len(factors.get("instance_size_levels", []))
        * len(factors.get("demand_density_levels", []))
        * len(factors.get("delay_families", []))
        * len(factors.get("delay_severities", []))
        * len(factors.get("policy_candidates", []))
        * len(factors.get("random_seeds", []))
    )


def validate_report(
    report: dict[str, Any],
    markdown_text: str,
    csv_rows: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []

    if report.get("report_type") != "experimental_design_matrix":
        problems.append("report_type must be experimental_design_matrix.")

    if report.get("scientific_stage") != "experimental_design":
        problems.append("scientific_stage must be experimental_design.")

    summary = report.get("summary")
    if not isinstance(summary, dict):
        problems.append("summary must be an object.")
        summary = {}

    factor_summary = report.get("factor_summary")
    if not isinstance(factor_summary, dict):
        problems.append("factor_summary must be an object.")
        factor_summary = {}

    rows = report.get("rows")
    if not isinstance(rows, list) or not rows:
        problems.append("rows must be a non-empty list.")
        rows = []

    expected_count = expected_product_count(report)
    experiment_count = as_int(summary.get("experiment_count"))

    if expected_count <= 0:
        problems.append("The experimental factor product must be greater than zero.")

    if experiment_count != len(rows):
        problems.append(
            f"summary.experiment_count must match rows length. "
            f"Expected {len(rows)}, found {experiment_count}."
        )

    if expected_count > 0 and len(rows) != expected_count:
        problems.append(
            f"rows length must match the full factor product. "
            f"Expected {expected_count}, found {len(rows)}."
        )

    if len(csv_rows) != len(rows):
        problems.append(
            f"CSV row count must match JSON rows. "
            f"Expected {len(rows)}, found {len(csv_rows)}."
        )

    if csv_rows:
        csv_fields = set(csv_rows[0].keys())
        missing_csv_fields = [
            field for field in REQUIRED_ROW_FIELDS if field not in csv_fields
        ]
        if missing_csv_fields:
            problems.append(
                "CSV is missing required fields: " + ", ".join(missing_csv_fields)
            )

    experiment_ids: set[str] = set()
    scenario_ids: set[str] = set()

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            problems.append(f"Row {index} must be an object.")
            continue

        missing_fields = [field for field in REQUIRED_ROW_FIELDS if field not in row]
        if missing_fields:
            problems.append(
                f"Row {index} is missing required fields: "
                + ", ".join(missing_fields)
            )

        experiment_id = str(row.get("experiment_id", "")).strip()
        scenario_id = str(row.get("scenario_id", "")).strip()

        if not experiment_id:
            problems.append(f"Row {index} has empty experiment_id.")
        elif experiment_id in experiment_ids:
            problems.append(f"Duplicated experiment_id: {experiment_id}")
        else:
            experiment_ids.add(experiment_id)

        if not scenario_id:
            problems.append(f"Row {index} has empty scenario_id.")
        else:
            scenario_ids.add(scenario_id)

        if as_int(row.get("customer_count")) <= 0:
            problems.append(f"Row {index} customer_count must be positive.")

        if as_int(row.get("technician_count")) <= 0:
            problems.append(f"Row {index} technician_count must be positive.")

        if as_int(row.get("time_horizon_minutes")) <= 0:
            problems.append(f"Row {index} time_horizon_minutes must be positive.")

        if as_int(row.get("random_seed")) <= 0:
            problems.append(f"Row {index} random_seed must be positive.")

        if str(row.get("status", "")).strip() != "planned":
            problems.append(f"Row {index} status must be planned.")

        planned_outputs = str(row.get("planned_outputs", "")).strip()
        if "statistical_comparison_input" not in planned_outputs:
            problems.append(
                f"Row {index} planned_outputs must include statistical_comparison_input."
            )

    scenario_count = as_int(summary.get("scenario_count"))
    if scenario_count != len(scenario_ids):
        problems.append(
            f"summary.scenario_count must match distinct scenario_id count. "
            f"Expected {len(scenario_ids)}, found {scenario_count}."
        )

    if not as_bool(
        summary.get("all_experiments_reproducible_from_explicit_factors")
    ):
        problems.append(
            "summary.all_experiments_reproducible_from_explicit_factors must be true."
        )

    required_factor_groups = [
        "instance_size_levels",
        "demand_density_levels",
        "delay_families",
        "delay_severities",
        "policy_candidates",
        "random_seeds",
    ]

    for group in required_factor_groups:
        value = factor_summary.get(group)
        if not isinstance(value, list) or not value:
            problems.append(f"factor_summary.{group} must be a non-empty list.")

    if "# FieldOps Lab experimental design matrix" not in markdown_text:
        problems.append("Markdown report must contain the expected title.")

    if "does not prove scientific validity" not in markdown_text.lower():
        problems.append(
            "Markdown report must explicitly state that the matrix does not prove scientific validity."
        )

    if not problems and not warnings:
        pass

    return problems, warnings


def build_quality_report(
    input_json_path: Path,
    input_markdown_path: Path,
    input_csv_path: Path,
) -> dict[str, Any]:
    report = read_json(input_json_path)
    markdown_text = input_markdown_path.read_text(encoding="utf-8")
    csv_rows = read_csv(input_csv_path)

    problems, warnings = validate_report(
        report=report,
        markdown_text=markdown_text,
        csv_rows=csv_rows,
    )

    return {
        "report_type": "experimental_design_matrix_quality_check",
        "input_json": str(input_json_path),
        "all_required_checks_passed": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "csv_row_count": len(csv_rows),
        "problems": problems,
        "warnings": warnings,
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# FieldOps Lab experimental design matrix quality check")
    lines.append("")
    lines.append(f"Input JSON: `{report['input_json']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| all_required_checks_passed | "
        f"{'yes' if report['all_required_checks_passed'] else 'no'} |"
    )
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    lines.append(f"| csv_row_count | {report['csv_row_count']} |")

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
            "The experimental design matrix passed structural verification."
        )
    else:
        lines.append(
            "The experimental design matrix failed structural verification."
        )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: verify_experimental_design_matrix.py "
            "<input_json> <input_markdown> <input_csv> "
            "<output_quality_markdown> <output_quality_json>",
            file=sys.stderr,
        )
        return 2

    input_json_path = Path(sys.argv[1])
    input_markdown_path = Path(sys.argv[2])
    input_csv_path = Path(sys.argv[3])
    output_quality_markdown_path = Path(sys.argv[4])
    output_quality_json_path = Path(sys.argv[5])

    report = build_quality_report(
        input_json_path=input_json_path,
        input_markdown_path=input_markdown_path,
        input_csv_path=input_csv_path,
    )

    write_markdown(output_quality_markdown_path, report)
    write_json(output_quality_json_path, report)

    print(f"Experimental design matrix quality report written to: {output_quality_markdown_path}")
    print(f"Experimental design matrix quality JSON written to: {output_quality_json_path}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Experimental design matrix quality check failed.", file=sys.stderr)
        for problem in report["problems"]:
            print(f"ERROR: {problem}", file=sys.stderr)
        for warning in report["warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)
        return 1

    print("Experimental design matrix quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())