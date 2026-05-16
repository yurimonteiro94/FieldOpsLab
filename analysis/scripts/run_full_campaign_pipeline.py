from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd()

REPORTS_DIR = Path("analysis/reports")
BLUEPRINT_DIR = Path("analysis/reports/campaign_batch_blueprints")
PERTURBATION_DIR = Path("data/perturbations/campaign_plans")
CAMPAIGN_BATCH_DIR = Path("data/experiments/campaign_batches")
CAMPAIGN_RESULT_DIR = Path("data/results/campaign_batches")

SAMPLE_BATCH_CONFIG = Path("data/experiments/sample_no_replanning_batch_001.json")

FULL_PIPELINE_REPORT = REPORTS_DIR / "full_campaign_pipeline_report.md"
FULL_PIPELINE_MANIFEST = REPORTS_DIR / "full_campaign_pipeline_manifest.json"
FULL_PIPELINE_LOG = REPORTS_DIR / "full_campaign_pipeline_log.txt"


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def path_text(path: Path) -> str:
    return str(path)


def command_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def ensure_directories() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)
    PERTURBATION_DIR.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_BATCH_DIR.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_RESULT_DIR.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def run_step(name: str, command: list[str], log_lines: list[str]) -> dict[str, Any]:
    start = now_text()
    cmd_text = command_text(command)

    log_lines.append("")
    log_lines.append("=" * 80)
    log_lines.append(f"STEP: {name}")
    log_lines.append(f"START: {start}")
    log_lines.append(f"COMMAND: {cmd_text}")
    log_lines.append("-" * 80)

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        shell=False,
    )

    end = now_text()

    if completed.stdout:
        log_lines.append("[stdout]")
        log_lines.append(completed.stdout.rstrip())

    if completed.stderr:
        log_lines.append("[stderr]")
        log_lines.append(completed.stderr.rstrip())

    status = "ok" if completed.returncode == 0 else "failed"

    log_lines.append(f"END: {end}")
    log_lines.append(f"RETURN_CODE: {completed.returncode}")
    log_lines.append(f"STATUS: {status}")

    return {
        "name": name,
        "command": cmd_text,
        "started_at_local": start,
        "finished_at_local": end,
        "return_code": completed.returncode,
        "status": status,
        "stdout_tail": completed.stdout[-2000:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-2000:] if completed.stderr else "",
    }


def py_command(script_path: Path, *args: Path | str) -> list[str]:
    return [sys.executable, path_text(script_path), *[path_text(Path(arg)) if isinstance(arg, Path) else str(arg) for arg in args]]


