from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


EXPECTED_CSV_HEADER = [
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

FORBIDDEN_ACCIDENTAL_ROOT_ARTIFACTS = [
    "Any",
    "None",
    "dict[str",
    "int",
    "list[Path]",
    "str",
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Text file not found: {path}") from exc


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            header = list(reader.fieldnames or [])
            rows = list(reader)
    except FileNotFoundError as exc:
        raise RuntimeError(f"CSV file not found: {path}") from exc

    return header, rows


def as_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return 0
        return int(float(text))

    return 0


def as_float(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))

    if isinstance(value, int | float):
        return float(value)

    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return 0.0
        return float(text)

    return 0.0


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int | float):
        return value != 0

    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "ok"}

    return False


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


def add_problem(problems: list[str], message: str) -> None:
    problems.append(message)


def add_warning(warnings: list[str], message: str) -> None:
    warnings.append(message)


def validate_json_structure(payload: dict[str, Any], problems: list[str], warnings: list[str]) -> None:
    manifest_type = payload.get("manifest_type")
    if manifest_type != "fieldops_lab_campaign_index":
        add_problem(
            problems,
            f"Unexpected manifest_type. Expected fieldops_lab_campaign_index, found {manifest_type!r}.",
        )

    campaign = payload.get("campaign")
    batches = payload.get("batches")

    if not isinstance(campaign, dict):
        add_problem(problems, "Missing or invalid campaign object.")
        campaign = {}

    if not isinstance(batches, list):
        add_problem(problems, "Missing or invalid batches list.")
        batches = []

    if not batches:
        add_problem(problems, "Campaign index has no batch rows.")

    manifest_count = as_int(campaign.get("manifest_count", 0))
    if manifest_count != len(batches):
        add_problem(
            problems,
            f"manifest_count mismatch. campaign={manifest_count}, batches={len(batches)}.",
        )

    total_configured = sum(as_int(row.get("configured_experiment_count", 0)) for row in batches if isinstance(row, dict))
    total_completed = sum(as_int(row.get("completed_experiment_count", 0)) for row in batches if isinstance(row, dict))

    if as_int(campaign.get("total_configured_experiment_count", 0)) != total_configured:
        add_problem(problems, "total_configured_experiment_count does not match batch rows.")

    if as_int(campaign.get("total_completed_experiment_count", 0)) != total_completed:
        add_problem(problems, "total_completed_experiment_count does not match batch rows.")

    if total_configured > 0:
        expected_completion = 100.0 * total_completed / total_configured
    else:
        expected_completion = 0.0

    observed_completion = as_float(campaign.get("global_completion_percent", 0))
    if abs(observed_completion - expected_completion) > 0.0001:
        add_problem(
            problems,
            f"global_completion_percent mismatch. expected={expected_completion}, observed={observed_completion}.",
        )

    complete_batch_count = sum(
        1
        for row in batches
        if isinstance(row, dict) and as_bool(row.get("is_complete", False))
    )
    quality_ok_batch_count = sum(
        1
        for row in batches
        if isinstance(row, dict) and as_bool(row.get("all_expected_files_ok", False))
    )

    if as_int(campaign.get("complete_batch_count", 0)) != complete_batch_count:
        add_problem(problems, "complete_batch_count does not match batch rows.")

    if as_int(campaign.get("quality_ok_batch_count", 0)) != quality_ok_batch_count:
        add_problem(problems, "quality_ok_batch_count does not match batch rows.")

    incomplete_batch_count = as_int(campaign.get("incomplete_batch_count", 0))
    quality_problem_batch_count = as_int(campaign.get("quality_problem_batch_count", 0))

    if incomplete_batch_count > 0:
        add_warning(
            warnings,
            f"Campaign contains {incomplete_batch_count} incomplete batch(es). This may be acceptable during development.",
        )

    if quality_problem_batch_count > 0:
        add_problem(
            problems,
            f"Campaign contains {quality_problem_batch_count} batch(es) with manifest-level quality problems.",
        )

    objective_only_batch_count = as_int(campaign.get("objective_only_batch_count", 0))
    if objective_only_batch_count > 0:
        add_warning(
            warnings,
            f"Campaign contains {objective_only_batch_count} objective-only batch(es). Treat conclusions as preliminary.",
        )

    fuzzy_used_batch_count = as_int(campaign.get("fuzzy_used_batch_count", 0))
    if fuzzy_used_batch_count > 0:
        add_warning(
            warnings,
            f"Campaign contains {fuzzy_used_batch_count} batch(es) using fuzzy logic in the main pipeline.",
        )


def validate_markdown(markdown_path: Path, text: str, problems: list[str]) -> None:
    required_fragments = [
        "# FieldOps Lab campaign index",
        "## Campaign overview",
        "## Batch table",
        "## Conservative interpretation",
    ]

    for fragment in required_fragments:
        if fragment not in text:
            add_problem(problems, f"Markdown file is missing expected text: {fragment}")

    if markdown_path.stat().st_size == 0:
        add_problem(problems, f"Markdown file is empty: {markdown_path}")


