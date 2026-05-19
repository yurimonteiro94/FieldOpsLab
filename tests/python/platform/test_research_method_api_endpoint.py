from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from services.api.fieldops_http_server import create_server


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_SOURCE_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"


class ResearchMethodApiEndpointTests(unittest.TestCase):
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

    def get_json(self, path: str) -> tuple[int, dict]:
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
            return error.code

    def test_research_method_route_is_available_over_http(self) -> None:
        status, payload = self.get_json("/api/v1/research-method")

        self.assertEqual(status, 200)
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["available"])
        self.assertEqual(
            payload["contract_path"],
            "platform/contracts/research_method_contract.json",
        )
        self.assertEqual(payload["framing_path"], "platform/research_framing.md")

    def test_research_method_route_exposes_conservative_method_flags(self) -> None:
        _status, payload = self.get_json("/api/v1/research-method")

        conservative = payload["conservative_interpretation"]

        self.assertTrue(conservative["does_not_claim_final_scientific_validity"])
        self.assertTrue(conservative["fuzzy_logic_is_optional"])
        self.assertTrue(conservative["practical_equivalence_must_be_handled"])
        self.assertTrue(
            conservative["real_company_data_requires_validation_before_decision_support"]
        )

    def test_health_route_advertises_research_method_endpoint(self) -> None:
        _status, payload = self.get_json("/api/v1/health")

        route_paths = {route["path"] for route in payload["routes"]}

        self.assertIn("/api/v1/research-method", route_paths)
        self.assertTrue(payload["research_method_contract"]["available"])
        self.assertEqual(
            payload["research_method_contract"]["path"],
            "platform/contracts/research_method_contract.json",
        )

    def test_research_method_endpoint_rejects_post(self) -> None:
        status = self.request_status("/api/v1/research-method", "POST")

        self.assertEqual(status, 405)

    def test_server_source_does_not_expose_execution_route(self) -> None:
        source = SERVER_SOURCE_PATH.read_text(encoding="utf-8").lower()

        self.assertNotIn("/api/v1/execute", source)
        self.assertNotIn("shell=true", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("eval(", source)


if __name__ == "__main__":
    unittest.main()