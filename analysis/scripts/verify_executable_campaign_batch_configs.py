from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_OUTPUT_KEYS = [
    "overview_csv_output_path",
    "summary_csv_output_path",
    "aggregate_csv_output_path",
    "ranking_csv_output_path",
    "recommendation_csv_output_path",
    "result_json_output_path",
]

REQUIRED_EXPORT_KEYS = [
    "export_overview_csv",
    "export_summary_csv",
    "export_aggregate_csv",
    "export_ranking_csv",
    "export_recommendation_csv",
    "export_result_json",
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


def normalize_path(value: Any) -> str:
    return str(value).replace("/", "\\").strip()


def get_index_rows(index_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = index_data.get("rows")

    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]

    raise RuntimeError("Executable config index does not contain a rows array.")


def path_is_under_campaign_results(path_value: Any) -> bool:
    normalized = normalize_path(path_value).lower()
    return normalized.startswith("data\\results\\campaign_batches\\")


def check_config(row: dict[str, Any]) -> dict[str, Any]:
    config_path = Path(str(row.get("config_path", "")))
    problems: list[str] = []
    warnings: list[str] = []

    if not config_path.exists():
        problems.append(f"Config file does not exist: {config_path}")
        return {
            "batch_id": row.get("batch_id", ""),
            "config_path": str(config_path),
            "exists": False,
            "size_bytes": 0,
            "experiment_count": 0,
            "unique_experiment_id_count": 0,
            "required_output_paths_ok": False,
            "required_export_flags_ok": False,
            "problems": problems,
            "warnings": warnings,
        }

    data = load_json(config_path)
    size_bytes = config_path.stat().st_size

    experiments = data.get("experiments")
    if not isinstance(experiments, list):
        problems.append("Config does not contain an experiments array.")
        experiments = []

    experiment_ids: list[str] = []
    for experiment in experiments:
        if not isinstance(experiment, dict):
            problems.append("Experiment item is not an object.")
            continue

        experiment_id = str(experiment.get("experiment_id", "")).strip()
        if not experiment_id:
            problems.append("Experiment has empty experiment_id.")
        else:
            experiment_ids.append(experiment_id)

        for required_key in ["instance_path", "perturbation_plan_path", "policy_id", "replanning_method_id", "scenario_id", "replication_id", "seed"]:
            if required_key not in experiment:
                problems.append(f"Experiment {experiment_id} is missing key: {required_key}")

    duplicate_experiment_ids = sorted(
        experiment_id for experiment_id in set(experiment_ids) if experiment_ids.count(experiment_id) > 1
    )

    if duplicate_experiment_ids:
        problems.append(f"Duplicate experiment IDs found: {duplicate_experiment_ids}")

    required_output_paths_ok = True

    for key in REQUIRED_OUTPUT_KEYS:
        value = data.get(key, "")

        if not value:
            problems.append(f"Missing output path key: {key}")
            required_output_paths_ok = False
            continue

        normalized = normalize_path(value)

        if "sample_no_replanning_batch" in normalized:
            problems.append(f"Output path still points to sample batch: {key}={normalized}")
            required_output_paths_ok = False

        if not path_is_under_campaign_results(normalized):
            problems.append(f"Output path is not under data/results/campaign_batches: {key}={normalized}")
            required_output_paths_ok = False

    required_export_flags_ok = True

    for key in REQUIRED_EXPORT_KEYS:
        value = data.get(key)

        if value is not True:
            problems.append(f"Required export flag is not true: {key}")
            required_export_flags_ok = False

    expected_experiment_count = row.get("generated_experiment_count")
    if expected_experiment_count is not None:
        try:
            expected_count = int(expected_experiment_count)
            if expected_count != len(experiments):
                problems.append(f"Experiment count mismatch. index={expected_count}, config={len(experiments)}")
        except (TypeError, ValueError):
            warnings.append(f"Could not parse expected experiment count: {expected_experiment_count}")

    return {
        "batch_id": row.get("batch_id", ""),
        "config_path": str(config_path),
        "exists": True,
        "size_bytes": size_bytes,
        "experiment_count": len(experiments),
        "unique_experiment_id_count": len(set(experiment_ids)),
        "required_output_paths_ok": required_output_paths_ok,
        "required_export_flags_ok": required_export_flags_ok,
        "problems": problems,
        "warnings": warnings,
    }


def write_markdown(path: Path, index_path: Path, checks: list[dict[str, Any]]) -> None:
    problem_count = sum(len(check["problems"]) for check in checks)
    warning_count = sum(len(check["warnings"]) for check in checks)
    total_experiments = sum(int(check["experiment_count"]) for check in checks)
    all_required_checks_passed = problem_count == 0

    lines: list[str] = []
    lines.append("# FieldOps Lab executable campaign batch config quality check")
    lines.append("")
    lines.append(f"Index JSON: `{index_path}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {format_number(all_required_checks_passed)} |")
    lines.append(f"| problem_count | {problem_count} |")
    lines.append(f"| warning_count | {warning_count} |")
    lines.append(f"| config_count | {len(checks)} |")
    lines.append(f"| total_experiment_count | {total_experiments} |")
    lines.append("")
    lines.append("## Config checks")
    lines.append("")
    lines.append("| Batch | Exists | Size bytes | Experiments | Unique IDs | Output paths ok | Export flags ok | Problems |")
    lines.append("| --- | --- | ---: | ---: | ---: | --- | --- | --- |")

    for check in checks:
        problems = "; ".join(check["problems"]) if check["problems"] else "none"
        lines.append(
            "| "
            f"{check['batch_id']} | "
            f"{format_number(check['exists'])} | "
            f"{check['size_bytes']} | "
            f"{check['experiment_count']} | "
            f"{check['unique_experiment_id_count']} | "
            f"{format_number(check['required_output_paths_ok'])} | "
            f"{format_number(check['required_export_flags_ok'])} | "
            f"{problems} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    problems_written = False
    for check in checks:
        for problem in check["problems"]:
            lines.append(f"- ERROR: {check['batch_id']}: {problem}")
            problems_written = True

    if not problems_written:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")

    warnings_written = False
    for check in checks:
        for warning in check["warnings"]:
            lines.append(f"- WARNING: {check['batch_id']}: {warning}")
            warnings_written = True

    if not warnings_written:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if all_required_checks_passed:
        lines.append("The executable campaign batch config candidates passed the structural quality check. They are coherent enough to be executed for pipeline validation.")
        lines.append("")
        lines.append("This still does not make them final scientific evidence because the perturbation plans are still template-based.")
    else:
        lines.append("The executable campaign batch config candidates did not pass the structural quality check. Do not execute or use these configs until the listed problems are corrected.")

    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(path: Path, checks: list[dict[str, Any]]) -> None:
    fieldnames = [
        "batch_id",
        "config_path",
        "exists",
        "size_bytes",
        "experiment_count",
        "unique_experiment_id_count",
        "required_output_paths_ok",
        "required_export_flags_ok",
        "problem_count",
        "warning_count",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for check in checks:
            writer.writerow(
                {
                    "batch_id": check["batch_id"],
                    "config_path": check["config_path"],
                    "exists": check["exists"],
                    "size_bytes": check["size_bytes"],
                    "experiment_count": check["experiment_count"],
                    "unique_experiment_id_count": check["unique_experiment_id_count"],
                    "required_output_paths_ok": check["required_output_paths_ok"],
                    "required_export_flags_ok": check["required_export_flags_ok"],
                    "problem_count": len(check["problems"]),
                    "warning_count": len(check["warnings"]),
                }
            )


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\verify_executable_campaign_batch_configs.py "
            "<index_json> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    index_path = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        index_data = load_json(index_path)
        rows = get_index_rows(index_data)
        checks = [check_config(row) for row in rows]

        problem_count = sum(len(check["problems"]) for check in checks)
        warning_count = sum(len(check["warnings"]) for check in checks)
        all_required_checks_passed = problem_count == 0

        payload = {
            "report_type": "fieldops_lab_executable_campaign_batch_config_quality_check",
            "index_path": str(index_path),
            "all_required_checks_passed": all_required_checks_passed,
            "problem_count": problem_count,
            "warning_count": warning_count,
            "config_count": len(checks),
            "total_experiment_count": sum(int(check["experiment_count"]) for check in checks),
            "checks": checks,
        }

        write_markdown(output_md, index_path, checks)
        write_json(output_json, payload)
        write_csv(output_csv, checks)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Executable campaign batch config quality report written to: {output_md}")
    print(f"Executable campaign batch config quality JSON written to: {output_json}")
    print(f"Executable campaign batch config quality CSV written to: {output_csv}")

    if not all_required_checks_passed:
        print("ERROR: Executable campaign batch config quality check failed.", file=sys.stderr)
        return 1

    print("Executable campaign batch config quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())