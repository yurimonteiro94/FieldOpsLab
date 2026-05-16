from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH_KEYS = [
    "overview_csv_output_path",
    "summary_csv_output_path",
    "aggregate_csv_output_path",
    "ranking_csv_output_path",
    "recommendation_csv_output_path",
    "result_json_output_path",
]


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


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def normalized_abs(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()

    return (Path.cwd() / path).resolve()


def is_under_directory(path: Path, directory: Path) -> bool:
    path_abs = normalized_abs(path)
    directory_abs = normalized_abs(directory)

    return path_abs == directory_abs or directory_abs in path_abs.parents


def discover_config_paths(config_dir: Path) -> list[Path]:
    if not config_dir.exists():
        raise RuntimeError(f"Config directory does not exist: {config_dir}")

    paths = sorted(config_dir.glob("campaign_*_batch.json"))

    if not paths:
        raise RuntimeError(f"No executable campaign batch configs found in: {config_dir}")

    return paths


def get_result_json_output_path(config: dict[str, Any]) -> Path:
    path_text = str(config.get("result_json_output_path", "")).strip()

    if not path_text:
        batch_id = str(config.get("batch_id", "unknown_batch"))
        raise RuntimeError(f"Missing result_json_output_path for batch: {batch_id}")

    return Path(path_text)


def output_written_key(output_path_key: str) -> str:
    return output_path_key.replace("_output_path", "_was_written")


def inspect_output_paths(
    result: dict[str, Any],
    expected_result_dir: Path,
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    outputs = result.get("outputs", {})

    if not isinstance(outputs, dict):
        return False, ["Result JSON has no valid outputs object."], []

    problems: list[str] = []
    checks: list[dict[str, Any]] = []

    for output_key in OUTPUT_PATH_KEYS:
        path_text = str(outputs.get(output_key, "")).strip()
        written_key = output_written_key(output_key)
        was_written = bool(outputs.get(written_key, False))

        if not path_text:
            problems.append(f"Missing output path: {output_key}")

            checks.append(
                {
                    "output_key": output_key,
                    "path": "",
                    "exists": False,
                    "was_written": was_written,
                    "under_expected_dir": False,
                    "problems": [f"Missing output path: {output_key}"],
                }
            )

            continue

        path = Path(path_text)
        exists = path.exists()
        under_expected_dir = is_under_directory(path, expected_result_dir)
        item_problems: list[str] = []

        if not exists:
            item_problems.append(f"Output file does not exist: {path_text}")

        if not was_written:
            item_problems.append(f"Output was not reported as written: {output_key}")

        if not under_expected_dir:
            item_problems.append(
                f"Output path is outside expected directory: {path_text}"
            )

        problems.extend(item_problems)

        checks.append(
            {
                "output_key": output_key,
                "path": path_text,
                "exists": exists,
                "was_written": was_written,
                "under_expected_dir": under_expected_dir,
                "problems": item_problems,
            }
        )

    return len(problems) == 0, problems, checks


def run_batch(
    fieldops_exe: Path,
    config_path: Path,
    expected_result_dir: Path,
) -> dict[str, Any]:
    config = load_json(config_path)
    batch_id = str(config.get("batch_id", config_path.stem))
    expected_result_json_path = get_result_json_output_path(config)

    problems: list[str] = []

    if not bool(config.get("campaign_perturbation_plan_connected", False)):
        problems.append("Config is not marked as connected to campaign perturbation plan.")

    perturbation_plan_path = str(config.get("campaign_perturbation_plan_path", "")).strip()

    if not perturbation_plan_path:
        problems.append("Missing campaign_perturbation_plan_path.")
    elif not Path(perturbation_plan_path).exists():
        problems.append(f"Perturbation plan path does not exist: {perturbation_plan_path}")

    started = time.perf_counter()

    completed = subprocess.run(
        [str(fieldops_exe), "batch", str(config_path)],
        capture_output=True,
        text=True,
        shell=False,
    )

    duration_seconds = time.perf_counter() - started

    if completed.returncode != 0:
        problems.append(f"Executable returned non-zero code: {completed.returncode}")

    result_json_exists = expected_result_json_path.exists()

    if not result_json_exists:
        problems.append(f"Result JSON was not generated: {expected_result_json_path}")

    result: dict[str, Any] = {}

    if result_json_exists:
        result = load_json(expected_result_json_path)

    batch = result.get("batch", {}) if isinstance(result, dict) else {}
    rankings = result.get("rankings", {}) if isinstance(result, dict) else {}
    recommendations = result.get("recommendations", {}) if isinstance(result, dict) else {}

    if not isinstance(batch, dict):
        batch = {}

    if not isinstance(rankings, dict):
        rankings = {}

    if not isinstance(recommendations, dict):
        recommendations = {}

    output_paths_ok = False
    output_path_checks: list[dict[str, Any]] = []

    if result_json_exists:
        output_paths_ok, output_path_problems, output_path_checks = inspect_output_paths(
            result,
            expected_result_dir,
        )
        problems.extend(output_path_problems)

    configured_count = int(batch.get("configured_experiment_count", 0) or 0)
    completed_count = int(batch.get("completed_experiment_count", 0) or 0)
    is_complete = bool(batch.get("is_complete", False))

    if result_json_exists and not is_complete:
        problems.append(f"Batch did not complete: {batch_id}")

    if result_json_exists and configured_count != completed_count:
        problems.append(
            f"Configured/completed mismatch for {batch_id}: "
            f"{configured_count}/{completed_count}"
        )

    row = {
        "batch_id": batch_id,
        "config_path": str(config_path),
        "result_json_output_path": str(expected_result_json_path),
        "return_code": completed.returncode,
        "duration_seconds": duration_seconds,
        "configured_experiment_count": configured_count,
        "completed_experiment_count": completed_count,
        "completion_percent": float(batch.get("completion_percent", 0.0) or 0.0),
        "is_complete": is_complete,
        "ranking_row_count": int(rankings.get("row_count", 0) or 0),
        "recommendation_count": int(recommendations.get("recommendation_count", 0) or 0),
        "result_json_exists": result_json_exists,
        "output_paths_ok": output_paths_ok,
        "problem_count": len(problems),
        "problems": problems,
        "output_path_checks": output_path_checks,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }

    return row


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "config_path",
        "result_json_output_path",
        "return_code",
        "duration_seconds",
        "configured_experiment_count",
        "completed_experiment_count",
        "completion_percent",
        "is_complete",
        "ranking_row_count",
        "recommendation_count",
        "result_json_exists",
        "output_paths_ok",
        "problem_count",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(
    path: Path,
    rows: list[dict[str, Any]],
    expected_result_dir: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    batch_count = len(rows)
    total_configured = sum(int(row["configured_experiment_count"]) for row in rows)
    total_completed = sum(int(row["completed_experiment_count"]) for row in rows)
    problem_count = sum(int(row["problem_count"]) for row in rows)
    complete_batch_count = sum(1 for row in rows if bool(row["is_complete"]))
    output_path_ok_count = sum(1 for row in rows if bool(row["output_paths_ok"]))

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign execution index")
    lines.append("")
    lines.append("This report indexes the execution of all executable campaign batch configs.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| batch_count | {format_number(batch_count)} |")
    lines.append(f"| complete_batch_count | {format_number(complete_batch_count)} |")
    lines.append(f"| output_path_ok_batch_count | {format_number(output_path_ok_count)} |")
    lines.append(f"| total_configured_experiment_count | {format_number(total_configured)} |")
    lines.append(f"| total_completed_experiment_count | {format_number(total_completed)} |")
    lines.append(f"| problem_count | {format_number(problem_count)} |")
    lines.append(f"| expected_result_dir | `{expected_result_dir}` |")
    lines.append("| execution_status | campaign_execution_validation |")
    lines.append("")
    lines.append("## Executed batches")
    lines.append("")
    lines.append("| Batch | Complete | Output paths ok | Experiments | Ranking rows | Recommendations | Problems |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{yes_no(row['is_complete'])} | "
            f"{yes_no(row['output_paths_ok'])} | "
            f"{format_number(row['completed_experiment_count'])}/{format_number(row['configured_experiment_count'])} | "
            f"{format_number(row['ranking_row_count'])} | "
            f"{format_number(row['recommendation_count'])} | "
            f"{format_number(row['problem_count'])} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    any_problem = False

    for row in rows:
        problems = row.get("problems", [])

        if not isinstance(problems, list) or not problems:
            continue

        any_problem = True
        lines.append(f"### {row['batch_id']}")
        lines.append("")

        for problem in problems:
            lines.append(f"- ERROR: {problem}")

        lines.append("")

    if not any_problem:
        lines.append("- None.")
        lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")

    if problem_count == 0:
        lines.append("All executable campaign batches ran successfully and reported isolated output paths.")
    else:
        lines.append("Some campaign batches failed execution or output-path validation. Do not use the campaign outputs until the listed problems are fixed.")

    lines.append("")
    lines.append("This is still an execution validation layer. It confirms that the campaign can run structurally, but it does not by itself establish final scientific conclusions.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index_json(
    path: Path,
    rows: list[dict[str, Any]],
    config_dir: Path,
    expected_result_dir: Path,
) -> None:
    batch_count = len(rows)
    total_configured = sum(int(row["configured_experiment_count"]) for row in rows)
    total_completed = sum(int(row["completed_experiment_count"]) for row in rows)
    problem_count = sum(int(row["problem_count"]) for row in rows)
    complete_batch_count = sum(1 for row in rows if bool(row["is_complete"]))
    output_path_ok_count = sum(1 for row in rows if bool(row["output_paths_ok"]))

    payload = {
        "index_type": "fieldops_lab_campaign_execution_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "config_dir": str(config_dir),
        "expected_result_dir": str(expected_result_dir),
        "batch_count": batch_count,
        "complete_batch_count": complete_batch_count,
        "output_path_ok_batch_count": output_path_ok_count,
        "total_configured_experiment_count": total_configured,
        "total_completed_experiment_count": total_completed,
        "problem_count": problem_count,
        "all_required_checks_passed": problem_count == 0,
        "execution_status": "campaign_execution_validation",
        "scientific_status": "pipeline_execution_validation_only",
        "rows": rows,
        "interpretation": {
            "status": "campaign_execution_index",
            "warning": "This validates structural execution of campaign batches. It does not prove scientific validity by itself.",
        },
    }

    write_json(path, payload)


def main() -> int:
    if len(sys.argv) != 7:
        print(
            "Usage: py -3 analysis\\scripts\\run_executable_campaign_batches.py "
            "<fieldops_exe> <config_dir> <expected_result_dir> "
            "<output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    fieldops_exe = Path(sys.argv[1])
    config_dir = Path(sys.argv[2])
    expected_result_dir = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])
    output_csv = Path(sys.argv[6])

    try:
        if not fieldops_exe.exists():
            raise RuntimeError(f"FieldOps executable not found: {fieldops_exe}")

        expected_result_dir.mkdir(parents=True, exist_ok=True)

        config_paths = discover_config_paths(config_dir)
        rows = [
            run_batch(fieldops_exe, config_path, expected_result_dir)
            for config_path in config_paths
        ]

        rows.sort(key=lambda row: str(row["batch_id"]))

        write_markdown(output_md, rows, expected_result_dir)
        write_index_json(output_json, rows, config_dir, expected_result_dir)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    problem_count = sum(int(row["problem_count"]) for row in rows)

    print(f"Campaign execution index markdown written to: {output_md}")
    print(f"Campaign execution index JSON written to: {output_json}")
    print(f"Campaign execution index CSV written to: {output_csv}")
    print(f"Executed batches: {len(rows)}")

    if problem_count > 0:
        print("ERROR: Campaign execution completed with validation problems.", file=sys.stderr)
        return 1

    print("Campaign execution validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())