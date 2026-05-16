from __future__ import annotations

import copy
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
        raise RuntimeError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def format_value(value: Any) -> str:
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


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def sanitize_id(value: str) -> str:
    sanitized = []

    for char in value:
        if char.isalnum() or char in ("_", "-"):
            sanitized.append(char)
        else:
            sanitized.append("_")

    result = "".join(sanitized).strip("_")

    while "__" in result:
        result = result.replace("__", "_")

    return result


def get_first_experiment_template(sample_config: dict[str, Any]) -> dict[str, Any]:
    experiments = sample_config.get("experiments", [])

    if not isinstance(experiments, list) or not experiments:
        raise RuntimeError("Sample config does not contain a non-empty experiments array.")

    first = experiments[0]

    if not isinstance(first, dict):
        raise RuntimeError("The first sample experiment is not a JSON object.")

    return copy.deepcopy(first)


def get_sample_experiments(sample_config: dict[str, Any]) -> list[dict[str, Any]]:
    experiments = sample_config.get("experiments", [])

    if not isinstance(experiments, list):
        raise RuntimeError("Sample config experiments field must be an array.")

    rows: list[dict[str, Any]] = []

    for item in experiments:
        if isinstance(item, dict):
            rows.append(item)

    if not rows:
        raise RuntimeError("Sample config does not contain valid experiment objects.")

    return rows


def infer_option_id(policy_id: str, method_id: str) -> str:
    if policy_id == "no_replanning_policy_v1":
        return "no_replanning_baseline"

    if method_id == "replanning_not_implemented_v1":
        return "threshold_without_solver"

    if method_id == "greedy_replanning_solver_v1":
        return "threshold_with_greedy_replanning"

    return sanitize_id(f"{policy_id}_{method_id}")


def extract_template_policy_options(sample_config: dict[str, Any]) -> list[dict[str, Any]]:
    sample_experiments = get_sample_experiments(sample_config)

    seen: set[tuple[str, str]] = set()
    options: list[dict[str, Any]] = []

    for experiment in sample_experiments:
        policy_id = str(experiment.get("policy_id", ""))
        method_id = str(experiment.get("replanning_method_id", ""))

        if not policy_id or not method_id:
            continue

        key = (policy_id, method_id)

        if key in seen:
            continue

        seen.add(key)

        options.append(
            {
                "option_id": infer_option_id(policy_id, method_id),
                "policy_id": policy_id,
                "replanning_method_id": method_id,
                "source": "sample_config_template",
            }
        )

    if not options:
        raise RuntimeError("Could not infer policy options from sample config.")

    return options


