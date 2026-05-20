from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import threading
import unittest
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = ROOT / "services" / "api" / "fieldops_http_server.py"
CONTRACT_PATH = ROOT / "platform" / "contracts" / "comparative_analysis_contract.json"
ENDPOINT = "/api/v1/comparative-analysis-contract"


def load_server_module():
    spec = importlib.util.spec_from_file_location("fieldops_http_server", SERVER_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())

    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)

    return str(value)


class ComparativeAnalysisApiEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server_source = SERVER_PATH.read_text(encoding="utf-8")
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def read_endpoint_payload(self) -> dict[str, Any]:
        server_module = load_server_module()
        server = server_module._create_server("127.0.0.1", 0)
        host, port = server.server_address
        base_url = f"http://{host}:{port}"

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with urllib.request.urlopen(base_url + ENDPOINT, timeout=10) as response:
                self.assertEqual(response.status, 200)
                return json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_server_declares_comparative_analysis_endpoint(self) -> None:
        self.assertIn(ENDPOINT, self.server_source)
        self.assertIn("comparative_analysis_contract.json", self.server_source)
        self.assertIn("_comparative_analysis_contract_payload", self.server_source)

    def test_self_test_exposes_comparative_analysis_contract_over_http(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SERVER_PATH), "--self-test"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        output = result.stdout
        self.assertEqual(result.returncode, 0, output)
        self.assertIn(f"{ENDPOINT} 200", output)

    def test_endpoint_remains_read_only_contract(self) -> None:
        payload = self.read_endpoint_payload()

        self.assertIs(payload["read_only"], True)
        self.assertIs(payload["execution_enabled"], False)
        self.assertIs(payload["write_operations_supported"], False)
        self.assertIs(payload["browser_triggered_execution_enabled"], False)

    def test_endpoint_exposes_current_contract_file_content(self) -> None:
        payload = self.read_endpoint_payload()

        self.assertEqual(payload["comparative_analysis_contract"], self.contract)
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/comparative_analysis_contract.json",
        )

    def test_endpoint_preserves_delay_propagation_focus(self) -> None:
        payload = self.read_endpoint_payload()
        text = flatten_text(payload).lower()

        self.assertIn("delay propagation", text)
        self.assertIn("delay", text)

    def test_endpoint_supports_policy_comparison_and_statistics(self) -> None:
        payload = self.read_endpoint_payload()
        text = flatten_text(payload).lower()

        self.assertIn("policy", text)
        self.assertIn("comparison", text)
        self.assertIn("statistical", text)
        self.assertIn("paired", text)

    def test_endpoint_keeps_solver_integration_as_future_layer(self) -> None:
        payload = self.read_endpoint_payload()
        text = flatten_text(payload).lower()

        self.assertIn("or-tools", text)
        self.assertIn("solver", text)
        self.assertIn("future", text)

    def test_endpoint_does_not_claim_runtime_execution(self) -> None:
        payload = self.read_endpoint_payload()
        safety_note = payload["safety_note"].lower()

        self.assertIn("does not execute", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("compute statistical tests", safety_note)
        self.assertIn("trigger backend jobs", safety_note)


if __name__ == "__main__":
    unittest.main()