def validate_csv(
    header: list[str],
    rows: list[dict[str, str]],
    payload: dict[str, Any],
    problems: list[str],
) -> None:
    if header != EXPECTED_CSV_HEADER:
        add_problem(
            problems,
            f"CSV header mismatch. expected={EXPECTED_CSV_HEADER}, observed={header}.",
        )

    batches = payload.get("batches", [])
    if not isinstance(batches, list):
        batches = []

    if len(rows) != len(batches):
        add_problem(
            problems,
            f"CSV row count mismatch. csv={len(rows)}, json_batches={len(batches)}.",
        )

    json_batch_ids = {
        str(row.get("batch_id", ""))
        for row in batches
        if isinstance(row, dict)
    }
    csv_batch_ids = {str(row.get("batch_id", "")) for row in rows}

    if json_batch_ids != csv_batch_ids:
        add_problem(
            problems,
            f"CSV batch IDs do not match JSON batch IDs. csv={sorted(csv_batch_ids)}, json={sorted(json_batch_ids)}.",
        )


def validate_forbidden_root_artifacts(problems: list[str]) -> None:
    found = []

    for artifact in FORBIDDEN_ACCIDENTAL_ROOT_ARTIFACTS:
        path = Path(artifact)
        if path.exists():
            found.append(artifact)

    if found:
        add_problem(
            problems,
            "Accidental root artifacts found. Remove these files before continuing: "
            + ", ".join(found),
        )


def write_markdown_report(
    output_path: Path,
    campaign_json_path: Path,
    campaign_md_path: Path,
    campaign_csv_path: Path,
    problems: list[str],
    warnings: list[str],
    payload: dict[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    campaign = payload.get("campaign", {})
    if not isinstance(campaign, dict):
        campaign = {}

    batches = payload.get("batches", [])
    if not isinstance(batches, list):
        batches = []

    lines: list[str] = []

    lines.append("# FieldOps Lab campaign quality check")
    lines.append("")
    lines.append(f"Campaign JSON: `{campaign_json_path}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {'yes' if not problems else 'no'} |")
    lines.append(f"| problem_count | {len(problems)} |")
    lines.append(f"| warning_count | {len(warnings)} |")
    lines.append(f"| batch_count | {len(batches)} |")
    lines.append(f"| campaign_markdown | `{campaign_md_path}` |")
    lines.append(f"| campaign_csv | `{campaign_csv_path}` |")
    lines.append("")

    lines.append("## Campaign values")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in [
        "manifest_count",
        "total_configured_experiment_count",
        "total_completed_experiment_count",
        "global_completion_percent",
        "complete_batch_count",
        "quality_ok_batch_count",
        "incomplete_batch_count",
        "quality_problem_batch_count",
        "objective_only_batch_count",
        "fuzzy_used_batch_count",
    ]:
        lines.append(f"| {key} | {format_number(campaign.get(key, ''))} |")
    lines.append("")

    lines.append("## Problems")
    lines.append("")
    if problems:
        for problem in problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if warnings:
        for warning in warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    if problems:
        lines.append(
            "The campaign index did not pass the quality check. Do not use this campaign index as evidence until the listed problems are corrected."
        )
    else:
        lines.append(
            "The campaign index passed the structural quality check. This does not prove scientific validity, but it reduces the risk of using missing, inconsistent, or accidentally contaminated campaign outputs."
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json_report(
    output_path: Path,
    campaign_json_path: Path,
    campaign_md_path: Path,
    campaign_csv_path: Path,
    problems: list[str],
    warnings: list[str],
    payload: dict[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "report_type": "fieldops_lab_campaign_quality_check",
        "generated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "campaign_json_path": str(campaign_json_path),
        "campaign_markdown_path": str(campaign_md_path),
        "campaign_csv_path": str(campaign_csv_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "problems": problems,
        "warnings": warnings,
        "campaign": payload.get("campaign", {}),
        "batch_count": len(payload.get("batches", [])) if isinstance(payload.get("batches", []), list) else 0,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_campaign_index.py "
            "<campaign_json> <campaign_md> <campaign_csv> <quality_md> <quality_json>",
            file=sys.stderr,
        )
        return 2

    campaign_json_path = Path(sys.argv[1])
    campaign_md_path = Path(sys.argv[2])
    campaign_csv_path = Path(sys.argv[3])
    quality_md_path = Path(sys.argv[4])
    quality_json_path = Path(sys.argv[5])

    problems: list[str] = []
    warnings: list[str] = []

    try:
        payload = load_json(campaign_json_path)
        markdown_text = read_text(campaign_md_path)
        csv_header, csv_rows = read_csv_rows(campaign_csv_path)

        validate_json_structure(payload, problems, warnings)
        validate_markdown(campaign_md_path, markdown_text, problems)
        validate_csv(csv_header, csv_rows, payload, problems)
        validate_forbidden_root_artifacts(problems)

        write_markdown_report(
            quality_md_path,
            campaign_json_path,
            campaign_md_path,
            campaign_csv_path,
            problems,
            warnings,
            payload,
        )
        write_json_report(
            quality_json_path,
            campaign_json_path,
            campaign_md_path,
            campaign_csv_path,
            problems,
            warnings,
            payload,
        )

    except RuntimeError as exc:
        problems.append(str(exc))

        fallback_payload: dict[str, Any] = {
            "campaign": {},
            "batches": [],
        }

        write_markdown_report(
            quality_md_path,
            campaign_json_path,
            campaign_md_path,
            campaign_csv_path,
            problems,
            warnings,
            fallback_payload,
        )
        write_json_report(
            quality_json_path,
            campaign_json_path,
            campaign_md_path,
            campaign_csv_path,
            problems,
            warnings,
            fallback_payload,
        )

    print(f"Campaign quality report written to: {quality_md_path}")
    print(f"Campaign quality JSON written to: {quality_json_path}")

    if problems:
        print("ERROR: Campaign quality check failed.", file=sys.stderr)
        return 1

    print("Campaign quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())