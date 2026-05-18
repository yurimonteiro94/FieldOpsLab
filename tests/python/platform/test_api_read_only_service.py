### `tests\python\platform\test_api_read_only_service.py`

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
API_PATH = PROJECT_ROOT / "services" / "api" / "fieldops_api.py"


def load_api_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fieldops_api", API_PATH)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load API module from {API_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class FieldOpsReadOnlyApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = load_api_module()

    def test_api_file_exists(self) -> None:
        self.assertTrue(API_PATH.exists())

    def test_health_endpoint_exposes_read_only_status(self) -> None:
        status_code, payload = self.api.build_response("/api/v1/health")

        self.assertEqual(status_code, 200)
        self.assertEqual(payload["service"], "fieldops_lab_api")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mode"], "read_only")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["allows_arbitrary_command_execution"])

    def test_routes_do_not_include_execution_endpoint(self) -> None:
        routes = self.api.routes()
        paths = {route["path"] for route in routes}

        self.assertIn("/api/v1/health", paths)
        self.assertIn("/api/v1/project-status", paths)
        self.assertIn("/api/v1/reports", paths)
        self.assertIn("/api/v1/experimental-design-matrix", paths)
        self.assertNotIn("/api/v1/execute", paths)
        self.assertNotIn("/api/v1/run-command", paths)

    def test_project_status_endpoint_reads_existing_report(self) -> None:
        status_code, payload = self.api.build_response("/api/v1/project-status")

        self.assertEqual(status_code, 200)
        self.assertEqual(payload["report"], "project_status")
        self.assertTrue(payload["source"]["exists"])
        self.assertTrue(payload["source"]["loaded"])
        self.assertIn("summary_metrics", payload)
        self.assertIn("engineering_status", payload["summary_metrics"])
        self.assertIn("does not prove scientific validity", payload["conservative_note"])

    def test_reports_endpoint_lists_known_report_artifacts(self) -> None:
        status_code, payload = self.api.build_response("/api/v1/reports")

        self.assertEqual(status_code, 200)
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["execution_supported"])

        report_ids = {report["id"] for report in payload["reports"]}

        self.assertIn("project_status", report_ids)
        self.assertIn("scientific_validation_plan", report_ids)
        self.assertIn("experimental_design_matrix", report_ids)

    def test_experimental_design_endpoint_exposes_summary(self) -> None:
        status_code, payload = self.api.build_response("/api/v1/experimental-design-matrix")

        self.assertEqual(status_code, 200)
        self.assertEqual(payload["report"], "experimental_design_matrix")
        self.assertTrue(payload["source"]["exists"])
        self.assertTrue(payload["source"]["loaded"])

        summary: dict[str, Any] = payload["summary"]

        self.assertGreater(summary["experiment_count"], 0)
        self.assertGreater(summary["scenario_count"], 0)
        self.assertGreater(summary["replication_count"], 0)
        self.assertTrue(summary["reproducible_from_explicit_factors"])

    def test_unknown_route_returns_404(self) -> None:
        status_code, payload = self.api.build_response("/api/v1/unknown")

        self.assertEqual(status_code, 404)
        self.assertEqual(payload["error"], "not_found")

    def test_api_source_does_not_use_unsafe_execution_primitives(self) -> None:
        source = API_PATH.read_text(encoding="utf-8").lower()

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


if __name__ == "__main__":
    unittest.main()