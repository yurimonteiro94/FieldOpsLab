from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PATH = (
    REPOSITORY_ROOT
    / "platform"
    / "contracts"
    / "simulation_state_sample.json"
)


class SimulationStateSampleContractTests(unittest.TestCase):
    def load_sample(self) -> dict[str, Any]:
        self.assertTrue(
            SAMPLE_PATH.exists(),
            "simulation_state_sample.json must exist.",
        )

        with SAMPLE_PATH.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        self.assertIsInstance(payload, dict)
        return payload

    def test_sample_is_valid_and_read_only(self) -> None:
        payload = self.load_sample()

        self.assertEqual(payload["schema"], "fieldops_lab.simulation_state_sample")
        self.assertEqual(payload["version"], "0.1.0")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["execution_enabled"])
        self.assertFalse(payload["write_operations_supported"])
        self.assertFalse(payload["browser_triggered_execution_enabled"])
        self.assertFalse(payload["arbitrary_command_execution_allowed"])

    def test_sample_defines_clock_for_visual_simulation(self) -> None:
        payload = self.load_sample()
        clock = payload["clock"]

        self.assertEqual(clock["simulation_id"], "demo_delay_propagation_001")
        self.assertEqual(clock["status"], "paused")
        self.assertEqual(clock["time_unit"], "minutes")
        self.assertLessEqual(clock["start_time"], clock["current_time"])
        self.assertLessEqual(clock["current_time"], clock["end_time"])
        self.assertFalse(clock["can_user_advance_time"])
        self.assertFalse(clock["can_user_inject_delay"])

    def test_sample_defines_map_entities(self) -> None:
        payload = self.load_sample()
        map_payload = payload["map"]

        self.assertEqual(map_payload["coordinate_system"], "normalized_demo_coordinates")
        self.assertGreaterEqual(len(map_payload["depots"]), 1)
        self.assertGreaterEqual(len(map_payload["technicians"]), 2)
        self.assertGreaterEqual(len(map_payload["tasks"]), 5)
        self.assertGreaterEqual(len(map_payload["routes"]), 2)

        technician_ids = {item["id"] for item in map_payload["technicians"]}
        task_ids = {item["id"] for item in map_payload["tasks"]}

        self.assertIn("tech_001", technician_ids)
        self.assertIn("tech_002", technician_ids)
        self.assertIn("task_003", task_ids)

    def test_sample_tracks_delay_propagation(self) -> None:
        payload = self.load_sample()
        timeline = payload["timeline"]

        event_types = {event["type"] for event in timeline}

        self.assertIn("travel_delay_detected", event_types)
        self.assertIn("replanning_evaluation_required", event_types)

        delay_events = [
            event
            for event in timeline
            if int(event.get("delay_minutes", 0)) > 0
        ]

        self.assertGreaterEqual(len(delay_events), 2)

    def test_sample_defines_replanning_decision_without_enabling_execution(self) -> None:
        payload = self.load_sample()
        decision = payload["replanning_decision"]

        self.assertEqual(decision["status"], "evaluation_required")
        self.assertEqual(decision["trigger"], "travel_delay_threshold")
        self.assertTrue(decision["delay_propagation_detected"])

        candidate_policies = decision["candidate_policies"]
        self.assertGreaterEqual(len(candidate_policies), 2)

        for policy in candidate_policies:
            self.assertFalse(policy["execution_enabled"])

        decision_fields = set(decision["decision_fields"])
        self.assertIn("route_stability", decision_fields)
        self.assertIn("computational_cost", decision_fields)
        self.assertIn("practical_equivalence_status", decision_fields)

    def test_sample_keeps_dissertation_scope_narrow(self) -> None:
        payload = self.load_sample()
        research_scope = payload["research_scope"]

        primary_scope = set(research_scope["primary_dissertation_scope"])
        future_perturbations = set(research_scope["future_platform_perturbations"])

        self.assertIn("delay_propagation", primary_scope)
        self.assertIn("travel_delay", primary_scope)
        self.assertIn("service_delay", primary_scope)

        self.assertIn("new_requests", future_perturbations)
        self.assertIn("cancellations", future_perturbations)
        self.assertIn("priority_changes", future_perturbations)

    def test_safety_notes_explicitly_block_execution(self) -> None:
        payload = self.load_sample()
        safety_notes = " ".join(payload["safety_notes"]).lower()

        self.assertIn("read-only", safety_notes)
        self.assertIn("must not trigger optimization", safety_notes)
        self.assertIn("solver calls", safety_notes)
        self.assertIn("file writes", safety_notes)
        self.assertIn("backend jobs", safety_notes)


if __name__ == "__main__":
    unittest.main()