def extract_blueprint_policy_options(
    blueprint: dict[str, Any],
    fallback_options: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw_options = blueprint.get("policy_options", [])

    if not isinstance(raw_options, list) or not raw_options:
        return copy.deepcopy(fallback_options)

    options: list[dict[str, Any]] = []

    for index, item in enumerate(raw_options, start=1):
        if not isinstance(item, dict):
            continue

        policy_id = str(item.get("policy_id", ""))
        method_id = str(item.get("replanning_method_id", item.get("method_id", "")))

        if not policy_id or not method_id:
            continue

        option_id = str(
            item.get(
                "option_id",
                item.get("policy_option_id", infer_option_id(policy_id, method_id)),
            )
        )

        options.append(
            {
                "option_id": sanitize_id(option_id) or f"policy_option_{index:03d}",
                "policy_id": policy_id,
                "replanning_method_id": method_id,
                "source": "blueprint",
            }
        )

    if not options:
        return copy.deepcopy(fallback_options)

    return options


def extract_planned_runs(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_keys = [
        "planned_runs",
        "runs",
        "conditions",
        "planned_conditions",
    ]

    for key in candidate_keys:
        raw_runs = blueprint.get(key, [])

        if isinstance(raw_runs, list) and raw_runs:
            return [item for item in raw_runs if isinstance(item, dict)]

    family_id = str(blueprint.get("scenario_family_id", "unknown_family"))
    severity_id = str(blueprint.get("severity_id", "unknown_severity"))
    replication_count = int(blueprint.get("replication_count", 1))

    runs: list[dict[str, Any]] = []

    for replication_id in range(1, replication_count + 1):
        runs.append(
            {
                "planned_run_id": f"planned_{family_id}_{severity_id}_rep{replication_id:03d}",
                "scenario_family_id": family_id,
                "severity_id": severity_id,
                "replication_id": replication_id,
                "expected_descriptor": blueprint.get("expected_descriptor", ""),
                "conservative_action": blueprint.get("conservative_action", ""),
            }
        )

    return runs


def build_perturbation_template_map(sample_config: dict[str, Any]) -> dict[str, str]:
    sample_experiments = get_sample_experiments(sample_config)

    path_by_key: dict[str, str] = {}

    for experiment in sample_experiments:
        scenario_id = str(experiment.get("scenario_id", "")).lower()
        perturbation_path = str(experiment.get("perturbation_plan_path", ""))

        if not perturbation_path:
            continue

        if "light" in scenario_id and "light" not in path_by_key:
            path_by_key["light"] = perturbation_path

        if "moderate" in scenario_id and "moderate" not in path_by_key:
            path_by_key["moderate"] = perturbation_path

        if "severe" in scenario_id and "severe" not in path_by_key:
            path_by_key["severe"] = perturbation_path

        if "reassignment" in scenario_id:
            path_by_key["reassignment"] = perturbation_path

    if not path_by_key:
        raise RuntimeError("Could not infer perturbation_plan_path templates from sample config.")

    return path_by_key


def choose_perturbation_plan_path(
    family_id: str,
    severity_id: str,
    perturbation_templates: dict[str, str],
) -> tuple[str, str]:
    normalized_family = family_id.lower()
    normalized_severity = severity_id.lower()

    if "reassignment" in normalized_family and normalized_severity != "light":
        path = perturbation_templates.get("reassignment", "")

        if path:
            return path, "reassignment_template_reused"

    path = perturbation_templates.get(normalized_severity, "")

    if path:
        return path, f"{normalized_severity}_severity_template_reused"

    fallback_path = next(iter(perturbation_templates.values()))

    return fallback_path, "fallback_template_reused"


def choose_template_experiment_for_option(
    sample_config: dict[str, Any],
    policy_id: str,
    method_id: str,
) -> dict[str, Any]:
    sample_experiments = get_sample_experiments(sample_config)

    for experiment in sample_experiments:
        if (
            str(experiment.get("policy_id", "")) == policy_id
            and str(experiment.get("replanning_method_id", "")) == method_id
        ):
            return copy.deepcopy(experiment)

    return get_first_experiment_template(sample_config)


def get_instance_path(sample_config: dict[str, Any]) -> str:
    sample_experiments = get_sample_experiments(sample_config)

    for experiment in sample_experiments:
        instance_path = str(experiment.get("instance_path", ""))

        if instance_path:
            return instance_path

    raise RuntimeError("Could not infer instance_path from sample config.")


def make_seed(batch_index: int, run_index: int, option_index: int, replication_id: int) -> int:
    return 100000 + batch_index * 10000 + run_index * 100 + option_index * 10 + replication_id


def build_executable_batch_config(
    sample_config: dict[str, Any],
    blueprint: dict[str, Any],
    blueprint_path: Path,
    batch_index: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fallback_options = extract_template_policy_options(sample_config)
    policy_options = extract_blueprint_policy_options(blueprint, fallback_options)
    planned_runs = extract_planned_runs(blueprint)

    if not planned_runs:
        raise RuntimeError(f"Blueprint has no planned runs: {blueprint_path}")

    family_id = str(blueprint.get("scenario_family_id", planned_runs[0].get("scenario_family_id", "unknown_family")))
    severity_id = str(blueprint.get("severity_id", planned_runs[0].get("severity_id", "unknown_severity")))

    raw_batch_id = str(blueprint.get("batch_id", blueprint_path.stem))
    batch_id = sanitize_id(raw_batch_id.replace("_blueprint", ""))

    instance_path = get_instance_path(sample_config)
    perturbation_templates = build_perturbation_template_map(sample_config)

    generated_experiments: list[dict[str, Any]] = []
    template_reuse_modes: set[str] = set()

    for run_index, planned_run in enumerate(planned_runs, start=1):
        replication_id = int(planned_run.get("replication_id", run_index))
        planned_run_id = str(
            planned_run.get(
                "planned_run_id",
                f"planned_{family_id}_{severity_id}_rep{replication_id:03d}",
            )
        )

        run_family_id = str(planned_run.get("scenario_family_id", family_id))
        run_severity_id = str(planned_run.get("severity_id", severity_id))

        perturbation_path, reuse_mode = choose_perturbation_plan_path(
            run_family_id,
            run_severity_id,
            perturbation_templates,
        )

        template_reuse_modes.add(reuse_mode)

        for option_index, option in enumerate(policy_options, start=1):
            policy_id = str(option["policy_id"])
            method_id = str(option["replanning_method_id"])
            option_id = sanitize_id(str(option["option_id"]))

            experiment = choose_template_experiment_for_option(
                sample_config,
                policy_id,
                method_id,
            )

            experiment["experiment_id"] = sanitize_id(f"{planned_run_id}_{option_id}")
            experiment["instance_path"] = instance_path
            experiment["perturbation_plan_path"] = perturbation_path
            experiment["policy_id"] = policy_id
            experiment["replanning_method_id"] = method_id
            experiment["replication_id"] = replication_id
            experiment["scenario_id"] = sanitize_id(f"{run_family_id}_{run_severity_id}")
            experiment["seed"] = make_seed(batch_index, run_index, option_index, replication_id)

            experiment["notes"] = (
                "Template-based campaign experiment generated from blueprint. "
                f"family={run_family_id}; severity={run_severity_id}; "
                f"planned_run_id={planned_run_id}; option_id={option_id}; "
                f"expected_descriptor={planned_run.get('expected_descriptor', '')}; "
                f"conservative_action={planned_run.get('conservative_action', '')}; "
                f"perturbation_template_reuse_mode={reuse_mode}. "
                "This config is executable as a pipeline validation candidate, but it is not yet the final scientific campaign because perturbation plans are reused from the sample template."
            )

            generated_experiments.append(experiment)

    config = copy.deepcopy(sample_config)

    config["batch_id"] = batch_id
    config["name"] = f"Campaign batch candidate: {family_id} / {severity_id}"
    config["description"] = (
        "Template-based executable campaign batch candidate generated from a campaign blueprint. "
        "This is intended for pipeline validation before implementing final family-specific perturbation generation."
    )
    config["experiments"] = generated_experiments

    config["summary_csv_output_path"] = f"data/results/campaign_batches/{batch_id}_summary.csv"
    config["aggregate_csv_output_path"] = f"data/results/campaign_batches/{batch_id}_aggregate_summary.csv"
    config["ranking_csv_output_path"] = f"data/results/campaign_batches/{batch_id}_ranking.csv"
    config["result_json_output_path"] = f"data/results/campaign_batches/{batch_id}_result.json"

    if "overview_csv_output_path" in config:
        config["overview_csv_output_path"] = f"data/results/campaign_batches/{batch_id}_overview.csv"

    if "recommendation_csv_output_path" in config:
        config["recommendation_csv_output_path"] = f"data/results/campaign_batches/{batch_id}_recommendation.csv"

    metadata = {
        "batch_id": batch_id,
        "source_blueprint_path": str(blueprint_path),
        "scenario_family_id": family_id,
        "severity_id": severity_id,
        "planned_run_count": len(planned_runs),
        "policy_option_count": len(policy_options),
        "generated_experiment_count": len(generated_experiments),
        "template_reuse_modes": sorted(template_reuse_modes),
        "semantic_status": "template_based_executable_candidate",
        "scientific_status": "not_final_campaign_semantics",
    }

    return config, metadata


def load_blueprint_paths(index_data: dict[str, Any], blueprint_dir: Path) -> list[Path]:
    paths: list[Path] = []

    raw_blueprints = index_data.get("blueprints", [])

    if isinstance(raw_blueprints, list):
        for item in raw_blueprints:
            if not isinstance(item, dict):
                continue

            raw_path = str(item.get("blueprint_path", ""))

            if raw_path:
                paths.append(Path(raw_path))

    if not paths:
        paths = sorted(blueprint_dir.glob("*.json"))

    unique_paths: list[Path] = []
    seen: set[str] = set()

    for path in paths:
        key = str(path)

        if key in seen:
            continue

        seen.add(key)
        unique_paths.append(path)

    if not unique_paths:
        raise RuntimeError("No blueprint paths found.")

    return unique_paths


def write_index_markdown(path: Path, rows: list[dict[str, Any]], output_config_dir: Path) -> None:
    total_batches = len(rows)
    total_experiments = sum(int(row["generated_experiment_count"]) for row in rows)

    lines: list[str] = []

    lines.append("# FieldOps Lab executable campaign batch config index")
    lines.append("")
    lines.append("This report indexes template-based executable batch config candidates generated from campaign blueprints.")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| output_config_dir | `{output_config_dir}` |")
    lines.append(f"| generated_batch_config_count | {format_value(total_batches)} |")
    lines.append(f"| generated_experiment_count | {format_value(total_experiments)} |")
    lines.append("| semantic_status | template_based_executable_candidate |")
    lines.append("| scientific_status | not_final_campaign_semantics |")
    lines.append("")
    lines.append("## Generated configs")
    lines.append("")
    lines.append("| Batch | Family | Severity | Experiments | Config path | Semantic status |")
    lines.append("| --- | --- | --- | ---: | --- | --- |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{format_value(row['generated_experiment_count'])} | "
            f"`{row['config_path']}` | "
            f"{row['semantic_status']} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "These configs are intended to validate the execution pipeline at campaign scale. "
        "They deliberately reuse perturbation plan templates inferred from the current sample batch config."
    )
    lines.append("")
    lines.append(
        "Do not treat results from these generated configs as final scientific evidence yet. "
        "The next required step is to generate family-specific perturbation plans so travel-only, service-only, combined-delay, and reassignment scenarios are semantically faithful."
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "planned_run_count",
        "policy_option_count",
        "generated_experiment_count",
        "config_path",
        "source_blueprint_path",
        "semantic_status",
        "scientific_status",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_index_json(path: Path, rows: list[dict[str, Any]], output_config_dir: Path) -> None:
    total_experiments = sum(int(row["generated_experiment_count"]) for row in rows)

    payload = {
        "report_type": "fieldops_lab_executable_campaign_batch_config_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "overview": {
            "output_config_dir": str(output_config_dir),
            "generated_batch_config_count": len(rows),
            "generated_experiment_count": total_experiments,
            "semantic_status": "template_based_executable_candidate",
            "scientific_status": "not_final_campaign_semantics",
        },
        "generated_configs": rows,
        "interpretation": {
            "warning": "Generated configs reuse sample perturbation plan templates. They validate the pipeline, but they are not final scientific campaign configs.",
            "next_step": "Generate family-specific perturbation plans and then regenerate executable campaign configs with full semantic fidelity.",
        },
    }

    write_json(path, payload)


def main() -> int:
    if len(sys.argv) != 8:
        print(
            "Usage: py -3 analysis\\scripts\\generate_executable_campaign_batch_configs.py "
            "<sample_config_json> <blueprint_index_json> <blueprint_dir> "
            "<output_config_dir> <output_index_md> <output_index_json> <output_index_csv>",
            file=sys.stderr,
        )
        return 2

    sample_config_path = Path(sys.argv[1])
    blueprint_index_path = Path(sys.argv[2])
    blueprint_dir = Path(sys.argv[3])
    output_config_dir = Path(sys.argv[4])
    output_index_md = Path(sys.argv[5])
    output_index_json = Path(sys.argv[6])
    output_index_csv = Path(sys.argv[7])

    try:
        sample_config = load_json(sample_config_path)
        blueprint_index = load_json(blueprint_index_path)
        blueprint_paths = load_blueprint_paths(blueprint_index, blueprint_dir)

        output_config_dir.mkdir(parents=True, exist_ok=True)

        rows: list[dict[str, Any]] = []

        for batch_index, blueprint_path in enumerate(blueprint_paths, start=1):
            blueprint = load_json(blueprint_path)

            config, metadata = build_executable_batch_config(
                sample_config,
                blueprint,
                blueprint_path,
                batch_index,
            )

            config_path = output_config_dir / f"{metadata['batch_id']}.json"
            write_json(config_path, config)

            row = dict(metadata)
            row["config_path"] = str(config_path)
            rows.append(row)

        rows.sort(key=lambda item: str(item["batch_id"]))

        write_index_markdown(output_index_md, rows, output_config_dir)
        write_index_json(output_index_json, rows, output_config_dir)
        write_index_csv(output_index_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Executable campaign batch configs written to: {output_config_dir}")
    print(f"Executable campaign batch config index markdown written to: {output_index_md}")
    print(f"Executable campaign batch config index JSON written to: {output_index_json}")
    print(f"Executable campaign batch config index CSV written to: {output_index_csv}")
    print(f"Generated configs: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())