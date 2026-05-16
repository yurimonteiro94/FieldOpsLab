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
        file.write("\n")


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


def read_csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def text_contains(path: Path, expected: str) -> bool:
    if not path.exists():
        return False

    return expected in path.read_text(encoding="utf-8")


def verify_index(
    index_path: Path,
    markdown_path: Path,
    csv_path: Path,
) -> dict[str, Any]:
    index = load_json(index_path)

    problems: list[str] = []
    warnings: list[str] = []

    rows = index.get("rows", [])

    if not isinstance(rows, list):
        rows = []
        problems.append("Execution index rows must be a list.")

    batch_count = int(index.get("batch_count", 0) or 0)
    complete_batch_count = int(index.get("complete_batch_count", 0) or 0)
    output_path_ok_batch_count = int(index.get("output_path_ok_batch_count", 0) or 0)
    total_configured = int(index.get("total_configured_experiment_count", 0) or 0)
    total_completed = int(index.get("total_completed_experiment_count", 0) or 0)
    problem_count_from_index = int(index.get("problem_count", 0) or 0)
    all_required_checks_passed = bool(index.get("all_required_checks_passed", False))

    if batch_count <= 0:
        problems.append("batch_count must be greater than zero.")

    if batch_count != len(rows):
        problems.append(
            f"batch_count does not match row count. batch_count={batch_count}; rows={len(rows)}"
        )

    if complete_batch_count != batch_count:
        problems.append(
            f"Not all batches are complete. complete_batch_count={complete_batch_count}; batch_count={batch_count}"
        )

    if output_path_ok_batch_count != batch_count:
        problems.append(
            f"Not all batches have valid output paths. output_path_ok_batch_count={output_path_ok_batch_count}; batch_count={batch_count}"
        )

    if total_configured <= 0:
        problems.append("total_configured_experiment_count must be greater than zero.")

    if total_completed != total_configured:
        problems.append(
            f"Campaign experiment completion mismatch. completed={total_completed}; configured={total_configured}"
        )

    if problem_count_from_index != 0:
        problems.append(f"Execution index reports problems. problem_count={problem_count_from_index}")

    if not all_required_checks_passed:
        problems.append("Execution index all_required_checks_passed is false.")

    if not markdown_path.exists():
        problems.append(f"Markdown execution index does not exist: {markdown_path}")
    elif not text_contains(markdown_path, "# FieldOps Lab campaign execution index"):
        problems.append("Markdown execution index does not contain the expected title.")

    csv_row_count = read_csv_row_count(csv_path)

    if not csv_path.exists():
        problems.append(f"CSV execution index does not exist: {csv_path}")
    elif csv_row_count != batch_count:
        problems.append(
            f"CSV row count does not match batch_count. csv_row_count={csv_row_count}; batch_count={batch_count}"
        )

    row_checks: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            problems.append("Execution row is not an object.")
            continue

        row_batch_id = str(row.get("batch_id", ""))
        row_problem_count = int(row.get("problem_count", 0) or 0)
        row_is_complete = bool(row.get("is_complete", False))
        row_output_paths_ok = bool(row.get("output_paths_ok", False))
        row_result_path = Path(str(row.get("result_json_output_path", "")))

        row_problems: list[str] = []

        if not row_batch_id:
            row_problems.append("Missing batch_id.")

        if row_problem_count != 0:
            row_problems.append(f"Row has problem_count={row_problem_count}.")

        if not row_is_complete:
            row_problems.append("Row is not complete.")

        if not row_output_paths_ok:
            row_problems.append("Row output_paths_ok is false.")

        if not row_result_path.exists():
            row_problems.append(f"Result JSON does not exist: {row_result_path}")

        problems.extend(row_problems)

        row_checks.append(
            {
                "batch_id": row_batch_id,
                "is_complete": row_is_complete,
                "output_paths_ok": row_output_paths_ok,
                "result_json_output_path": str(row_result_path),
                "problem_count": row_problem_count,
                "problems": row_problems,
            }
        )

    return {
        "report_type": "fieldops_lab_campaign_execution_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "index_path": str(index_path),
        "markdown_path": str(markdown_path),
        "csv_path": str(csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "batch_count": batch_count,
        "complete_batch_count": complete_batch_count,
        "output_path_ok_batch_count": output_path_ok_batch_count,
        "total_configured_experiment_count": total_configured,
        "total_completed_experiment_count": total_completed,
        "csv_row_count": csv_row_count,
        "problems": problems,
        "warnings": warnings,
        "row_checks": row_checks,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign execution quality check")
    lines.append("")
    lines.append(f"Execution index JSON: `{report['index_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {format_number(report['all_required_checks_passed'])} |")
    lines.append(f"| problem_count | {format_number(report['problem_count'])} |")
    lines.append(f"| warning_count | {format_number(report['warning_count'])} |")
    lines.append(f"| batch_count | {format_number(report['batch_count'])} |")
    lines.append(f"| complete_batch_count | {format_number(report['complete_batch_count'])} |")
    lines.append(f"| output_path_ok_batch_count | {format_number(report['output_path_ok_batch_count'])} |")
    lines.append(f"| total_configured_experiment_count | {format_number(report['total_configured_experiment_count'])} |")
    lines.append(f"| total_completed_experiment_count | {format_number(report['total_completed_experiment_count'])} |")
    lines.append(f"| csv_row_count | {format_number(report['csv_row_count'])} |")
    lines.append("")
    lines.append("## Batch checks")
    lines.append("")
    lines.append("| Batch | Complete | Output paths ok | Problems |")
    lines.append("| --- | --- | --- | ---: |")

    for row in report["row_checks"]:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{format_number(row['is_complete'])} | "
            f"{format_number(row['output_paths_ok'])} | "
            f"{format_number(row['problem_count'])} |"
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
        lines.append("The campaign execution index passed the structural quality check. All discovered campaign batches completed and reported valid output paths.")
    else:
        lines.append("The campaign execution index failed the structural quality check. Do not use campaign execution outputs until the listed problems are fixed.")

    lines.append("")
    lines.append("This still does not prove scientific validity. It validates execution integrity and output organization.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_execution_index.py "
            "<execution_index_json> <execution_index_md> <execution_index_csv> "
            "<output_quality_md> <output_quality_json>",
            file=sys.stderr,
        )
        return 2

    index_path = Path(sys.argv[1])
    markdown_path = Path(sys.argv[2])
    csv_path = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    try:
        report = verify_index(index_path, markdown_path, csv_path)
        write_markdown(output_md, report)
        write_json(output_json, report)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign execution quality report written to: {output_md}")
    print(f"Campaign execution quality JSON written to: {output_json}")

    if not bool(report["all_required_checks_passed"]):
        print("ERROR: Campaign execution quality check failed.", file=sys.stderr)
        return 1

    print("Campaign execution quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())