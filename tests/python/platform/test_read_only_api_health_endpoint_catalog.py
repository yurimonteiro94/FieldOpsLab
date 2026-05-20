from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"


def load_server_module() -> Any:
    module_name = "fieldops_http_server_health_catalog_test"
    spec = importlib.util.spec_from_file_location(module_name, SERVER_PATH)

    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load fieldops_http_server.py module spec.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class ReadOnlyApiHealthEndpointCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server_module = load_server_module()
        cls.payload = cls.server_module._health_payload()
        cls.endpoints = cls.payload["endpoints"]

    def test_health_payload_remains_read_only_and_execution_disabled(self) -> None:
        self.assertEqual(self.payload["status"], "ok")
        self.assertIs(self.payload["read_only"], True)
        self.assertIs(self.payload["execution_enabled"], False)
        self.assertIs(self.payload["write_operations_supported"], False)
        self.assertIs(self.payload["browser_triggered_execution_enabled"], False)

    def test_endpoint_catalog_contains_only_strings(self) -> None:
        self.assertTrue(self.endpoints)
        self.assertTrue(
            all(isinstance(endpoint, str) for endpoint in self.endpoints),
            self.endpoints,
        )

    def test_endpoint_catalog_has_no_duplicates(self) -> None:
        self.assertEqual(len(self.endpoints), len(set(self.endpoints)))

    def test_endpoint_catalog_exposes_current_read_only_contracts(self) -> None:
        required_endpoints = {
            "/api/v1/health",
            "/api/v1/project-status",
            "/api/v1/reports",
            "/api/v1/reports/{report_id}",
            "/api/v1/experimental-design-matrix",
            "/api/v1/research-method",
            "/api/v1/simulation-state-contract",
            "/api/v1/simulation-state-sample",
            "/api/v1/delay-injection-request-contract",
            "/api/v1/replanning-decision-response-contract",
            "/api/v1/replanning-decision-response-sample",
            "/api/v1/simulation-playback-control-contract",
            "/api/v1/simulation-playback-state-sample",
            "/api/v1/solver-integration-contract",
            "/api/v1/comparative-analysis-contract",
            "/api/v1/comparative-analysis-sample",
            "/api/v1/deployment-readiness-contract",
        }

        self.assertTrue(required_endpoints.issubset(set(self.endpoints)))

    def test_simulation_playback_state_sample_is_declared_once(self) -> None:
        self.assertEqual(
            self.endpoints.count("/api/v1/simulation-playback-state-sample"),
            1,
        )


if __name__ == "__main__":
    unittest.main()