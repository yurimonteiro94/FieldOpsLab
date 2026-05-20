import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SERVER_PATH = REPOSITORY_ROOT / "services" / "api" / "fieldops_http_server.py"
SAMPLE_PATH = REPOSITORY_ROOT / "platform" / "contracts" / "simulation_playback_state_sample.json"

ENDPOINT = "/api/v1/simulation-playback-state-sample"


class SimulationPlaybackStateSampleApiEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server_source = SERVER_PATH.read_text(encoding="utf-8")
        with SAMPLE_PATH.open("r", encoding="utf-8") as file:
            cls.sample = json.load(file)

    def test_server_declares_playback_state_sample_endpoint(self) -> None:
        self.assertIn(ENDPOINT, self.server_source)
        self.assertIn("SIMULATION_PLAYBACK_STATE_SAMPLE_PATH", self.server_source)
        self.assertIn("simulation_playback_state_sample.json", self.server_source)

    def test_self_test_exposes_playback_state_sample_over_http(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SERVER_PATH), "--self-test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        output = result.stdout + result.stderr

        self.assertEqual(result.returncode, 0, output)
        self.assertIn(f"{ENDPOINT} 200", output)
        self.assertIn("FieldOps Lab read-only API self-test passed.", output)

    def test_sample_payload_is_read_only_and_disabled(self) -> None:
        self.assertEqual(self.sample["schema"], "fieldops_lab.simulation_playback_state_sample")
        self.assertTrue(self.sample["read_only"])
        self.assertFalse(self.sample["execution_enabled"])
        self.assertFalse(self.sample["write_operations_supported"])
        self.assertFalse(self.sample["browser_triggered_execution_enabled"])

    def test_sample_payload_preserves_delay_propagation_focus(self) -> None:
        scope = self.sample["dissertation_scope"]
        delay_view = self.sample["delay_propagation_view"]

        self.assertEqual(scope["primary_focus"], "delay propagation")
        self.assertIn("travel_delay", scope["included_delay_types"])
        self.assertIn("service_delay", scope["included_delay_types"])
        self.assertIn("delay propagation", delay_view["dissertation_alignment"])

    def test_sample_payload_exposes_disabled_playback_controls(self) -> None:
        controls = self.sample["playback_controls"]

        for control_name in ["play", "pause", "step_forward", "step_backward", "reset"]:
            with self.subTest(control_name=control_name):
                self.assertTrue(controls[control_name]["visible"])
                self.assertFalse(controls[control_name]["enabled"])
                self.assertIn("disabled_reason", controls[control_name])

    def test_sample_payload_exposes_disabled_speed_and_scrubber(self) -> None:
        speed = self.sample["speed_control"]
        scrubber = self.sample["timeline_scrubber"]

        self.assertTrue(speed["visible"])
        self.assertFalse(speed["enabled"])
        self.assertTrue(scrubber["visible"])
        self.assertFalse(scrubber["enabled"])
        self.assertEqual(scrubber["current_value"], self.sample["clock_state"]["current_time"])

    def test_sample_payload_connects_to_decision_preview_without_execution(self) -> None:
        binding = self.sample["decision_preview_binding"]

        self.assertTrue(binding["visible"])
        self.assertFalse(binding["enabled"])
        self.assertFalse(binding["mutation_allowed"])
        self.assertEqual(binding["decision_status"], "not_executed")
        self.assertIn("does not execute", binding["tradeoff_summary"])

    def test_server_source_keeps_endpoint_read_only(self) -> None:
        endpoint_index = self.server_source.find(ENDPOINT)
        self.assertGreater(endpoint_index, -1)

        nearby_source = self.server_source[
            max(0, endpoint_index - 1200) : endpoint_index + 1600
        ].lower()

        forbidden_tokens = [
            "do_post",
            "do_put",
            "do_patch",
            "do_delete",
            "subprocess.run",
            "os.system",
            "popen",
            "write_text",
        ]

        for token in forbidden_tokens:
            with self.subTest(token=token):
                self.assertNotIn(token, nearby_source)


if __name__ == "__main__":
    unittest.main()