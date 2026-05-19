from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

PROJECT_STATUS_PATH = REPOSITORY_ROOT / "analysis" / "reports" / "project_status_report.json"
REPORTS_ROOT = REPOSITORY_ROOT / "analysis" / "reports"
EXPERIMENTAL_DESIGN_PATH = REPOSITORY_ROOT / "analysis" / "reports" / "experimental_design_matrix.json"
PLATFORM_CONTRACT_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "fieldops_platform_contract.json"
RESEARCH_METHOD_CONTRACT_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "research_method_contract.json"
RESEARCH_FRAMING_PATH = REPOSITORY_ROOT / "platform" / "research_framing.md"


def read_json_file(path: Path, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return fallback or {}

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, dict):
        return payload

    return fallback or {}


def read_text_file(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def path_exists_as_bool(path: Path) -> bool:
    return path.exists() and path.is_file()


def known_reports() -> list[dict[str, Any]]:
    report_definitions = [
        {
            "id": "project_status",
            "title": "Project status",
            "category": "engineering",
            "description": "Current structural engineering status.",
            "artifact_path": "analysis/reports/project_status_report.json",
            "quality_path": "analysis/reports/project_status_quality_check.json",
        },
        {
            "id": "test_inventory",
            "title": "Test inventory",
            "category": "engineering",
            "description": "Current automated test inventory.",
            "artifact_path": "analysis/reports/test_inventory_report.json",
            "quality_path": "analysis/reports/test_inventory_quality_check.json",
        },
        {
            "id": "experimental_design_matrix",
            "title": "Experimental design matrix",
            "category": "scientific_design",
            "description": "Explicit experimental factors, scenarios, and planned replications.",
            "artifact_path": "analysis/reports/experimental_design_matrix.json",
            "quality_path": "analysis/reports/experimental_design_matrix_quality_check.json",
        },
        {
            "id": "ranking_sensitive_scenario",
            "title": "Ranking-sensitive scenario report",
            "category": "diagnostic",
            "description": "Scenarios where ranking decisions may be sensitive.",
            "artifact_path": "analysis/reports/ranking_sensitive_scenario_report.json",
            "quality_path": "analysis/reports/ranking_sensitive_scenario_quality_check.json",
        },
        {
            "id": "ranking_sensitivity_explanation",
            "title": "Ranking sensitivity explanation",
            "category": "diagnostic",
            "description": "Explanation of ranking sensitivity and practical equivalence risks.",
            "artifact_path": "analysis/reports/ranking_sensitivity_explanation_report.json",
            "quality_path": "analysis/reports/ranking_sensitivity_explanation_quality_check.json",
        },
        {
            "id": "scientific_validation_plan",
            "title": "Scientific validation plan",
            "category": "scientific_validation",
            "description": "Planned validation actions and methodological warnings.",
            "artifact_path": "analysis/reports/scientific_validation_plan.json",
            "quality_path": "analysis/reports/scientific_validation_plan_quality_check.json",
        },
    ]

    reports: list[dict[str, Any]] = []

    for item in report_definitions:
        artifact_path = REPOSITORY_ROOT / item["artifact_path"]
        quality_path = REPOSITORY_ROOT / item["quality_path"]
        quality_payload = read_json_file(quality_path)

        reports.append(
            {
                **item,
                "available": path_exists_as_bool(artifact_path),
                "loaded": path_exists_as_bool(artifact_path),
                "quality_available": path_exists_as_bool(quality_path),
                "quality_passed": quality_payload.get("passed"),
            }
        )

    return reports


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
        {
            "method": "GET",
            "path": "/api/v1/research-method",
            "description": "Return the conservative research method framing and contract.",
        },
    ]


def health_payload() -> dict[str, Any]:
    return {
        "service": "fieldops_lab_api",
        "status": "ok",
        "mode": "read_only",
        "read_only": True,
        "allows_arbitrary_command_execution": False,
        "contract": {
            "available": path_exists_as_bool(PLATFORM_CONTRACT_PATH),
            "path": "platform/contracts/fieldops_platform_contract.json",
        },
        "research_method_contract": {
            "available": path_exists_as_bool(RESEARCH_METHOD_CONTRACT_PATH),
            "path": "platform/contracts/research_method_contract.json",
        },
        "routes": routes(),
    }


def project_status_payload() -> dict[str, Any]:
    payload = read_json_file(PROJECT_STATUS_PATH)

    if payload:
        return {
            "report": "project_status",
            "available": True,
            "read_only": True,
            "source": {
                "exists": path_exists_as_bool(PROJECT_STATUS_PATH),
                "loaded": path_exists_as_bool(PROJECT_STATUS_PATH),
                "path": "analysis/reports/project_status_report.json",
            },
            "conservative_note": payload.get(
                "conservative_note",
                "This dashboard does not prove scientific validity.",
            ),
            **payload,
        }

    return {
        "report": "project_status",
        "available": False,
        "read_only": True,
        "summary_metrics": {
            "product_completeness": 50,
            "engineering_status": "report_unavailable",
            "scientific_status": "diagnostic_only_with_methodological_warnings",
        },
        "conservative_note": "Project status report is not available.",
    }


