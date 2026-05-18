from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS = [
    {
        "id": "project_status",
        "title": "Project status report",
        "json_path": "analysis/reports/project_status_report.json",
        "markdown_path": "analysis/reports/project_status_report.md",
        "quality_path": "analysis/reports/project_status_quality_check.json",
    },
    {
        "id": "scientific_validation_plan",
        "title": "Scientific validation plan",
        "json_path": "analysis/reports/scientific_validation_plan.json",
        "markdown_path": "analysis/reports/scientific_validation_plan.md",
        "quality_path": "analysis/reports/scientific_validation_plan_quality_check.json",
    },
    {
        "id": "experimental_design_matrix",
        "title": "Experimental design matrix",
        "json_path": "analysis/reports/experimental_design_matrix.json",
        "markdown_path": "analysis/reports/experimental_design_matrix.md",
        "quality_path": "analysis/reports/experimental_design_matrix_quality_check.json",
    },
    {
        "id": "ranking_sensitivity_explanation",
        "title": "Ranking sensitivity explanation",
        "json_path": "analysis/reports/ranking_sensitivity_explanation_report.json",
        "markdown_path": "analysis/reports/ranking_sensitivity_explanation_report.md",
        "quality_path": "analysis/reports/ranking_sensitivity_explanation_quality_check.json",
    },
    {
        "id": "test_inventory",
        "title": "Test inventory report",
        "json_path": "analysis/reports/test_inventory_report.json",
        "markdown_path": "analysis/reports/test_inventory_report.md",
        "quality_path": "analysis/reports/test_inventory_quality_check.json",
    },
]


def project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path


def read_json_file(relative_path: str) -> dict[str, Any]:
    path = project_path(relative_path)

    if not path.exists():
        return {
            "path": relative_path,
            "exists": False,
            "loaded": False,
            "data": None,
            "error": "missing_file",
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": relative_path,
            "exists": True,
            "loaded": False,
            "data": None,
            "error": f"invalid_json: {exc}",
        }

    return {
        "path": relative_path,
        "exists": True,
        "loaded": True,
        "data": data,
        "error": None,
    }


def file_status(relative_path: str) -> dict[str, Any]:
    path = project_path(relative_path)
    return {
        "path": relative_path,
        "exists": path.exists(),
    }


def recursive_find(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]

        for value in data.values():
            found = recursive_find(value, key)
            if found is not None:
                return found

    if isinstance(data, list):
        for item in data:
            found = recursive_find(item, key)
            if found is not None:
                return found

    return None


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_bool(value: Any) -> bool:
    return bool(value)


def routes() -> list[dict[str, str]]:
    return [
        {
            "method": "GET",
            "path": "/api/v1/health",
            "description": "Return API status and read-only mode.",
        },
        {
            "method": "GET",
            "path": "/api/v1/project-status",
            "description": "Return the current project status report summary.",
        },
        {
            "method": "GET",
            "path": "/api/v1/reports",
            "description": "Return available generated reports and quality checks.",
        },
        {
            "method": "GET",
            "path": "/api/v1/experimental-design-matrix",
            "description": "Return the experimental design matrix summary.",
        },
    ]


def build_health_response() -> dict[str, Any]:
    contract = read_json_file("platform/contracts/fieldops_platform_contract.json")

    return {
        "service": "fieldops_lab_api",
        "status": "ok",
        "mode": "read_only",
        "read_only": True,
        "allows_arbitrary_command_execution": False,
        "contract": {
            "path": contract["path"],
            "available": contract["loaded"],
        },
        "routes": routes(),
    }


def build_project_status_response() -> dict[str, Any]:
    report = read_json_file("analysis/reports/project_status_report.json")
    quality = read_json_file("analysis/reports/project_status_quality_check.json")
    data = report["data"] if isinstance(report["data"], dict) else {}

    return {
        "report": "project_status",
        "source": {
            "path": report["path"],
            "exists": report["exists"],
            "loaded": report["loaded"],
            "error": report["error"],
        },
        "quality_check": {
            "path": quality["path"],
            "exists": quality["exists"],
            "loaded": quality["loaded"],
            "error": quality["error"],
            "passed": recursive_find(quality["data"], "all_required_checks_passed") is True,
        },
        "summary_metrics": data.get("summary_metrics", {}),
        "conservative_note": (
            "This endpoint exposes diagnostic and engineering status only. "
            "It does not prove scientific validity."
        ),
    }


