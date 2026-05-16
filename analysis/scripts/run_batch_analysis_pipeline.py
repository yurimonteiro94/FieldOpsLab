import json
import subprocess
import sys
from pathlib import Path


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def run_command(command, log_lines):
    log_lines.append("")
    log_lines.append("Command:")
    log_lines.append(" ".join(str(part) for part in command))
    log_lines.append("")

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    output = completed.stdout or ""

    if output.strip():
        log_lines.append(output.rstrip())

    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed with exit code "
            f"{completed.returncode}: {' '.join(str(part) for part in command)}\n\n{output}"
        )

    return output


def write_text(path, content):
    ensure_parent(path)
    Path(path).write_text(content, encoding="utf-8")


def file_status(path):
    path = Path(path)

    if not path.exists():
        return "missing"

    if path.is_file() and path.stat().st_size <= 0:
        return "empty"

    return "ok"


def markdown_escape(value):
    return str(value).replace("|", "\\|")


def build_index_report(data, outputs, pipeline_log_path):
    batch = data.get("batch", {})
    rankings = data.get("rankings", {})
    recommendations = data.get("recommendations", {})

    lines = []

    lines.append("# FieldOps Lab batch analysis index")
    lines.append("")
    lines.append(f"Batch ID: `{markdown_escape(batch.get('batch_id', ''))}`")
    lines.append("")
    lines.append(f"Batch name: {markdown_escape(batch.get('name', ''))}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file is an index for the generated analysis reports. "
        "It centralizes the post-processing outputs produced from one batch result JSON."
    )
    lines.append("")
    lines.append("## Batch status")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| configured_experiment_count | {batch.get('configured_experiment_count', '')} |")
    lines.append(f"| completed_experiment_count | {batch.get('completed_experiment_count', '')} |")
    lines.append(f"| completion_percent | {batch.get('completion_percent', '')} |")
    lines.append(f"| is_complete | {batch.get('is_complete', '')} |")
    lines.append(f"| recommendation_count | {recommendations.get('recommendation_count', '')} |")
    lines.append("")
    lines.append("## Ranking status")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    ranking_config = rankings.get("ranking_config", {})
    lines.append(f"| ranking_config_id | `{markdown_escape(ranking_config.get('ranking_config_id', ''))}` |")
    lines.append(f"| ranking_score_definition | {markdown_escape(rankings.get('ranking_score_definition', ''))} |")
    lines.append("")
    lines.append("## Generated reports")
    lines.append("")
    lines.append("| Report | Path | Status |")
    lines.append("| --- | --- | --- |")

    for label, path in outputs:
        lines.append(f"| {markdown_escape(label)} | `{markdown_escape(path)}` | {file_status(path)} |")

    lines.append(f"| pipeline_log | `{markdown_escape(pipeline_log_path)}` | {file_status(pipeline_log_path)} |")
    lines.append("")
    lines.append("## Recommended reading order")
    lines.append("")
    lines.append("1. Summary text")
    lines.append("2. Main markdown report")
    lines.append("3. Recommendation audit")
    lines.append("4. Ranking sensitivity")
    lines.append("5. Scenario descriptors")
    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")
    lines.append(
        "This pipeline does not generate a fuzzy decision report. "
        "That is intentional. The current recommended direction is to keep fuzzy logic as a possible future decision layer, "
        "not as the main method at this stage."
    )
    lines.append("")
    lines.append(
        "The current analysis is suitable for validating the experimental pipeline and organizing evidence. "
        "It is not yet enough for final research conclusions because the batch is still small and handcrafted."
    )
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: py -3 analysis\\scripts\\run_batch_analysis_pipeline.py "
            "<batch_result_json> <output_dir> <report_prefix>"
        )
        return 1

    batch_result_json = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    report_prefix = sys.argv[3]

    if not batch_result_json.exists():
        print(f"Batch result JSON not found: {batch_result_json}")
        return 1

    script_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_txt = output_dir / f"{report_prefix}_summary.txt"
    main_report_md = output_dir / f"{report_prefix}_report.md"
    audit_report_md = output_dir / f"{report_prefix}_audit.md"
    sensitivity_report_md = output_dir / f"{report_prefix}_ranking_sensitivity.md"
    descriptors_report_md = output_dir / f"{report_prefix}_scenario_descriptors.md"
    descriptors_csv = output_dir / f"{report_prefix}_scenario_descriptors.csv"
    index_report_md = output_dir / f"{report_prefix}_analysis_index.md"
    pipeline_log_txt = output_dir / f"{report_prefix}_pipeline_log.txt"

    log_lines = []
    log_lines.append("FieldOps Lab batch analysis pipeline")
    log_lines.append("====================================")
    log_lines.append(f"Input JSON: {batch_result_json}")
    log_lines.append(f"Output directory: {output_dir}")
    log_lines.append(f"Report prefix: {report_prefix}")

    try:
        summary_output = run_command(
            [
                sys.executable,
                str(script_dir / "summarize_batch_result.py"),
                str(batch_result_json),
            ],
            log_lines,
        )
        write_text(summary_txt, summary_output)

        run_command(
            [
                sys.executable,
                str(script_dir / "generate_batch_markdown_report.py"),
                str(batch_result_json),
                str(main_report_md),
            ],
            log_lines,
        )

        run_command(
            [
                sys.executable,
                str(script_dir / "audit_batch_recommendations.py"),
                str(batch_result_json),
                str(audit_report_md),
            ],
            log_lines,
        )

        run_command(
            [
                sys.executable,
                str(script_dir / "run_ranking_sensitivity.py"),
                str(batch_result_json),
                str(sensitivity_report_md),
            ],
            log_lines,
        )

        run_command(
            [
                sys.executable,
                str(script_dir / "generate_scenario_descriptors.py"),
                str(batch_result_json),
                str(descriptors_report_md),
                str(descriptors_csv),
            ],
            log_lines,
        )

        outputs = [
            ("summary_text", str(summary_txt)),
            ("main_markdown_report", str(main_report_md)),
            ("recommendation_audit", str(audit_report_md)),
            ("ranking_sensitivity", str(sensitivity_report_md)),
            ("scenario_descriptors_markdown", str(descriptors_report_md)),
            ("scenario_descriptors_csv", str(descriptors_csv)),
        ]

        data = read_json(batch_result_json)
        index_content = build_index_report(data, outputs, str(pipeline_log_txt))
        write_text(index_report_md, index_content)

        log_lines.append("")
        log_lines.append("Pipeline finished successfully.")
        log_lines.append(f"Index report: {index_report_md}")

        write_text(pipeline_log_txt, "\n".join(log_lines))

        print("Batch analysis pipeline finished.")
        print(f"Summary TXT: {summary_txt}")
        print(f"Main report: {main_report_md}")
        print(f"Audit report: {audit_report_md}")
        print(f"Ranking sensitivity report: {sensitivity_report_md}")
        print(f"Scenario descriptor report: {descriptors_report_md}")
        print(f"Scenario descriptor CSV: {descriptors_csv}")
        print(f"Index report: {index_report_md}")
        print(f"Pipeline log: {pipeline_log_txt}")

        return 0

    except Exception as error:
        log_lines.append("")
        log_lines.append("Pipeline failed.")
        log_lines.append(str(error))
        write_text(pipeline_log_txt, "\n".join(log_lines))

        print("Batch analysis pipeline failed.")
        print(str(error))
        print(f"Pipeline log: {pipeline_log_txt}")

        return 1


if __name__ == "__main__":
    raise SystemExit(main())