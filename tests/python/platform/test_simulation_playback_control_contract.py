import json
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = PROJECT_ROOT / "platform" / "contracts" / "simulation_playback_control_contract.json"


def load_contract() -> dict[str, Any]:
    with CONTRACT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(flatten_strings(item))
        return result
    if isinstance(value, dict):
        result = []
        for item in value.values():
            result.extend(flatten_strings(item))
        return result
    return []


class SimulationPlaybackControlContractTests(unittest.TestCase):
    def test_contract_is_valid_read_only_and_disabled(self) -> None:
        contract = load_contract()

        self.assertEqual("simulation_playback_control_contract", contract["contract_id"])
        self.assertEqual("read_only_contract", contract["status"])
        self.assertTrue(contract["read_only"])
        self.assertFalse(contract["enabled"])
        self.assertFalse(contract["execution_exposed"])
        self.assertFalse(contract["future_endpoint"]["enabled"])
        self.assertFalse(contract["future_endpoint"]["post_allowed"])

    def test_playback_controls_are_visible_but_disabled(self) -> None:
        contract = load_contract()
        playback_controls = contract["playback_controls"]

        expected_controls = ["play", "pause", "step_forward", "step_backward", "reset"]
        for control_name in expected_controls:
            with self.subTest(control_name=control_name):
                self.assertIn(control_name, playback_controls)
                self.assertTrue(playback_controls[control_name]["visible"])
                self.assertFalse(playback_controls[control_name]["enabled"])
                self.assertIn("disabled_reason", playback_controls[control_name])

    def test_speed_controls_are_contract_only(self) -> None:
        contract = load_contract()
        speed_controls = contract["speed_controls"]

        self.assertTrue(speed_controls["visible"])
        self.assertFalse(speed_controls["enabled"])
        self.assertEqual(1.0, speed_controls["selected_speed"])
        self.assertIn(0.25, speed_controls["available_speeds"])
        self.assertIn(1.0, speed_controls["available_speeds"])
        self.assertIn(60.0, speed_controls["available_speeds"])
        self.assertFalse(speed_controls["can_change_backend_execution_speed"])

    def test_clock_controls_bind_to_simulation_state_without_mutation(self) -> None:
        contract = load_contract()
        clock_controls = contract["clock_controls"]

        self.assertEqual("clock.current_time", clock_controls["current_time_field"])
        self.assertEqual("clock.start_time", clock_controls["start_time_field"])
        self.assertEqual("clock.end_time", clock_controls["end_time_field"])
        self.assertTrue(clock_controls["can_display_current_time"])
        self.assertFalse(clock_controls["can_change_backend_time"])
        self.assertFalse(clock_controls["can_seek_backend_execution"])

    def test_timeline_scrubber_tracks_future_views_without_mutation(self) -> None:
        contract = load_contract()
        scrubber = contract["timeline_scrubber"]

        self.assertTrue(scrubber["visible"])
        self.assertFalse(scrubber["enabled"])
        self.assertEqual("timeline.events", scrubber["source_fields"]["timeline_events"])
        self.assertEqual("timeline.current_event_id", scrubber["source_fields"]["current_event_id"])
        self.assertIn("delay_propagation_chain", scrubber["supported_future_views"])
        self.assertIn("replanning_decision_marker", scrubber["supported_future_views"])
        self.assertFalse(scrubber["can_mutate_timeline"])
        self.assertFalse(scrubber["can_create_events"])
        self.assertFalse(scrubber["can_delete_events"])

    def test_contract_keeps_dissertation_scope_on_delay_propagation(self) -> None:
        contract = load_contract()
        scope = contract["research_scope"]

        self.assertEqual("delay_propagation", scope["dissertation_focus"])
        self.assertIn("travel_delay", scope["primary_perturbations"])
        self.assertIn("service_delay", scope["primary_perturbations"])
        self.assertIn("new_demand", scope["platform_extension_targets"])
        self.assertIn("not enabled", scope["scope_note"])

    def test_delay_visualization_bindings_track_propagation(self) -> None:
        contract = load_contract()
        bindings = contract["delay_visualization_bindings"]

        self.assertIn("delays.travel_delay_minutes", bindings["delay_source_fields"])
        self.assertIn("delays.service_delay_minutes", bindings["delay_source_fields"])
        self.assertIn("propagation.affected_tasks", bindings["delay_source_fields"])
        self.assertIn("show_downstream_affected_tasks", bindings["expected_visual_outputs"])
        self.assertIn("show_before_after_stability_summary", bindings["expected_visual_outputs"])
        self.assertIn("delay propagation", bindings["dissertation_alignment"])

    def test_decision_response_bindings_are_preview_only(self) -> None:
        contract = load_contract()
        bindings = contract["decision_response_bindings"]

        self.assertEqual("replanning_decision_response_sample", bindings["decision_source"])
        self.assertIn("decision_summary.selected_policy_id", bindings["display_fields"])
        self.assertIn("stability.changed_assignments_count", bindings["display_fields"])
        self.assertIn("cost.computational_cost_class", bindings["display_fields"])
        self.assertFalse(bindings["can_trigger_decision"])
        self.assertFalse(bindings["can_apply_decision"])
        self.assertFalse(bindings["can_persist_decision"])

    def test_validation_rules_block_browser_triggered_execution(self) -> None:
        contract = load_contract()
        rules = contract["validation_rules"]

        rule_ids = {rule["rule_id"] for rule in rules}
        self.assertIn("playback_controls_must_remain_disabled", rule_ids)
        self.assertIn("no_browser_triggered_execution", rule_ids)
        self.assertIn("timeline_scrubber_is_read_only", rule_ids)
        self.assertIn("decision_response_is_preview_only", rule_ids)

        blocking_rules = [rule for rule in rules if rule["severity"] == "blocking"]
        self.assertGreaterEqual(len(blocking_rules), 4)

    def test_safety_requirements_are_conservative(self) -> None:
        contract = load_contract()
        safety = contract["safety_requirements"]

        self.assertTrue(safety["conservative_default"])
        self.assertTrue(safety["requires_explicit_future_enablement"])
        self.assertTrue(safety["requires_backend_validation_before_execution"])
        self.assertTrue(safety["requires_experiment_traceability_before_use"])
        self.assertTrue(safety["requires_read_only_ui_until_validated"])
        self.assertIn("simulation_execution", safety["blocked_until_validated"])
        self.assertIn("replanning_execution", safety["blocked_until_validated"])
        self.assertIn("production_data_mutation", safety["blocked_until_validated"])

    def test_conservative_note_blocks_execution_claims(self) -> None:
        contract = load_contract()
        note = contract["conservative_note"].lower()

        self.assertIn("read-only", note)
        self.assertIn("does not execute simulation", note)
        self.assertIn("does not execute optimization", note)
        self.assertIn("does not inject delays", note)
        self.assertIn("does not trigger re-planning", note)
        self.assertIn("does not dispatch routes", note)
        self.assertIn("does not mutate", note)

    def test_quality_requirements_are_explicit(self) -> None:
        contract = load_contract()
        quality_text = " ".join(contract["quality_requirements"]).lower()

        self.assertIn("valid json", quality_text)
        self.assertIn("read-only", quality_text)
        self.assertIn("playback controls disabled", quality_text)
        self.assertIn("browser-triggered execution", quality_text)
        self.assertIn("delay propagation", quality_text)
        self.assertIn("without requiring a live api server", quality_text)

    def test_related_contracts_connect_current_platform_artifacts(self) -> None:
        contract = load_contract()
        related = contract["related_contracts"]

        self.assertEqual("platform/contracts/simulation_state_contract.json", related["simulation_state_contract"])
        self.assertEqual("platform/contracts/simulation_state_sample.json", related["simulation_state_sample"])
        self.assertEqual("platform/contracts/delay_injection_request_contract.json", related["delay_injection_request_contract"])
        self.assertEqual("platform/contracts/replanning_decision_response_contract.json", related["replanning_decision_response_contract"])
        self.assertEqual("platform/contracts/replanning_decision_response_sample.json", related["replanning_decision_response_sample"])

    def test_contract_text_does_not_claim_operational_enablement(self) -> None:
        contract = load_contract()
        all_text = " ".join(flatten_strings(contract)).lower()

        forbidden_phrases = [
            "ready for production dispatch",
            "executes live simulation",
            "executes optimization",
            "applies route changes",
            "mutates production data"
        ]

        for phrase in forbidden_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, all_text)


if __name__ == "__main__":
    unittest.main()