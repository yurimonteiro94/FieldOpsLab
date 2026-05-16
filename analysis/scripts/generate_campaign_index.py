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
        raise RuntimeError(f"Manifest file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"Manifest root must be a JSON object: {path}")

    return data


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


def discover_manifest_paths(reports_dir: Path) -> list[Path]:
    if not reports_dir.exists():
        raise RuntimeError(f"Reports directory does not exist: {reports_dir}")

    if not reports_dir.is_dir():
        raise RuntimeError(f"Reports path is not a directory: {reports_dir}")

    paths = sorted(reports_dir.glob("*_analysis_manifest.json"))

    if not paths:
        raise RuntimeError(f"No analysis manifest files found in: {reports_dir}")

    return paths


def safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def build_manifest_row(path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    batch = safe_dict(manifest.get("batch", {}))
    ranking = safe_dict(manifest.get("ranking", {}))
    recommendations = safe_dict(manifest.get("recommendations", {}))
    quality_gate = safe_dict(manifest.get("quality_gate", {}))
    interpretation = safe_dict(manifest.get("interpretation", {}))

    generated_files = manifest.get("generated_files", [])
    generated_file_count = len(generated_files) if isinstance(generated_files, list) else 0

    return {
        "manifest_path": str(path),
        "batch_id": batch.get("batch_id", ""),
        "batch_name": batch.get("name", ""),
        "configured_experiment_count": batch.get("configured_experiment_count", 0),
        "completed_experiment_count": batch.get("completed_experiment_count", 0),
        "completion_percent": batch.get("completion_percent", 0),
        "is_complete": batch.get("is_complete", False),
        "experiment_count": batch.get("experiment_count", 0),
        "ranking_config_id": ranking.get("ranking_config_id", ""),
        "ranking_row_count": ranking.get("row_count", 0),
        "recommendation_count": recommendations.get("recommendation_count", 0),
        "generated_file_count": generated_file_count,
        "all_expected_files_ok": quality_gate.get("all_expected_files_ok", False),
        "missing_or_invalid_file_count": quality_gate.get("missing_or_invalid_file_count", 0),
        "fuzzy_logic_status": interpretation.get("fuzzy_logic_status", ""),
        "scientific_status": interpretation.get("scientific_status", ""),
        "warning": interpretation.get("warning", ""),
    }


def to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_campaign(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_configured = sum(to_int(row["configured_experiment_count"]) for row in rows)
    total_completed = sum(to_int(row["completed_experiment_count"]) for row in rows)

    complete_batch_count = sum(1 for row in rows if bool(row["is_complete"]))
    quality_ok_count = sum(1 for row in rows if bool(row["all_expected_files_ok"]))

    incomplete_batches = [
        row["batch_id"]
        for row in rows
        if not bool(row["is_complete"])
    ]

    quality_problem_batches = [
        row["batch_id"]
        for row in rows
        if not bool(row["all_expected_files_ok"])
    ]

    objective_only_batches = [
        row["batch_id"]
        for row in rows
        if str(row["ranking_config_id"]) == "default_objective_delta_ranking_v1"
    ]

    fuzzy_used_batches = [
        row["batch_id"]
        for row in rows
        if str(row["fuzzy_logic_status"]) not in ("", "not_used_in_main_pipeline")
    ]

    if total_configured > 0:
        global_completion_percent = 100.0 * total_completed / total_configured
    else:
        global_completion_percent = 0.0

    return {
        "manifest_count": len(rows),
        "total_configured_experiment_count": total_configured,
        "total_completed_experiment_count": total_completed,
        "global_completion_percent": global_completion_percent,
        "complete_batch_count": complete_batch_count,
        "quality_ok_batch_count": quality_ok_count,
        "incomplete_batch_count": len(incomplete_batches),
        "quality_problem_batch_count": len(quality_problem_batches),
        "objective_only_batch_count": len(objective_only_batches),
        "fuzzy_used_batch_count": len(fuzzy_used_batches),
        "incomplete_batches": incomplete_batches,
        "quality_problem_batches": quality_problem_batches,
        "objective_only_batches": objective_only_batches,
        "fuzzy_used_batches": fuzzy_used_batches,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "batch_name",
        "configured_experiment_count",
        "completed_experiment_count",
        "completion_percent",
        "is_complete",
        "experiment_count",
        "ranking_config_id",
        "ranking_row_count",
        "recommendation_count",
        "generated_file_count",
        "all_expected_files_ok",
        "missing_or_invalid_file_count",
        "fuzzy_logic_status",
        "scientific_status",
        "manifest_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, campaign: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "manifest_type": "fieldops_lab_campaign_index",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "campaign": campaign,
        "batches": rows,
        "interpretation": {
            "status": "campaign_index_only",
            "warning": "This file consolidates analysis manifests. It does not prove scientific validity by itself.",
        },
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def write_markdown(path: Path, campaign: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign index")
    lines.append("")
    lines.append("This report consolidates all batch analysis manifests found in the reports directory.")
    lines.append("")
    lines.append("## Campaign overview")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| manifest_count | {format_number(campaign['manifest_count'])} |")
    lines.append(f"| total_configured_experiment_count | {format_number(campaign['total_configured_experiment_count'])} |")
    lines.append(f"| total_completed_experiment_count | {format_number(campaign['total_completed_experiment_count'])} |")
    lines.append(f"| global_completion_percent | {format_number(campaign['global_completion_percent'])} |")
    lines.append(f"| complete_batch_count | {format_number(campaign['complete_batch_count'])} |")
    lines.append(f"| quality_ok_batch_count | {format_number(campaign['quality_ok_batch_count'])} |")
    lines.append(f"| incomplete_batch_count | {format_number(campaign['incomplete_batch_count'])} |")
    lines.append(f"| quality_problem_batch_count | {format_number(campaign['quality_problem_batch_count'])} |")
    lines.append(f"| objective_only_batch_count | {format_number(campaign['objective_only_batch_count'])} |")
    lines.append(f"| fuzzy_used_batch_count | {format_number(campaign['fuzzy_used_batch_count'])} |")
    lines.append("")

    lines.append("## Batch table")
    lines.append("")
    lines.append("| Batch | Complete | Quality ok | Experiments | Completion | Ranking config | Recommendations | Scientific status |")
    lines.append("| --- | --- | --- | ---: | ---: | --- | ---: | --- |")

    for row in rows:
        lines.append(
            "| "
            f"{row['batch_id']} | "
            f"{yes_no(row['is_complete'])} | "
            f"{yes_no(row['all_expected_files_ok'])} | "
            f"{format_number(row['completed_experiment_count'])}/{format_number(row['configured_experiment_count'])} | "
            f"{format_number(row['completion_percent'])} | "
            f"{row['ranking_config_id']} | "
            f"{format_number(row['recommendation_count'])} | "
            f"{row['scientific_status']} |"
        )

    lines.append("")
    lines.append("## Quality notes")
    lines.append("")

    if campaign["quality_problem_batches"]:
        lines.append("The following batches have quality problems:")
        lines.append("")

        for batch_id in campaign["quality_problem_batches"]:
            lines.append(f"- {batch_id}")
    else:
        lines.append("No manifest-level quality problems were detected.")

    lines.append("")

    if campaign["incomplete_batches"]:
        lines.append("The following batches are incomplete:")
        lines.append("")

        for batch_id in campaign["incomplete_batches"]:
            lines.append(f"- {batch_id}")
    else:
        lines.append("All discovered batches are marked as complete.")

    lines.append("")
    lines.append("## Methodological notes")
    lines.append("")

    if campaign["manifest_count"] == 1:
        lines.append("- Only one batch manifest was found. This is enough to validate the reporting pipeline, but not enough for a campaign-level conclusion.")
    else:
        lines.append("- Multiple batch manifests were found. This is the beginning of a campaign-level evidence layer.")

    if campaign["objective_only_batch_count"] > 0:
        lines.append("- At least one batch still uses an objective-only ranking configuration. This should be treated as preliminary.")

    if campaign["fuzzy_used_batch_count"] == 0:
        lines.append("- Fuzzy logic is not being used in the main analysis pipeline. This matches the current conservative project direction.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append("This index is a project organization layer. It helps track batches, reports, quality status, and preliminary scientific status. It does not replace statistical validation, broader scenarios, or final methodological justification.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\generate_campaign_index.py "
            "<reports_dir> <output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )

        return 2

    reports_dir = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    output_json = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    try:
        manifest_paths = discover_manifest_paths(reports_dir)

        rows = []

        for manifest_path in manifest_paths:
            manifest = load_json(manifest_path)
            rows.append(build_manifest_row(manifest_path, manifest))

        rows.sort(key=lambda row: str(row["batch_id"]))

        campaign = build_campaign(rows)

        write_markdown(output_md, campaign, rows)
        write_json(output_json, campaign, rows)
        write_csv(output_csv, rows)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Campaign index markdown written to: {output_md}")
    print(f"Campaign index JSON written to: {output_json}")
    print(f"Campaign index CSV written to: {output_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())