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


class ReportDetailApiEndpointTests(unittest.TestCase):
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

    def request_json_with_error(self, path: str) -> tuple[int, dict]:
        request = urllib.request.Request(self.base_url + path, method="GET")

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, payload
        except urllib.error.HTTPError as error:
            payload = json.loads(error.read().decode("utf-8"))
            return error.code, payload

    def request_status(self, path: str, method: str) -> int:
        request = urllib.request.Request(self.base_url + path, method=method)

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status
        except urllib.error.HTTPError as error:
            return error.code

    def test_health_route_advertises_report_detail_endpoint(self) -> None:
        status, payload = self.get_json("/api/v1/health")

        self.assertEqual(status, 200)

        route_paths = {route["path"] for route in payload["routes"]}

        self.assertIn("/api/v1/reports", route_paths)
        self.assertIn("/api/v1/reports/{id}", route_paths)

    def test_reports_catalog_exposes_campaign_outputs(self) -> None:
        status, payload = self.get_json("/api/v1/reports")

        self.assertEqual(status, 200)
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_supported"])
        self.assertFalse(payload["write_operations_supported"])

        report_ids = {report["id"] for report in payload["reports"]}

        self.assertIn("experiment_campaign_plan", report_ids)
        self.assertIn("campaign_index", report_ids)
        self.assertIn("campaign_decision_matrix", report_ids)
        self.assertIn("campaign_perturbation_plan_index", report_ids)
        self.assertIn("campaign_execution_index", report_ids)
        self.assertIn("campaign_result_summary", report_ids)
        self.assertIn("campaign_ranking_profile_sensitivity", report_ids)
        self.assertIn("campaign_final_diagnostic_report", report_ids)
        self.assertIn("full_campaign_pipeline", report_ids)
        self.assertIn("policy_trigger_behavior_audit", report_ids)

    def test_report_detail_route_returns_known_project_status_report(self) -> None:
        status, payload = self.get_json("/api/v1/reports/project_status")

        self.assertEqual(status, 200)
        self.assertEqual(payload["report"], "report_detail")
        self.assertEqual(payload["id"], "project_status")
        self.assertEqual(payload["title"], "Project status")
        self.assertEqual(payload["category"], "engineering")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_supported"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertTrue(payload["available"])

        artifact = payload["artifact"]
        self.assertEqual(
            artifact["path"],
            "analysis/reports/project_status_report.json",
        )
        self.assertTrue(artifact["exists"])
        self.assertTrue(artifact["loaded"])
        self.assertIsInstance(artifact["data"], dict)

    def test_report_detail_route_returns_campaign_final_diagnostic_report(self) -> None:
        status, payload = self.get_json(
            "/api/v1/reports/campaign_final_diagnostic_report"
        )

        self.assertEqual(status, 200)
        self.assertEqual(payload["report"], "report_detail")
        self.assertEqual(payload["id"], "campaign_final_diagnostic_report")
        self.assertEqual(payload["title"], "Campaign final diagnostic report")
        self.assertEqual(payload["category"], "campaign_analysis")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_supported"])
        self.assertFalse(payload["write_operations_supported"])

        self.assertEqual(
            payload["artifact"]["path"],
            "analysis/reports/campaign_final_diagnostic_report.json",
        )
        self.assertTrue(payload["artifact"]["exists"])
        self.assertTrue(payload["artifact"]["loaded"])

        self.assertEqual(
            payload["markdown"]["path"],
            "analysis/reports/campaign_final_diagnostic_report.md",
        )
        self.assertTrue(payload["markdown"]["exists"])
        self.assertTrue(payload["markdown"]["loaded"])

        self.assertEqual(
            payload["quality_check"]["path"],
            "analysis/reports/campaign_final_diagnostic_report_quality_check.json",
        )
        self.assertTrue(payload["quality_check"]["exists"])
        self.assertTrue(payload["quality_check"]["loaded"])

    def test_report_detail_route_returns_full_pipeline_manifest(self) -> None:
        status, payload = self.get_json("/api/v1/reports/full_campaign_pipeline")

        self.assertEqual(status, 200)
        self.assertEqual(payload["id"], "full_campaign_pipeline")
        self.assertEqual(payload["category"], "pipeline")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_supported"])

        self.assertEqual(
            payload["artifact"]["path"],
            "analysis/reports/full_campaign_pipeline_manifest.json",
        )
        self.assertTrue(payload["artifact"]["exists"])
        self.assertTrue(payload["artifact"]["loaded"])

        self.assertEqual(
            payload["markdown"]["path"],
            "analysis/reports/full_campaign_pipeline_report.md",
        )
        self.assertTrue(payload["markdown"]["exists"])
        self.assertTrue(payload["markdown"]["loaded"])

    def test_report_detail_route_exposes_markdown_and_quality_check(self) -> None:
        _status, payload = self.get_json("/api/v1/reports/project_status")

        markdown = payload["markdown"]
        quality_check = payload["quality_check"]

        self.assertEqual(
            markdown["path"],
            "analysis/reports/project_status_report.md",
        )
        self.assertTrue(markdown["exists"])
        self.assertTrue(markdown["loaded"])
        self.assertIsInstance(markdown["text"], str)

        self.assertEqual(
            quality_check["path"],
            "analysis/reports/project_status_quality_check.json",
        )
        self.assertTrue(quality_check["exists"])
        self.assertTrue(quality_check["loaded"])
        self.assertIsInstance(quality_check["data"], dict)

        self.assertIn("inspection only", payload["conservative_note"])
        self.assertIn("does not execute", payload["conservative_note"])

    def test_unknown_report_detail_returns_404_without_file_access(self) -> None:
        status, payload = self.request_json_with_error(
            "/api/v1/reports/unknown_report"
        )

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "report_not_found")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["available"])
        self.assertIn("project_status", payload["known_report_ids"])
        self.assertIn("campaign_final_diagnostic_report", payload["known_report_ids"])

    def test_nested_report_path_is_rejected(self) -> None:
        status, payload = self.request_json_with_error(
            "/api/v1/reports/../project_status"
        )

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "report_not_found")
        self.assertTrue(payload["read_only"])

    def test_report_detail_endpoint_rejects_post(self) -> None:
        status = self.request_status("/api/v1/reports/project_status", "POST")

        self.assertEqual(status, 405)

    def test_server_source_keeps_report_detail_read_only(self) -> None:
        source = SERVER_SOURCE_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("/api/v1/reports/{id}", source)
        self.assertIn("campaign_final_diagnostic_report", source)
        self.assertNotIn("/api/v1/execute", source)
        self.assertNotIn("shell=true", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("eval(", source)


if __name__ == "__main__":
    unittest.main()