def build_steps(fieldops_exe: Path) -> list[tuple[str, list[str]]]:
    return [
        (
            "generate_experiment_campaign_plan",
            py_command(
                Path("analysis/scripts/generate_experiment_campaign_plan.py"),
                REPORTS_DIR / "experiment_campaign_plan.md",
                REPORTS_DIR / "experiment_campaign_plan.json",
                REPORTS_DIR / "experiment_campaign_plan.csv",
            ),
        ),
        (
            "verify_experiment_campaign_plan",
            py_command(
                Path("analysis/scripts/verify_experiment_campaign_plan.py"),
                REPORTS_DIR / "experiment_campaign_plan.json",
                REPORTS_DIR / "experiment_campaign_plan.md",
                REPORTS_DIR / "experiment_campaign_plan.csv",
                REPORTS_DIR / "experiment_campaign_plan_quality_check.md",
                REPORTS_DIR / "experiment_campaign_plan_quality_check.json",
            ),
        ),
        (
            "generate_campaign_batch_blueprints",
            py_command(
                Path("analysis/scripts/generate_campaign_batch_blueprints.py"),
                REPORTS_DIR / "experiment_campaign_plan.json",
                BLUEPRINT_DIR,
                REPORTS_DIR / "campaign_batch_blueprint_index.md",
                REPORTS_DIR / "campaign_batch_blueprint_index.json",
                REPORTS_DIR / "campaign_batch_blueprint_index.csv",
            ),
        ),
        (
            "verify_campaign_batch_blueprints",
            py_command(
                Path("analysis/scripts/verify_campaign_batch_blueprints.py"),
                REPORTS_DIR / "campaign_batch_blueprint_index.json",
                REPORTS_DIR / "campaign_batch_blueprint_index.md",
                REPORTS_DIR / "campaign_batch_blueprint_index.csv",
                BLUEPRINT_DIR,
                REPORTS_DIR / "campaign_batch_blueprint_quality_check.md",
                REPORTS_DIR / "campaign_batch_blueprint_quality_check.json",
            ),
        ),
        (
            "generate_campaign_perturbation_plans",
            py_command(
                Path("analysis/scripts/generate_campaign_perturbation_plans.py"),
                SAMPLE_BATCH_CONFIG,
                REPORTS_DIR / "experiment_campaign_plan.json",
                PERTURBATION_DIR,
                REPORTS_DIR / "campaign_perturbation_plan_index.md",
                REPORTS_DIR / "campaign_perturbation_plan_index.json",
                REPORTS_DIR / "campaign_perturbation_plan_index.csv",
            ),
        ),
        (
            "verify_campaign_perturbation_plans",
            py_command(
                Path("analysis/scripts/verify_campaign_perturbation_plans.py"),
                REPORTS_DIR / "campaign_perturbation_plan_index.json",
                REPORTS_DIR / "campaign_perturbation_plan_quality_check.md",
                REPORTS_DIR / "campaign_perturbation_plan_quality_check.json",
                REPORTS_DIR / "campaign_perturbation_plan_quality_check.csv",
            ),
        ),
        (
            "generate_executable_campaign_batch_configs",
            py_command(
                Path("analysis/scripts/generate_executable_campaign_batch_configs.py"),
                SAMPLE_BATCH_CONFIG,
                REPORTS_DIR / "campaign_batch_blueprint_index.json",
                BLUEPRINT_DIR,
                CAMPAIGN_BATCH_DIR,
                REPORTS_DIR / "campaign_executable_batch_config_index.md",
                REPORTS_DIR / "campaign_executable_batch_config_index.json",
                REPORTS_DIR / "campaign_executable_batch_config_index.csv",
            ),
        ),
        (
            "connect_campaign_batch_configs_to_perturbation_plans",
            py_command(
                Path("analysis/scripts/connect_campaign_batch_configs_to_perturbation_plans.py"),
                CAMPAIGN_BATCH_DIR,
                PERTURBATION_DIR,
                REPORTS_DIR / "campaign_perturbation_connection.md",
                REPORTS_DIR / "campaign_perturbation_connection.json",
                REPORTS_DIR / "campaign_perturbation_connection.csv",
            ),
        ),
        (
            "verify_executable_campaign_batch_configs",
            py_command(
                Path("analysis/scripts/verify_executable_campaign_batch_configs.py"),
                REPORTS_DIR / "campaign_executable_batch_config_index.json",
                REPORTS_DIR / "campaign_executable_batch_config_quality_check.md",
                REPORTS_DIR / "campaign_executable_batch_config_quality_check.json",
                REPORTS_DIR / "campaign_executable_batch_config_quality_check.csv",
            ),
        ),
        (
            "run_executable_campaign_batches",
            py_command(
                Path("analysis/scripts/run_executable_campaign_batches.py"),
                fieldops_exe,
                CAMPAIGN_BATCH_DIR,
                CAMPAIGN_RESULT_DIR,
                REPORTS_DIR / "campaign_execution_index.md",
                REPORTS_DIR / "campaign_execution_index.json",
                REPORTS_DIR / "campaign_execution_index.csv",
            ),
        ),
        (
            "verify_campaign_execution_index",
            py_command(
                Path("analysis/scripts/verify_campaign_execution_index.py"),
                REPORTS_DIR / "campaign_execution_index.json",
                REPORTS_DIR / "campaign_execution_index.md",
                REPORTS_DIR / "campaign_execution_index.csv",
                REPORTS_DIR / "campaign_execution_quality_check.md",
                REPORTS_DIR / "campaign_execution_quality_check.json",
            ),
        ),
        (
            "generate_campaign_result_summary",
            py_command(
                Path("analysis/scripts/generate_campaign_result_summary.py"),
                REPORTS_DIR / "campaign_execution_index.json",
                REPORTS_DIR / "campaign_result_summary.md",
                REPORTS_DIR / "campaign_result_summary.json",
                REPORTS_DIR / "campaign_result_summary.csv",
            ),
        ),
        (
            "verify_campaign_result_summary",
            py_command(
                Path("analysis/scripts/verify_campaign_result_summary.py"),
                REPORTS_DIR / "campaign_result_summary.json",
                REPORTS_DIR / "campaign_result_summary.md",
                REPORTS_DIR / "campaign_result_summary.csv",
                REPORTS_DIR / "campaign_result_summary_quality_check.md",
                REPORTS_DIR / "campaign_result_summary_quality_check.json",
            ),
        ),
        (
            "inspect_campaign_result_semantics",
            py_command(
                Path("analysis/scripts/inspect_campaign_result_semantics.py"),
                REPORTS_DIR / "campaign_execution_index.json",
                REPORTS_DIR / "campaign_result_semantic_inspection.md",
                REPORTS_DIR / "campaign_result_semantic_inspection.json",
                REPORTS_DIR / "campaign_result_semantic_inspection.csv",
            ),
        ),
        (
            "audit_service_delay_impact",
            py_command(
                Path("analysis/scripts/audit_service_delay_impact.py"),
                CAMPAIGN_RESULT_DIR,
                REPORTS_DIR / "service_delay_impact_audit.md",
                REPORTS_DIR / "service_delay_impact_audit.json",
                REPORTS_DIR / "service_delay_impact_audit.csv",
            ),
        ),
        (
            "verify_service_delay_impact_audit",
            py_command(
                Path("analysis/scripts/verify_service_delay_impact_audit.py"),
                REPORTS_DIR / "service_delay_impact_audit.json",
                REPORTS_DIR / "service_delay_impact_audit.md",
                REPORTS_DIR / "service_delay_impact_audit.csv",
                REPORTS_DIR / "service_delay_impact_audit_quality_check.md",
                REPORTS_DIR / "service_delay_impact_audit_quality_check.json",
            ),
        ),
        (
            "audit_policy_trigger_behavior",
            py_command(
                Path("analysis/scripts/audit_policy_trigger_behavior.py"),
                CAMPAIGN_RESULT_DIR,
                REPORTS_DIR / "policy_trigger_behavior_audit.md",
                REPORTS_DIR / "policy_trigger_behavior_audit.json",
                REPORTS_DIR / "policy_trigger_behavior_audit.csv",
            ),
        ),
        (
            "verify_policy_trigger_behavior_audit",
            py_command(
                Path("analysis/scripts/verify_policy_trigger_behavior_audit.py"),
                REPORTS_DIR / "policy_trigger_behavior_audit.json",
                REPORTS_DIR / "policy_trigger_behavior_audit.md",
                REPORTS_DIR / "policy_trigger_behavior_audit.csv",
                REPORTS_DIR / "policy_trigger_behavior_audit_quality_check.md",
                REPORTS_DIR / "policy_trigger_behavior_audit_quality_check.json",
            ),
        ),
        (
            "generate_campaign_decision_matrix",
            py_command(
                Path("analysis/scripts/generate_campaign_decision_matrix.py"),
                REPORTS_DIR / "campaign_result_summary.json",
                REPORTS_DIR / "campaign_result_semantic_inspection.json",
                REPORTS_DIR / "service_delay_impact_audit.json",
                REPORTS_DIR / "policy_trigger_behavior_audit.json",
                REPORTS_DIR / "campaign_decision_matrix.md",
                REPORTS_DIR / "campaign_decision_matrix.json",
                REPORTS_DIR / "campaign_decision_matrix.csv",
            ),
        ),
        (
            "verify_campaign_decision_matrix",
            py_command(
                Path("analysis/scripts/verify_campaign_decision_matrix.py"),
                REPORTS_DIR / "campaign_decision_matrix.json",
                REPORTS_DIR / "campaign_decision_matrix.md",
                REPORTS_DIR / "campaign_decision_matrix.csv",
                REPORTS_DIR / "campaign_decision_matrix_quality_check.md",
                REPORTS_DIR / "campaign_decision_matrix_quality_check.json",
            ),
        ),
        (
            "generate_campaign_ranking_profile_sensitivity",
            py_command(
                Path("analysis/scripts/generate_campaign_ranking_profile_sensitivity.py"),
                Path("data/results/campaign_batches"),
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.md",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.json",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.csv",
            ),
        ),
        (
            "verify_campaign_ranking_profile_sensitivity",
            py_command(
                Path("analysis/scripts/verify_campaign_ranking_profile_sensitivity.py"),
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.json",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.md",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity.csv",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity_quality_check.md",
                REPORTS_DIR / "campaign_ranking_profile_sensitivity_quality_check.json",
            ),
        ),
        (
            "generate_campaign_final_diagnostic_report",
            py_command(
                Path("analysis/scripts/generate_campaign_final_diagnostic_report.py"),
                REPORTS_DIR / "campaign_execution_index.json",
                REPORTS_DIR / "campaign_result_summary.json",
                REPORTS_DIR / "campaign_result_semantic_inspection.json",
                REPORTS_DIR / "service_delay_impact_audit.json",
                REPORTS_DIR / "policy_trigger_behavior_audit.json",
                REPORTS_DIR / "campaign_decision_matrix.json",
                REPORTS_DIR / "campaign_final_diagnostic_report.md",
                REPORTS_DIR / "campaign_final_diagnostic_report.json",
                REPORTS_DIR / "campaign_final_diagnostic_report.csv",
            ),
        ),
        (
            "verify_campaign_final_diagnostic_report",
            py_command(
                Path("analysis/scripts/verify_campaign_final_diagnostic_report.py"),
                REPORTS_DIR / "campaign_final_diagnostic_report.json",
                REPORTS_DIR / "campaign_final_diagnostic_report.md",
                REPORTS_DIR / "campaign_final_diagnostic_report.csv",
                REPORTS_DIR / "campaign_final_diagnostic_report_quality_check.md",
                REPORTS_DIR / "campaign_final_diagnostic_report_quality_check.json",
            ),
        ),
    ]


