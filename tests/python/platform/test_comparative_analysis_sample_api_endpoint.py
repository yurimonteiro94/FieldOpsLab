import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"
SAMPLE_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "comparative_analysis_sample.json"
ENDPOINT = "/api/v1/comparative-analysis-sample"


def load_server_module():
    module_name = "fieldops_http_server_for_comparative_analysis_sample_api_test"
    spec = importlib.util.spec_from_file_location(module_name, SERVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load fieldops_http_server module spec.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class ComparativeAnalysisSampleApiEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_source = SERVER_PATH.read_text(encoding="utf-8")
        with SAMPLE_PATH.open("r", encoding="utf-8") as file:
            cls.sample_file_payload = json.load(file)

    def read_endpoint_payload(self):
        server_module = load_server_module()
        return server_module._comparative_analysis_sample_payload()

    def test_server_declares_comparative_analysis_sample_endpoint(self):
        self.assertIn(ENDPOINT, self.server_source)
        self.assertIn("comparative_analysis_sample.json", self.server_source)
        self.assertIn("_comparative_analysis_sample_payload", self.server_source)

    def test_self_test_exposes_comparative_analysis_sample_over_http(self):
        result = subprocess.run(
            [sys.executable, str(SERVER_PATH), "--self-test"],
            cwd=REPOSITORY_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        output = result.stdout
        self.assertEqual(result.returncode, 0, output)
        self.assertIn(f"{ENDPOINT} 200", output)

    def test_endpoint_remains_read_only_contract(self):
        payload = self.read_endpoint_payload()

        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])

    def test_endpoint_exposes_current_sample_file_content(self):
        payload = self.read_endpoint_payload()

        self.assertEqual(payload["comparative_analysis_sample"], self.sample_file_payload)
        self.assertEqual(payload["artifact_path"], "platform/contracts/comparative_analysis_sample.json")
        self.assertEqual(payload["sample_id"], self.sample_file_payload["sample_id"])

    def test_endpoint_preserves_delay_propagation_focus(self):
        payload = self.read_endpoint_payload()
        alignment = payload["research_alignment"]

        self.assertIn("Delay propagation", alignment["dissertation_focus"])
        self.assertIn("TRSP", alignment["problem_family"])
        self.assertIn("WSRP", alignment["problem_family"])

    def test_endpoint_supports_policy_comparison_and_statistics(self):
        payload = self.read_endpoint_payload()

        self.assertGreaterEqual(len(payload["candidate_policies"]), 4)
        self.assertGreaterEqual(len(payload["sample_results"]), 4)
        self.assertTrue(payload["statistical_analysis_plan"]["blocks_single_run_claims"])

    def test_endpoint_keeps_ortools_as_future_solver_backed_policy(self):
        payload = self.read_endpoint_payload()
        policies = {
            policy["policy_id"]: policy
            for policy in payload["candidate_policies"]
        }

        self.assertIn("ortools_vrp_reoptimization", policies)
        self.assertEqual(
            policies["ortools_vrp_reoptimization"]["preferred_solver_family"],
            "OR-Tools",
        )
        self.assertIn(
            "future",
            policies["ortools_vrp_reoptimization"]["current_platform_status"],
        )

    def test_endpoint_does_not_claim_runtime_execution(self):
        payload = self.read_endpoint_payload()
        runtime_status = payload["runtime_status"]
        safety_note = payload["safety_note"].lower()

        self.assertFalse(runtime_status["is_real_experiment_result"])
        self.assertTrue(runtime_status["is_static_sample"])
        self.assertIn("does not execute experiments", safety_note)
        self.assertIn("run solvers", safety_note)
        self.assertIn("real experimental evidence", safety_note)


if __name__ == "__main__":
    unittest.main()
