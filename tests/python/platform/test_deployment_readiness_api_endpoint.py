from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"
CONTRACT_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "deployment_readiness_contract.json"
ENDPOINT = "/api/v1/deployment-readiness-contract"


def load_server_module():
    module_name = "fieldops_http_server_for_deployment_readiness_api_test"
    spec = importlib.util.spec_from_file_location(module_name, SERVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load server module spec.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class DeploymentReadinessApiEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_source = SERVER_PATH.read_text(encoding="utf-8")
        with CONTRACT_PATH.open("r", encoding="utf-8") as file:
            cls.contract = json.load(file)

    def read_endpoint_payload(self):
        server_module = load_server_module()
        return server_module._deployment_readiness_contract_payload()

    def test_server_declares_deployment_readiness_endpoint(self):
        self.assertIn(ENDPOINT, self.server_source)
        self.assertIn("_deployment_readiness_contract_payload", self.server_source)
        self.assertIn("deployment_readiness_contract.json", self.server_source)

    def test_self_test_exposes_deployment_readiness_contract_over_http(self):
        result = subprocess.run(
            [
                "py",
                "-3",
                str(SERVER_PATH),
                "--self-test",
            ],
            cwd=REPOSITORY_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        output = result.stdout + result.stderr

        self.assertEqual(result.returncode, 0, output)
        self.assertIn(f"{ENDPOINT} 200", output)
        self.assertIn("FieldOps Lab read-only API self-test passed.", output)

    def test_endpoint_remains_read_only_contract(self):
        payload = self.read_endpoint_payload()

        self.assertEqual(payload["schema"], "fieldops_lab.deployment_readiness_contract_endpoint")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertFalse(payload["deployment_execution_enabled"])

    def test_endpoint_exposes_current_contract_file_content(self):
        payload = self.read_endpoint_payload()
        exposed_contract = payload["deployment_readiness_contract"]

        self.assertEqual(
            exposed_contract["schema"],
            "fieldops_lab.deployment_readiness_contract",
        )
        self.assertEqual(exposed_contract, self.contract)
        self.assertEqual(
            payload["artifact_path"],
            "platform/contracts/deployment_readiness_contract.json",
        )

    def test_endpoint_exposes_firebase_and_cloud_run_target_architecture(self):
        payload = self.read_endpoint_payload()
        architecture = payload["target_architecture"]

        self.assertEqual(architecture["frontend"]["platform"], "Firebase Hosting")
        self.assertEqual(architecture["api"]["platform"], "Cloud Run")
        self.assertEqual(architecture["frontend"]["source_directory"], "apps/web")
        self.assertEqual(
            architecture["api"]["source_entrypoint"],
            "services/api/fieldops_http_server.py",
        )

    def test_endpoint_keeps_solver_jobs_as_future_blocked_layer(self):
        payload = self.read_endpoint_payload()
        architecture = payload["target_architecture"]
        job_layer = architecture["future_job_execution_layer"]

        self.assertEqual(job_layer["status"], "future_required_layer")
        self.assertEqual(job_layer["preferred_solver_family"], "OR-Tools")
        self.assertEqual(job_layer["optional_solver_family"], "Gurobi")
        self.assertIn("resource limits", job_layer["required_before_enabling"])
        self.assertIn("authentication or restricted access", job_layer["required_before_enabling"])

    def test_endpoint_exposes_deployment_targets_without_claiming_live_status(self):
        payload = self.read_endpoint_payload()
        targets = {
            target["target_id"]: target
            for target in payload["deployment_targets"]
        }

        self.assertEqual(targets["local_development"]["status"], "currently_supported")
        self.assertEqual(targets["firebase_hosting_frontend"]["status"], "planned")
        self.assertEqual(targets["cloud_run_read_only_api"]["status"], "planned")
        self.assertEqual(targets["cloud_run_solver_jobs"]["status"], "future_blocked")

        current_status = payload["deployment_readiness_contract"]["current_status"]
        self.assertFalse(current_status["is_live_production_system"])
        self.assertFalse(current_status["can_be_deployed_now"])

    def test_endpoint_exposes_quality_gate_and_smoke_test_requirements(self):
        payload = self.read_endpoint_payload()
        quality = payload["quality_gate_requirements"]

        self.assertTrue(quality["local_quality_gate_must_pass_before_deploy"])
        self.assertIn("web build", " ".join(quality["required_local_checks"]).lower())
        self.assertIn("read-only api self-test", " ".join(quality["required_local_checks"]).lower())
        self.assertIn(
            "post to read-only endpoints remains blocked",
            " ".join(quality["deployment_smoke_tests_required"]).lower(),
        )

    def test_endpoint_preserves_research_alignment(self):
        payload = self.read_endpoint_payload()
        alignment = payload["research_alignment"]

        self.assertIn("dynamic TRSP/WSRP", alignment["system_goal"])
        self.assertIn("Delay propagation", alignment["dissertation_focus"])
        self.assertEqual(alignment["solver_plan"]["preferred"], "OR-Tools")
        self.assertTrue(alignment["comparative_analysis_plan"]["must_compare_multiple_policies"])
        self.assertTrue(alignment["comparative_analysis_plan"]["must_not_claim_single_run_evidence"])

    def test_endpoint_safety_note_does_not_claim_deployment_or_execution(self):
        payload = self.read_endpoint_payload()
        note = payload["safety_note"].lower()

        self.assertIn("does not deploy", note)
        self.assertIn("run solvers", note)
        self.assertIn("start jobs", note)
        self.assertIn("write files", note)
        self.assertIn("trigger backend execution", note)


if __name__ == "__main__":
    unittest.main()
