import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PATH = ROOT / "platform" / "contracts" / "replanning_decision_response_sample.json"


class ReplanningDecisionResponseSampleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))

    def test_sample_is_valid_read_only_and_disabled(self):
        self.assertEqual(
            self.sample["schema"],
            "fieldops_lab.replanning_decision_response_sample",
        )
        self.assertTrue(self.sample["read_only"])
        self.assertTrue(self.sample["available"])
        self.assertFalse(self.sample["execution_enabled"])
        self.assertFalse(self.sample["write_operations_supported"])
        self.assertFalse(self.sample["browser_triggered_execution_enabled"])
        self.assertEqual(
            self.sample["contract_reference"],
            "platform/contracts/replanning_decision_response_contract.json",
        )

    def test_sample_links_simulation_delay_request_policy_and_solutions(self):
        references = self.sample["input_references"]

        self.assertEqual(
            references["simulation_state_sample_id"],
            "demo_delay_propagation_001",
        )
        self.assertEqual(
            references["delay_injection_request_contract"],
            "platform/contracts/delay_injection_request_contract.json",
        )
        self.assertIn("replanning_policy_id", references)
        self.assertIn("baseline_solution_id", references)
        self.assertIn("candidate_solution_id", references)

    def test_decision_summary_is_not_executed(self):
        decision = self.sample["decision_summary"]

        self.assertEqual(decision["decision_status"], "not_executed_by_this_sample")
        self.assertFalse(decision["decision_enabled"])
        self.assertEqual(decision["execution_status"], "disabled")
        self.assertIn("manual_review", decision["recommendation"])
        self.assertIn("does not execute", decision["reason"])

    def test_response_tracks_core_decision_sections(self):
        required_sections = [
            "feasibility",
            "performance_delta",
            "stability_delta",
            "computational_cost",
            "delay_propagation",
            "tradeoff_summary",
            "explanation",
        ]

        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, self.sample)
                self.assertIsInstance(self.sample[section], dict)

    def test_delay_propagation_is_central(self):
        scope = self.sample["scope"]
        propagation = self.sample["delay_propagation"]

        self.assertEqual(scope["primary_dissertation_scope"], "delay_propagation")
        self.assertEqual(scope["primary_perturbation_type"], "service_delay")
        self.assertGreater(propagation["injected_delay_minutes"], 0)
        self.assertGreater(
            propagation["propagated_delay_minutes_baseline"],
            propagation["propagated_delay_minutes_candidate"],
        )
        self.assertGreater(propagation["recovered_delay_minutes"], 0)
        self.assertGreaterEqual(
            propagation["affected_tasks_count_baseline"],
            propagation["affected_tasks_count_candidate"],
        )

    def test_performance_and_stability_capture_tradeoff(self):
        performance = self.sample["performance_delta"]
        stability = self.sample["stability_delta"]
        tradeoff = self.sample["tradeoff_summary"]

        self.assertLess(performance["total_delay_delta_minutes"], 0)
        self.assertLess(performance["lateness_delta_minutes"], 0)
        self.assertGreater(stability["changed_assignments_count"], 0)
        self.assertGreater(stability["changed_sequence_count"], 0)
        self.assertEqual(tradeoff["dominant_benefit"], "lower_delay_propagation")
        self.assertEqual(tradeoff["dominant_risk"], "schedule_instability")
        self.assertTrue(tradeoff["policy_comparison_ready"])
        self.assertFalse(tradeoff["statistical_claim_ready"])
        self.assertFalse(tradeoff["decision_rule_ready"])

    def test_computational_cost_makes_no_execution_explicit(self):
        cost = self.sample["computational_cost"]

        self.assertEqual(cost["solver_time_ms"], 0)
        self.assertEqual(cost["wall_time_ms"], 0)
        self.assertEqual(cost["iteration_count"], 0)
        self.assertEqual(cost["execution_engine"], "none")
        self.assertEqual(cost["cost_status"], "not_measured")

    def test_safety_requirements_are_conservative(self):
        safety = self.sample["safety_requirements"]

        self.assertTrue(safety["no_browser_solver_execution"])
        self.assertTrue(safety["no_file_write_from_browser"])
        self.assertTrue(safety["no_schedule_mutation"])
        self.assertTrue(safety["no_operational_claim_without_backend_result"])
        self.assertTrue(safety["no_scientific_claim_from_single_sample"])

    def test_conservative_note_blocks_operational_use(self):
        note = self.sample["conservative_note"].lower()
        explanation = self.sample["explanation"]

        self.assertIn("static read-only sample", note)
        self.assertIn("does not execute", note)
        self.assertIn("does not call a solver", note)
        self.assertIn("does not mutate schedules", note)
        self.assertIn("operational recommendation", note)
        self.assertIn("not produced by a validated backend", explanation["why_not_operationally_valid_yet"].lower())

    def test_quality_requirements_keep_sample_as_ui_contract_artifact(self):
        requirements = " ".join(self.sample["quality_requirements"]).lower()

        self.assertIn("read-only", requirements)
        self.assertIn("no solver", requirements)
        self.assertIn("delay propagation", requirements)
        self.assertIn("ui rendering", requirements)
        self.assertIn("without enabling execution", requirements)


if __name__ == "__main__":
    unittest.main()