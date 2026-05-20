from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = Path("deploy/cloud-run/read_only_api.Dockerfile")

DEFAULT_IMAGE = "fieldops-read-only-api"
DEFAULT_CONTAINER_NAME = "fieldops-read-only-api-smoke-test"
DEFAULT_PORT = 8080

REQUIRED_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/project-status",
    "/api/v1/reports",
    "/api/v1/reports/{report_id}",
    "/api/v1/experimental-design-matrix",
    "/api/v1/research-method",
    "/api/v1/simulation-state-contract",
    "/api/v1/simulation-state-sample",
    "/api/v1/delay-injection-request-contract",
    "/api/v1/replanning-decision-response-contract",
    "/api/v1/replanning-decision-response-sample",
    "/api/v1/simulation-playback-control-contract",
    "/api/v1/simulation-playback-state-sample",
    "/api/v1/solver-integration-contract",
    "/api/v1/comparative-analysis-contract",
    "/api/v1/comparative-analysis-sample",
    "/api/v1/deployment-readiness-contract",
]


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str


class SmokeTestError(RuntimeError):
    pass


def format_command(command: Sequence[str]) -> str:
    return " ".join(command)


def run_captured_command(
    command: Sequence[str],
    *,
    check: bool = True,
    cwd: Path = REPOSITORY_ROOT,
) -> CommandResult:
    print(f"> {format_command(command)}", flush=True)
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = completed.stdout or ""
    if output.strip():
        print(output.rstrip(), flush=True)

    if check and completed.returncode != 0:
        raise SmokeTestError(
            f"Command failed with exit code {completed.returncode}: {format_command(command)}"
        )

    return CommandResult(returncode=completed.returncode, stdout=output)


def run_streamed_command(
    command: Sequence[str],
    *,
    check: bool = True,
    cwd: Path = REPOSITORY_ROOT,
) -> CommandResult:
    print(f"> {format_command(command)}", flush=True)
    process = subprocess.Popen(
        list(command),
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )

    output_lines: list[str] = []

    try:
        assert process.stdout is not None
        for line in process.stdout:
            output_lines.append(line)
            print(line, end="", flush=True)

        returncode = process.wait()
    except KeyboardInterrupt:
        print("\nSmoke test interrupted. Stopping current Docker command...", flush=True)
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        raise

    output = "".join(output_lines)

    if check and returncode != 0:
        raise SmokeTestError(
            f"Command failed with exit code {returncode}: {format_command(command)}"
        )

    return CommandResult(returncode=returncode, stdout=output)


def verify_docker_is_available() -> None:
    run_captured_command(["docker", "version"])


def build_image(image: str) -> None:
    if not (REPOSITORY_ROOT / DOCKERFILE_PATH).exists():
        raise SmokeTestError(f"Dockerfile not found: {DOCKERFILE_PATH}")

    run_streamed_command(
        [
            "docker",
            "build",
            "-f",
            str(DOCKERFILE_PATH),
            "-t",
            image,
            ".",
        ]
    )


def remove_named_container(container_name: str) -> None:
    run_captured_command(
        ["docker", "rm", "-f", container_name],
        check=False,
    )


def stop_container(container_id_or_name: str) -> None:
    if not container_id_or_name.strip():
        return

    run_captured_command(
        ["docker", "stop", container_id_or_name],
        check=False,
    )


def containers_publishing_port(port: int) -> list[str]:
    completed = run_captured_command(
        [
            "docker",
            "ps",
            "--filter",
            f"publish={port}",
            "--format",
            "{{.ID}}",
        ],
        check=False,
    )

    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def stop_containers_publishing_port(port: int) -> None:
    for container_id in containers_publishing_port(port):
        stop_container(container_id)


def start_container(image: str, container_name: str, port: int) -> str:
    completed = run_captured_command(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "--name",
            container_name,
            "-p",
            f"{port}:{port}",
            "-e",
            f"PORT={port}",
            image,
        ]
    )

    container_id = completed.stdout.strip().splitlines()[-1].strip()
    if not container_id:
        raise SmokeTestError("Docker did not return a container id.")

    return container_id


def request_json(url: str, *, timeout_seconds: float = 3.0) -> tuple[int, dict]:
    request = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        raw_payload = response.read().decode("utf-8")
        payload = json.loads(raw_payload)
        return response.status, payload


