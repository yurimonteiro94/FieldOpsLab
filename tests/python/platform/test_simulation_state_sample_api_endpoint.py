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


class SimulationStateSampleApiEndpointTests(unittest.TestCase):
    def test_health_route_advertises_simulation_state_sample_endpoint(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/health")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("/api/v1/simulation-state-sample", payload["endpoints"])
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_simulation_state_sample_endpoint_is_available_over_http(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/simulation-state-sample")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(payload["schema"], "fieldops_lab.simulation_state_sample_endpoint")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/simulation_state_sample.json",
        )

    def test_simulation_state_sample_route_exposes_clock_map_and_timeline(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-state-sample")

        sample = payload["simulation_state_sample"]

        self.assertEqual(sample["schema"], "fieldops_lab.simulation_state_sample")
        self.assertEqual(sample["clock"]["simulation_id"], "demo_delay_propagation_001")
        self.assertIn("map", sample)
        self.assertIn("timeline", sample)
        self.assertGreaterEqual(len(sample["map"]["technicians"]), 2)
        self.assertGreaterEqual(len(sample["map"]["tasks"]), 5)
        self.assertGreaterEqual(len(sample["timeline"]), 5)

    def test_simulation_state_sample_route_keeps_delay_focus(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-state-sample")

        sample = payload["simulation_state_sample"]
        primary_scope = set(sample["research_scope"]["primary_dissertation_scope"])
        future_perturbations = set(sample["research_scope"]["future_platform_perturbations"])

        self.assertIn("delay_propagation", primary_scope)
        self.assertIn("travel_delay", primary_scope)
        self.assertIn("service_delay", primary_scope)
        self.assertIn("new_requests", future_perturbations)
        self.assertIn("cancellations", future_perturbations)
        self.assertIn("priority_changes", future_perturbations)

    def test_simulation_state_sample_endpoint_rejects_post(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.request_json(
                "/api/v1/simulation-state-sample",
                method="POST",
            )

        self.assertEqual(status, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_server_source_keeps_simulation_sample_read_only(self) -> None:
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

        self.assertIn("/api/v1/simulation-state-sample", source)
        self.assertIn("simulation_state_sample.json", source)
        self.assertIn("do_POST", source)
        self.assertIn("METHOD_NOT_ALLOWED", source)


if __name__ == "__main__":
    unittest.main()