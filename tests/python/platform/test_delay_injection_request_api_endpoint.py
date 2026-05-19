from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path
from typing import Any

from services.api.fieldops_http_server import _create_server


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_SOURCE_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"


class RunningApiServer:
    def __enter__(self) -> "RunningApiServer":
        self.server = _create_server("127.0.0.1", 0)
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def get_json(self, path: str) -> tuple[int, dict[str, Any]]:
        with urllib.request.urlopen(self.base_url + path, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload

    def request_json(self, path: str, method: str) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(self.base_url + path, method=method)

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, payload
        except urllib.error.HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
            finally:
                error.close()

            return error.code, payload


class DelayInjectionRequestApiEndpointTests(unittest.TestCase):
    def test_health_route_advertises_delay_injection_contract_endpoint(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/health")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("/api/v1/delay-injection-request-contract", payload["endpoints"])
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])

    def test_delay_injection_contract_endpoint_is_available_over_http(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/delay-injection-request-contract")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(
            payload["schema"],
            "fieldops_lab.delay_injection_request_contract_endpoint",
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/delay_injection_request_contract.json",
        )

    def test_delay_injection_contract_route_exposes_request_shape(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/delay-injection-request-contract")

        contract = payload["delay_injection_request_contract"]
        request_shape = contract["request_shape"]

        self.assertEqual(contract["contract"], "delay_injection_request_contract")
        self.assertEqual(contract["status"], "planned_disabled")
        self.assertTrue(contract["read_only"])
        self.assertFalse(contract["execution_enabled"])

        self.assertIn("event_type", request_shape)
        self.assertIn("target_type", request_shape)
        self.assertIn("delay_minutes", request_shape)
        self.assertEqual(
            request_shape["event_type"]["allowed_values"],
            ["travel_delay", "service_delay"],
        )
        self.assertEqual(
            request_shape["target_type"]["allowed_values"],
            ["technician", "task", "route_leg"],
        )

    def test_delay_injection_contract_route_keeps_planned_endpoint_disabled(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/delay-injection-request-contract")

        planned_endpoint = payload["planned_endpoint"]

        self.assertEqual(planned_endpoint["method"], "POST")
        self.assertEqual(
            planned_endpoint["path"],
            "/api/v1/simulation-runs/{simulation_run_id}/delay-events",
        )
        self.assertEqual(planned_endpoint["status"], "planned_not_enabled")
        self.assertFalse(planned_endpoint["execution_enabled"])
        self.assertTrue(planned_endpoint["requires_future_authentication"])
        self.assertTrue(planned_endpoint["requires_future_server_side_validation"])
        self.assertTrue(planned_endpoint["requires_future_audit_log"])

    def test_delay_injection_contract_endpoint_rejects_post(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.request_json(
                "/api/v1/delay-injection-request-contract",
                method="POST",
            )

        self.assertEqual(status, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_delay_injection_contract_route_blocks_execution_claims(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/delay-injection-request-contract")

        safety_note = payload["safety_note"].lower()
        contract_note = payload["delay_injection_request_contract"]["conservative_note"].lower()

        self.assertIn("does not inject delays", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("backend jobs", safety_note)

        self.assertIn("does not enable delay injection", contract_note)
        self.assertIn("simulation execution", contract_note)
        self.assertIn("solver execution", contract_note)
        self.assertIn("write operations", contract_note)

    def test_server_source_keeps_delay_injection_contract_read_only(self) -> None:
        source = SERVER_SOURCE_PATH.read_text(encoding="utf-8")

        forbidden_fragments = [
            "subprocess",
            "os.system",
            "Popen",
            "exec(",
            "eval(",
            "shell=True",
        ]

        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, source)

        self.assertIn("/api/v1/delay-injection-request-contract", source)
        self.assertIn("delay_injection_request_contract.json", source)
        self.assertIn("do_POST", source)
        self.assertIn("METHOD_NOT_ALLOWED", source)


if __name__ == "__main__":
    unittest.main()