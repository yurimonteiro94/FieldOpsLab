import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "platform" / "contracts" / "replanning_decision_response_contract.json"


def load_contract() -> dict:
    with CONTRACT_PATH.open("r", encoding="utf-8") as contract_file:
        return json.load(contract_file)


def flatten_text(value) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    return str(value)


class ReplanningDecisionResponseContractTests(unittest.TestCase):
    def test_contract_is_valid_read_only_and_disabled(self):
        contract = load_contract()

        self.assertEqual(contract["contract_name"], "replanning_decision_response_contract")
        self.assertEqual(contract["status"], "planned_read_only_contract")
        self.assertFalse(contract["enabled"])
        self.assertFalse(contract["execution_enabled"])
        self.assertFalse(contract["current_endpoint_enabled"])

        text = flatten_text(contract).lower()
        self.assertIn("read-only", text)
        self.assertIn("does not execute", text)

    def test_future_endpoint_is_planned_but_not_enabled(self):
        contract = load_contract()
        future_endpoint = contract["future_endpoint"]

        self.assertEqual(future_endpoint["method"], "POST")
        self.assertEqual(future_endpoint["path"], "/api/v1/replanning-decisions")
        self.assertFalse(future_endpoint["enabled"])
        self.assertIn("intentionally disabled", future_endpoint["reason"].lower())

    def test_related_contracts_connect_delay_injection_to_simulation_state(self):
        contract = load_contract()
        related_contracts = set(contract["related_contracts"])

        self.assertIn("simulation_state_contract", related_contracts)
        self.assertIn("simulation_state_sample", related_contracts)
        self.assertIn("delay_injection_request_contract", related_contracts)

    def test_scope_keeps_dissertation_centered_on_delays(self):
        contract = load_contract()
        scope = contract["scope"]

        primary_scope = " ".join(scope["primary_dissertation_scope"]).lower()
        future_scope = " ".join(scope["future_extensible_perturbations"]).lower()
        boundary = scope["dissertation_boundary"].lower()

        self.assertIn("delay propagation", primary_scope)
        self.assertIn("travel delay", primary_scope)
        self.assertIn("service delay", primary_scope)
        self.assertIn("new demand", future_scope)
        self.assertIn("cancellation", future_scope)
        self.assertIn("dissertation", boundary)
        self.assertIn("delay", boundary)

    def test_input_references_track_simulation_request_policy_and_solutions(self):
        contract = load_contract()
        input_references = contract["input_references"]

        expected_references = {
            "simulation_id",
            "delay_injection_request_id",
            "policy_id",
            "baseline_solution_id",
            "candidate_solution_id",
        }

        self.assertTrue(expected_references.issubset(input_references.keys()))
        self.assertTrue(input_references["simulation_id"]["required"])
        self.assertTrue(input_references["delay_injection_request_id"]["required"])
        self.assertTrue(input_references["policy_id"]["required"])
        self.assertTrue(input_references["baseline_solution_id"]["required"])
        self.assertFalse(input_references["candidate_solution_id"]["required"])

    def test_response_shape_tracks_feasibility_performance_stability_cost_and_propagation(self):
        contract = load_contract()
        response_shape = contract["response_shape"]

        required_sections = {
            "decision_id",
            "status",
            "selected_policy",
            "feasibility",
            "performance_delta",
            "stability_delta",
            "computational_cost",
            "delay_propagation",
            "explanation",
        }

        self.assertTrue(required_sections.issubset(response_shape.keys()))

        for section in required_sections:
            self.assertTrue(response_shape[section]["required"], section)

        self.assertIn("objective_delta", response_shape["performance_delta"]["fields"])
        self.assertIn("stability_score", response_shape["stability_delta"]["fields"])
        self.assertIn("solver_time_ms", response_shape["computational_cost"]["fields"])
        self.assertIn("affected_tasks_count", response_shape["delay_propagation"]["fields"])
        self.assertIn("decision_reason", response_shape["explanation"]["fields"])

    def test_status_values_distinguish_contract_from_execution(self):
        contract = load_contract()
        allowed_values = contract["response_shape"]["status"]["allowed_values"]

        self.assertIn("not_executed_read_only", allowed_values)
        self.assertIn("rejected_by_validation", allowed_values)
        self.assertIn("accepted_for_future_evaluation", allowed_values)

    def test_validation_rules_prevent_false_execution_claims(self):
        contract = load_contract()
        rules = " ".join(contract["validation_rules"]).lower()

        self.assertIn("simulation_id", rules)
        self.assertIn("delay_injection_request_id", rules)
        self.assertIn("selected policy", rules)
        self.assertIn("solver", rules)
        self.assertIn("execution_enabled is false", rules)
        self.assertIn("planned response contract", rules)

    def test_quality_requirements_support_statistical_and_policy_comparison(self):
        contract = load_contract()
        quality_requirements = " ".join(contract["quality_requirements"]).lower()

        self.assertIn("deterministic", quality_requirements)
        self.assertIn("statistical comparison", quality_requirements)
        self.assertIn("stability impact", quality_requirements)
        self.assertIn("performance impact", quality_requirements)
        self.assertIn("computational cost", quality_requirements)
        self.assertIn("delay propagation", quality_requirements)

    def test_safety_requirements_are_conservative(self):
        contract = load_contract()
        safety_requirements = " ".join(contract["safety_requirements"]).lower()

        self.assertIn("read-only", safety_requirements)
        self.assertIn("must not execute solvers", safety_requirements)
        self.assertIn("must not execute optimization", safety_requirements)
        self.assertIn("must not execute simulation steps", safety_requirements)
        self.assertIn("must not write files", safety_requirements)
        self.assertIn("must not mutate project state", safety_requirements)
        self.assertIn("must not expose a live post endpoint", safety_requirements)

    def test_conservative_note_blocks_operational_execution(self):
        contract = load_contract()
        note = contract["conservative_note"].lower()

        self.assertIn("only defines the future response shape", note)
        self.assertIn("does not execute", note)
        self.assertIn("solvers", note)
        self.assertIn("optimization", note)
        self.assertIn("simulation", note)
        self.assertIn("operational changes", note)


if __name__ == "__main__":
    unittest.main()