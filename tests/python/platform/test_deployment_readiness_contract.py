import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "deployment_readiness_contract.json"


class DeploymentReadinessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONTRACT_PATH.open("r", encoding="utf-8") as file:
            cls.contract = json.load(file)

    def test_contract_is_valid_read_only_and_disabled(self):
        self.assertEqual(
            self.contract["schema"],
            "fieldops_lab.deployment_readiness_contract",
        )
        self.assertTrue(self.contract["read_only"])
        self.assertFalse(self.contract["execution_enabled"])
        self.assertFalse(self.contract["write_operations_supported"])
        self.assertFalse(self.contract["browser_triggered_execution_enabled"])
        self.assertFalse(self.contract["deployment_execution_enabled"])

    def test_current_status_is_honest_about_not_being_live(self):
        current_status = self.contract["current_status"]

        self.assertEqual(current_status["status"], "contract_only")
        self.assertFalse(current_status["is_live_production_system"])
        self.assertFalse(current_status["can_be_deployed_now"])
        self.assertIn("does not mean the site is already hosted", current_status["honesty_note"])

    def test_target_architecture_uses_firebase_and_cloud_run(self):
        architecture = self.contract["target_architecture"]

        self.assertEqual(architecture["frontend"]["platform"], "Firebase Hosting")
        self.assertEqual(architecture["api"]["platform"], "Cloud Run")
        self.assertEqual(architecture["frontend"]["source_directory"], "apps/web")
        self.assertEqual(
            architecture["api"]["source_entrypoint"],
            "services/api/fieldops_http_server.py",
        )

    def test_frontend_must_not_run_solvers_or_mutate_backend_state(self):
        frontend = self.contract["target_architecture"]["frontend"]
        forbidden = " ".join(frontend["must_not_do"]).lower()

        self.assertIn("run solvers", forbidden)
        self.assertIn("mutate backend state", forbidden)
        self.assertIn("static samples", forbidden)

    def test_api_remains_read_only_until_controlled_jobs_exist(self):
        api = self.contract["target_architecture"]["api"]
        forbidden = " ".join(api["must_not_do_now"]).lower()

        self.assertEqual(api["current_api_mode"], "read_only")
        self.assertIn("unauthenticated endpoints", forbidden)
        self.assertIn("write experiment outputs", forbidden)
        self.assertIn("destructive operations", forbidden)

    def test_future_job_execution_layer_prefers_ortools(self):
        job_layer = self.contract["target_architecture"]["future_job_execution_layer"]

        self.assertEqual(job_layer["status"], "future_required_layer")
        self.assertEqual(job_layer["preferred_solver_family"], "OR-Tools")
        self.assertEqual(job_layer["optional_solver_family"], "Gurobi")
        self.assertIn("job request contract", job_layer["required_before_enabling"])
        self.assertIn("resource limits", job_layer["required_before_enabling"])
        self.assertIn("authentication or restricted access", job_layer["required_before_enabling"])

    def test_deployment_targets_cover_local_firebase_cloud_run_and_solver_jobs(self):
        targets = {
            target["target_id"]: target
            for target in self.contract["deployment_targets"]
        }

        self.assertIn("local_development", targets)
        self.assertIn("firebase_hosting_frontend", targets)
        self.assertIn("cloud_run_read_only_api", targets)
        self.assertIn("cloud_run_solver_jobs", targets)

        self.assertEqual(targets["local_development"]["status"], "currently_supported")
        self.assertEqual(targets["firebase_hosting_frontend"]["status"], "planned")
        self.assertEqual(targets["cloud_run_read_only_api"]["status"], "planned")
        self.assertEqual(targets["cloud_run_solver_jobs"]["status"], "future_blocked")

    def test_environment_variables_include_frontend_api_url_and_cloud_run_port(self):
        variables = {
            variable["name"]: variable
            for variable in self.contract["required_environment_variables"]
        }

        self.assertIn("FIELDOPS_API_BASE_URL", variables)
        self.assertIn("PORT", variables)
        self.assertIn("FIELDOPS_RUNTIME_MODE", variables)
        self.assertEqual(variables["FIELDOPS_API_BASE_URL"]["required_for"], "frontend_production")
        self.assertEqual(variables["PORT"]["required_for"], "cloud_run_api")

    def test_quality_gate_requires_local_checks_before_deploy(self):
        quality = self.contract["quality_gate_requirements"]
        checks = " ".join(quality["required_local_checks"]).lower()
        smoke_tests = " ".join(quality["deployment_smoke_tests_required"]).lower()

        self.assertTrue(quality["local_quality_gate_must_pass_before_deploy"])
        self.assertIn("c++ tests", checks)
        self.assertIn("python unit tests", checks)
        self.assertIn("web build", checks)
        self.assertIn("web unit tests", checks)
        self.assertIn("read-only api self-test", checks)
        self.assertIn("api health endpoint returns 200", smoke_tests)
        self.assertIn("post to read-only endpoints remains blocked", smoke_tests)

    def test_research_alignment_keeps_scope_and_solver_plan_clear(self):
        alignment = self.contract["research_alignment"]
        solver_plan = alignment["solver_plan"]
        comparative_plan = alignment["comparative_analysis_plan"]

        self.assertIn("dynamic TRSP/WSRP", alignment["system_goal"])
        self.assertIn("Delay propagation", alignment["dissertation_focus"])
        self.assertEqual(solver_plan["preferred"], "OR-Tools")
        self.assertEqual(solver_plan["optional"], "Gurobi")
        self.assertIn("threshold_delay_replanning", solver_plan["current_internal_baselines"])
        self.assertTrue(comparative_plan["must_compare_multiple_policies"])
        self.assertTrue(comparative_plan["must_use_controlled_experiments"])
        self.assertTrue(comparative_plan["must_not_claim_single_run_evidence"])

    def test_safety_requirements_are_conservative(self):
        safety = self.contract["safety_requirements"]
        forbidden = " ".join(safety["forbidden_current_behaviors"]).lower()

        self.assertEqual(safety["default_public_mode"], "read_only")
        self.assertTrue(safety["require_authentication_before_write_or_execution"])
        self.assertTrue(safety["require_job_queue_before_solver_execution"])
        self.assertTrue(safety["require_resource_limits_before_solver_execution"])
        self.assertTrue(safety["require_cost_controls_before_solver_execution"])
        self.assertIn("browser-triggered solver execution", forbidden)
        self.assertIn("public unauthenticated experiment execution", forbidden)
        self.assertIn("destructive operations", forbidden)

    def test_next_steps_include_api_web_firebase_cloud_run_and_smoke_tests(self):
        next_steps = {
            step["title"].lower()
            for step in self.contract["next_implementation_steps"]
        }

        self.assertTrue(any("read-only api" in step for step in next_steps))
        self.assertTrue(any("web ui" in step for step in next_steps))
        self.assertTrue(any("firebase hosting" in step for step in next_steps))
        self.assertTrue(any("cloud run" in step for step in next_steps))
        self.assertTrue(any("smoke test" in step for step in next_steps))

    def test_conservative_note_separates_local_correctness_from_real_deploy(self):
        note = self.contract["conservative_note"].lower()

        self.assertIn("local correctness", note)
        self.assertIn("deployment readiness", note)
        self.assertIn("real runtime execution", note)
        self.assertIn("deployed site", note)
        self.assertIn("production solver-backed experiment engine", note)


if __name__ == "__main__":
    unittest.main()