from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from services.api.fieldops_http_server import create_server


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_SOURCE_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"


class SimulationStateApiEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_server("127.0.0.1", 0)
        self.port = int(self.server.server_address[1])
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def get_json(self, path: str) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(self.base_url + path, method="GET")

        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload

    def request_status(self, path: str, method: str) -> int:
        request = urllib.request.Request(self.base_url + path, method=method)

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status
        except urllib.error.HTTPError as error:
            try:
                return error.code
            finally:
                error.close()

    def test_simulation_state_contract_route_is_available_over_http(self) -> None:
        status, payload = self.get_json("/api/v1/simulation-state-contract")

        self.assertEqual(status, 200)
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["available"])
        self.assertEqual(
            payload["contract_path"],
            "platform/contracts/simulation_state_contract.json",
        )

        contract = payload["contract"]
        self.assertEqual(
            contract["contract"],
            "fieldops_lab_simulation_state_contract",
        )
        self.assertEqual(contract["status"], "draft")
        self.assertTrue(contract["read_only"])

    def test_simulation_state_route_exposes_conservative_execution_flags(self) -> None:
        _status, payload = self.get_json("/api/v1/simulation-state-contract")

        conservative = payload["conservative_interpretation"]

        self.assertFalse(conservative["is_visual_simulation_implemented"])
        self.assertFalse(conservative["is_real_time_map_implemented"])
        self.assertFalse(conservative["allows_browser_triggered_execution"])
        self.assertFalse(conservative["allows_arbitrary_command_execution"])
        self.assertFalse(conservative["supports_user_delay_injection_in_ui_now"])
        self.assertTrue(conservative["defines_future_safe_contract_only"])

        self.assertIn("inspection only", payload["conservative_note"])
        self.assertIn("does not start simulations", payload["conservative_note"])
        self.assertIn("does not", payload["conservative_note"])

    def test_health_route_advertises_simulation_state_contract_endpoint(self) -> None:
        status, payload = self.get_json("/api/v1/health")

        self.assertEqual(status, 200)

        route_paths = {route["path"] for route in payload["routes"]}

        self.assertIn("/api/v1/simulation-state-contract", route_paths)
        self.assertTrue(payload["simulation_state_contract"]["available"])
        self.assertEqual(
            payload["simulation_state_contract"]["path"],
            "platform/contracts/simulation_state_contract.json",
        )

    def test_simulation_state_contract_endpoint_rejects_post(self) -> None:
        status = self.request_status("/api/v1/simulation-state-contract", "POST")

        self.assertEqual(status, 405)

    def test_simulation_contract_keeps_modes_and_future_job_gated(self) -> None:
        _status, payload = self.get_json("/api/v1/simulation-state-contract")
        contract = payload["contract"]

        target_modes = contract["target_modes"]

        self.assertIn("optimization_mode", target_modes)
        self.assertIn("simulation_mode", target_modes)
        self.assertEqual(
            target_modes["simulation_mode"]["current_status"],
            "design_contract_only",
        )

        endpoint_by_id = {
            endpoint["id"]: endpoint
            for endpoint in contract["minimum_future_api_endpoints"]
        }

        self.assertEqual(
            endpoint_by_id["simulation_state_snapshot"]["method"],
            "GET",
        )
        self.assertEqual(
            endpoint_by_id["simulation_event_log"]["method"],
            "GET",
        )
        self.assertEqual(
            endpoint_by_id["controlled_simulation_job"]["status"],
            "future_gated",
        )

    def test_server_source_keeps_simulation_contract_read_only(self) -> None:
        source = SERVER_SOURCE_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("/api/v1/simulation-state-contract", source)
        self.assertNotIn("/api/v1/execute", source)
        self.assertNotIn("shell=true", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("eval(", source)


if __name__ == "__main__":
    unittest.main()