from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SIMULATION_STATE_CONTRACT_PATH = (
    PROJECT_ROOT / "platform" / "contracts" / "simulation_state_contract.json"
)


class SimulationStateContractTests(unittest.TestCase):
    def load_contract(self) -> dict[str, Any]:
        self.assertTrue(SIMULATION_STATE_CONTRACT_PATH.exists())
        return json.loads(
            SIMULATION_STATE_CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def test_simulation_state_contract_is_valid_and_conservative(self) -> None:
        contract = self.load_contract()

        self.assertEqual(
            contract["contract"],
            "fieldops_lab_simulation_state_contract",
        )
        self.assertEqual(contract["status"], "draft")
        self.assertTrue(contract["read_only"])

        interpretation = contract["conservative_interpretation"]
        self.assertFalse(interpretation["is_visual_simulation_implemented"])
        self.assertFalse(interpretation["is_real_time_map_implemented"])
        self.assertFalse(interpretation["allows_browser_triggered_execution"])
        self.assertFalse(interpretation["allows_arbitrary_command_execution"])
        self.assertFalse(interpretation["supports_user_delay_injection_in_ui_now"])
        self.assertTrue(interpretation["defines_future_safe_contract_only"])

    def test_contract_distinguishes_optimization_and_simulation_modes(self) -> None:
        contract = self.load_contract()
        target_modes = contract["target_modes"]

        self.assertIn("optimization_mode", target_modes)
        self.assertIn("simulation_mode", target_modes)

        optimization_mode = target_modes["optimization_mode"]
        simulation_mode = target_modes["simulation_mode"]

        self.assertFalse(optimization_mode["requires_visual_map"])
        self.assertTrue(optimization_mode["requires_controlled_execution_backend"])

        self.assertTrue(simulation_mode["requires_visual_map"])
        self.assertTrue(simulation_mode["requires_timeline"])
        self.assertTrue(simulation_mode["requires_user_event_injection"])
        self.assertTrue(simulation_mode["requires_controlled_execution_backend"])
        self.assertEqual(simulation_mode["current_status"], "design_contract_only")

    def test_contract_defines_clock_map_entities_and_timeline(self) -> None:
        contract = self.load_contract()

        clock_fields = contract["simulation_clock"]["required_fields"]
        self.assertIn("current_time", clock_fields)
        self.assertIn("speed_multiplier", clock_fields)
        self.assertIn("status", clock_fields)
        self.assertIn("paused", contract["simulation_clock"]["allowed_status"])

        map_layer = contract["map_layer"]
        self.assertIn("technician_position", map_layer["required_objects"])
        self.assertIn("planned_route_segment", map_layer["required_objects"])
        self.assertIn("active_delay_marker", map_layer["required_objects"])
        self.assertIn("latitude", map_layer["required_coordinate_fields"])
        self.assertIn("longitude", map_layer["required_coordinate_fields"])
        self.assertEqual(
            map_layer["fallback_coordinate_mode"],
            "cartesian_xy_for_synthetic_instances",
        )

        entities = contract["entities"]
        self.assertIn("technician", entities)
        self.assertIn("task", entities)
        self.assertIn("route_segment", entities)

        technician_fields = entities["technician"]["required_fields"]
        self.assertIn("current_location", technician_fields)
        self.assertIn("route_progress", technician_fields)
        self.assertIn("accumulated_delay", technician_fields)

        task_fields = entities["task"]["required_fields"]
        self.assertIn("time_window", task_fields)
        self.assertIn("planned_start", task_fields)
        self.assertIn("actual_finish", task_fields)

        timeline_events = contract["timeline_events"]
        self.assertIn("event_type", timeline_events["required_fields"])
        self.assertIn("travel_delay_started", timeline_events["allowed_event_types"])
        self.assertIn("service_delay_started", timeline_events["allowed_event_types"])
        self.assertIn("replanning_triggered", timeline_events["allowed_event_types"])

    def test_contract_keeps_delays_as_primary_dissertation_scope(self) -> None:
        contract = self.load_contract()
        perturbations = contract["perturbation_events"]

        primary_scope = perturbations["primary_dissertation_scope"]
        future_scope = perturbations["future_extension_scope"]

        self.assertIn("delay_propagation", primary_scope)
        self.assertIn("travel_delay", primary_scope)
        self.assertIn("service_delay", primary_scope)

        self.assertIn("new_request", future_scope)
        self.assertIn("cancellation", future_scope)
        self.assertIn("priority_change", future_scope)

        self.assertFalse(perturbations["allowed_user_injected_now"])

        required_fields = perturbations["required_fields"]
        self.assertIn("perturbation_type", required_fields)
        self.assertIn("target_entity_id", required_fields)
        self.assertIn("propagation_policy", required_fields)

    def test_replanning_decision_contract_tracks_cost_and_stability(self) -> None:
        contract = self.load_contract()
        replanning_decision = contract["replanning_decision"]

        required_fields = replanning_decision["required_fields"]
        self.assertIn("policy_id", required_fields)
        self.assertIn("decision", required_fields)
        self.assertIn("objective_delta", required_fields)
        self.assertIn("stability_delta", required_fields)
        self.assertIn("computational_time_ms", required_fields)

        allowed_decisions = replanning_decision["allowed_decisions"]
        self.assertIn("no_replanning", allowed_decisions)
        self.assertIn("replan_subset", allowed_decisions)
        self.assertIn("replan_global", allowed_decisions)
        self.assertIn("manual_review_required", allowed_decisions)

    def test_safety_requirements_prevent_unsafe_execution(self) -> None:
        contract = self.load_contract()
        safety = contract["safety_requirements"]

        self.assertTrue(
            safety["web_dashboard_must_remain_read_only_until_execution_contract_exists"]
        )
        self.assertTrue(safety["browser_must_not_call_subprocess_or_shell"])
        self.assertTrue(safety["simulation_execution_requires_allowlisted_backend_job"])
        self.assertTrue(
            safety["real_company_data_requires_authentication_and_access_control"]
        )
        self.assertTrue(safety["user_injected_events_require_validation"])
        self.assertTrue(safety["simulation_results_must_be_replayable"])

    def test_future_api_endpoints_are_planned_not_currently_enabled(self) -> None:
        contract = self.load_contract()
        endpoints = contract["minimum_future_api_endpoints"]

        endpoint_by_id = {endpoint["id"]: endpoint for endpoint in endpoints}

        self.assertEqual(
            endpoint_by_id["simulation_state_snapshot"]["method"],
            "GET",
        )
        self.assertEqual(
            endpoint_by_id["simulation_event_log"]["method"],
            "GET",
        )

        controlled_job_endpoint = endpoint_by_id["controlled_simulation_job"]
        self.assertEqual(controlled_job_endpoint["method"], "POST")
        self.assertEqual(controlled_job_endpoint["status"], "future_gated")

    def test_quality_requirements_mention_core_constraints(self) -> None:
        contract = self.load_contract()
        quality_requirements = " ".join(contract["quality_requirements"]).lower()

        self.assertIn("valid json", quality_requirements)
        self.assertIn("must not claim", quality_requirements)
        self.assertIn("browser-triggered execution", quality_requirements)
        self.assertIn("delay propagation", quality_requirements)
        self.assertIn("geographic and synthetic coordinates", quality_requirements)
        self.assertIn("computational cost", quality_requirements)
        self.assertIn("stability impact", quality_requirements)


if __name__ == "__main__":
    unittest.main()