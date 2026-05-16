from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_OUTPUT_KEYS = [
    "overview_csv_output_path",
    "summary_csv_output_path",
    "aggregate_csv_output_path",
    "ranking_csv_output_path",
    "recommendation_csv_output_path",
    "result_json_output_path",
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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


def normalize_path(value: Any) -> str:
    return str(value).replace("/", "\\").strip()


def path_is_under_expected_dir(path_value: Any, expected_dir: str) -> bool:
    normalized_path = normalize_path(path_value).lower()
    normalized_expected_dir = normalize_path(expected_dir).lower().rstrip("\\") + "\\"

    return normalized_path.startswith(normalized_expected_dir)


def write_markdown(
    path: Path,
    result_path: Path,
    expected_result_dir: str,
    checks: list[dict[str, Any]],
    problem_count: int,
) -> None:
    all_required_checks_passed = problem_count == 0

    lines: list[str] = []
    lines.append("# FieldOps Lab executed campaign batch result path check")
    lines.append("")
    lines.append(f"Result JSON: `{result_path}`")
    lines.append("")
    lines.append("## Overall result")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| all_required_checks_passed | {format_bool(all_required_checks_passed)} |")
    lines.append(f"| problem_count | {problem_count} |")
    lines.append(f"| expected_result_dir | `{expected_result_dir}` |")
    lines.append("")
    lines.append("## Output path checks")
    lines.append("")
    lines.append("| Output key | Path | Under expected dir | Written | Problems |")
    lines.append("| --- | --- | --- | --- | --- |")

    for check in checks:
        problems = "; ".join(check["problems"]) if check["problems"] else "none"
        lines.append(
            "| "
            f"{check['key']} | "
            f"`{check['path']}` | "
            f"{format_bool(check['under_expected_dir'])} | "
            f"{format_bool(check['was_written'])} | "
            f"{problems} |"
        )

    lines.append("")
    lines.append("## Conservative interpretation")
    lines.append("")

    if all_required_checks_passed:
        lines.append("The executed batch result reports isolated campaign output paths. This reduces the risk of overwriting sample-batch outputs.")
    else:
        lines.append("The executed batch result still reports one or more unsafe or stale output paths. This means the generated config may be correct, but the C++ loader or execution layer is probably not loading every output path field yet.")

    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: py -3 analysis\\scripts\\verify_executed_campaign_batch_result_paths.py "
            "<result_json> <expected_result_dir> <output_md> <output_json>",
            file=sys.stderr,
        )
        return 2

    result_path = Path(sys.argv[1])
    expected_result_dir = sys.argv[2]
    output_md = Path(sys.argv[3])
    output_json = Path(sys.argv[4])

    try:
        result_data = load_json(result_path)
        outputs = result_data.get("outputs")

        if not isinstance(outputs, dict):
            raise RuntimeError("Result JSON does not contain an outputs object.")

        checks: list[dict[str, Any]] = []

        for key in REQUIRED_OUTPUT_KEYS:
            value = outputs.get(key, "")
            normalized = normalize_path(value)
            problems: list[str] = []

            if not normalized:
                problems.append(f"Missing output key: {key}")

            if "sample_no_replanning_batch" in normalized:
                problems.append("Path still points to sample batch output.")

            under_expected_dir = path_is_under_expected_dir(normalized, expected_result_dir)

            if not under_expected_dir:
                problems.append("Path is not under expected campaign result directory.")

            written_key = key.replace("_output_path", "_was_written")
            was_written = bool(outputs.get(written_key, False))

            if not was_written:
                problems.append(f"Output was not reported as written: {written_key}")

            checks.append(
                {
                    "key": key,
                    "path": normalized,
                    "under_expected_dir": under_expected_dir,
                    "was_written": was_written,
                    "problems": problems,
                }
            )

        problem_count = sum(len(check["problems"]) for check in checks)
        all_required_checks_passed = problem_count == 0

        payload = {
            "report_type": "fieldops_lab_executed_campaign_batch_result_path_check",
            "result_path": str(result_path),
            "expected_result_dir": expected_result_dir,
            "all_required_checks_passed": all_required_checks_passed,
            "problem_count": problem_count,
            "checks": checks,
        }

        write_markdown(output_md, result_path, expected_result_dir, checks, problem_count)
        write_json(output_json, payload)

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Executed campaign batch result path report written to: {output_md}")
    print(f"Executed campaign batch result path JSON written to: {output_json}")

    if not all_required_checks_passed:
        print("ERROR: Executed campaign batch result path check failed.", file=sys.stderr)
        return 1

    print("Executed campaign batch result path check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())