from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


POLICY_OPTION_ORDER = [
    "no_replanning_baseline",
    "threshold_without_solver",
    "threshold_with_greedy_replanning",
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


def sanitize_identifier(value: str) -> str:
    clean = value.strip().lower()
    clean = clean.replace("\\", "_").replace("/", "_").replace(" ", "_")
    clean = clean.replace("-", "_")

    allowed = []
    for char in clean:
        if char.isalnum() or char == "_":
            allowed.append(char)

    result = "".join(allowed)

    while "__" in result:
        result = result.replace("__", "_")

    return result.strip("_")


def get_nested(data: dict[str, Any], *keys: str, default: Any = "") -> Any:
    current: Any = data

    for key in keys:
        if not isinstance(current, dict):
            return default

        if key not in current:
            return default

        current = current[key]

    return current


def get_blueprint_entries(index_data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        index_data.get("blueprints"),
        index_data.get("rows"),
        index_data.get("generated_blueprints"),
        index_data.get("batch_blueprints"),
    ]

    for candidate in candidates:
        if isinstance(candidate, list):
            return [entry for entry in candidate if isinstance(entry, dict)]

    generated_files = index_data.get("generated_files")
    if isinstance(generated_files, list):
        return [entry for entry in generated_files if isinstance(entry, dict)]

    raise RuntimeError("Could not find blueprint entries in blueprint index JSON.")


def normalize_path(path_value: Any) -> str:
    return str(path_value).replace("/", "\\").strip()


def get_blueprint_path(entry: dict[str, Any], blueprint_dir: Path) -> Path:
    for key in ["blueprint_path", "path", "file_path", "output_path"]:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            path = Path(value)

            if path.exists():
                return path

            candidate = blueprint_dir / path.name
            if candidate.exists():
                return candidate

            return path

    batch_id = str(entry.get("batch_id", "")).strip()
    if not batch_id:
        raise RuntimeError(f"Blueprint entry has no path or batch_id: {entry}")

    filename = f"{batch_id}_blueprint.json"
    return blueprint_dir / filename


def get_array(data: dict[str, Any], candidate_keys: list[str]) -> list[dict[str, Any]]:
    for key in candidate_keys:
        value = data.get(key)

        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def get_blueprint_runs(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    runs = get_array(
        blueprint,
        [
            "planned_runs",
            "runs",
            "batch_runs",
            "replications",
        ],
    )

    if runs:
        return runs

    nested = get_nested(blueprint, "blueprint", "planned_runs", default=[])
    if isinstance(nested, list):
        return [item for item in nested if isinstance(item, dict)]

    nested = get_nested(blueprint, "batch", "planned_runs", default=[])
    if isinstance(nested, list):
        return [item for item in nested if isinstance(item, dict)]

    return []


def get_policy_options(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    options = get_array(
        blueprint,
        [
            "policy_options",
            "policies",
            "options",
            "planned_policy_options",
        ],
    )

    if options:
        return options

    nested = get_nested(blueprint, "blueprint", "policy_options", default=[])
    if isinstance(nested, list):
        return [item for item in nested if isinstance(item, dict)]

    nested = get_nested(blueprint, "batch", "policy_options", default=[])
    if isinstance(nested, list):
        return [item for item in nested if isinstance(item, dict)]

    return [
        {
            "option_id": "no_replanning_baseline",
            "policy_id": "no_replanning_policy_v1",
            "replanning_method_id": "replanning_not_implemented_v1",
        },
        {
            "option_id": "threshold_without_solver",
            "policy_id": "threshold_delay_replanning_policy_v1",
            "replanning_method_id": "replanning_not_implemented_v1",
        },
        {
            "option_id": "threshold_with_greedy_replanning",
            "policy_id": "threshold_delay_replanning_policy_v1",
            "replanning_method_id": "greedy_replanning_solver_v1",
        },
    ]


def get_text_value(data: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = data.get(key)

        if value is not None and str(value).strip():
            return str(value).strip()

    return default


def get_int_value(data: dict[str, Any], keys: list[str], default: int = 0) -> int:
    for key in keys:
        value = data.get(key)

        if value is None or value == "":
            continue

        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    return default


def get_bool_value(data: dict[str, Any], keys: list[str], default: bool = False) -> bool:
    for key in keys:
        value = data.get(key)

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in ("true", "yes", "1"):
                return True

            if normalized in ("false", "no", "0"):
                return False

    return default


def get_batch_family_and_severity(blueprint: dict[str, Any], entry: dict[str, Any]) -> tuple[str, str]:
    family = get_text_value(
        blueprint,
        ["scenario_family_id", "family_id", "family", "scenario_family"],
        "",
    )
    severity = get_text_value(
        blueprint,
        ["severity_id", "severity", "severity_level_id"],
        "",
    )

    if not family:
        family = get_text_value(
            entry,
            ["scenario_family_id", "family_id", "family", "scenario_family"],
            "",
        )

    if not severity:
        severity = get_text_value(
            entry,
            ["severity_id", "severity", "severity_level_id"],
            "",
        )

    batch = blueprint.get("batch")
    if isinstance(batch, dict):
        if not family:
            family = get_text_value(
                batch,
                ["scenario_family_id", "family_id", "family", "scenario_family"],
                "",
            )

        if not severity:
            severity = get_text_value(
                batch,
                ["severity_id", "severity", "severity_level_id"],
                "",
            )

    if not family or not severity:
        batch_id = get_text_value(
            blueprint,
            ["batch_id", "blueprint_id"],
            get_text_value(entry, ["batch_id"], ""),
        )

        normalized = sanitize_identifier(batch_id)

        known_families = [
            "travel_delay_only",
            "service_delay_only",
            "combined_delay",
            "reassignment_opportunity",
        ]

        known_severities = ["light", "moderate", "severe"]

        for candidate_family in known_families:
            if candidate_family in normalized and not family:
                family = candidate_family

        for candidate_severity in known_severities:
            if candidate_severity in normalized and not severity:
                severity = candidate_severity

    if not family:
        family = "unknown_family"

    if not severity:
        severity = "unknown_severity"

    return sanitize_identifier(family), sanitize_identifier(severity)


def get_blueprint_batch_id(blueprint: dict[str, Any], entry: dict[str, Any], family: str, severity: str) -> str:
    raw_id = get_text_value(
        blueprint,
        ["batch_id", "blueprint_id"],
        get_text_value(entry, ["batch_id"], ""),
    )

    if not raw_id:
        batch = blueprint.get("batch")

        if isinstance(batch, dict):
            raw_id = get_text_value(batch, ["batch_id", "blueprint_id"], "")

    if not raw_id:
        raw_id = f"campaign_{family}_{severity}_batch_blueprint"

    raw_id = sanitize_identifier(raw_id)

    for suffix in [
        "_blueprint_blueprint",
        "_batch_blueprint",
        "_blueprint",
    ]:
        if raw_id.endswith(suffix):
            raw_id = raw_id[: -len(suffix)]

    if not raw_id.endswith("_batch"):
        raw_id = f"{raw_id}_batch"

    return raw_id


def build_sample_experiment_templates(sample_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    experiments = sample_config.get("experiments")

    if not isinstance(experiments, list):
        raise RuntimeError("Sample batch config does not contain an experiments array.")

    templates: dict[str, dict[str, Any]] = {}

    for item in experiments:
        if not isinstance(item, dict):
            continue

        policy_id = str(item.get("policy_id", "")).strip()
        method_id = str(item.get("replanning_method_id", "")).strip()

        if policy_id == "no_replanning_policy_v1":
            templates.setdefault("no_replanning_baseline", item)

        if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "replanning_not_implemented_v1":
            templates.setdefault("threshold_without_solver", item)

        if policy_id == "threshold_delay_replanning_policy_v1" and method_id == "greedy_replanning_solver_v1":
            templates.setdefault("threshold_with_greedy_replanning", item)

    missing = [option_id for option_id in POLICY_OPTION_ORDER if option_id not in templates]

    if missing:
        raise RuntimeError(f"Sample config is missing required policy templates: {missing}")

    return templates


def build_perturbation_templates(sample_config: dict[str, Any]) -> dict[str, str]:
    experiments = sample_config.get("experiments")

    if not isinstance(experiments, list):
        raise RuntimeError("Sample batch config does not contain an experiments array.")

    mapping: dict[str, str] = {}

    for item in experiments:
        if not isinstance(item, dict):
            continue

        scenario_id = str(item.get("scenario_id", "")).lower()
        perturbation_path = str(item.get("perturbation_plan_path", "")).strip()

        if not perturbation_path:
            continue

        if "light" in scenario_id:
            mapping.setdefault("light", perturbation_path)

        if "moderate" in scenario_id:
            mapping.setdefault("moderate", perturbation_path)

        if "severe" in scenario_id:
            mapping.setdefault("severe", perturbation_path)

        if "reassignment" in scenario_id:
            mapping.setdefault("reassignment", perturbation_path)

    first = ""

    for item in experiments:
        if isinstance(item, dict) and str(item.get("perturbation_plan_path", "")).strip():
            first = str(item.get("perturbation_plan_path", "")).strip()
            break

    if first:
        mapping.setdefault("light", first)
        mapping.setdefault("moderate", first)
        mapping.setdefault("severe", first)
        mapping.setdefault("reassignment", first)

    return mapping


def choose_perturbation_template(
    family: str,
    severity: str,
    perturbation_templates: dict[str, str],
) -> tuple[str, str]:
    if family == "reassignment_opportunity" and severity in ("moderate", "severe"):
        return (
            perturbation_templates.get("reassignment", perturbation_templates.get(severity, "")),
            "reassignment_template_reused",
        )

    if severity in perturbation_templates:
        return (
            perturbation_templates[severity],
            f"{severity}_severity_template_reused",
        )

    return (
        perturbation_templates.get("light", ""),
        "fallback_template_reused",
    )


def build_seed(family: str, severity: str, replication_id: int, option_index: int) -> int:
    family_codes = {
        "travel_delay_only": 2,
        "service_delay_only": 3,
        "combined_delay": 4,
        "reassignment_opportunity": 5,
    }

    severity_codes = {
        "light": 1,
        "moderate": 2,
        "severe": 3,
    }

    family_code = family_codes.get(family, 9)
    severity_code = severity_codes.get(severity, 9)

    return 100000 + family_code * 10000 + severity_code * 1000 + replication_id * 100 + option_index * 10 + replication_id


def build_experiment(
    template: dict[str, Any],
    run: dict[str, Any],
    policy_option: dict[str, Any],
    family: str,
    severity: str,
    perturbation_plan_path: str,
    perturbation_reuse_mode: str,
    option_index: int,
) -> dict[str, Any]:
    planned_run_id = get_text_value(
        run,
        ["planned_run_id", "run_id", "id"],
        f"planned_{family}_{severity}_rep001",
    )

    option_id = get_text_value(
        policy_option,
        ["option_id", "id"],
        POLICY_OPTION_ORDER[option_index - 1] if 0 <= option_index - 1 < len(POLICY_OPTION_ORDER) else f"option_{option_index}",
    )

    replication_id = get_int_value(run, ["replication_id", "replication"], 1)
    expected_descriptor = get_text_value(run, ["expected_descriptor", "descriptor"], "unknown_descriptor")
    conservative_action = get_text_value(run, ["conservative_action", "action"], "unknown_action")

    experiment = dict(template)

    experiment["experiment_id"] = sanitize_identifier(f"{planned_run_id}_{option_id}")
    experiment["scenario_id"] = sanitize_identifier(f"{family}_{severity}")
    experiment["replication_id"] = replication_id
    experiment["seed"] = build_seed(family, severity, replication_id, option_index)
    experiment["policy_id"] = get_text_value(policy_option, ["policy_id"], str(template.get("policy_id", "")))
    experiment["replanning_method_id"] = get_text_value(
        policy_option,
        ["replanning_method_id", "method_id"],
        str(template.get("replanning_method_id", "")),
    )
    experiment["perturbation_plan_path"] = perturbation_plan_path

    experiment["notes"] = (
        "Template-based campaign experiment generated from blueprint. "
        f"family={family}; "
        f"severity={severity}; "
        f"planned_run_id={planned_run_id}; "
        f"option_id={option_id}; "
        f"expected_descriptor={expected_descriptor}; "
        f"conservative_action={conservative_action}; "
        f"perturbation_template_reuse_mode={perturbation_reuse_mode}. "
        "This config is executable as a pipeline validation candidate, but it is not yet the final scientific campaign because perturbation plans are reused from the sample template."
    )

    return experiment


def build_output_paths(batch_id: str) -> dict[str, str]:
    base_dir = "data/results/campaign_batches"

    return {
        "overview_csv_output_path": f"{base_dir}/{batch_id}_overview.csv",
        "summary_csv_output_path": f"{base_dir}/{batch_id}_summary.csv",
        "aggregate_csv_output_path": f"{base_dir}/{batch_id}_aggregate_summary.csv",
        "ranking_csv_output_path": f"{base_dir}/{batch_id}_ranking.csv",
        "recommendation_csv_output_path": f"{base_dir}/{batch_id}_recommendation.csv",
        "result_json_output_path": f"{base_dir}/{batch_id}_result.json",
    }


def build_batch_config(
    sample_config: dict[str, Any],
    blueprint: dict[str, Any],
    entry: dict[str, Any],
    sample_templates: dict[str, dict[str, Any]],
    perturbation_templates: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    family, severity = get_batch_family_and_severity(blueprint, entry)
    batch_id = get_blueprint_batch_id(blueprint, entry, family, severity)

    runs = get_blueprint_runs(blueprint)
    if not runs:
        raise RuntimeError(f"Blueprint has no planned runs: {batch_id}")

    policy_options = get_policy_options(blueprint)
    if not policy_options:
        raise RuntimeError(f"Blueprint has no policy options: {batch_id}")

    output_paths = build_output_paths(batch_id)

    experiments: list[dict[str, Any]] = []

    for run in runs:
        perturbation_plan_path, perturbation_reuse_mode = choose_perturbation_template(
            family,
            severity,
            perturbation_templates,
        )

        for option_index, option in enumerate(policy_options, start=1):
            option_id = get_text_value(option, ["option_id", "id"], "")

            if not option_id:
                policy_id = get_text_value(option, ["policy_id"], "")
                method_id = get_text_value(option, ["replanning_method_id", "method_id"], "")

                if policy_id == "no_replanning_policy_v1":
                    option_id = "no_replanning_baseline"
                elif method_id == "replanning_not_implemented_v1":
                    option_id = "threshold_without_solver"
                elif method_id == "greedy_replanning_solver_v1":
                    option_id = "threshold_with_greedy_replanning"

            if option_id not in sample_templates:
                raise RuntimeError(f"Could not map policy option to sample template. batch={batch_id}, option={option}")

            experiments.append(
                build_experiment(
                    sample_templates[option_id],
                    run,
                    option,
                    family,
                    severity,
                    perturbation_plan_path,
                    perturbation_reuse_mode,
                    option_index,
                )
            )

    batch_config: dict[str, Any] = {
        "batch_id": batch_id,
        "name": f"Campaign batch candidate: {family} / {severity}",
        "description": (
            "Template-based executable campaign batch candidate generated from a campaign blueprint. "
            "This is intended for pipeline validation before implementing final family-specific perturbation generation."
        ),
        "verbose": bool(sample_config.get("verbose", False)),
        "export_individual_results": bool(sample_config.get("export_individual_results", False)),
        "export_overview_csv": True,
        "export_summary_csv": True,
        "export_aggregate_csv": True,
        "export_ranking_csv": True,
        "export_recommendation_csv": True,
        "export_result_json": True,
        **output_paths,
        "experiments": experiments,
    }

    metadata = {
        "batch_id": batch_id,
        "scenario_family_id": family,
        "severity_id": severity,
        "replication_count": len(runs),
        "planned_run_count": len(runs),
        "policy_option_count": len(policy_options),
        "generated_experiment_count": len(experiments),
        "planned_algorithm_run_count": len(experiments),
        "config_path": "",
        "result_json_output_path": output_paths["result_json_output_path"],
        "overview_csv_output_path": output_paths["overview_csv_output_path"],
        "summary_csv_output_path": output_paths["summary_csv_output_path"],
        "aggregate_csv_output_path": output_paths["aggregate_csv_output_path"],
        "ranking_csv_output_path": output_paths["ranking_csv_output_path"],
        "recommendation_csv_output_path": output_paths["recommendation_csv_output_path"],
        "semantic_status": "template_based_executable_candidate",
        "scientific_status": "not_final_campaign_semantics",
    }

    return batch_config, metadata


def write_index_markdown(path: Path, rows: list[dict[str, Any]], output_config_dir: Path) -> None:
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
    lines.append(f"| generated_batch_config_count | {len(rows)} |")
    lines.append(f"| generated_experiment_count | {total_experiments} |")
    lines.append("| semantic_status | template_based_executable_candidate |")
    lines.append("| scientific_status | not_final_campaign_semantics |")
    lines.append("")
    lines.append("## Generated configs")
    lines.append("")
    lines.append("| Batch | Family | Severity | Experiments | Config path | Result path | Semantic status |")
    lines.append("| --- | --- | --- | ---: | --- | --- | --- |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{row['scenario_family_id']} | "
            f"{row['severity_id']} | "
            f"{row['generated_experiment_count']} | "
            f"`{row['config_path']}` | "
            f"`{row['result_json_output_path']}` | "
            f"{row['semantic_status']} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append("These configs are intended to validate the execution pipeline at campaign scale. They deliberately reuse perturbation plan templates inferred from the current sample batch config.")
    lines.append("")
    lines.append("Do not treat results from these generated configs as final scientific evidence yet. The next required step is to generate family-specific perturbation plans so travel-only, service-only, combined-delay, and reassignment scenarios are semantically faithful.")
    lines.append("")
    lines.append("This version also writes isolated output paths for overview, summary, aggregate, ranking, recommendation, and result JSON files under `data/results/campaign_batches`.")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_index_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "batch_id",
        "config_path",
        "scenario_family_id",
        "severity_id",
        "replication_count",
        "planned_run_count",
        "policy_option_count",
        "generated_experiment_count",
        "result_json_output_path",
        "overview_csv_output_path",
        "summary_csv_output_path",
        "aggregate_csv_output_path",
        "ranking_csv_output_path",
        "recommendation_csv_output_path",
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
        "index_type": "fieldops_lab_executable_campaign_batch_config_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "output_config_dir": str(output_config_dir),
        "generated_batch_config_count": len(rows),
        "generated_experiment_count": total_experiments,
        "semantic_status": "template_based_executable_candidate",
        "scientific_status": "not_final_campaign_semantics",
        "warning": (
            "These configs are executable candidates generated from templates. "
            "They are useful for pipeline validation, but not final scientific evidence."
        ),
        "rows": rows,
    }

    write_json(path, payload)


def main() -> int:
    if len(sys.argv) != 8:
        print(
            "Usage: py -3 analysis\\scripts\\generate_executable_campaign_batch_configs.py "
            "<sample_batch_config_json> <blueprint_index_json> <blueprint_dir> "
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

        sample_templates = build_sample_experiment_templates(sample_config)
        perturbation_templates = build_perturbation_templates(sample_config)

        entries = get_blueprint_entries(blueprint_index)

        if not entries:
            raise RuntimeError("No blueprint entries found.")

        output_config_dir.mkdir(parents=True, exist_ok=True)

        rows: list[dict[str, Any]] = []

        for entry in entries:
            blueprint_path = get_blueprint_path(entry, blueprint_dir)
            blueprint = load_json(blueprint_path)

            batch_config, row = build_batch_config(
                sample_config,
                blueprint,
                entry,
                sample_templates,
                perturbation_templates,
            )

            config_path = output_config_dir / f"{row['batch_id']}.json"
            row["config_path"] = str(config_path)

            write_json(config_path, batch_config)
            rows.append(row)

        rows.sort(key=lambda row: str(row["batch_id"]))

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