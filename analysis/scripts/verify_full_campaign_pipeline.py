from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_QUALITY_FILES = [
    "analysis/reports/experiment_campaign_plan_quality_check.json",
    "analysis/reports/campaign_batch_blueprint_quality_check.json",
    "analysis/reports/campaign_perturbation_plan_quality_check.json",
    "analysis/reports/campaign_executable_batch_config_quality_check.json",
    "analysis/reports/campaign_execution_quality_check.json",
    "analysis/reports/campaign_result_summary_quality_check.json",
    "analysis/reports/service_delay_impact_audit_quality_check.json",
    "analysis/reports/policy_trigger_behavior_audit_quality_check.json",
    "analysis/reports/campaign_decision_matrix_quality_check.json",
    "analysis/reports/campaign_final_diagnostic_report_quality_check.json",
]

REQUIRED_OUTPUT_FILES = [
    "analysis/reports/full_campaign_pipeline_report.md",
    "analysis/reports/full_campaign_pipeline_manifest.json",
    "analysis/reports/full_campaign_pipeline_log.txt",
    "analysis/reports/campaign_execution_index.json",
    "analysis/reports/campaign_result_summary.json",
    "analysis/reports/campaign_result_semantic_inspection.json",
    "analysis/reports/service_delay_impact_audit.json",
    "analysis/reports/policy_trigger_behavior_audit.json",
    "analysis/reports/campaign_decision_matrix.json",
    "analysis/reports/campaign_final_diagnostic_report.json",
]


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


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


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1", "ok", "passed"}

    return bool(value)


def int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def quality_file_passed(path: Path) -> tuple[bool, int, list[str]]:
    problems: list[str] = []

    if not path.exists():
        return False, 0, [f"Quality file missing: {path}"]

    data = load_json(path)

    passed = bool_value(data.get("all_required_checks_passed", False))
    problem_count = int_value(data.get("problem_count", 0))

    if not passed:
        problems.append(f"Quality file did not pass: {path}")

    if problem_count > 0:
        problems.append(f"Quality file has problem_count={problem_count}: {path}")

    return passed and problem_count == 0, problem_count, problems


def build_quality_report(
    manifest_path: Path,
    report_path: Path,
    log_path: Path,
) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []
    quality_checks: list[dict[str, Any]] = []
    output_checks: list[dict[str, Any]] = []

    manifest = load_json(manifest_path)

    if not report_path.exists():
        problems.append(f"Pipeline report not found: {report_path}")

    if not log_path.exists():
        problems.append(f"Pipeline log not found: {log_path}")

    all_steps_passed = bool_value(manifest.get("all_steps_passed", False))
    failed_step_count = int_value(manifest.get("failed_step_count", 0))
    step_count = int_value(manifest.get("step_count", 0))

    if not all_steps_passed:
        problems.append("Manifest says not all steps passed.")

    if failed_step_count != 0:
        problems.append(f"Manifest failed_step_count is {failed_step_count}, expected 0.")

    if step_count <= 0:
        problems.append("Manifest step_count must be positive.")

    for file_path_text in REQUIRED_OUTPUT_FILES:
        path = Path(file_path_text)
        exists = path.exists()
        size_bytes = path.stat().st_size if exists else 0

        if not exists:
            problems.append(f"Required output file missing: {path}")
        elif size_bytes <= 0:
            problems.append(f"Required output file is empty: {path}")

        output_checks.append(
            {
                "path": str(path),
                "exists": exists,
                "size_bytes": size_bytes,
            }
        )

    for file_path_text in REQUIRED_QUALITY_FILES:
        path = Path(file_path_text)
        passed, problem_count, file_problems = quality_file_passed(path)

        problems.extend(file_problems)

        quality_checks.append(
            {
                "path": str(path),
                "passed": passed,
                "problem_count": problem_count,
            }
        )

    final_quality_path = Path("analysis/reports/campaign_final_diagnostic_report_quality_check.json")
    if final_quality_path.exists():
        final_quality = load_json(final_quality_path)
        final_warning_count = int_value(final_quality.get("warning_count", 0))

        if final_warning_count > 0:
            warnings.append(
                f"Final diagnostic report has {final_warning_count} methodological warning(s)."
            )

    return {
        "report_type": "fieldops_lab_full_campaign_pipeline_quality_check",
        "generated_at_local": now_text(),
        "manifest_path": str(manifest_path),
        "pipeline_report_path": str(report_path),
        "pipeline_log_path": str(log_path),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "step_count": step_count,
        "failed_step_count": failed_step_count,
        "required_output_file_count": len(REQUIRED_OUTPUT_FILES),
        "required_quality_file_count": len(REQUIRED_QUALITY_FILES),
        "problems": problems,
        "warnings": warnings,
        "output_checks": output_checks,
        "quality_checks": quality_checks,
        "interpretation": {
            "status": "full_campaign_pipeline_quality_check",
            "warning": "This check verifies structural and pipeline consistency, not final scientific validity.",
        },
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    lines.append("# FieldOps Lab full campaign pipeline quality check")
    lines.append("")
    lines.append(f"Manifest: `{report['manifest_path']}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {'yes' if report['all_required_checks_passed'] else 'no'} |")
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    lines.append(f"| step_count | {report['step_count']} |")
    lines.append(f"| failed_step_count | {report['failed_step_count']} |")
    lines.append(f"| required_output_file_count | {report['required_output_file_count']} |")
    lines.append(f"| required_quality_file_count | {report['required_quality_file_count']} |")
    lines.append("")

    lines.append("## Output checks")
    lines.append("")
    lines.append("| Path | Exists | Size bytes |")
    lines.append("| --- | --- | ---: |")

    for item in report["output_checks"]:
        lines.append(
            f"| `{item['path']}` | {'yes' if item['exists'] else 'no'} | {item['size_bytes']} |"
        )

    lines.append("")
    lines.append("## Quality file checks")
    lines.append("")
    lines.append("| Path | Passed | Problem count |")
    lines.append("| --- | --- | ---: |")

    for item in report["quality_checks"]:
        lines.append(
            f"| `{item['path']}` | {'yes' if item['passed'] else 'no'} | {item['problem_count']} |"
        )

    lines.append("")
    lines.append("## Problems")
    lines.append("")

    if report["problems"]:
        for problem in report["problems"]:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")

    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if report["all_required_checks_passed"]:
        lines.append(
            "The full campaign pipeline passed the structural quality check. This means the automated campaign flow is reproducible enough to use as the current engineering baseline."
        )
    else:
        lines.append(
            "The full campaign pipeline failed the structural quality check. Do not use its outputs as evidence until the listed problems are fixed."
        )

    lines.append("")
    lines.append(
        "This does not prove final scientific validity. It confirms that the execution and reporting pipeline is internally consistent."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "Usage: py -3 analysis\\scripts\\verify_full_campaign_pipeline.py "
            "<manifest_json> <pipeline_report_md> <pipeline_log_txt> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    manifest_path = Path(sys.argv[1])
    report_path = Path(sys.argv[2])
    log_path = Path(sys.argv[3])
    output_md = Path(sys.argv[4])
    output_json = Path(sys.argv[5])

    try:
        report = build_quality_report(manifest_path, report_path, log_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_markdown(output_md, report)
    write_json(output_json, report)

    print(f"Full campaign pipeline quality report written to: {output_md}")
    print(f"Full campaign pipeline quality JSON written to: {output_json}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Full campaign pipeline quality check failed.", file=sys.stderr)
        return 1

    print("Full campaign pipeline quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())