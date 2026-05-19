import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "platform" / "contracts" / "delay_injection_request_contract.json"


class DelayInjectionRequestContractTests(unittest.TestCase):
    def load_contract(self):
        self.assertTrue(CONTRACT_PATH.exists(), f"Missing contract: {CONTRACT_PATH}")
        with CONTRACT_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)

    def test_contract_is_valid_read_only_and_disabled(self):
        contract = self.load_contract()

        self.assertEqual(contract["contract"], "delay_injection_request_contract")
        self.assertEqual(contract["status"], "planned_disabled")
        self.assertTrue(contract["read_only"])
        self.assertFalse(contract["execution_enabled"])
        self.assertFalse(contract["write_operations_supported"])
        self.assertFalse(contract["browser_execution_enabled"])

    def test_planned_endpoint_is_not_enabled(self):
        contract = self.load_contract()
        endpoint = contract["planned_endpoint"]

        self.assertEqual(endpoint["method"], "POST")
        self.assertEqual(
            endpoint["path"],
            "/api/v1/simulation-runs/{simulation_run_id}/delay-events",
        )
        self.assertEqual(endpoint["status"], "planned_not_enabled")
        self.assertFalse(endpoint["execution_enabled"])
        self.assertTrue(endpoint["requires_future_authentication"])
        self.assertTrue(endpoint["requires_future_server_side_validation"])
        self.assertTrue(endpoint["requires_future_audit_log"])

    def test_request_shape_defines_delay_injection_fields(self):
        contract = self.load_contract()
        shape = contract["request_shape"]

        required_fields = [
            "simulation_run_id",
            "event_id",
            "event_type",
            "target_type",
            "target_id",
            "injected_at_simulation_time_minutes",
            "delay_minutes",
            "source",
        ]

        for field in required_fields:
            self.assertIn(field, shape)
            self.assertTrue(shape[field]["required"], field)

        self.assertEqual(
            shape["event_type"]["allowed_values"],
            ["travel_delay", "service_delay"],
        )
        self.assertEqual(
            shape["target_type"]["allowed_values"],
            ["technician", "task", "route_leg"],
        )
        self.assertEqual(shape["injected_at_simulation_time_minutes"]["minimum"], 0)
        self.assertEqual(shape["delay_minutes"]["minimum"], 0)

    def test_contract_keeps_dissertation_scope_narrow(self):
        contract = self.load_contract()
        alignment = contract["research_alignment"]

        self.assertIn("delay_propagation", alignment["primary_dissertation_scope"])
        self.assertIn("travel_delay", alignment["primary_dissertation_scope"])
        self.assertIn("service_delay", alignment["primary_dissertation_scope"])

        self.assertIn("new_requests", alignment["future_platform_extensions"])
        self.assertIn("cancellations", alignment["future_platform_extensions"])
        self.assertIn("priority_changes", alignment["future_platform_extensions"])

        self.assertIn("delays and delay propagation", alignment["scope_policy"])

    def test_validation_rules_prevent_unsafe_execution(self):
        contract = self.load_contract()
        joined_rules = "\n".join(contract["validation_rules"]).lower()

        self.assertIn("must not mutate production data", joined_rules)
        self.assertIn("must not execute solvers directly from the browser", joined_rules)
        self.assertIn("controlled backend job api", joined_rules)
        self.assertIn("audit logging", joined_rules)

    def test_expected_future_effects_track_delay_propagation(self):
        contract = self.load_contract()
        effects = "\n".join(contract["expected_future_effects"]).lower()

        self.assertIn("simulation timeline", effects)
        self.assertIn("delayed", effects)
        self.assertIn("propagated delay", effects)
        self.assertIn("re-planning decision", effects)

    def test_replanning_decision_output_tracks_cost_stability_and_feasibility(self):
        contract = self.load_contract()
        fields = contract["replanning_decision_output"]["required_future_fields"]

        self.assertIn("previous_plan_cost", fields)
        self.assertIn("candidate_plan_cost", fields)
        self.assertIn("stability_delta", fields)
        self.assertIn("feasibility_status", fields)
        self.assertIn("computational_time_ms", fields)
        self.assertEqual(
            contract["replanning_decision_output"]["current_status"],
            "not_executed_by_this_contract",
        )

    def test_safety_requirements_are_conservative(self):
        contract = self.load_contract()
        safety = contract["safety_requirements"]

        self.assertTrue(safety["read_only_contract_only"])
        self.assertTrue(safety["no_browser_solver_execution"])
        self.assertTrue(safety["no_arbitrary_command_execution"])
        self.assertTrue(safety["no_file_system_mutation_from_web"])
        self.assertTrue(safety["no_production_data_mutation"])
        self.assertTrue(safety["future_endpoint_requires_authentication"])
        self.assertTrue(safety["future_endpoint_requires_server_side_validation"])
        self.assertTrue(safety["future_endpoint_requires_audit_log"])

    def test_quality_requirements_are_explicit(self):
        contract = self.load_contract()
        quality = "\n".join(contract["quality_requirements"]).lower()

        self.assertIn("travel delay", quality)
        self.assertIn("service delay", quality)
        self.assertIn("delay propagation", quality)
        self.assertIn("current execution as disabled", quality)
        self.assertIn("non-negative time and delay", quality)
        self.assertIn("re-planning decisions", quality)

    def test_conservative_note_blocks_execution_claims(self):
        contract = self.load_contract()
        note = contract["conservative_note"].lower()

        self.assertIn("read-only planning contract", note)
        self.assertIn("does not enable delay injection", note)
        self.assertIn("simulation execution", note)
        self.assertIn("solver execution", note)
        self.assertIn("write operations", note)


if __name__ == "__main__":
    unittest.main()