def request_status(url: str, *, method: str = "GET", timeout_seconds: float = 3.0) -> int:
    request = urllib.request.Request(url, method=method)

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response.read()
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def wait_for_health(base_url: str, timeout_seconds: float) -> dict:
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        attempt += 1
        try:
            status, payload = request_json(f"{base_url}/api/v1/health")
            if status == 200:
                print(f"Health check passed on attempt {attempt}.", flush=True)
                return payload
        except Exception as error:
            last_error = error
            print(f"Health check attempt {attempt} failed. Retrying...", flush=True)

        time.sleep(1.0)

    if last_error is not None:
        raise SmokeTestError(f"Health check did not pass before timeout. Last error: {last_error}")

    raise SmokeTestError("Health check did not pass before timeout.")


def validate_health_payload(payload: dict) -> None:
    expected_flags = {
        "status": "ok",
        "read_only": True,
        "execution_enabled": False,
        "browser_triggered_execution_enabled": False,
        "write_operations_supported": False,
    }

    for key, expected_value in expected_flags.items():
        actual_value = payload.get(key)
        if actual_value != expected_value:
            raise SmokeTestError(
                f"Invalid health payload field {key!r}: expected {expected_value!r}, got {actual_value!r}"
            )

    endpoints = payload.get("endpoints")
    if not isinstance(endpoints, list):
        raise SmokeTestError("Health payload field 'endpoints' must be a list.")

    if not all(isinstance(endpoint, str) for endpoint in endpoints):
        raise SmokeTestError("Health payload endpoint catalog must contain only strings.")

    if len(endpoints) != len(set(endpoints)):
        raise SmokeTestError("Health payload endpoint catalog must not contain duplicates.")

    missing = [endpoint for endpoint in REQUIRED_ENDPOINTS if endpoint not in endpoints]
    if missing:
        raise SmokeTestError(f"Health payload endpoint catalog is missing endpoints: {missing}")


def validate_read_only_http_behavior(base_url: str) -> None:
    unknown_report_status = request_status(
        f"{base_url}/api/v1/reports/unknown_report",
        method="GET",
    )
    if unknown_report_status != 404:
        raise SmokeTestError(
            f"Expected unknown report request to return 404, got {unknown_report_status}."
        )

    post_health_status = request_status(
        f"{base_url}/api/v1/health",
        method="POST",
    )
    if post_health_status != 405:
        raise SmokeTestError(
            f"Expected POST /api/v1/health to return 405, got {post_health_status}."
        )


def print_container_logs(container_id_or_name: str) -> None:
    if not container_id_or_name.strip():
        return

    run_captured_command(
        ["docker", "logs", container_id_or_name],
        check=False,
    )


def run_smoke_test(args: argparse.Namespace) -> int:
    container_id = ""

    print(
        "This smoke test validates the read-only API container only. "
        "It does not run solvers, does not start experiments, does not mutate schedules, "
        "does not write experiment outputs, does not deploy resources, and does not trigger backend jobs.",
        flush=True,
    )

    try:
        verify_docker_is_available()
        stop_containers_publishing_port(args.port)
        remove_named_container(args.container_name)

        if not args.skip_build:
            build_image(args.image)

        stop_containers_publishing_port(args.port)
        remove_named_container(args.container_name)

        container_id = start_container(args.image, args.container_name, args.port)
        base_url = f"http://127.0.0.1:{args.port}"

        payload = wait_for_health(base_url, args.startup_timeout_seconds)
        validate_health_payload(payload)
        validate_read_only_http_behavior(base_url)

        print("Read-only API container smoke test passed.", flush=True)
        return 0

    except KeyboardInterrupt:
        print("Smoke test interrupted by user.", flush=True)
        return 130

    except SmokeTestError as error:
        print(f"Smoke test failed: {error}", flush=True)
        if container_id:
            print_container_logs(container_id)
        return 1

    finally:
        if container_id:
            stop_container(container_id)

        remove_named_container(args.container_name)
        stop_containers_publishing_port(args.port)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and smoke-test the FieldOps Lab read-only API Docker container."
    )
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER_NAME)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--startup-timeout-seconds", type=float, default=45.0)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Use an existing local Docker image instead of rebuilding it.",
    )
    return parser


def main(argv: Sequence[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_smoke_test(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))