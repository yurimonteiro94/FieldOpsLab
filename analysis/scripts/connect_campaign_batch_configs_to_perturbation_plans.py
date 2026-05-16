from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SEVERITY_IDS = ["light", "moderate", "severe"]


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


def normalize_path_text(path: Path) -> str:
    return path.as_posix()


def infer_family_and_severity_from_batch_id(batch_id: str) -> tuple[str, str]:
    text = batch_id.strip()

    if text.startswith("campaign_"):
        text = text[len("campaign_"):]

    if text.endswith("_batch"):
        text = text[: -len("_batch")]

    for severity in SEVERITY_IDS:
        suffix = f"_{severity}"

        if text.endswith(suffix):
            family = text[: -len(suffix)]

            if not family:
                break

            return family, severity

    raise RuntimeError(f"Could not infer family and severity from batch_id: {batch_id}")


def discover_config_paths(config_dir: Path) -> list[Path]:
    if not config_dir.exists():
        raise RuntimeError(f"Config directory does not exist: {config_dir}")

    paths = sorted(config_dir.glob("campaign_*_batch.json"))

    if not paths:
        raise RuntimeError(f"No campaign batch configs found in: {config_dir}")

    return paths


def discover_perturbation_plan_paths(plan_dir: Path) -> dict[tuple[str, str], Path]:
    if not plan_dir.exists():
        raise RuntimeError(f"Perturbation plan directory does not exist: {plan_dir}")

    mapping: dict[tuple[str, str], Path] = {}

    for path in sorted(plan_dir.glob("campaign_*_perturbation_plan.json")):
        data = load_json(path)

        family = str(data.get("scenario_family_id", "")).strip()
        severity = str(data.get("severity_id", "")).strip()

        if not family or not severity:
            continue

        mapping[(family, severity)] = path

    if not mapping:
        raise RuntimeError(f"No usable campaign perturbation plans found in: {plan_dir}")

    return mapping


def update_experiment(
    experiment: dict[str, Any],
    perturbation_plan_path: Path,
    perturbation_plan_id: str,
) -> bool:
    expected_path = normalize_path_text(perturbation_plan_path)
    changed = False

    if experiment.get("perturbation_plan_path") != expected_path:
        experiment["perturbation_plan_path"] = expected_path
        changed = True

    if experiment.get("perturbation_plan_id") != perturbation_plan_id:
        experiment["perturbation_plan_id"] = perturbation_plan_id
        changed = True

    notes = str(experiment.get("notes", "")).strip()
    marker = "campaign_perturbation_plan_connected=true"

    if marker not in notes:
        if notes:
            notes = f"{notes} {marker}."
        else:
            notes = f"{marker}."

        experiment["notes"] = notes
        changed = True

    return changed


