from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPORT_TYPE = "fieldops_lab_test_inventory_report"


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def path_text(path: Path) -> str:
    return str(path).replace("/", "\\")


def relative_text(root: Path, path: Path) -> str:
    try:
        return path_text(path.relative_to(root))
    except ValueError:
        return path_text(path)


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def find_files(root: Path, pattern: str) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob(pattern) if path.is_file())


def find_analysis_scripts(root: Path) -> list[Path]:
    scripts_dir = root / "analysis" / "scripts"
    return sorted(
        path
        for path in scripts_dir.glob("*.py")
        if path.is_file() and path.name != "__init__.py"
    )


def find_python_tests(root: Path) -> list[Path]:
    return find_files(root / "tests" / "python", "test_*.py")


def find_cpp_tests(root: Path) -> list[Path]:
    return sorted(
        path
        for path in (root / "tests").rglob("*.cpp")
        if path.is_file()
    )


def find_cpp_test_support_headers(root: Path) -> list[Path]:
    return sorted(
        path
        for path in (root / "tests").rglob("*.h")
        if path.is_file()
    )


def normalize_script_token(stem: str) -> str:
    prefixes = [
        "generate_",
        "verify_",
        "audit_",
        "inspect_",
        "integrate_",
        "connect_",
        "summarize_",
        "run_",
    ]

    token = stem
    for prefix in prefixes:
        if token.startswith(prefix):
            token = token[len(prefix) :]
            break

    return token


def count_related_tests(
    script: Path,
    python_tests: list[Path],
) -> tuple[list[str], list[str]]:
    stem = script.stem
    token = normalize_script_token(stem)

    direct_matches: list[str] = []
    related_matches: list[str] = []

    for test_path in python_tests:
        test_name = test_path.stem
        test_text = read_text_safe(test_path)

        direct = (
            stem in test_name
            or stem in test_text
            or script.name in test_text
            or path_text(script) in test_text
            or script.as_posix() in test_text
        )

        related = direct or token in test_name or token in test_text

        if direct:
            direct_matches.append(path_text(test_path))

        if related:
            related_matches.append(path_text(test_path))

    return sorted(set(direct_matches)), sorted(set(related_matches))


def build_rows(root: Path) -> list[dict[str, Any]]:
    scripts = find_analysis_scripts(root)
    python_tests = find_python_tests(root)

    rows: list[dict[str, Any]] = []

    generic_test_count = sum(
        1
        for path in python_tests
        if path.name
        in {
            "test_all_analysis_scripts_compile.py",
            "test_analysis_script_usage_contracts.py",
            "test_verifier_negative_contracts.py",
            "test_project_quality_gate_contract.py",
        }
    )

    for script in scripts:
        direct_tests, related_tests = count_related_tests(script, python_tests)
        is_patch_script = script.name.startswith("patch_")

        if is_patch_script:
            status = "temporary_patch_script_left_in_tree"
        elif direct_tests:
            status = "direct_test_found"
        elif related_tests:
            status = "related_test_found"
        elif generic_test_count > 0:
            status = "covered_by_generic_contract_tests"
        else:
            status = "needs_test_review"

        rows.append(
            {
                "script_path": relative_text(root, script),
                "script_name": script.name,
                "script_stem": script.stem,
                "is_patch_script": is_patch_script,
                "direct_python_test_count": len(direct_tests),
                "related_python_test_count": len(related_tests),
                "generic_python_test_count": generic_test_count,
                "status": status,
                "direct_python_tests": direct_tests,
                "related_python_tests": related_tests,
            }
        )

    return rows


