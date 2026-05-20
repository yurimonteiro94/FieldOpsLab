import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "platform" / "contracts" / "solver_integration_contract.json"


class SolverIntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_valid_read_only_and_disabled(self):
        self.assertEqual(self.contract["contract_id"], "fieldops_solver_integration_contract_v1")
        self.assertEqual(self.contract["status"], "read_only_contract")
        self.assertTrue(self.contract["read_only"])
        self.assertFalse(self.contract["execution_enabled"])
        self.assertFalse(self.contract["browser_execution_enabled"])
        self.assertFalse(self.contract["operational_use_enabled"])

    def test_ortools_is_preferred_solver_family(self):
        strategy = self.contract["solver_strategy"]

        self.assertEqual(strategy["preferred_solver_family"], "OR-Tools")
        self.assertIn("C++", strategy["preferred_solver_reason"])
        self.assertIn("open", self._candidate_by_id("ortools_routing_or_cp_sat_adapter")["license_dependency"])

    def test_gurobi_is_optional_and_not_required(self):
        strategy = self.contract["solver_strategy"]
        gurobi = self._candidate_by_id("gurobi_mip_adapter")

        self.assertEqual(strategy["gurobi_role"], "optional_future_benchmark_or_mip_backend")
        self.assertFalse(gurobi["enabled_now"])
        self.assertEqual(gurobi["priority"], "optional")
        self.assertIn("not required", strategy["gurobi_not_required_reason"])

    def test_project_does_not_depend_on_building_full_solver_from_scratch(self):
        strategy = self.contract["solver_strategy"]

        self.assertIn("baseline", strategy["custom_solver_role"])
        self.assertIn("must not depend", strategy["custom_solver_warning"])
        self.assertIn("from scratch", strategy["custom_solver_warning"])

    def test_internal_baselines_remain_current_and_useful(self):
        baseline = self._candidate_by_id("internal_greedy_and_threshold_baselines")

        self.assertTrue(baseline["enabled_now"])
        self.assertFalse(baseline["requires_external_dependency"])
        self.assertEqual(baseline["planned_language_binding"], "C++")
        self.assertIn("baseline", baseline["planned_role"])

    def test_adapter_input_preserves_delay_context(self):
        input_contract = self.contract["adapter_boundary"]["input_contract"]

        self.assertTrue(input_contract["must_include_delay_context"])
        self.assertIn("active_perturbations", input_contract["required_sections"])
        self.assertIn("current_solution", input_contract["required_sections"])
        self.assertIn("objective_weights", input_contract["required_sections"])

    def test_adapter_output_supports_policy_comparison(self):
        output_contract = self.contract["adapter_boundary"]["output_contract"]

        self.assertTrue(output_contract["must_be_comparable_across_policies"])
        self.assertIn("delay_propagation_summary", output_contract["required_sections"])
        self.assertIn("route_stability_summary", output_contract["required_sections"])
        self.assertIn("computational_cost", output_contract["required_sections"])

    def test_execution_boundary_blocks_browser_solver_execution(self):
        boundary = self.contract["adapter_boundary"]["execution_boundary"]

        self.assertTrue(boundary["planned_backend_only"])
        self.assertTrue(boundary["browser_must_not_trigger_solver_directly"])
        self.assertTrue(boundary["future_execution_requires_api_gate"])
        self.assertTrue(boundary["future_execution_requires_job_id"])
        self.assertTrue(boundary["future_execution_requires_persisted_input_snapshot"])
        self.assertTrue(boundary["future_execution_requires_persisted_output_snapshot"])

    def test_research_alignment_mentions_trsp_wsrp_and_comparative_analysis(self):
        alignment = self.contract["research_alignment"]

        self.assertIn("TRSP", alignment["why_solver_is_needed"])
        self.assertIn("WSRP", alignment["why_solver_is_needed"])
        self.assertIn("compared", alignment["comparative_analysis_role"])
        self.assertIn("statistical", alignment["statistical_analysis_role"])

    def test_policy_comparison_requirements_are_experimental_not_single_run_claims(self):
        requirements = self.contract["policy_comparison_requirements"]

        self.assertIn("same instance must be reusable across multiple policies", requirements)
        self.assertIn("same perturbation set must be reusable across multiple policies", requirements)
        self.assertIn("solver output must not claim statistical superiority from a single run", requirements)

    def test_safety_requirements_are_conservative(self):
        safety_text = " ".join(self.contract["safety_requirements"])

        self.assertIn("Do not expose solver execution from the browser", safety_text)
        self.assertIn("Do not require Gurobi", safety_text)
        self.assertIn("Do not treat OR-Tools integration as already implemented", safety_text)
        self.assertIn("delay propagation", safety_text)

    def test_future_milestones_include_ortools_and_statistics(self):
        milestone_ids = {milestone["id"] for milestone in self.contract["future_milestones"]}

        self.assertIn("solver_request_contract", milestone_ids)
        self.assertIn("solver_response_contract", milestone_ids)
        self.assertIn("ortools_adapter_spike", milestone_ids)
        self.assertIn("comparative_statistics_pipeline", milestone_ids)

    def test_conservative_notes_block_false_execution_claims(self):
        text = " ".join(
            [
                self.contract["conservative_note"],
                self.contract["safety_note"],
            ]
        )

        self.assertIn("does not execute OR-Tools", text)
        self.assertIn("does not execute", text)
        self.assertIn("read-only", text)

    def _candidate_by_id(self, candidate_id):
        for candidate in self.contract["solver_candidates"]:
            if candidate["id"] == candidate_id:
                return candidate

        self.fail(f"Missing solver candidate: {candidate_id}")


if __name__ == "__main__":
    unittest.main()