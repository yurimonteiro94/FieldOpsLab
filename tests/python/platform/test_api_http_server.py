## 4. Conteúdo completo de `tests\python\platform\test_api_http_server.py`

from __future__ import annotations

import importlib.util
import json
import threading
import unittest
from http import HTTPStatus
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[3]
HTTP_SERVER_PATH = PROJECT_ROOT / "services" / "api" / "fieldops_http_server.py"


def load_http_server_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "fieldops_http_server",
        HTTP_SERVER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load HTTP server module from {HTTP_SERVER_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def read_json_url(url: str) -> tuple[int, dict[str, Any], Any]:
    with urlopen(url, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload, response.headers


class FieldOpsHttpServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server_module = load_http_server_module()

    def test_http_server_file_exists(self) -> None:
        self.assertTrue(HTTP_SERVER_PATH.exists())

    def test_http_server_source_does_not_use_unsafe_execution_primitives(self) -> None:
        source = HTTP_SERVER_PATH.read_text(encoding="utf-8").lower()

        forbidden_fragments = [
            "subprocess",
            "os.system",
            "popen",
            "shell=true",
            "eval(",
            "exec(",
        ]

        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, source)

    def test_self_test_passes(self) -> None:
        self.assertEqual(self.server_module.run_self_test(), 0)

    def test_health_route_is_available_over_http(self) -> None:
        server = self.server_module.create_server(host="127.0.0.1", port=0, quiet=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address
            status_code, payload, headers = read_json_url(
                f"http://{host}:{port}/api/v1/health"
            )

            self.assertEqual(status_code, HTTPStatus.OK)
            self.assertEqual(payload["service"], "fieldops_lab_api")
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["mode"], "read_only")
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["allows_arbitrary_command_execution"])
            self.assertIn("application/json", headers["Content-Type"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_project_status_route_is_available_over_http(self) -> None:
        server = self.server_module.create_server(host="127.0.0.1", port=0, quiet=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address
            status_code, payload, _headers = read_json_url(
                f"http://{host}:{port}/api/v1/project-status"
            )

            self.assertEqual(status_code, HTTPStatus.OK)
            self.assertEqual(payload["report"], "project_status")
            self.assertTrue(payload["source"]["exists"])
            self.assertTrue(payload["source"]["loaded"])
            self.assertIn("summary_metrics", payload)
            self.assertIn("does not prove scientific validity", payload["conservative_note"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_unknown_route_returns_404_over_http(self) -> None:
        server = self.server_module.create_server(host="127.0.0.1", port=0, quiet=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address

            with self.assertRaises(HTTPError) as context:
                urlopen(f"http://{host}:{port}/api/v1/unknown", timeout=5)

            self.assertEqual(context.exception.code, HTTPStatus.NOT_FOUND)

            payload = json.loads(context.exception.read().decode("utf-8"))
            self.assertEqual(payload["error"], "not_found")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_post_request_is_rejected(self) -> None:
        server = self.server_module.create_server(host="127.0.0.1", port=0, quiet=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address
            request = Request(
                f"http://{host}:{port}/api/v1/health",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )

            with self.assertRaises(HTTPError) as context:
                urlopen(request, timeout=5)

            self.assertEqual(context.exception.code, HTTPStatus.METHOD_NOT_ALLOWED)

            payload = json.loads(context.exception.read().decode("utf-8"))
            self.assertEqual(payload["error"], "method_not_allowed")
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["write_operations_supported"])
            self.assertFalse(payload["execution_supported"])
            self.assertFalse(payload["allows_arbitrary_command_execution"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_options_request_exposes_local_cors_headers(self) -> None:
        server = self.server_module.create_server(host="127.0.0.1", port=0, quiet=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address
            request = Request(
                f"http://{host}:{port}/api/v1/health",
                method="OPTIONS",
                headers={"Origin": "http://127.0.0.1:5173"},
            )

            with urlopen(request, timeout=5) as response:
                self.assertEqual(response.status, HTTPStatus.NO_CONTENT)
                self.assertEqual(
                    response.headers["Access-Control-Allow-Origin"],
                    "http://127.0.0.1:5173",
                )
                self.assertIn("GET", response.headers["Access-Control-Allow-Methods"])
                self.assertIn("HEAD", response.headers["Access-Control-Allow-Methods"])
                self.assertIn("OPTIONS", response.headers["Access-Control-Allow-Methods"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()