def build_report(root: Path) -> dict[str, Any]:
    rows = build_rows(root)

    analysis_scripts = find_analysis_scripts(root)
    python_tests = find_python_tests(root)
    cpp_tests = find_cpp_tests(root)
    cpp_headers = find_cpp_test_support_headers(root)

    patch_rows = [row for row in rows if row["is_patch_script"]]
    no_direct_rows = [
        row
        for row in rows
        if not row["is_patch_script"] and int(row["direct_python_test_count"]) == 0
    ]
    needs_review_rows = [
        row
        for row in rows
        if row["status"] in {"needs_test_review", "covered_by_generic_contract_tests"}
    ]

    problems: list[str] = []
    warnings: list[str] = []

    if not analysis_scripts:
        problems.append("No analysis scripts were found.")

    if not python_tests:
        problems.append("No Python tests were found.")

    if not cpp_tests:
        problems.append("No C++ test source files were found.")

    if patch_rows:
        problems.append(f"{len(patch_rows)} temporary patch script(s) remain in analysis/scripts.")

    if no_direct_rows:
        warnings.append(
            f"{len(no_direct_rows)} analysis script(s) do not have a direct Python test reference."
        )

    if needs_review_rows:
        warnings.append(
            f"{len(needs_review_rows)} analysis script(s) rely on generic or indirect test coverage."
        )

    overview = {
        "analysis_script_count": len(analysis_scripts),
        "python_test_count": len(python_tests),
        "cpp_test_source_count": len(cpp_tests),
        "cpp_test_support_header_count": len(cpp_headers),
        "script_with_direct_python_test_count": sum(
            1 for row in rows if int(row["direct_python_test_count"]) > 0
        ),
        "script_without_direct_python_test_count": len(no_direct_rows),
        "script_needing_test_review_count": len(needs_review_rows),
        "patch_script_count": len(patch_rows),
        "row_count": len(rows),
    }

    return {
        "report_type": REPORT_TYPE,
        "generated_at_local": now_text(),
        "project_root": path_text(root),
        "all_required_checks_passed": len(problems) == 0,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "overview": overview,
        "rows": rows,
        "problems": problems,
        "warnings": warnings,
        "interpretation": {
            "status": "test_inventory_diagnostic_only",
            "scientific_status": "test_structure_review_only",
            "warning": (
                "This report measures structural test coverage signals. "
                "It does not prove semantic correctness or scientific validity."
            ),
        },
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "script_path",
        "script_name",
        "script_stem",
        "is_patch_script",
        "direct_python_test_count",
        "related_python_test_count",
        "generic_python_test_count",
        "status",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    overview = report["overview"]
    rows = report["rows"]

    lines: list[str] = []
    lines.append("# FieldOps Lab test inventory report")
    lines.append("")
    lines.append("This report audits the structural organization of C++ and Python tests.")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| all_required_checks_passed | {'yes' if report['all_required_checks_passed'] else 'no'} |"
    )
    lines.append(f"| problem_count | {report['problem_count']} |")
    lines.append(f"| warning_count | {report['warning_count']} |")
    for key, value in overview.items():
        lines.append(f"| {key} | {value} |")
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

    lines.append("## Analysis script test signals")
    lines.append("")
    lines.append(
        "| Script | Direct tests | Related tests | Generic tests | Status |"
    )
    lines.append("| --- | ---: | ---: | ---: | --- |")
    for row in rows:
        lines.append(
            f"| `{row['script_path']}` | "
            f"{row['direct_python_test_count']} | "
            f"{row['related_python_test_count']} | "
            f"{row['generic_python_test_count']} | "
            f"{row['status']} |"
        )
    lines.append("")

    lines.append("## Conservative interpretation")
    lines.append("")
    if report["all_required_checks_passed"]:
        lines.append(
            "The project has a centralized Python test tree and no temporary patch scripts were found."
        )
    else:
        lines.append(
            "The test inventory found structural problems. Fix them before using this as a quality baseline."
        )
    lines.append("")
    lines.append(
        "Scripts without direct tests are not automatically wrong, but they should be reviewed over time."
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: py -3 analysis\\scripts\\generate_test_inventory_report.py "
            "<output_md> <output_json> <output_csv>",
            file=sys.stderr,
        )
        return 2

    root = Path.cwd()
    output_md = Path(sys.argv[1])
    output_json = Path(sys.argv[2])
    output_csv = Path(sys.argv[3])

    report = build_report(root)

    write_markdown(output_md, report)
    write_json(output_json, report)
    write_csv(output_csv, report["rows"])

    print(f"Test inventory markdown written to: {output_md}")
    print(f"Test inventory JSON written to: {output_json}")
    print(f"Test inventory CSV written to: {output_csv}")

    if not report["all_required_checks_passed"]:
        print("ERROR: Test inventory found structural problems.", file=sys.stderr)
        return 1

    print("Test inventory completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())