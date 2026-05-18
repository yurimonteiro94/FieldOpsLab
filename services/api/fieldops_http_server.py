from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_PATH = Path(__file__).with_name("fieldops_api.py")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080

ALLOWED_LOCAL_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://localhost:5173",
}


def load_api_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "fieldops_read_only_api",
        API_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load API module from {API_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["fieldops_read_only_api"] = module
    spec.loader.exec_module(module)

    return module


def encode_json(payload: Any) -> bytes:
    return json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")


def make_handler(
    api_module: ModuleType,
    quiet: bool = True,
) -> type[BaseHTTPRequestHandler]:
    class FieldOpsReadOnlyRequestHandler(BaseHTTPRequestHandler):
        server_version = "FieldOpsLabReadOnlyHTTP/0.1"

        def log_message(self, format: str, *args: Any) -> None:
            if not quiet:
                super().log_message(format, *args)

        def end_headers(self) -> None:
            origin = self.headers.get("Origin")

            if origin in ALLOWED_LOCAL_ORIGINS:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")

            self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def do_OPTIONS(self) -> None:
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

        def do_HEAD(self) -> None:
            self.write_api_response(send_body=False)

        def do_GET(self) -> None:
            self.write_api_response(send_body=True)

        def do_POST(self) -> None:
            self.write_method_not_allowed()

        def do_PUT(self) -> None:
            self.write_method_not_allowed()

        def do_PATCH(self) -> None:
            self.write_method_not_allowed()

        def do_DELETE(self) -> None:
            self.write_method_not_allowed()

        def write_method_not_allowed(self) -> None:
            payload = {
                "error": "method_not_allowed",
                "allowed_methods": ["GET", "HEAD", "OPTIONS"],
                "read_only": True,
                "write_operations_supported": False,
                "execution_supported": False,
                "allows_arbitrary_command_execution": False,
            }

            body = encode_json(payload)

            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def write_api_response(self, send_body: bool) -> None:
            route_path = self.path.split("?", maxsplit=1)[0]

            status_code, payload = api_module.build_response(route_path)
            body = encode_json(payload)

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()

            if send_body:
                self.wfile.write(body)

    return FieldOpsReadOnlyRequestHandler


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    quiet: bool = True,
) -> ThreadingHTTPServer:
    api_module = load_api_module()
    handler = make_handler(api_module=api_module, quiet=quiet)

    return ThreadingHTTPServer((host, port), handler)


def run_self_test() -> int:
    api_module = load_api_module()

    required_routes = [
        "/api/v1/health",
        "/api/v1/project-status",
        "/api/v1/reports",
        "/api/v1/experimental-design-matrix",
    ]

    for route in required_routes:
        status_code, payload = api_module.build_response(route)

        if status_code != HTTPStatus.OK:
            print(f"Self-test failed for route {route}: {status_code}", file=sys.stderr)
            return 1

        if not isinstance(payload, dict):
            print(f"Self-test failed for route {route}: payload is not a dict", file=sys.stderr)
            return 1

    unknown_status_code, unknown_payload = api_module.build_response("/api/v1/unknown")

    if unknown_status_code != HTTPStatus.NOT_FOUND:
        print("Self-test failed: unknown route did not return 404", file=sys.stderr)
        return 1

    if unknown_payload.get("error") != "not_found":
        print("Self-test failed: unknown route payload is not conservative", file=sys.stderr)
        return 1

    print("FieldOps Lab read-only HTTP API self-test passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the FieldOps Lab read-only local HTTP API server."
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Host interface to bind. Default: 127.0.0.1",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to bind. Default: 8080",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable HTTP request logging.",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a conservative local self-test without starting the server.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    server = create_server(
        host=args.host,
        port=args.port,
        quiet=not args.verbose,
    )

    print(f"FieldOps Lab read-only API listening on http://{args.host}:{args.port}")
    print("Allowed methods: GET, HEAD, OPTIONS")
    print("Execution endpoints are intentionally disabled.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stopping FieldOps Lab read-only API server.")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())