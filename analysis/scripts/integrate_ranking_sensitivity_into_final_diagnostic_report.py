from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ADDED_FIELDS = [
    "ranking_stability_class",
    "ranking_unique_policy_count",
    "ranking_profile_recommendations",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}. Error: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")

    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_id(value: Any) -> str:
    return normalize_text(value).strip()


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


def int_value(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    try:
        text = str(value).strip()
        if not text:
            return default

        return int(float(text))
    except (TypeError, ValueError):
        return default


def first_present(data: dict[str, Any], keys: list[str], default: Any = "") -> Any:
    for key in keys:
        if key in data:
            value = data[key]
            if value is not None:
                return value

    return default


def recursive_find_value(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]

        for value in data.values():
            found = recursive_find_value(value, key)
            if found is not None:
                return found

    if isinstance(data, list):
        for item in data:
            found = recursive_find_value(item, key)
            if found is not None:
                return found

    return None


def collect_dict_lists(data: Any) -> list[list[dict[str, Any]]]:
    lists: list[list[dict[str, Any]]] = []

    if isinstance(data, dict):
        for value in data.values():
            lists.extend(collect_dict_lists(value))

    if isinstance(data, list):
        dict_items = [item for item in data if isinstance(item, dict)]

        if dict_items and len(dict_items) == len(data):
            lists.append(dict_items)

        for item in data:
            lists.extend(collect_dict_lists(item))

    return lists


def list_score_for_scenario_summary(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    keys = set()
    for row in rows[:5]:
        keys.update(str(key) for key in row.keys())

    score = 0

    if "batch_id" in keys:
        score += 5

    if "stability_class" in keys or "stability" in keys:
        score += 5

    if "unique_policy_count" in keys or "unique_recommended_policy_count" in keys:
        score += 3

    if "profile_recommendations" in keys or "profile_recommendation_summary" in keys:
        score += 3

    if 6 <= len(rows) <= 60:
        score += 2

    return score


def stringify_profile_recommendations(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        parts = []

        for key in sorted(value.keys()):
            item = value[key]

            if isinstance(item, dict):
                policy = first_present(
                    item,
                    [
                        "recommended_policy_id",
                        "policy_id",
                        "recommended_policy",
                        "policy",
                    ],
                    "",
                )
                method = first_present(
                    item,
                    [
                        "recommended_replanning_method_id",
                        "replanning_method_id",
                        "method_id",
                        "method",
                    ],
                    "",
                )

                if policy and method:
                    parts.append(f"{key}={policy}+{method}")
                elif policy:
                    parts.append(f"{key}={policy}")
                else:
                    parts.append(f"{key}={item}")
            else:
                parts.append(f"{key}={item}")

        return "; ".join(parts)

    if isinstance(value, list):
        return "; ".join(str(item) for item in value)

    return str(value)


def extract_sensitivity_rows(sensitivity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    direct_candidates = [
        sensitivity.get("scenario_summaries"),
        sensitivity.get("scenario_summary"),
        sensitivity.get("scenario_summary_rows"),
        sensitivity.get("summaries"),
    ]

    candidate_lists: list[list[dict[str, Any]]] = []

    for candidate in direct_candidates:
        if isinstance(candidate, list):
            rows = [item for item in candidate if isinstance(item, dict)]
            if rows:
                candidate_lists.append(rows)

    candidate_lists.extend(collect_dict_lists(sensitivity))

    best_rows: list[dict[str, Any]] = []
    best_score = -1

    for rows in candidate_lists:
        score = list_score_for_scenario_summary(rows)

        if score > best_score:
            best_score = score
            best_rows = rows

    by_batch: dict[str, dict[str, Any]] = {}

    for row in best_rows:
        batch_id = normalize_id(first_present(row, ["batch_id", "batch"], ""))

        if not batch_id:
            continue

        stability = normalize_id(
            first_present(
                row,
                [
                    "stability_class",
                    "stability",
                    "ranking_stability_class",
                    "recommendation_stability_class",
                ],
                "",
            )
        )

        unique_policy_count = first_present(
            row,
            [
                "unique_policy_count",
                "unique_recommended_policy_count",
                "unique_policies",
                "unique_recommended_policies",
            ],
            0,
        )

        if isinstance(unique_policy_count, list):
            unique_policy_count = len(unique_policy_count)

        recommendations = first_present(
            row,
            [
                "profile_recommendations",
                "profile_recommendation_summary",
                "profile_recommendations_text",
                "recommendation_summary",
            ],
            "",
        )

        by_batch[batch_id] = {
            "ranking_stability_class": stability,
            "ranking_unique_policy_count": int_value(unique_policy_count, 0),
            "ranking_profile_recommendations": stringify_profile_recommendations(
                recommendations
            ),
        }

    return by_batch


def extract_sensitivity_summary(
    sensitivity: dict[str, Any],
    sensitivity_by_batch: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ranking_profile_count = recursive_find_value(sensitivity, "ranking_profile_count")
    scenario_summary_count = recursive_find_value(sensitivity, "scenario_summary_count")
    recommendation_count = recursive_find_value(sensitivity, "recommendation_count")
    ranking_row_count = recursive_find_value(sensitivity, "ranking_row_count")
    sensitive_count = recursive_find_value(sensitivity, "sensitive_to_ranking_profile_count")

    stability_counts: dict[str, int] = {}

    for row in sensitivity_by_batch.values():
        stability = normalize_id(row.get("ranking_stability_class", "")) or "unknown"
        stability_counts[stability] = stability_counts.get(stability, 0) + 1

    if sensitive_count is None:
        sensitive_count = sum(
            count
            for stability, count in stability_counts.items()
            if stability not in {"stable_across_profiles", "unknown"}
        )

    return {
        "integrated_at_local": datetime.now().replace(microsecond=0).isoformat(),
        "ranking_profile_count": int_value(ranking_profile_count, 0),
        "scenario_summary_count": int_value(
            scenario_summary_count,
            len(sensitivity_by_batch),
        ),
        "recommendation_count": int_value(recommendation_count, 0),
        "ranking_row_count": int_value(ranking_row_count, 0),
        "sensitive_to_ranking_profile_count": int_value(sensitive_count, 0),
        "stability_counts": stability_counts,
        "interpretation": {
            "status": "ranking_sensitivity_integrated_into_final_diagnostic",
            "warning": "This integration is diagnostic. It does not prove which ranking profile is scientifically correct.",
        },
    }


def pick_final_rows(final_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = final_data.get("rows")

    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]

    for key in ["decision_rows", "final_rows", "diagnostic_rows"]:
        rows = final_data.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]

    return []


def integrate_json(
    final_json_path: Path,
    sensitivity_json_path: Path,
) -> dict[str, Any]:
    final_data = load_json(final_json_path)
    sensitivity = load_json(sensitivity_json_path)

    sensitivity_by_batch = extract_sensitivity_rows(sensitivity)
    sensitivity_summary = extract_sensitivity_summary(sensitivity, sensitivity_by_batch)

    final_data["ranking_profile_sensitivity"] = sensitivity_summary

    overview = final_data.get("overview")
    if isinstance(overview, dict):
        overview["ranking_profile_count"] = sensitivity_summary["ranking_profile_count"]
        overview["ranking_scenario_summary_count"] = sensitivity_summary[
            "scenario_summary_count"
        ]
        overview["ranking_sensitive_to_profile_count"] = sensitivity_summary[
            "sensitive_to_ranking_profile_count"
        ]

    rows = pick_final_rows(final_data)

    for row in rows:
        batch_id = normalize_id(row.get("batch_id", ""))
        sensitivity_row = sensitivity_by_batch.get(batch_id, {})

        for field in ADDED_FIELDS:
            row[field] = sensitivity_row.get(field, "")

    write_json(final_json_path, final_data)

    return {
        "summary": sensitivity_summary,
        "rows": rows,
        "sensitivity_by_batch": sensitivity_by_batch,
    }


def build_markdown_section(integration: dict[str, Any]) -> str:
    summary = integration["summary"]
    rows = integration["rows"]

    lines: list[str] = []

    lines.append("## Ranking profile sensitivity integration")
    lines.append("")
    lines.append("This section connects the final diagnostic report to the ranking profile sensitivity analysis.")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| ranking_profile_count | {format_number(summary['ranking_profile_count'])} |")
    lines.append(f"| scenario_summary_count | {format_number(summary['scenario_summary_count'])} |")
    lines.append(f"| recommendation_count | {format_number(summary['recommendation_count'])} |")
    lines.append(f"| ranking_row_count | {format_number(summary['ranking_row_count'])} |")
    lines.append(
        f"| sensitive_to_ranking_profile_count | {format_number(summary['sensitive_to_ranking_profile_count'])} |"
    )
    lines.append("")

    stability_counts = summary.get("stability_counts", {})
    if isinstance(stability_counts, dict) and stability_counts:
        lines.append("### Ranking stability counts")
        lines.append("")
        lines.append("| Stability class | Count |")
        lines.append("| --- | ---: |")

        for stability, count in sorted(stability_counts.items()):
            lines.append(f"| {stability} | {format_number(count)} |")

        lines.append("")

    lines.append("### Ranking sensitivity by final diagnostic row")
    lines.append("")
    lines.append("| Batch | Family | Severity | Ranking stability | Unique policies |")
    lines.append("| --- | --- | --- | --- | ---: |")

    for row in rows:
        lines.append(
            "| "
            f"{row.get('batch_id', '')} | "
            f"{row.get('scenario_family_id', '')} | "
            f"{row.get('severity_id', '')} | "
            f"{row.get('ranking_stability_class', '')} | "
            f"{format_number(row.get('ranking_unique_policy_count', ''))} |"
        )

    lines.append("")
    lines.append(
        "Conservative interpretation: stable recommendations across ranking profiles are less fragile, but this still does not validate the ranking profile scientifically."
    )
    lines.append("")

    return "\n".join(lines)


def integrate_markdown(final_md_path: Path, integration: dict[str, Any]) -> None:
    text = final_md_path.read_text(encoding="utf-8")
    section = build_markdown_section(integration)

    start_marker = "## Ranking profile sensitivity integration"
    next_marker = "## What this report supports"

    if start_marker in text:
        start = text.index(start_marker)
        next_pos = text.find(next_marker, start)

        if next_pos == -1:
            text = text[:start].rstrip() + "\n\n" + section + "\n"
        else:
            text = text[:start].rstrip() + "\n\n" + section + "\n" + text[next_pos:]
    elif next_marker in text:
        text = text.replace(next_marker, section + "\n" + next_marker, 1)
    else:
        text = text.rstrip() + "\n\n" + section + "\n"

    final_md_path.write_text(text, encoding="utf-8")


def integrate_csv(final_csv_path: Path, integration: dict[str, Any]) -> None:
    sensitivity_by_batch = integration["sensitivity_by_batch"]

    with final_csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    for field in ADDED_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)

    for row in rows:
        batch_id = normalize_id(row.get("batch_id", ""))
        sensitivity_row = sensitivity_by_batch.get(batch_id, {})

        for field in ADDED_FIELDS:
            row[field] = str(sensitivity_row.get(field, ""))

    with final_csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\integrate_ranking_sensitivity_into_final_diagnostic_report.py "
            "<final_json> <final_md> <final_csv> <ranking_sensitivity_json>",
            file=sys.stderr,
        )
        return 2

    final_json_path = Path(sys.argv[1])
    final_md_path = Path(sys.argv[2])
    final_csv_path = Path(sys.argv[3])
    sensitivity_json_path = Path(sys.argv[4])

    try:
        integration = integrate_json(final_json_path, sensitivity_json_path)
        integrate_markdown(final_md_path, integration)
        integrate_csv(final_csv_path, integration)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Ranking sensitivity integrated into final diagnostic report.")
    print(f"Final JSON updated: {final_json_path}")
    print(f"Final markdown updated: {final_md_path}")
    print(f"Final CSV updated: {final_csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())