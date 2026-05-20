import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "comparative_analysis_sample.json"


class ComparativeAnalysisSampleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SAMPLE_PATH.open("r", encoding="utf-8") as file:
            cls.sample = json.load(file)

    def test_sample_is_valid_read_only_and_disabled(self):
        self.assertEqual(self.sample["schema"], "fieldops_lab.comparative_analysis_sample")
        self.assertTrue(self.sample["read_only"])
        self.assertFalse(self.sample["execution_enabled"])
        self.assertFalse(self.sample["write_operations_supported"])
        self.assertFalse(self.sample["browser_triggered_execution_enabled"])

    def test_sample_is_not_claimed_as_real_experiment_result(self):
        runtime_status = self.sample["runtime_status"]

        self.assertFalse(runtime_status["is_real_experiment_result"])
        self.assertTrue(runtime_status["is_static_sample"])
        self.assertIn("future comparative analysis output", runtime_status["purpose"])

    def test_research_alignment_keeps_delay_propagation_focus(self):
        alignment = self.sample["research_alignment"]

        self.assertIn("TRSP", alignment["problem_family"])
        self.assertIn("WSRP", alignment["problem_family"])
        self.assertIn("Delay propagation", alignment["dissertation_focus"])
        self.assertIn("re-planning policy", alignment["main_question"])

    def test_comparison_unit_requires_paired_controlled_experiments(self):
        comparison_unit = self.sample["comparison_unit"]

        self.assertEqual(comparison_unit["unit_type"], "paired controlled experiment")
        self.assertFalse(comparison_unit["single_run_claims_allowed"])
        self.assertGreaterEqual(comparison_unit["minimum_replications_required"], 30)

        pairing_rule = comparison_unit["pairing_rule"].lower()
        self.assertIn("same instance", pairing_rule)
        self.assertIn("same", pairing_rule)
        self.assertIn("random seed", pairing_rule)

    def test_candidate_policies_include_current_and_future_methods(self):
        policies = {
            policy["policy_id"]: policy
            for policy in self.sample["candidate_policies"]
        }

        self.assertIn("no_replanning", policies)
        self.assertIn("threshold_delay_replanning", policies)
        self.assertIn("periodic_replanning", policies)
        self.assertIn("ortools_vrp_reoptimization", policies)

        self.assertEqual(
            policies["no_replanning"]["current_platform_status"],
            "implemented baseline",
        )
        self.assertEqual(
            policies["threshold_delay_replanning"]["current_platform_status"],
            "implemented baseline",
        )
        self.assertEqual(
            policies["ortools_vrp_reoptimization"]["preferred_solver_family"],
            "OR-Tools",
        )

    def test_gurobi_is_optional_not_required(self):
        policies = {
            policy["policy_id"]: policy
            for policy in self.sample["candidate_policies"]
        }

        self.assertIn("gurobi_mip_reoptimization", policies)
        self.assertEqual(
            policies["gurobi_mip_reoptimization"]["policy_family"],
            "solver_backed_optional",
        )
        self.assertIn(
            "optional",
            policies["gurobi_mip_reoptimization"]["current_platform_status"],
        )

    def test_metrics_cover_research_tradeoffs(self):
        metrics = self.sample["metrics"]

        required_groups = [
            "performance",
            "service_quality",
            "stability",
            "robustness",
            "computational_cost",
            "feasibility",
        ]

        for group in required_groups:
            self.assertIn(group, metrics)
            self.assertGreater(len(metrics[group]), 0)

        self.assertIn("time_window_violation_minutes", metrics["service_quality"])
        self.assertIn("route_edit_distance", metrics["stability"])
        self.assertIn("runtime_ms", metrics["computational_cost"])

    def test_sample_results_include_multiple_policies_and_replications(self):
        results = self.sample["sample_results"]

        self.assertGreaterEqual(len(results), 4)

        for result in results:
            self.assertGreaterEqual(result["replications"], 30)
            self.assertIn("mean_composite_score", result)
            self.assertIn("interpretation", result)

    def test_statistical_plan_blocks_single_run_claims(self):
        plan = self.sample["statistical_analysis_plan"]

        self.assertEqual(plan["design"], "paired repeated experiment over the same scenario seeds")
        self.assertTrue(plan["blocks_single_run_claims"])
        self.assertIn("Friedman", plan["primary_test"])

        post_hoc_text = " ".join(plan["post_hoc_tests"]).lower()
        self.assertIn("effect size", post_hoc_text)
        self.assertIn("confidence", " ".join(plan["minimum_reporting_requirements"]).lower())

    def test_decision_framework_output_is_explicit(self):
        output = self.sample["decision_framework_output"]

        self.assertEqual(
            output["recommended_policy_for_sample_scenario"],
            "threshold_delay_replanning",
        )
        self.assertEqual(
            output["best_pure_performance_policy"],
            "ortools_vrp_reoptimization",
        )
        self.assertIn("reproducible rule", output["future_framework_goal"])

    def test_related_contracts_connect_current_platform_artifacts(self):
        related = self.sample["related_contracts"]

        self.assertIn("platform/contracts/comparative_analysis_contract.json", related)
        self.assertIn("platform/contracts/solver_integration_contract.json", related)
        self.assertIn("platform/contracts/replanning_decision_response_sample.json", related)

    def test_quality_requirements_prevent_hidden_tradeoffs(self):
        requirements = " ".join(self.sample["quality_requirements"]).lower()

        self.assertIn("never rank policies from a single run", requirements)
        self.assertIn("paired scenarios", requirements)
        self.assertIn("trade-offs", requirements)
        self.assertIn("placeholders", requirements)

    def test_safety_requirements_are_conservative(self):
        requirements = " ".join(self.sample["safety_requirements"]).lower()

        self.assertIn("browser must not execute solvers", requirements)
        self.assertIn("browser must not start experiments", requirements)
        self.assertIn("must not mutate schedules", requirements)

    def test_conservative_note_does_not_claim_execution(self):
        note = self.sample["conservative_note"].lower()

        self.assertIn("static read-only sample", note)
        self.assertIn("does not prove", note)
        self.assertIn("does not execute or-tools", note)
        self.assertIn("does not represent real experimental evidence yet", note)


if __name__ == "__main__":
    unittest.main()