def build_manifest(fieldops_exe: Path, steps: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [step for step in steps if step["status"] != "ok"]

    return {
        "report_type": "fieldops_lab_full_campaign_pipeline_manifest",
        "generated_at_local": now_text(),
        "fieldops_exe": path_text(fieldops_exe),
        "all_steps_passed": len(failed) == 0,
        "step_count": len(steps),
        "failed_step_count": len(failed),
        "failed_steps": [step["name"] for step in failed],
        "steps": steps,
        "important_outputs": {
            "campaign_execution_index": path_text(REPORTS_DIR / "campaign_execution_index.json"),
            "campaign_result_summary": path_text(REPORTS_DIR / "campaign_result_summary.json"),
            "campaign_result_semantic_inspection": path_text(REPORTS_DIR / "campaign_result_semantic_inspection.json"),
            "service_delay_impact_audit": path_text(REPORTS_DIR / "service_delay_impact_audit.json"),
            "policy_trigger_behavior_audit": path_text(REPORTS_DIR / "policy_trigger_behavior_audit.json"),
            "campaign_decision_matrix": path_text(REPORTS_DIR / "campaign_decision_matrix.json"),
            "campaign_ranking_profile_sensitivity": path_text(REPORTS_DIR / "campaign_ranking_profile_sensitivity.json"),
            "campaign_ranking_profile_sensitivity_quality_check": path_text(REPORTS_DIR / "campaign_ranking_profile_sensitivity_quality_check.json"),
            "campaign_final_diagnostic_report": path_text(REPORTS_DIR / "campaign_final_diagnostic_report.json"),
            "campaign_final_diagnostic_quality_check": path_text(REPORTS_DIR / "campaign_final_diagnostic_report_quality_check.json"),
        },
        "interpretation": {
            "status": "full_campaign_pipeline_execution",
            "fuzzy_logic_status": "not_used_in_main_pipeline",
            "warning": "This pipeline validates execution and reporting consistency. It does not prove final scientific validity.",
        },
    }


def write_report(manifest: dict[str, Any]) -> None:
    lines: list[str] = []

    lines.append("# FieldOps Lab full campaign pipeline report")
    lines.append("")
    lines.append("This report summarizes the automated execution of the full campaign pipeline.")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_steps_passed | {'yes' if manifest['all_steps_passed'] else 'no'} |")
    lines.append(f"| step_count | {manifest['step_count']} |")
    lines.append(f"| failed_step_count | {manifest['failed_step_count']} |")
    lines.append(f"| fieldops_exe | `{manifest['fieldops_exe']}` |")
    lines.append("")

    lines.append("## Pipeline steps")
    lines.append("")
    lines.append("| Step | Status | Return code |")
    lines.append("| --- | --- | ---: |")

    for step in manifest["steps"]:
        lines.append(
            f"| {step['name']} | {step['status']} | {step['return_code']} |"
        )

    lines.append("")
    lines.append("## Important outputs")
    lines.append("")
    lines.append("| Output | Path |")
    lines.append("| --- | --- |")

    for label, path in manifest["important_outputs"].items():
        lines.append(f"| {label} | `{path}` |")

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This pipeline is now useful as an engineering automation layer. It reduces manual command errors and creates a repeatable path from campaign design to final diagnostic report."
    )
    lines.append("")
    lines.append(
        "It still does not prove final scientific validity. Broader instances, stronger ranking profiles, richer policies, and statistical validation are still required."
    )

    write_text(FULL_PIPELINE_REPORT, "\n".join(lines) + "\n")


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: py -3 analysis\\scripts\\run_full_campaign_pipeline.py <fieldops_exe>",
            file=sys.stderr,
        )
        return 2

    fieldops_exe = Path(sys.argv[1])

    ensure_directories()

    log_lines: list[str] = []
    log_lines.append("FieldOps Lab full campaign pipeline")
    log_lines.append("=" * 80)
    log_lines.append(f"Generated at: {now_text()}")
    log_lines.append(f"Project root: {PROJECT_ROOT}")
    log_lines.append(f"FieldOps executable: {fieldops_exe}")

    if not fieldops_exe.exists():
        log_lines.append(f"ERROR: FieldOps executable not found: {fieldops_exe}")
        write_text(FULL_PIPELINE_LOG, "\n".join(log_lines) + "\n")

        manifest = build_manifest(fieldops_exe, [])
        manifest["all_steps_passed"] = False
        manifest["failed_step_count"] = 1
        manifest["failed_steps"] = ["fieldops_exe_missing"]
        write_json(FULL_PIPELINE_MANIFEST, manifest)
        write_report(manifest)
        return 1

    executed_steps: list[dict[str, Any]] = []
    pipeline_failed = False

    for name, command in build_steps(fieldops_exe):
        step = run_step(name, command, log_lines)
        executed_steps.append(step)

        write_text(FULL_PIPELINE_LOG, "\n".join(log_lines) + "\n")

        if step["status"] != "ok":
            pipeline_failed = True
            break

    manifest = build_manifest(fieldops_exe, executed_steps)
    write_json(FULL_PIPELINE_MANIFEST, manifest)
    write_report(manifest)
    write_text(FULL_PIPELINE_LOG, "\n".join(log_lines) + "\n")

    print(f"Full campaign pipeline report written to: {FULL_PIPELINE_REPORT}")
    print(f"Full campaign pipeline manifest written to: {FULL_PIPELINE_MANIFEST}")
    print(f"Full campaign pipeline log written to: {FULL_PIPELINE_LOG}")

    if pipeline_failed:
        print("ERROR: Full campaign pipeline failed.", file=sys.stderr)
        return 1

    print("Full campaign pipeline finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())