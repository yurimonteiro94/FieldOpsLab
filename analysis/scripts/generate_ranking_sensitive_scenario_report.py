from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_PATH = (
    PROJECT_ROOT
    / "analysis"
    / "reports"
    / "campaign_ranking_profile_sensitivity.json"
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default

    return default


def as_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value)


def project_relative_text(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_recommended_policies(profile_policy_pairs: str) -> list[str]:
    policies: set[str] = set()

    for raw_pair in profile_policy_pairs.split(";"):
        pair = raw_pair.strip()

        if not pair or "=" not in pair:
            continue

        _, recommendation = pair.split("=", 1)
        policy_id = recommendation.strip().split("+", 1)[0].strip()

        if policy_id:
            policies.add(policy_id)

    return sorted(policies)


def parse_recommendation_classes_from_rows(
    rows: list[dict[str, Any]],
    batch_id: str,
) -> list[str]:
    classes: set[str] = set()

    for row in rows:
        if as_text(row.get("batch_id")) != batch_id:
            continue

        if not row.get("is_recommended"):
            continue

        recommendation_class = as_text(row.get("recommendation_class"))

        if recommendation_class:
            classes.add(recommendation_class)

    return sorted(classes)


def is_ranking_sensitive_row(
    summary_row: dict[str, Any],
    recommendation_classes: list[str],
) -> bool:
    unique_policy_count = max(
        as_int(summary_row.get("unique_recommended_policy_count")),
        len(
            parse_recommended_policies(
                as_text(summary_row.get("recommended_profile_policy_pairs"))
            )
        ),
    )

    unique_class_count = max(
        as_int(summary_row.get("unique_recommendation_class_count")),
        len(recommendation_classes),
    )

    stability_class = as_text(summary_row.get("stability_class"))

    return (
        unique_policy_count >= 2
        or unique_class_count >= 2
        or stability_class != "stable_across_profiles"
    )


def sensitivity_reason(
    unique_policy_count: int,
    unique_class_count: int,
    stability_class: str,
) -> str:
    if unique_policy_count >= 2:
        return "recommended_policy_changes_across_profiles"

    if unique_class_count >= 2:
        return "same_policy_but_recommendation_class_changes_across_profiles"

    if stability_class != "stable_across_profiles":
        return "ranking_summary_marked_as_not_stable"

    return "stable_across_profiles"


def investigation_status_for_reason(reason: str) -> str:
    if reason == "recommended_policy_changes_across_profiles":
        return "requires_policy_change_explanation"

    if reason == "same_policy_but_recommendation_class_changes_across_profiles":
        return "requires_recommendation_class_explanation"

    if reason == "ranking_summary_marked_as_not_stable":
        return "requires_stability_class_explanation"

    return "no_investigation_required"


def interpretation_for_reason(reason: str) -> str:
    if reason == "recommended_policy_changes_across_profiles":
        return (
            "The recommended policy changes under different ranking profiles. "
            "This scenario needs metric-level explanation before it can support "
            "a robust scientific recommendation."
        )

    if reason == "same_policy_but_recommendation_class_changes_across_profiles":
        return (
            "The recommended policy remains the same, but the recommendation class "
            "changes under different ranking profiles. This means the policy choice "
            "looks stable, but the strength or quality of the recommendation is fragile."
        )

    if reason == "ranking_summary_marked_as_not_stable":
        return (
            "The scenario is not marked as stable across ranking profiles. "
            "Its ranking behavior should be inspected before using it as scientific evidence."
        )

    return "No ranking sensitivity was detected for this scenario."


def build_sensitive_scenario_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    raw_summary_rows = source.get("summary_rows", [])
    raw_rows = source.get("rows", [])

    if not isinstance(raw_summary_rows, list):
        raise ValueError(
            "campaign_ranking_profile_sensitivity.json must contain a list named summary_rows"
        )

    if not isinstance(raw_rows, list):
        raw_rows = []

    ranking_rows = [row for row in raw_rows if isinstance(row, dict)]

    sensitive_rows: list[dict[str, Any]] = []

    for item in raw_summary_rows:
        if not isinstance(item, dict):
            continue

        batch_id = as_text(item.get("batch_id"))
        profile_policy_pairs = as_text(item.get("recommended_profile_policy_pairs"))
        recommended_policies = parse_recommended_policies(profile_policy_pairs)
        recommendation_classes = parse_recommendation_classes_from_rows(
            ranking_rows,
            batch_id,
        )

        unique_recommended_policy_count = max(
            as_int(item.get("unique_recommended_policy_count")),
            len(recommended_policies),
        )

        unique_recommendation_class_count = max(
            as_int(item.get("unique_recommendation_class_count")),
            len(recommendation_classes),
        )

        stability_class = as_text(item.get("stability_class"))

        if not is_ranking_sensitive_row(item, recommendation_classes):
            continue

        reason = sensitivity_reason(
            unique_recommended_policy_count,
            unique_recommendation_class_count,
            stability_class,
        )

        sensitive_rows.append(
            {
                "batch_id": batch_id,
                "scenario_id": as_text(item.get("scenario_id")),
                "scenario_family_id": as_text(item.get("scenario_family_id")),
                "severity_id": as_text(item.get("severity_id")),
                "ranking_profile_count": as_int(item.get("profile_count")),
                "profile_count": as_int(item.get("profile_count")),
                "sensitive_to_ranking_profile": True,
                "sensitivity_reason": reason,
                "unique_recommended_policy_count": unique_recommended_policy_count,
                "unique_recommendation_class_count": unique_recommendation_class_count,
                "recommended_policies": recommended_policies,
                "recommendation_classes": recommendation_classes,
                "stability_class": stability_class,
                "recommended_profile_policy_pairs": profile_policy_pairs,
                "investigation_status": investigation_status_for_reason(reason),
                "interpretation": interpretation_for_reason(reason),
            }
        )

    sensitive_rows.sort(
        key=lambda row: (
            row["scenario_family_id"],
            row["severity_id"],
            row["batch_id"],
        )
    )

    return sensitive_rows


def build_input_status(source: dict[str, Any]) -> dict[str, Any]:
    summary_rows = source.get("summary_rows", [])
    rows = source.get("rows", [])

    if not isinstance(summary_rows, list):
        summary_rows = []

    if not isinstance(rows, list):
        rows = []

    all_required_inputs_available = (
        SOURCE_PATH.exists()
        and bool(summary_rows)
        and bool(rows)
    )

    return {
        "all_required_inputs_available": all_required_inputs_available,
        "source_path": project_relative_text(SOURCE_PATH),
        "source_exists": SOURCE_PATH.exists(),
        "source_report_type": as_text(source.get("report_type")),
        "source_scenario_summary_count": as_int(
            source.get("scenario_summary_count"),
            default=len(summary_rows),
        ),
        "source_ranking_row_count": as_int(
            source.get("ranking_row_count"),
            default=len(rows),
        ),
        "source_ranking_profile_count": as_int(source.get("ranking_profile_count")),
        "source_has_summary_rows": bool(summary_rows),
        "source_has_ranking_rows": bool(rows),
    }


def build_report(source: dict[str, Any]) -> dict[str, Any]:
    raw_summary_rows = source.get("summary_rows", [])
    raw_rows = source.get("rows", [])

    if not isinstance(raw_summary_rows, list):
        raw_summary_rows = []

    if not isinstance(raw_rows, list):
        raw_rows = []

    sensitive_scenarios = build_sensitive_scenario_rows(source)

    scenario_summary_count = as_int(
        source.get("scenario_summary_count"),
        default=len(raw_summary_rows),
    )

    ranking_row_count = as_int(
        source.get("ranking_row_count"),
        default=len(raw_rows),
    )

    ranking_profile_count = as_int(
        source.get("ranking_profile_count"),
        default=0,
    )

    sensitive_scenario_count = len(sensitive_scenarios)
    stable_scenario_count = max(0, scenario_summary_count - sensitive_scenario_count)

    policy_change_count = sum(
        1
        for row in sensitive_scenarios
        if row["sensitivity_reason"] == "recommended_policy_changes_across_profiles"
    )

    class_change_count = sum(
        1
        for row in sensitive_scenarios
        if row["sensitivity_reason"]
        == "same_policy_but_recommendation_class_changes_across_profiles"
    )

    return {
        "report_type": "ranking_sensitive_scenario_report",
        "generated_at_local": datetime.now().isoformat(timespec="seconds"),
        "input_status": build_input_status(source),
        "summary": {
            "scenario_summary_count": scenario_summary_count,
            "ranking_row_count": ranking_row_count,
            "ranking_profile_count": ranking_profile_count,
            "sensitive_scenario_count": sensitive_scenario_count,
            "policy_change_sensitive_scenario_count": policy_change_count,
            "class_change_sensitive_scenario_count": class_change_count,
            "stable_scenario_count": stable_scenario_count,
            "ranking_fragility_status": (
                "some_scenarios_sensitive_to_ranking_profile"
                if sensitive_scenario_count > 0
                else "no_ranking_sensitivity_detected_under_current_profiles"
            ),
        },
        "sensitive_scenarios": sensitive_scenarios,
        "interpretation": {
            "conservative_reading": (
                "A ranking-sensitive scenario is a scenario where the recommended policy "
                "changes, or where the recommendation class changes, when the ranking "
                "profile changes."
            ),
            "scientific_warning": (
                "This report identifies recommendation fragility in the current diagnostic "
                "campaign. It does not prove statistical significance or general validity."
            ),
        },
    }


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")


def write_csv(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "batch_id",
        "scenario_family_id",
        "severity_id",
        "ranking_profile_count",
        "sensitive_to_ranking_profile",
        "sensitivity_reason",
        "unique_recommended_policy_count",
        "unique_recommendation_class_count",
        "recommended_policies",
        "recommendation_classes",
        "stability_class",
        "investigation_status",
        "interpretation",
        "recommended_profile_policy_pairs",
        "scenario_id",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in report["sensitive_scenarios"]:
            csv_row = dict(row)
            csv_row["recommended_policies"] = "; ".join(row["recommended_policies"])
            csv_row["recommendation_classes"] = "; ".join(row["recommendation_classes"])
            writer.writerow({field: csv_row.get(field, "") for field in fieldnames})


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in rows:
        lines.append("| " + " | ".join(as_text(value) for value in row) + " |")

    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    summary = report["summary"]
    input_status = report["input_status"]
    sensitive_scenarios = report["sensitive_scenarios"]

    lines: list[str] = []

    lines.append("# FieldOps Lab ranking-sensitive scenario report")
    lines.append("")
    lines.append(
        "This report identifies scenarios where the recommendation changes under "
        "different ranking profiles."
    )
    lines.append("")
    lines.append(
        "A change can mean a different recommended policy, or the same policy with "
        "a different recommendation class."
    )
    lines.append("")
    lines.append("This is a diagnostic report. It does not prove statistical validity.")
    lines.append("")

    lines.append("## Input status")
    lines.append("")
    lines.append(
        markdown_table(
            ["Field", "Value"],
            [
                ["all_required_inputs_available", "yes" if input_status["all_required_inputs_available"] else "no"],
                ["source_path", input_status["source_path"]],
                ["source_exists", "yes" if input_status["source_exists"] else "no"],
                ["source_report_type", input_status["source_report_type"]],
                ["source_scenario_summary_count", input_status["source_scenario_summary_count"]],
                ["source_ranking_row_count", input_status["source_ranking_row_count"]],
                ["source_ranking_profile_count", input_status["source_ranking_profile_count"]],
                ["source_has_summary_rows", "yes" if input_status["source_has_summary_rows"] else "no"],
                ["source_has_ranking_rows", "yes" if input_status["source_has_ranking_rows"] else "no"],
            ],
        )
    )
    lines.append("")

    lines.append("## Overall result")
    lines.append("")
    lines.append(
        markdown_table(
            ["Field", "Value"],
            [
                ["scenario_summary_count", summary["scenario_summary_count"]],
                ["ranking_row_count", summary["ranking_row_count"]],
                ["ranking_profile_count", summary["ranking_profile_count"]],
                ["sensitive_scenario_count", summary["sensitive_scenario_count"]],
                ["policy_change_sensitive_scenario_count", summary["policy_change_sensitive_scenario_count"]],
                ["class_change_sensitive_scenario_count", summary["class_change_sensitive_scenario_count"]],
                ["stable_scenario_count", summary["stable_scenario_count"]],
                ["ranking_fragility_status", summary["ranking_fragility_status"]],
            ],
        )
    )
    lines.append("")

    lines.append("## Sensitive scenarios")
    lines.append("")

    if sensitive_scenarios:
        lines.append(
            markdown_table(
                [
                    "Batch",
                    "Family",
                    "Severity",
                    "Ranking profiles",
                    "Reason",
                    "Recommended policies",
                    "Recommendation classes",
                    "Investigation status",
                ],
                [
                    [
                        row["batch_id"],
                        row["scenario_family_id"],
                        row["severity_id"],
                        row["ranking_profile_count"],
                        row["sensitivity_reason"],
                        "; ".join(row["recommended_policies"]),
                        "; ".join(row["recommendation_classes"]),
                        row["investigation_status"],
                    ]
                    for row in sensitive_scenarios
                ],
            )
        )
    else:
        lines.append("- None detected in the current diagnostic campaign.")

    lines.append("")

    lines.append("## Required investigation")
    lines.append("")

    if sensitive_scenarios:
        for row in sensitive_scenarios:
            lines.append(f"### `{row['batch_id']}`")
            lines.append("")
            lines.append(f"- Scenario family: `{row['scenario_family_id']}`")
            lines.append(f"- Severity: `{row['severity_id']}`")
            lines.append("- Sensitive to ranking profile: `yes`")
            lines.append(f"- Sensitivity reason: `{row['sensitivity_reason']}`")
            lines.append(
                f"- Recommended policies: `{'; '.join(row['recommended_policies'])}`"
            )
            lines.append(
                f"- Recommendation classes: `{'; '.join(row['recommendation_classes'])}`"
            )
            lines.append(f"- Investigation status: `{row['investigation_status']}`")
            lines.append(f"- Interpretation: {row['interpretation']}")
            lines.append(
                f"- Profile-policy pairs: `{row['recommended_profile_policy_pairs']}`"
            )
            lines.append("")
    else:
        lines.append("- No ranking-sensitive scenario was detected.")
        lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "Scenarios listed here are fragile recommendations. They need metric-level "
        "explanation before being used as scientific evidence."
    )
    lines.append("")
    lines.append(
        "The next step is to explain which objective components, recommendation classes, "
        "and ranking weights caused each sensitivity signal."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> tuple[Path, Path, Path]:
    if len(argv) != 4:
        raise ValueError(
            "Usage: generate_ranking_sensitive_scenario_report.py "
            "<output_md> <output_json> <output_csv>"
        )

    return (
        Path(argv[1]),
        Path(argv[2]),
        Path(argv[3]),
    )


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    try:
        output_md, output_json, output_csv = parse_args(argv)

        source = read_json(SOURCE_PATH)
        report = build_report(source)

        write_markdown(output_md, report)
        write_json(output_json, report)
        write_csv(output_csv, report)

        print(
            "Ranking-sensitive scenario markdown written to: "
            f"{project_relative_text(output_md)}"
        )
        print(
            "Ranking-sensitive scenario JSON written to: "
            f"{project_relative_text(output_json)}"
        )
        print(
            "Ranking-sensitive scenario CSV written to: "
            f"{project_relative_text(output_csv)}"
        )
        print("Ranking-sensitive scenario report completed successfully.")

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())