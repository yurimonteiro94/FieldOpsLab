from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FileCheck:
    label: str
    path: str
    exists: bool
    size_bytes: int
    status_from_manifest: str
    expected_text_found: bool
    expected_text: str
    sha256: str
    problems: list[str]


EXPECTED_TEXT_BY_LABEL: dict[str, str] = {
    "summary_text": "FieldOps Lab batch result summary",
    "main_markdown_report": "# FieldOps Lab batch report",
    "recommendation_audit": "# FieldOps Lab recommendation audit",
    "ranking_sensitivity": "# FieldOps Lab ranking sensitivity report",
    "scenario_descriptors_markdown": "# FieldOps Lab scenario descriptor report",
    "scenario_descriptors_csv": "scenario_id,",
    "analysis_index": "# FieldOps Lab batch analysis index",
    "pipeline_log": "FieldOps Lab batch analysis pipeline",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def check_generated_file(entry: dict[str, Any]) -> FileCheck:
    label = str(entry.get("label", ""))
    raw_path = str(entry.get("path", ""))
    status_from_manifest = str(entry.get("status", ""))

    path = Path(raw_path)
    expected_text = EXPECTED_TEXT_BY_LABEL.get(label, "")

    problems: list[str] = []

    if not label:
        problems.append("Missing file label.")

    if not raw_path:
        problems.append("Missing file path.")

    exists = path.exists()
    size_bytes = path.stat().st_size if exists else 0
    sha256 = compute_sha256(path) if exists and path.is_file() else ""

    if status_from_manifest != "ok":
        problems.append(f"Manifest status is not ok. status={status_from_manifest}")

    if not exists:
        problems.append("File does not exist.")
    elif not path.is_file():
        problems.append("Path exists but is not a file.")
    elif size_bytes <= 0:
        problems.append("File is empty.")

    expected_text_found = True

    if exists and path.is_file() and expected_text:
        text = read_text_safely(path)
        expected_text_found = expected_text in text

        if not expected_text_found:
            problems.append(f"Expected text not found: {expected_text}")

    return FileCheck(
        label=label,
        path=raw_path,
        exists=exists,
        size_bytes=size_bytes,
        status_from_manifest=status_from_manifest,
        expected_text_found=expected_text_found,
        expected_text=expected_text,
        sha256=sha256,
        problems=problems,
    )


def find_duplicate_content(checks: list[FileCheck]) -> list[str]:
    problems: list[str] = []

    by_hash: dict[str, list[FileCheck]] = {}

    for check in checks:
        if check.sha256:
            by_hash.setdefault(check.sha256, []).append(check)

    for same_hash_checks in by_hash.values():
        if len(same_hash_checks) <= 1:
            continue

        labels = [check.label for check in same_hash_checks]
        paths = [check.path for check in same_hash_checks]

        problems.append(
            "Duplicate file content detected. "
            f"labels={labels}; paths={paths}"
        )

    return problems


def find_suspicious_same_size(checks: list[FileCheck]) -> list[str]:
    warnings: list[str] = []

    by_size: dict[int, list[FileCheck]] = {}

    for check in checks:
        if check.size_bytes > 0:
            by_size.setdefault(check.size_bytes, []).append(check)

    for size, same_size_checks in by_size.items():
        if len(same_size_checks) <= 1:
            continue

        labels = [check.label for check in same_size_checks]

        warnings.append(
            "Suspicious same file size detected. "
            f"size_bytes={size}; labels={labels}. "
            "This is not necessarily wrong, but it should be reviewed."
        )

    return warnings


def build_markdown_report(
    manifest_path: Path,
    checks: list[FileCheck],
    duplicate_content_problems: list[str],
    suspicious_same_size_warnings: list[str],
) -> str:
    total_problem_count = (
        sum(len(check.problems) for check in checks)
        + len(duplicate_content_problems)
    )

    warning_count = len(suspicious_same_size_warnings)

    all_ok = total_problem_count == 0

    lines: list[str] = []

    lines.append("# FieldOps Lab analysis output quality check")
    lines.append("")
    lines.append(f"Manifest: `{manifest_path}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {'yes' if all_ok else 'no'} |")
    lines.append(f"| problem_count | {total_problem_count} |")
    lines.append(f"| warning_count | {warning_count} |")
    lines.append(f"| checked_file_count | {len(checks)} |")
    lines.append("")

    lines.append("## File checks")
    lines.append("")
    lines.append(
        "| Label | Exists | Size bytes | Manifest status | Expected text found | Problems |"
    )
    lines.append("| --- | --- | ---: | --- | --- | --- |")

    for check in checks:
        problems = "; ".join(check.problems) if check.problems else "none"

        lines.append(
            f"| {check.label} | "
            f"{'yes' if check.exists else 'no'} | "
            f"{check.size_bytes} | "
            f"{check.status_from_manifest} | "
            f"{'yes' if check.expected_text_found else 'no'} | "
            f"{problems} |"
        )

    lines.append("")

    lines.append("## Duplicate content checks")
    lines.append("")

    if duplicate_content_problems:
        for problem in duplicate_content_problems:
            lines.append(f"- ERROR: {problem}")
    else:
        lines.append("- No exact duplicate file content detected.")

    lines.append("")

    lines.append("## Same-size warnings")
    lines.append("")

    if suspicious_same_size_warnings:
        for warning in suspicious_same_size_warnings:
            lines.append(f"- WARNING: {warning}")
    else:
        lines.append("- No suspicious same-size files detected.")

    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")

    if all_ok:
        lines.append(
            "The generated analysis outputs passed the structural quality check. "
            "This does not prove the scientific validity of the experiment, but it reduces "
            "the risk of using missing, empty, mislabeled, or accidentally duplicated reports."
        )
    else:
        lines.append(
            "The generated analysis outputs did not pass the structural quality check. "
            "Do not use these reports as evidence until the listed problems are corrected."
        )

    lines.append("")

    return "\n".join(lines)


def build_json_report(
    manifest_path: Path,
    checks: list[FileCheck],
    duplicate_content_problems: list[str],
    suspicious_same_size_warnings: list[str],
) -> dict[str, Any]:
    total_problem_count = (
        sum(len(check.problems) for check in checks)
        + len(duplicate_content_problems)
    )

    return {
        "report_type": "fieldops_lab_analysis_output_quality_check",
        "manifest_path": str(manifest_path),
        "all_required_checks_passed": total_problem_count == 0,
        "problem_count": total_problem_count,
        "warning_count": len(suspicious_same_size_warnings),
        "checked_file_count": len(checks),
        "file_checks": [
            {
                "label": check.label,
                "path": check.path,
                "exists": check.exists,
                "size_bytes": check.size_bytes,
                "status_from_manifest": check.status_from_manifest,
                "expected_text": check.expected_text,
                "expected_text_found": check.expected_text_found,
                "sha256": check.sha256,
                "problems": check.problems,
            }
            for check in checks
        ],
        "duplicate_content_problems": duplicate_content_problems,
        "suspicious_same_size_warnings": suspicious_same_size_warnings,
    }


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: py -3 analysis\\scripts\\verify_analysis_outputs.py "
            "<analysis_manifest.json> <quality_report.md> <quality_report.json>"
        )
        return 2

    manifest_path = Path(sys.argv[1])
    markdown_output_path = Path(sys.argv[2])
    json_output_path = Path(sys.argv[3])

    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}")
        return 1

    manifest = read_json(manifest_path)

    generated_files = manifest.get("generated_files", [])

    if not isinstance(generated_files, list):
        print("ERROR: manifest.generated_files must be a list.")
        return 1

    checks = []

    for entry in generated_files:
        if isinstance(entry, dict):
            checks.append(check_generated_file(entry))

    duplicate_content_problems = find_duplicate_content(checks)
    suspicious_same_size_warnings = find_suspicious_same_size(checks)

    markdown_report = build_markdown_report(
        manifest_path=manifest_path,
        checks=checks,
        duplicate_content_problems=duplicate_content_problems,
        suspicious_same_size_warnings=suspicious_same_size_warnings,
    )

    json_report = build_json_report(
        manifest_path=manifest_path,
        checks=checks,
        duplicate_content_problems=duplicate_content_problems,
        suspicious_same_size_warnings=suspicious_same_size_warnings,
    )

    markdown_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown_output_path.write_text(markdown_report, encoding="utf-8")
    json_output_path.write_text(
        json.dumps(json_report, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Analysis output quality report written to: {markdown_output_path}")
    print(f"Analysis output quality JSON written to: {json_output_path}")

    if not json_report["all_required_checks_passed"]:
        print("ERROR: Analysis output quality check failed.")
        return 1

    if suspicious_same_size_warnings:
        print("WARNING: Same-size files detected. Review the quality report.")

    print("Analysis output quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())