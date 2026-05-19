import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "simulation_playback_state_sample.json"


class SimulationPlaybackStateSampleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with SAMPLE_PATH.open("r", encoding="utf-8") as file:
            cls.sample = json.load(file)

    def test_sample_is_valid_read_only_and_disabled(self) -> None:
        self.assertEqual(self.sample["schema"], "fieldops_lab.simulation_playback_state_sample")
        self.assertEqual(self.sample["version"], "0.1.0")
        self.assertTrue(self.sample["read_only"])
        self.assertFalse(self.sample["execution_enabled"])
        self.assertFalse(self.sample["write_operations_supported"])
        self.assertFalse(self.sample["browser_triggered_execution_enabled"])

    def test_sample_links_current_contract_artifacts(self) -> None:
        identity = self.sample["sample_identity"]

        self.assertEqual(identity["simulation_id"], "demo_delay_propagation_001")
        self.assertEqual(
            identity["source_simulation_state_sample"],
            "platform/contracts/simulation_state_sample.json",
        )
        self.assertEqual(
            identity["source_playback_control_contract"],
            "platform/contracts/simulation_playback_control_contract.json",
        )
        self.assertEqual(
            identity["source_decision_response_sample"],
            "platform/contracts/replanning_decision_response_sample.json",
        )

    def test_clock_state_is_paused_and_deterministic(self) -> None:
        clock = self.sample["clock_state"]

        self.assertEqual(clock["status"], "paused")
        self.assertEqual(clock["start_time"], 480)
        self.assertEqual(clock["current_time"], 615)
        self.assertEqual(clock["end_time"], 1020)
        self.assertEqual(clock["display_time"], "10:15")
        self.assertFalse(clock["mutation_allowed"])
        self.assertGreaterEqual(clock["progress_ratio"], 0.0)
        self.assertLessEqual(clock["progress_ratio"], 1.0)

    def test_playback_controls_are_visible_but_disabled(self) -> None:
        controls = self.sample["playback_controls"]

        for control_name in ["play", "pause", "step_forward", "step_backward", "reset"]:
            with self.subTest(control_name=control_name):
                self.assertTrue(controls[control_name]["visible"])
                self.assertFalse(controls[control_name]["enabled"])
                self.assertIn("disabled_reason", controls[control_name])

    def test_speed_control_is_contract_only(self) -> None:
        speed = self.sample["speed_control"]

        self.assertTrue(speed["visible"])
        self.assertFalse(speed["enabled"])
        self.assertEqual(speed["selected_multiplier"], 1.0)
        self.assertIn(1.0, speed["available_multipliers"])
        self.assertIn("preview-only", speed["disabled_reason"])

    def test_timeline_scrubber_is_visible_but_does_not_mutate_state(self) -> None:
        scrubber = self.sample["timeline_scrubber"]

        self.assertTrue(scrubber["visible"])
        self.assertFalse(scrubber["enabled"])
        self.assertEqual(scrubber["current_value"], self.sample["clock_state"]["current_time"])
        self.assertEqual(scrubber["minimum_value"], self.sample["clock_state"]["start_time"])
        self.assertEqual(scrubber["maximum_value"], self.sample["clock_state"]["end_time"])
        self.assertGreaterEqual(scrubber["normalized_position"], 0.0)
        self.assertLessEqual(scrubber["normalized_position"], 1.0)

    def test_visible_window_highlights_delay_entities(self) -> None:
        window = self.sample["visible_window"]

        self.assertLess(window["window_start_time"], self.sample["clock_state"]["current_time"])
        self.assertGreater(window["window_end_time"], self.sample["clock_state"]["current_time"])
        self.assertEqual(window["selected_event_id"], "event_service_delay_task_002")
        self.assertIn("technician_001", window["highlighted_entities"])
        self.assertIn("task_002", window["highlighted_entities"])

    def test_delay_propagation_view_tracks_downstream_effects(self) -> None:
        view = self.sample["delay_propagation_view"]

        self.assertTrue(view["visible"])
        self.assertEqual(view["primary_delay_type"], "service_delay")
        self.assertGreater(view["delay_minutes"], 0)
        self.assertIn("task_002", view["affected_task_ids"])
        self.assertIn("task_003", view["affected_task_ids"])
        self.assertIn("technician_001", view["affected_technician_ids"])
        self.assertGreaterEqual(len(view["downstream_effects"]), 2)
        self.assertIn("delay propagation", view["dissertation_alignment"])

    def test_decision_preview_binding_is_not_execution(self) -> None:
        binding = self.sample["decision_preview_binding"]

        self.assertTrue(binding["visible"])
        self.assertFalse(binding["enabled"])
        self.assertFalse(binding["mutation_allowed"])
        self.assertEqual(binding["decision_status"], "not_executed")
        self.assertEqual(binding["recommended_policy_id"], "threshold_delay_replanning_policy")
        self.assertIn("does not execute", binding["tradeoff_summary"])

    def test_dissertation_scope_stays_narrow(self) -> None:
        scope = self.sample["dissertation_scope"]

        self.assertEqual(scope["primary_focus"], "delay propagation")
        self.assertIn("travel_delay", scope["included_delay_types"])
        self.assertIn("service_delay", scope["included_delay_types"])
        self.assertIn("new_requests", scope["excluded_from_current_scope"])
        self.assertIn("cancellations", scope["excluded_from_current_scope"])
        self.assertIn("priority_changes", scope["excluded_from_current_scope"])

    def test_quality_requirements_are_explicit(self) -> None:
        requirements = " ".join(self.sample["ui_quality_requirements"]).lower()

        self.assertIn("disabled", requirements)
        self.assertIn("delay propagation", requirements)
        self.assertIn("deterministic", requirements)
        self.assertIn("inspection-only", requirements)

    def test_safety_requirements_are_conservative(self) -> None:
        safety = " ".join(self.sample["safety_requirements"]).lower()

        self.assertIn("post", safety)
        self.assertIn("simulation execution", safety)
        self.assertIn("mutate files", safety)
        self.assertIn("production dispatch", safety)

    def test_validation_rules_block_false_execution_claims(self) -> None:
        validation = " ".join(self.sample["validation_rules"]).lower()
        note = self.sample["conservative_note"].lower()

        self.assertIn("read_only must be true", validation)
        self.assertIn("execution_enabled must be false", validation)
        self.assertIn("playback controls must be visible but disabled", validation)
        self.assertIn("does not start", note)
        self.assertIn("does not apply", note)


if __name__ == "__main__":
    unittest.main()