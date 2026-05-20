import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "platform" / "contracts" / "comparative_analysis_contract.json"


class ComparativeAnalysisContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_valid_read_only_and_disabled(self):
        self.assertEqual(
            self.contract["schema"],
            "fieldops_lab.comparative_analysis_contract",
        )
        self.assertTrue(self.contract["read_only"])
        self.assertFalse(self.contract["execution_enabled"])
        self.assertFalse(self.contract["browser_execution_enabled"])
        self.assertFalse(self.contract["operational_use_enabled"])

    def test_research_alignment_keeps_delay_propagation_focus(self):
        alignment = self.contract["research_alignment"]

        self.assertIn("dynamic TRSP", alignment["problem_family"])
        self.assertIn("dynamic WSRP", alignment["problem_family"])
        self.assertIn("Delay propagation", alignment["dissertation_scope"])
        self.assertIn("policy or technique", alignment["central_question"])
        self.assertIn("replicable recommendation method", alignment["decision_framework_goal"])

    def test_comparison_unit_requires_paired_experiments(self):
        comparison_unit = self.contract["comparison_unit"]

        self.assertTrue(comparison_unit["paired_design_required"])
        self.assertTrue(comparison_unit["same_instance_required"])
        self.assertTrue(comparison_unit["same_initial_solution_required"])
        self.assertTrue(comparison_unit["same_perturbation_scenario_required"])
        self.assertTrue(comparison_unit["same_random_seed_required_when_randomness_exists"])
        self.assertIn("single isolated run is not enough", comparison_unit["reason"])

    def test_candidate_policy_families_include_current_and_future_methods(self):
        policy_ids = {
            policy["id"]
            for policy in self.contract["candidate_policy_families"]
        }

        self.assertIn("no_replanning", policy_ids)
        self.assertIn("threshold_delay_replanning", policy_ids)
        self.assertIn("solver_backed_replanning", policy_ids)
        self.assertIn("hybrid_or_metaheuristic_replanning", policy_ids)

    def test_solver_backed_policy_prefers_ortools(self):
        policies = {
            policy["id"]: policy
            for policy in self.contract["candidate_policy_families"]
        }

        solver_policy = policies["solver_backed_replanning"]

        self.assertEqual(solver_policy["preferred_solver_family"], "OR-Tools")
        self.assertEqual(solver_policy["current_status"], "future adapter")
        self.assertIn("adapter boundary", solver_policy["role"])

    def test_required_input_dimensions_support_controlled_experiments(self):
        dimensions = set(self.contract["required_input_dimensions"])

        required = {
            "instance_id",
            "instance_class",
            "delay_type",
            "delay_magnitude",
            "delay_location",
            "perturbation_seed",
            "policy_id",
            "policy_parameters",
            "solver_or_technique_id",
            "computational_budget",
        }

        self.assertTrue(required.issubset(dimensions))

    def test_required_metrics_cover_delay_stability_service_and_cost(self):
        metric_families = {
            family["id"]: set(family["metrics"])
            for family in self.contract["required_metric_families"]
        }

        self.assertIn("delay_propagation", metric_families)
        self.assertIn("route_stability", metric_families)
        self.assertIn("service_quality", metric_families)
        self.assertIn("computational_cost", metric_families)
        self.assertIn("propagated_delay_minutes", metric_families["delay_propagation"])
        self.assertIn("route_edit_distance_proxy", metric_families["route_stability"])
        self.assertIn("runtime_ms", metric_families["computational_cost"])

    def test_statistical_plan_blocks_single_run_claims(self):
        plan = self.contract["statistical_analysis_plan"]

        self.assertIn("confidence_interval_for_mean_difference", plan["paired_comparisons"])
        self.assertIn(
            "nonparametric_signed_rank_option_when_distribution_is_not_safe",
            plan["paired_comparisons"],
        )
        self.assertIn("detect_ranking_sensitive_scenarios", plan["ranking_analysis"])
        self.assertIn("single run", plan["minimum_scientific_rule"])

    def test_expected_outputs_include_decision_framework_outputs(self):
        outputs = set(self.contract["expected_outputs"])

        self.assertIn("comparative_summary_json", outputs)
        self.assertIn("comparative_summary_csv", outputs)
        self.assertIn("policy_ranking_table", outputs)
        self.assertIn("statistical_validation_report", outputs)
        self.assertIn("decision_framework_candidate_rules", outputs)

    def test_quality_requirements_prevent_hidden_tradeoffs(self):
        quality_text = " ".join(self.contract["quality_requirements"])

        self.assertIn("Every comparison", quality_text)
        self.assertIn("Every policy ranking", quality_text)
        self.assertIn("solver status", quality_text)
        self.assertIn("scenario class", quality_text)

    def test_safety_requirements_are_conservative(self):
        safety_text = " ".join(self.contract["safety_requirements"])

        self.assertIn("Do not expose comparative experiment execution", safety_text)
        self.assertIn("Do not claim operational deployment readiness", safety_text)
        self.assertIn("Do not hide failed runs", safety_text)
        self.assertIn("Do not mix policies", safety_text)

    def test_current_platform_status_is_honest(self):
        status = self.contract["current_platform_status"]

        self.assertTrue(status["internal_baselines_exist"])
        self.assertTrue(status["batch_ranking_exists"])
        self.assertTrue(status["ranking_sensitivity_reports_exist"])
        self.assertTrue(status["scientific_validation_reports_exist"])
        self.assertFalse(status["solver_adapter_exists"])
        self.assertFalse(status["full_statistical_engine_exists"])
        self.assertFalse(status["browser_execution_enabled"])

    def test_conservative_note_does_not_claim_execution(self):
        note = self.contract["conservative_note"]

        self.assertIn("does not execute experiments", note)
        self.assertIn("run solvers", note)
        self.assertIn("perform statistical tests", note)
        self.assertIn("trigger backend jobs", note)


if __name__ == "__main__":
    unittest.main()