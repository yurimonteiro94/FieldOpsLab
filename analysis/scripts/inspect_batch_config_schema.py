from __future__ import annotations

import json
import sys
from collections import Counter
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


def get_top_level_shape(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for key in sorted(data.keys()):
        value = data[key]

        if isinstance(value, dict):
            value_type = "object"
            item_count = len(value)
        elif isinstance(value, list):
            value_type = "array"
            item_count = len(value)
        else:
            value_type = type(value).__name__
            item_count = 1

        rows.append(
            {
                "key": key,
                "type": value_type,
                "item_count": item_count,
            }
        )

    return rows


def find_candidate_experiment_arrays(data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, list):
            object_count = sum(1 for item in value if isinstance(item, dict))
            candidate_score = 0

            sample_keys: list[str] = []
            if value and isinstance(value[0], dict):
                sample_keys = sorted(str(key) for key in value[0].keys())

                important_keys = {
                    "experiment_id",
                    "scenario_id",
                    "policy",
                    "policy_id",
                    "replication_id",
                    "seed",
                    "instance_id",
                    "perturbation_plan_id",
                }

                candidate_score = sum(1 for key in sample_keys if key in important_keys)

            candidates.append(
                {
                    "path": path,
                    "length": len(value),
                    "object_count": object_count,
                    "candidate_score": candidate_score,
                    "sample_keys": sample_keys,
                }
            )

            for index, item in enumerate(value[:3]):
                walk(item, f"{path}[{index}]")

        elif isinstance(value, dict):
            for key, child in value.items():
                next_path = f"{path}.{key}" if path else str(key)
                walk(child, next_path)

    walk(data, "")

    candidates.sort(
        key=lambda row: (
            -int(row["candidate_score"]),
            -int(row["length"]),
            str(row["path"]),
        )
    )

    return candidates


def collect_key_paths(data: Any) -> Counter[str]:
    counter: Counter[str] = Counter()

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                next_path = f"{path}.{key}" if path else str(key)
                counter[next_path] += 1
                walk(child, next_path)
        elif isinstance(value, list):
            for item in value:
                walk(item, f"{path}[]")

    walk(data, "")
    return counter


def summarize_blueprint_index(index_data: dict[str, Any]) -> dict[str, Any]:
    blueprints = index_data.get("blueprints", [])

    if not isinstance(blueprints, list):
        blueprints = []

    family_counter: Counter[str] = Counter()
    severity_counter: Counter[str] = Counter()
    status_counter: Counter[str] = Counter()

    total_planned_runs = 0
    total_algorithm_runs = 0

    for item in blueprints:
        if not isinstance(item, dict):
            continue

        family_counter[str(item.get("scenario_family_id", ""))] += 1
        severity_counter[str(item.get("severity_id", ""))] += 1
        status_counter[str(item.get("executable_status", ""))] += 1

        total_planned_runs += int(item.get("planned_run_count", 0))
        total_algorithm_runs += int(item.get("planned_algorithm_run_count", 0))

    return {
        "blueprint_count": len(blueprints),
        "family_counter": dict(sorted(family_counter.items())),
        "severity_counter": dict(sorted(severity_counter.items())),
        "status_counter": dict(sorted(status_counter.items())),
        "total_planned_run_count": total_planned_runs,
        "total_planned_algorithm_run_count": total_algorithm_runs,
    }


def inspect_blueprint_files(blueprint_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if not blueprint_dir.exists():
        raise RuntimeError(f"Blueprint directory does not exist: {blueprint_dir}")

    if not blueprint_dir.is_dir():
        raise RuntimeError(f"Blueprint path is not a directory: {blueprint_dir}")

    for path in sorted(blueprint_dir.glob("*.json")):
        data = load_json(path)

        top_level_keys = sorted(data.keys())
        key_counter = collect_key_paths(data)

        rows.append(
            {
                "path": str(path),
                "file_name": path.name,
                "size_bytes": path.stat().st_size,
                "top_level_key_count": len(top_level_keys),
                "top_level_keys": top_level_keys,
                "key_path_count": len(key_counter),
            }
        )

    return rows


def write_json_report(
    output_path: Path,
    sample_config_path: Path,
    blueprint_index_path: Path,
    blueprint_dir: Path,
    sample_config: dict[str, Any],
    blueprint_index: dict[str, Any],
    blueprint_files: list[dict[str, Any]],
) -> None:
    sample_key_counter = collect_key_paths(sample_config)

    payload = {
        "report_type": "fieldops_lab_batch_config_schema_inspection",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "inputs": {
            "sample_config_path": str(sample_config_path),
            "blueprint_index_path": str(blueprint_index_path),
            "blueprint_dir": str(blueprint_dir),
        },
        "sample_config": {
            "top_level_shape": get_top_level_shape(sample_config),
            "candidate_experiment_arrays": find_candidate_experiment_arrays(sample_config),
            "key_path_count": len(sample_key_counter),
            "most_common_key_paths": [
                {"path": key, "count": count}
                for key, count in sample_key_counter.most_common(80)
            ],
        },
        "blueprint_index": summarize_blueprint_index(blueprint_index),
        "blueprint_files": blueprint_files,
        "interpretation": {
            "status": "schema_inspection_only",
            "next_step": "Use this inspection to implement a safer blueprint-to-executable-batch-config generator.",
            "warning": "This report does not modify executable configs. It only inspects the current structure.",
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_markdown_report(
    output_path: Path,
    sample_config_path: Path,
    blueprint_index_path: Path,
    blueprint_dir: Path,
    sample_config: dict[str, Any],
    blueprint_index: dict[str, Any],
    blueprint_files: list[dict[str, Any]],
) -> None:
    top_level_shape = get_top_level_shape(sample_config)
    candidate_arrays = find_candidate_experiment_arrays(sample_config)
    blueprint_summary = summarize_blueprint_index(blueprint_index)

    lines: list[str] = []

    lines.append("# FieldOps Lab batch config schema inspection")
    lines.append("")
    lines.append("This report inspects the current executable sample batch config and the campaign blueprints.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("| Input | Path |")
    lines.append("| --- | --- |")
    lines.append(f"| sample_config | `{sample_config_path}` |")
    lines.append(f"| blueprint_index | `{blueprint_index_path}` |")
    lines.append(f"| blueprint_dir | `{blueprint_dir}` |")
    lines.append("")
    lines.append("## Sample config top-level shape")
    lines.append("")
    lines.append("| Key | Type | Item count |")
    lines.append("| --- | --- | ---: |")

    for row in top_level_shape:
        lines.append(
            f"| {row['key']} | {row['type']} | {format_value(row['item_count'])} |"
        )

    lines.append("")
    lines.append("## Candidate experiment arrays in sample config")
    lines.append("")
    lines.append("| Path | Length | Object count | Candidate score | Sample keys |")
    lines.append("| --- | ---: | ---: | ---: | --- |")

    for row in candidate_arrays[:12]:
        sample_keys = ", ".join(row["sample_keys"][:12])
        if len(row["sample_keys"]) > 12:
            sample_keys += ", ..."

        lines.append(
            "| "
            f"{row['path']} | "
            f"{format_value(row['length'])} | "
            f"{format_value(row['object_count'])} | "
            f"{format_value(row['candidate_score'])} | "
            f"{sample_keys} |"
        )

    lines.append("")
    lines.append("## Blueprint index summary")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| blueprint_count | {format_value(blueprint_summary['blueprint_count'])} |")
    lines.append(
        f"| total_planned_run_count | {format_value(blueprint_summary['total_planned_run_count'])} |"
    )
    lines.append(
        f"| total_planned_algorithm_run_count | {format_value(blueprint_summary['total_planned_algorithm_run_count'])} |"
    )
    lines.append("")

    lines.append("## Blueprint files")
    lines.append("")
    lines.append("| File | Size bytes | Top-level key count | Key path count |")
    lines.append("| --- | ---: | ---: | ---: |")

    for row in blueprint_files:
        lines.append(
            "| "
            f"{row['file_name']} | "
            f"{format_value(row['size_bytes'])} | "
            f"{format_value(row['top_level_key_count'])} | "
            f"{format_value(row['key_path_count'])} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This inspection is a safety step before generating executable campaign configs. "
        "The project currently has valid planning blueprints, but they still need to be mapped carefully to the actual batch config schema used by the C++ executable."
    )
    lines.append("")
    lines.append(
        "The next step should be a generator that creates concrete batch config JSON files from these blueprints, using the current sample config as the structural template."
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\inspect_batch_config_schema.py "
            "<sample_config_json> <blueprint_index_json> <blueprint_dir> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    sample_config_path = Path(sys.argv[1])
    blueprint_index_path = Path(sys.argv[2])
    blueprint_dir = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    try:
        sample_config = load_json(sample_config_path)
        blueprint_index = load_json(blueprint_index_path)
        blueprint_files = inspect_blueprint_files(blueprint_dir)

        write_markdown_report(
            output_md,
            sample_config_path,
            blueprint_index_path,
            blueprint_dir,
            sample_config,
            blueprint_index,
            blueprint_files,
        )

        write_json_report(
            output_json,
            sample_config_path,
            blueprint_index_path,
            blueprint_dir,
            sample_config,
            blueprint_index,
            blueprint_files,
        )

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Batch config schema inspection markdown written to: {output_md}")
    print(f"Batch config schema inspection JSON written to: {output_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())