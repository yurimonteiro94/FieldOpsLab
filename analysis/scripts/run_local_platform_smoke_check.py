from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_SCRIPT = PROJECT_ROOT / "services" / "api" / "fieldops_http_server.py"

DEFAULT_HOST = "127.0.0.1"

EXPECTED_ROUTES = [
    "/api/v1/health",
    "/api/v1/project-status",
    "/api/v1/reports",
    "/api/v1/experimental-design-matrix",
]

FORBIDDEN_ROUTE_FRAGMENTS = [
    "/api/v1/execute",
    "/api/v1/run",
    "/api/v1/dispatch",
    "/api/v1/command",
]


@dataclass(frozen=True)
class HttpJsonResult:
    path: str
    status: int
    payload: dict[str, Any]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def find_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def read_json_endpoint(base_url: str, path: str, timeout_seconds: float) -> HttpJsonResult:
    url = f"{base_url}{path}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        raw_body = response.read().decode("utf-8")
        payload = json.loads(raw_body)

        ensure(
            isinstance(payload, dict),
            f"Endpoint {path} did not return a JSON object.",
        )

        return HttpJsonResult(
            path=path,
            status=int(response.status),
            payload=payload,
        )


def reject_post_request(base_url: str, path: str, timeout_seconds: float) -> None:
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=b"{}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        urllib.request.urlopen(request, timeout=timeout_seconds)
    except urllib.error.HTTPError as error:
        ensure(
            error.code == 405,
            f"Expected POST {path} to be rejected with 405, got {error.code}.",
        )
        return

    raise RuntimeError(f"POST {path} was unexpectedly accepted.")


def route_paths(health_payload: dict[str, Any]) -> list[str]:
    routes = health_payload.get("routes")

    ensure(isinstance(routes, list), "Health payload does not expose a routes list.")

    paths: list[str] = []

    for route in routes:
        ensure(isinstance(route, dict), "Health route entry is not an object.")

        path = route.get("path")
        method = route.get("method")

        ensure(isinstance(path, str), "Health route entry has no path string.")
        ensure(isinstance(method, str), "Health route entry has no method string.")
        ensure(method.upper() == "GET", f"Route {path} is not GET-only.")

        paths.append(path)

    return paths


def validate_health(payload: dict[str, Any]) -> None:
    ensure(payload.get("status") == "ok", "Health status is not ok.")
    ensure(payload.get("mode") == "read_only", "API mode is not read_only.")
    ensure(payload.get("read_only") is True, "API does not report read_only=true.")
    ensure(
        payload.get("allows_arbitrary_command_execution") is False,
        "API reports arbitrary command execution as allowed.",
    )

    paths = route_paths(payload)

    for expected_route in EXPECTED_ROUTES:
        ensure(
            expected_route in paths,
            f"Expected route missing from health payload: {expected_route}",
        )

    serialized = json.dumps(payload, sort_keys=True).lower()

    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        ensure(
            fragment not in serialized,
            f"Forbidden execution route fragment exposed by health payload: {fragment}",
        )


def validate_project_status(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True).lower()

    ensure(
        "scientific" in serialized,
        "Project status payload does not expose scientific status context.",
    )
    ensure(
        "engineering" in serialized or "quality" in serialized,
        "Project status payload does not expose engineering or quality context.",
    )

    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        ensure(
            fragment not in serialized,
            f"Forbidden execution route fragment exposed by project status: {fragment}",
        )


def validate_reports(payload: dict[str, Any]) -> None:
    reports = payload.get("reports")

    ensure(isinstance(reports, list), "Reports payload does not expose a reports list.")
    ensure(len(reports) > 0, "Reports payload exposes an empty reports list.")

    if "read_only" in payload:
        ensure(payload.get("read_only") is True, "Reports payload is not read_only.")

    if "execution_supported" in payload:
        ensure(
            payload.get("execution_supported") is False,
            "Reports payload says execution is supported.",
        )

    for report in reports:
        ensure(isinstance(report, dict), "Report entry is not an object.")
        ensure(isinstance(report.get("id"), str), "Report entry has no id string.")

    serialized = json.dumps(payload, sort_keys=True).lower()

    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        ensure(
            fragment not in serialized,
            f"Forbidden execution route fragment exposed by reports payload: {fragment}",
        )