def experimental_design_payload() -> dict[str, Any]:
    payload = read_json_file(EXPERIMENTAL_DESIGN_PATH)

    if payload:
        return payload

    return {
        "report": "experimental_design_matrix",
        "available": False,
        "read_only": True,
        "summary": {
            "experiment_count": 0,
            "scenario_count": 0,
            "replication_count": 0,
            "reproducible_from_explicit_factors": False,
        },
    }


def reports_payload() -> dict[str, Any]:
    return {
        "read_only": True,
        "execution_supported": False,
        "reports_root": "analysis/reports",
        "reports": known_reports(),
    }


def research_method_payload() -> dict[str, Any]:
    contract = read_json_file(RESEARCH_METHOD_CONTRACT_PATH)
    framing = read_text_file(RESEARCH_FRAMING_PATH)

    return {
        "read_only": True,
        "available": bool(contract) or bool(framing),
        "contract_path": "platform/contracts/research_method_contract.json",
        "framing_path": "platform/research_framing.md",
        "contract": contract,
        "framing_markdown": framing,
        "conservative_interpretation": {
            "does_not_claim_final_scientific_validity": True,
            "fuzzy_logic_is_optional": True,
            "practical_equivalence_must_be_handled": True,
            "real_company_data_requires_validation_before_decision_support": True,
        },
    }


def route_payload(path: str) -> tuple[int, dict[str, Any]]:
    if path == "/api/v1/health":
        return HTTPStatus.OK, health_payload()

    if path == "/api/v1/project-status":
        return HTTPStatus.OK, project_status_payload()

    if path == "/api/v1/reports":
        return HTTPStatus.OK, reports_payload()

    if path == "/api/v1/experimental-design-matrix":
        return HTTPStatus.OK, experimental_design_payload()

    if path == "/api/v1/research-method":
        return HTTPStatus.OK, research_method_payload()

    return HTTPStatus.NOT_FOUND, {
        "error": "not_found",
        "read_only": True,
        "path": path,
    }


class FieldOpsRequestHandler(BaseHTTPRequestHandler):
    server_version = "FieldOpsLabReadOnlyAPI/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

    def do_HEAD(self) -> None:
        status_code, payload = route_payload(self.path.split("?", 1)[0])
        self.send_json(status_code, payload)

    def do_GET(self) -> None:
        status_code, payload = route_payload(self.path.split("?", 1)[0])
        self.send_json(status_code, payload)

    def do_POST(self) -> None:
        self.send_json(
            HTTPStatus.METHOD_NOT_ALLOWED,
            {
                "error": "method_not_allowed",
                "read_only": True,
                "write_operations_supported": False,
                "execution_supported": False,
                "allows_arbitrary_command_execution": False,
                "allowed_methods": ["GET", "HEAD", "OPTIONS"],
            },
        )

    def do_PUT(self) -> None:
        self.do_POST()

    def do_PATCH(self) -> None:
        self.do_POST()

    def do_DELETE(self) -> None:
        self.do_POST()


def create_server(host: str, port: int, quiet: bool = False) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), FieldOpsRequestHandler)


def read_url_json(url: str) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
    except urllib.error.HTTPError as error:
        payload = json.loads(error.read().decode("utf-8"))
        return error.code, payload


def read_url_status_for_method(url: str, method: str) -> int:
    request = urllib.request.Request(url, method=method)

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def run_self_test() -> int:
    host = "127.0.0.1"
    server = create_server(host, 0)
    port = int(server.server_address[1])

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://{host}:{port}"
        expected_paths = [
            "/api/v1/health",
            "/api/v1/project-status",
            "/api/v1/reports",
            "/api/v1/experimental-design-matrix",
            "/api/v1/research-method",
        ]

        for path in expected_paths:
            status, payload = read_url_json(base_url + path)
            print(path, status)
            if status != HTTPStatus.OK:
                raise RuntimeError(f"Expected HTTP 200 for {path}, got {status}")
            if not payload.get("read_only", True):
                raise RuntimeError(f"Endpoint {path} did not preserve read-only contract")

        post_status = read_url_status_for_method(base_url + "/api/v1/health", "POST")
        print("POST /api/v1/health", post_status)

        if post_status != HTTPStatus.METHOD_NOT_ALLOWED:
            raise RuntimeError("POST request should be rejected with 405")

        research_status, research_payload = read_url_json(base_url + "/api/v1/research-method")

        if research_status != HTTPStatus.OK:
            raise RuntimeError("Research method endpoint is unavailable")

        conservative = research_payload.get("conservative_interpretation", {})

        if conservative.get("fuzzy_logic_is_optional") is not True:
            raise RuntimeError("Research method endpoint must keep fuzzy logic optional")

        if conservative.get("practical_equivalence_must_be_handled") is not True:
            raise RuntimeError("Research method endpoint must handle practical equivalence")

        print("FieldOps Lab read-only API self-test passed.")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description="FieldOps Lab read-only local HTTP API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        raise SystemExit(run_self_test())


    server = create_server(args.host, args.port)

    print(f"FieldOps Lab read-only API listening on http://{args.host}:{args.port}")
    print("Allowed methods: GET, HEAD, OPTIONS")
    print("Execution endpoints are intentionally disabled.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping FieldOps Lab read-only API server.")
        server.server_close()
        time.sleep(0.1)


if __name__ == "__main__":
    main()