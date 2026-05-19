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


class ReplanningDecisionResponseSampleApiEndpointTests(unittest.TestCase):
    def test_health_route_advertises_replanning_decision_response_sample_endpoint(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json("/api/v1/health")

        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn(
            "/api/v1/replanning-decision-response-sample",
            payload["endpoints"],
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])

    def test_replanning_decision_response_sample_endpoint_is_available_over_http(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.get_json(
                "/api/v1/replanning-decision-response-sample"
            )

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(
            payload["schema"],
            "fieldops_lab.replanning_decision_response_sample_endpoint",
        )
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/replanning_decision_response_sample.json",
        )

    def test_replanning_decision_response_sample_route_exposes_sample_identity(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-sample"
            )

        sample = payload["replanning_decision_response_sample"]

        self.assertEqual(
            payload["sample_id"],
            "demo_replanning_decision_response_001",
        )
        self.assertEqual(
            sample["schema"],
            "fieldops_lab.replanning_decision_response_sample",
        )
        self.assertTrue(sample["read_only"])
        self.assertFalse(sample["execution_enabled"])
        self.assertEqual(sample["sample_status"], "planned_not_executed")

    def test_replanning_decision_response_sample_route_exposes_decision_without_execution(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-sample"
            )

        decision = payload["decision_summary"]

        self.assertEqual(decision["decision_status"], "not_executed_by_this_sample")
        self.assertFalse(decision["decision_enabled"])
        self.assertEqual(decision["execution_status"], "disabled")
        self.assertIn("manual_review", decision["recommendation"])
        self.assertIn("does not execute", decision["reason"])

    def test_replanning_decision_response_sample_route_exposes_delay_tradeoff(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-sample"
            )

        propagation = payload["delay_propagation"]
        tradeoff = payload["tradeoff_summary"]

        self.assertGreater(propagation["injected_delay_minutes"], 0)
        self.assertGreater(
            propagation["propagated_delay_minutes_baseline"],
            propagation["propagated_delay_minutes_candidate"],
        )
        self.assertGreater(propagation["recovered_delay_minutes"], 0)
        self.assertEqual(tradeoff["dominant_benefit"], "lower_delay_propagation")
        self.assertEqual(tradeoff["dominant_risk"], "schedule_instability")
        self.assertTrue(tradeoff["policy_comparison_ready"])
        self.assertFalse(tradeoff["statistical_claim_ready"])
        self.assertFalse(tradeoff["decision_rule_ready"])

    def test_replanning_decision_response_sample_endpoint_rejects_post(self) -> None:
        with RunningApiServer() as api:
            status, payload = api.request_json(
                "/api/v1/replanning-decision-response-sample",
                method="POST",
            )

        self.assertEqual(status, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(payload["status"], "error")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])

    def test_replanning_decision_response_sample_route_blocks_execution_claims(self) -> None:
        with RunningApiServer() as api:
            _status, payload = api.get_json(
                "/api/v1/replanning-decision-response-sample"
            )

        safety_note = payload["safety_note"].lower()
        sample_note = payload["replanning_decision_response_sample"][
            "conservative_note"
        ].lower()

        self.assertIn("static read-only sample", safety_note)
        self.assertIn("does not execute re-planning", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("mutate schedules", safety_note)
        self.assertIn("backend jobs", safety_note)
        self.assertIn("does not execute", sample_note)
        self.assertIn("does not call a solver", sample_note)
        self.assertIn("does not mutate schedules", sample_note)

    def test_server_source_keeps_replanning_decision_response_sample_read_only(self) -> None:
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

        self.assertIn("/api/v1/replanning-decision-response-sample", source)
        self.assertIn("replanning_decision_response_sample.json", source)
        self.assertIn("do_POST", source)
        self.assertIn("METHOD_NOT_ALLOWED", source)


if __name__ == "__main__":
    unittest.main()