def read_number_from_keys(payload: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = payload.get(key)

        if isinstance(value, int | float):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value.replace("%", "").strip())
            except ValueError:
                continue

    return None


def validate_experimental_design(payload: dict[str, Any]) -> None:
    summary = payload.get("summary")

    ensure(
        isinstance(summary, dict),
        "Experimental design payload does not expose a summary object.",
    )

    experiment_count = read_number_from_keys(
        summary,
        ["experiment_count", "experimentcount"],
    )

    ensure(
        experiment_count is not None and experiment_count > 0,
        "Experimental design summary does not expose a positive experiment count.",
    )

    serialized = json.dumps(payload, sort_keys=True).lower()

    ensure(
        "reproducible" in serialized or "replication" in serialized,
        "Experimental design payload does not expose reproducibility or replication context.",
    )


def wait_for_api(
    process: subprocess.Popen[str],
    base_url: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1)
            raise RuntimeError(
                "API server stopped before becoming ready.\n"
                f"stdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )

        try:
            return read_json_endpoint(
                base_url,
                "/api/v1/health",
                timeout_seconds=1.0,
            ).payload
        except Exception as error:
            last_error = error
            time.sleep(0.2)

    raise RuntimeError(f"API server did not become ready. Last error: {last_error}")


def stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    process.terminate()

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def start_api_server(host: str, port: int) -> subprocess.Popen[str]:
    ensure(API_SCRIPT.exists(), f"API script not found: {API_SCRIPT}")

    command = [
        sys.executable,
        str(API_SCRIPT),
        "--host",
        host,
        "--port",
        str(port),
    ]

    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_smoke_check(
    host: str,
    port: int,
    timeout_seconds: float,
    base_url: str | None,
) -> int:
    process: subprocess.Popen[str] | None = None

    if base_url is None:
        selected_port = port if port > 0 else find_free_port(host)
        selected_base_url = f"http://{host}:{selected_port}"

        process = start_api_server(host=host, port=selected_port)
        health_payload = wait_for_api(
            process=process,
            base_url=selected_base_url,
            timeout_seconds=timeout_seconds,
        )
    else:
        selected_base_url = base_url.rstrip("/")
        health_payload = read_json_endpoint(
            selected_base_url,
            "/api/v1/health",
            timeout_seconds=timeout_seconds,
        ).payload

    try:
        validate_health(health_payload)

        project_status = read_json_endpoint(
            selected_base_url,
            "/api/v1/project-status",
            timeout_seconds=timeout_seconds,
        )
        validate_project_status(project_status.payload)

        reports = read_json_endpoint(
            selected_base_url,
            "/api/v1/reports",
            timeout_seconds=timeout_seconds,
        )
        validate_reports(reports.payload)

        experimental_design = read_json_endpoint(
            selected_base_url,
            "/api/v1/experimental-design-matrix",
            timeout_seconds=timeout_seconds,
        )
        validate_experimental_design(experimental_design.payload)

        reject_post_request(
            selected_base_url,
            "/api/v1/health",
            timeout_seconds=timeout_seconds,
        )

        for path in EXPECTED_ROUTES:
            print(f"{path} 200")

        print("POST /api/v1/health 405")
        print("FieldOps Lab local platform smoke check passed.")
        return 0
    finally:
        if process is not None:
            stop_process(process)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local smoke check against the FieldOps Lab read-only platform API."
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Host used when starting the local API server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port used when starting the local API server. Use 0 to pick a free port.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=15.0,
        help="Maximum time to wait for local API readiness and endpoint responses.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Validate an already running API server instead of starting a new one.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    return run_smoke_check(
        host=args.host,
        port=args.port,
        timeout_seconds=args.timeout_seconds,
        base_url=args.base_url,
    )


if __name__ == "__main__":
    raise SystemExit(main())