def update_batch_config(
    config_path: Path,
    plan_mapping: dict[tuple[str, str], Path],
) -> dict[str, Any]:
    config = load_json(config_path)

    batch_id = str(config.get("batch_id", config_path.stem)).strip()
    family, severity = infer_family_and_severity_from_batch_id(batch_id)

    key = (family, severity)

    if key not in plan_mapping:
        raise RuntimeError(
            f"No perturbation plan found for family={family}, severity={severity}"
        )

    plan_path = plan_mapping[key]
    plan = load_json(plan_path)
    plan_id = str(plan.get("perturbation_plan_id", plan_path.stem)).strip()

    experiments = config.get("experiments", [])

    if not isinstance(experiments, list):
        raise RuntimeError(f"experiments must be a list in config: {config_path}")

    updated_experiment_count = 0
    problem_count = 0
    problems: list[str] = []

    for index, experiment in enumerate(experiments):
        if not isinstance(experiment, dict):
            problem_count += 1
            problems.append(f"Experiment at index {index} is not an object.")
            continue

        if update_experiment(experiment, plan_path, plan_id):
            updated_experiment_count += 1

    config["campaign_perturbation_plan_path"] = normalize_path_text(plan_path)
    config["campaign_perturbation_plan_id"] = plan_id
    config["campaign_perturbation_plan_connected"] = True
    config["semantic_status"] = "executable_campaign_config_with_family_specific_perturbations"
    config["scientific_status"] = "candidate_campaign_execution_config"

    write_json(config_path, config)

    return {
        "batch_id": batch_id,
        "config_path": normalize_path_text(config_path),
        "scenario_family_id": family,
        "severity_id": severity,
        "perturbation_plan_id": plan_id,
        "perturbation_plan_path": normalize_path_text(plan_path),
        "experiment_count": len(experiments),
        "updated_experiment_count": updated_experiment_count,
        "problem_count": problem_count,
        "problems": problems,
        "semantic_status": "executable_campaign_config_with_family_specific_perturbations",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "config_path",
        "scenario_family_id",
        "severity_id",
        "perturbation_plan_id",
        "perturbation_plan_path",
        "experiment_count",
        "updated_experiment_count",
        "problem_count",
        "semantic_status",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    total_configs = len(rows)
    total_experiments = sum(int(row["experiment_count"]) for row in rows)
    total_updated = sum(int(row["updated_experiment_count"]) for row in rows)
    total_problems = sum(int(row["problem_count"]) for row in rows)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign perturbation connection report")
    lines.append("")
    lines.append("This report confirms that executable campaign batch configs were connected to family-specific perturbation plans.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| connected_config_count | {format_number(total_configs)} |")
    lines.append(f"| total_experiment_count | {format_number(total_experiments)} |")
    lines.append(f"| updated_experiment_count | {format_number(total_updated)} |")
    lines.append(f"| problem_count | {format_number(total_problems)} |")
    lines.append("| semantic_status | executable_campaign_config_with_family_specific_perturbations |")
    lines.append("")
    lines.append("## Connected configs")
    lines.append("")
    lines.append("| Batch | Family | Severity | Experiments | Perturbation plan | Problems |")
    lines.append("| --- | --- | --- | ---: | --- | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{format_number(row['experiment_count'])} | "
            f"`{row['perturbation_plan_path']}` | "
            f"{format_number(row['problem_count'])} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append("The executable campaign configs now point to family-specific perturbation plans instead of reusing only the sample perturbation templates.")
    lines.append("")
    lines.append("This is still not the final scientific campaign. It is the next executable validation layer, suitable for checking whether all campaign batches can run without contaminating sample outputs.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index_json(path: Path, rows: list[dict[str, Any]]) -> None:
    total_configs = len(rows)
    total_experiments = sum(int(row["experiment_count"]) for row in rows)
    total_updated = sum(int(row["updated_experiment_count"]) for row in rows)
    total_problems = sum(int(row["problem_count"]) for row in rows)

    payload = {
        "index_type": "fieldops_lab_campaign_perturbation_connection_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "connected_config_count": total_configs,
        "total_experiment_count": total_experiments,
        "updated_experiment_count": total_updated,
        "problem_count": total_problems,
        "all_required_checks_passed": total_problems == 0,
        "semantic_status": "executable_campaign_config_with_family_specific_perturbations",
        "scientific_status": "candidate_campaign_execution_config",
        "rows": rows,
        "interpretation": {
            "status": "campaign_config_connection_only",
            "warning": "This connects executable configs to family-specific perturbation plans. It does not prove scientific validity by itself.",
        },
    }

    write_json(path, payload)


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\connect_campaign_batch_configs_to_perturbation_plans.py "
            "<config_dir> <perturbation_plan_dir> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    config_dir = Path(sys.argv[1])
    plan_dir = Path(sys.argv[2])
    output_md = Path(sys.argv[3])
    output_json = Path(sys.argv[4])
    output_csv = Path(sys.argv[5])

    try:
        config_paths = discover_config_paths(config_dir)
        plan_mapping = discover_perturbation_plan_paths(plan_dir)

        rows = [
            update_batch_config(config_path, plan_mapping)
            for config_path in config_paths
        ]

        rows.sort(key=lambda row: str(row["batch_id"]))

        write_markdown(output_md, rows)
        write_index_json(output_json, rows)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign perturbation connection markdown written to: {output_md}")
    print(f"Campaign perturbation connection JSON written to: {output_json}")
    print(f"Campaign perturbation connection CSV written to: {output_csv}")
    print(f"Connected configs: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())