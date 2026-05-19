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


class SimulationPlaybackControlApiEndpointTests(unittest.TestCase):
    def test_health_route_advertises_simulation_playback_control_endpoint(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/health")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("/api/v1/simulation-playback-control-contract", payload["endpoints"])
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])

    def test_simulation_playback_control_endpoint_is_available_over_http(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/simulation-playback-control-contract")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(
            payload["schema"],
            "fieldops_lab.simulation_playback_control_contract_endpoint",
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/simulation_playback_control_contract.json",
        )

    def test_simulation_playback_control_route_exposes_disabled_controls(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-playback-control-contract")

        contract = payload["simulation_playback_control_contract"]
        controls = contract["playback_controls"]

        for control_name in ["play", "pause", "step_forward", "step_backward", "reset"]:
            with self.subTest(control_name=control_name):
                self.assertTrue(controls[control_name]["visible"])
                self.assertFalse(controls[control_name]["enabled"])

        self.assertTrue(contract["speed_controls"]["visible"])
        self.assertFalse(contract["speed_controls"]["enabled"])
        self.assertTrue(contract["timeline_scrubber"]["visible"])
        self.assertFalse(contract["timeline_scrubber"]["enabled"])

    def test_simulation_playback_control_route_preserves_delay_focus(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-playback-control-contract")

        contract = payload["simulation_playback_control_contract"]
        self.assertEqual(contract["research_scope"]["dissertation_focus"], "delay_propagation")
        self.assertIn("travel_delay", contract["research_scope"]["primary_perturbations"])
        self.assertIn("service_delay", contract["research_scope"]["primary_perturbations"])
        self.assertIn(
            "delay propagation",
            contract["delay_visualization_bindings"]["dissertation_alignment"],
        )

    def test_simulation_playback_control_route_connects_current_artifacts(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-playback-control-contract")

        related = payload["simulation_playback_control_contract"]["related_contracts"]

        self.assertEqual(
            related["simulation_state_sample"],
            "platform/contracts/simulation_state_sample.json",
        )
        self.assertEqual(
            related["delay_injection_request_contract"],
            "platform/contracts/delay_injection_request_contract.json",
        )
        self.assertEqual(
            related["replanning_decision_response_sample"],
            "platform/contracts/replanning_decision_response_sample.json",
        )

    def test_simulation_playback_control_endpoint_rejects_post(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.request_json(
                "/api/v1/simulation-playback-control-contract",
                method="POST",
            )

        self.assertEqual(status, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_simulation_playback_control_route_blocks_execution_claims(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json("/api/v1/simulation-playback-control-contract")

        safety_note = payload["safety_note"].lower()
        contract_note = payload["simulation_playback_control_contract"][
            "conservative_note"
        ].lower()

        self.assertIn("does not play", safety_note)
        self.assertIn("start simulation execution", safety_note)
        self.assertIn("inject delays", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("mutate backend state", safety_note)
        self.assertIn("does not execute simulation", contract_note)
        self.assertIn("does not trigger re-planning", contract_note)
        self.assertIn("does not mutate", contract_note)

    def test_server_source_keeps_simulation_playback_control_read_only(self) -> None:
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
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, source)

        self.assertIn("/api/v1/simulation-playback-control-contract", source)
        self.assertIn("simulation_playback_control_contract.json", source)
        self.assertIn("do_POST", source)
        self.assertIn("METHOD_NOT_ALLOWED", source)


if __name__ == "__main__":
    unittest.main()