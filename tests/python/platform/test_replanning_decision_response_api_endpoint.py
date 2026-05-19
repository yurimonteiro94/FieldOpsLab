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


class ReplanningDecisionResponseApiEndpointTests(unittest.TestCase):
    def test_health_route_advertises_replanning_decision_response_contract_endpoint(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/health")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn(
            "/api/v1/replanning-decision-response-contract",
            payload["endpoints"],
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])

    def test_replanning_decision_response_contract_endpoint_is_available_over_http(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json(
                "/api/v1/replanning-decision-response-contract"
            )

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(
            payload["schema"],
            "fieldops_lab.replanning_decision_response_contract_endpoint",
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/replanning_decision_response_contract.json",
        )

    def test_replanning_decision_response_route_exposes_future_endpoint_as_disabled(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-contract"
            )

        future_endpoint = payload["future_endpoint"]

        self.assertEqual(future_endpoint["method"], "POST")
        self.assertEqual(future_endpoint["path"], "/api/v1/replanning-decisions")
        self.assertFalse(future_endpoint["enabled"])
        self.assertIn("intentionally disabled", future_endpoint["reason"].lower())

    def test_replanning_decision_response_route_exposes_core_response_sections(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-contract"
            )

        contract = payload["replanning_decision_response_contract"]
        response_shape = contract["response_shape"]

        self.assertEqual(
            contract["contract_name"],
            "replanning_decision_response_contract",
        )
        self.assertEqual(contract["status"], "planned_read_only_contract")
        self.assertFalse(contract["enabled"])
        self.assertFalse(contract["execution_enabled"])
        self.assertFalse(contract["current_endpoint_enabled"])

        expected_sections = {
            "decision_id",
            "status",
            "selected_policy",
            "feasibility",
            "performance_delta",
            "stability_delta",
            "computational_cost",
            "delay_propagation",
            "explanation",
        }

        self.assertTrue(expected_sections.issubset(response_shape.keys()))
        self.assertIn("objective_delta", response_shape["performance_delta"]["fields"])
        self.assertIn("stability_score", response_shape["stability_delta"]["fields"])
        self.assertIn("solver_time_ms", response_shape["computational_cost"]["fields"])
        self.assertIn("affected_tasks_count", response_shape["delay_propagation"]["fields"])

    def test_replanning_decision_response_route_connects_to_delay_and_simulation_contracts(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-contract"
            )

        contract = payload["replanning_decision_response_contract"]
        related_contracts = set(contract["related_contracts"])
        input_references = contract["input_references"]

        self.assertIn("simulation_state_contract", related_contracts)
        self.assertIn("simulation_state_sample", related_contracts)
        self.assertIn("delay_injection_request_contract", related_contracts)
        self.assertIn("simulation_id", input_references)
        self.assertIn("delay_injection_request_id", input_references)
        self.assertIn("policy_id", input_references)
        self.assertIn("baseline_solution_id", input_references)

    def test_replanning_decision_response_endpoint_rejects_post(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.request_json(
                "/api/v1/replanning-decision-response-contract",
                method="POST",
            )

        self.assertEqual(status, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_replanning_decision_response_route_blocks_execution_claims(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-contract"
            )

        safety_note = payload["safety_note"].lower()
        contract_note = payload["replanning_decision_response_contract"][
            "conservative_note"
        ].lower()

        self.assertIn("does not execute re-planning decisions", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("start optimization", safety_note)
        self.assertIn("backend jobs", safety_note)
        self.assertIn("only defines the future response shape", contract_note)
        self.assertIn("does not execute", contract_note)
        self.assertIn("solvers", contract_note)
        self.assertIn("optimization", contract_note)
        self.assertIn("simulation", contract_note)

    def test_server_source_keeps_replanning_decision_response_contract_read_only(self) -> None:
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

        self.assertIn("/api/v1/replanning-decision-response-contract", source)
        self.assertIn("replanning_decision_response_contract.json", source)
        self.assertIn("do_POST", source)
        self.assertIn("METHOD_NOT_ALLOWED", source)


if __name__ == "__main__":
    unittest.main()