def build_reports_response() -> dict[str, Any]:
    report_items = []

    for item in REPORTS:
        report_items.append(
            {
                "id": item["id"],
                "title": item["title"],
                "json": file_status(item["json_path"]),
                "markdown": file_status(item["markdown_path"]),
                "quality_check": file_status(item["quality_path"]),
            }
        )

    return {
        "reports": report_items,
        "read_only": True,
        "write_operations_supported": False,
        "execution_supported": False,
    }


def build_experimental_design_response() -> dict[str, Any]:
    report = read_json_file("analysis/reports/experimental_design_matrix.json")
    quality = read_json_file("analysis/reports/experimental_design_matrix_quality_check.json")
    data = report["data"] if isinstance(report["data"], dict) else {}

    experiment_count = as_int(recursive_find(data, "experiment_count"))
    scenario_count = as_int(recursive_find(data, "scenario_count"))
    replication_count = as_int(recursive_find(data, "replication_count"))
    reproducible = as_bool(
        recursive_find(data, "all_experiments_reproducible_from_explicit_factors")
    )

    return {
        "report": "experimental_design_matrix",
        "source": {
            "path": report["path"],
            "exists": report["exists"],
            "loaded": report["loaded"],
            "error": report["error"],
        },
        "quality_check": {
            "path": quality["path"],
            "exists": quality["exists"],
            "loaded": quality["loaded"],
            "error": quality["error"],
            "passed": recursive_find(quality["data"], "all_required_checks_passed") is True,
        },
        "summary": {
            "experiment_count": experiment_count,
            "scenario_count": scenario_count,
            "replication_count": replication_count,
            "reproducible_from_explicit_factors": reproducible,
        },
        "conservative_note": (
            "The design matrix defines planned experiments. "
            "It still requires execution, replications, and statistical comparison."
        ),
    }


def build_response(path: str) -> tuple[int, dict[str, Any]]:
    parsed_path = urlparse(path).path.rstrip("/") or "/"

    if parsed_path == "/api/v1/health":
        return 200, build_health_response()

    if parsed_path == "/api/v1/project-status":
        return 200, build_project_status_response()

    if parsed_path == "/api/v1/reports":
        return 200, build_reports_response()

    if parsed_path == "/api/v1/experimental-design-matrix":
        return 200, build_experimental_design_response()

    return 404, {
        "error": "not_found",
        "path": parsed_path,
        "available_routes": routes(),
    }


class FieldOpsApiHandler(BaseHTTPRequestHandler):
    server_version = "FieldOpsLabReadOnlyApi/0.1"

    def send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        status_code, payload = build_response(self.path)
        self.send_json(status_code, payload)

    def do_POST(self) -> None:
        self.send_json(
            405,
            {
                "error": "method_not_allowed",
                "message": "This API skeleton is read-only.",
            },
        )

    def do_PUT(self) -> None:
        self.do_POST()

    def do_PATCH(self) -> None:
        self.do_POST()

    def do_DELETE(self) -> None:
        self.do_POST()

    def log_message(self, format_text: str, *args: Any) -> None:
        return


def run_self_test() -> int:
    expected_ok_paths = [
        "/api/v1/health",
        "/api/v1/project-status",
        "/api/v1/reports",
        "/api/v1/experimental-design-matrix",
    ]

    for path in expected_ok_paths:
        status_code, payload = build_response(path)

        if status_code != 200:
            print(f"ERROR: {path} returned {status_code}")
            return 1

        if not isinstance(payload, dict):
            print(f"ERROR: {path} did not return a JSON object")
            return 1

    status_code, payload = build_response("/api/v1/unknown")

    if status_code != 404:
        print("ERROR: unknown route did not return 404")
        return 1

    if payload.get("error") != "not_found":
        print("ERROR: unknown route did not return not_found")
        return 1

    print("FieldOps Lab read-only API self-test passed.")
    return 0


def serve(host: str, port: int) -> int:
    server = ThreadingHTTPServer((host, port), FieldOpsApiHandler)

    print(f"FieldOps Lab read-only API listening on http://{host}:{port}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping FieldOps Lab read-only API.")
    finally:
        server.server_close()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="FieldOps Lab read-only local API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--self-test", action="store_true")

    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return serve(args.host, args.port)


if __name__ == "__main__":
    raise SystemExit(main())