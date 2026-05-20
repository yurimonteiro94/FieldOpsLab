import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = ROOT / "services" / "api" / "fieldops_http_server.py"
CONTRACT_PATH = ROOT / "platform" / "contracts" / "solver_integration_contract.json"
ENDPOINT = "/api/v1/solver-integration-contract"


class SolverIntegrationApiEndpointTests(unittest.TestCase):
    def setUp(self):
        self.server_source = SERVER_PATH.read_text(encoding="utf-8")
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_server_declares_solver_integration_endpoint(self):
        self.assertIn(ENDPOINT, self.server_source)
        self.assertIn("_solver_integration_contract_payload", self.server_source)
        self.assertIn("solver_integration_contract.json", self.server_source)

    def test_self_test_exposes_solver_integration_contract_over_http(self):
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

    def test_endpoint_remains_read_only_contract(self):
        self.assertTrue(self.contract["read_only"])
        self.assertFalse(self.contract["execution_enabled"])
        self.assertFalse(self.contract["browser_execution_enabled"])
        self.assertFalse(self.contract["operational_use_enabled"])

    def test_ortools_is_preferred_without_claiming_execution(self):
        strategy = self.contract["solver_strategy"]
        conservative_note = self.contract["conservative_note"]

        self.assertEqual(strategy["preferred_solver_family"], "OR-Tools")
        self.assertIn("does not execute OR-Tools", conservative_note)

    def test_gurobi_remains_optional(self):
        candidates = {
            candidate["id"]: candidate
            for candidate in self.contract["solver_candidates"]
        }

        self.assertIn("gurobi_mip_adapter", candidates)
        self.assertEqual(candidates["gurobi_mip_adapter"]["priority"], "optional")
        self.assertFalse(candidates["gurobi_mip_adapter"]["enabled_now"])

    def test_comparative_statistics_are_future_experimental_layer(self):
        output_contract = self.contract["adapter_boundary"]["output_contract"]
        alignment = self.contract["research_alignment"]

        self.assertIn("delay_propagation_summary", output_contract["required_sections"])
        self.assertIn("route_stability_summary", output_contract["required_sections"])
        self.assertIn("computational_cost", output_contract["required_sections"])
        self.assertIn("statistical", alignment["statistical_analysis_role"])

    def test_browser_solver_execution_is_blocked(self):
        boundary = self.contract["adapter_boundary"]["execution_boundary"]

        self.assertTrue(boundary["planned_backend_only"])
        self.assertTrue(boundary["browser_must_not_trigger_solver_directly"])
        self.assertTrue(boundary["future_execution_requires_api_gate"])

    def test_safety_requirements_are_conservative(self):
        safety_text = " ".join(self.contract["safety_requirements"])

        self.assertIn("Do not require Gurobi", safety_text)
        self.assertIn("Do not hide licensing or deployment constraints", safety_text)
        self.assertIn("Do not expose solver execution from the browser", safety_text)


if __name__ == "__main__":
    unittest.main()
