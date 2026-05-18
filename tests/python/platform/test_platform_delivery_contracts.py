import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PLATFORM_PLAN_PATH = PROJECT_ROOT / "docs" / "platform_delivery_plan.md"
PLATFORM_CONTRACT_PATH = (
    PROJECT_ROOT / "platform" / "contracts" / "fieldops_platform_contract.json"
)
API_README_PATH = PROJECT_ROOT / "services" / "api" / "README.md"
WEB_README_PATH = PROJECT_ROOT / "apps" / "web" / "README.md"


class PlatformDeliveryContractTests(unittest.TestCase):
    def test_required_platform_documents_exist(self) -> None:
        required_paths = [
            PLATFORM_PLAN_PATH,
            PLATFORM_CONTRACT_PATH,
            API_README_PATH,
            WEB_README_PATH,
        ]

        for path in required_paths:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                self.assertTrue(path.exists(), f"Missing required platform file: {path}")
                self.assertGreater(
                    path.stat().st_size,
                    0,
                    f"Platform file must not be empty: {path}",
                )

    def test_platform_contract_is_valid_and_conservative(self) -> None:
        contract = json.loads(PLATFORM_CONTRACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            contract["contract_type"],
            "fieldops_lab_platform_contract",
        )
        self.assertEqual(contract["version"], "0.1.0")
        self.assertGreaterEqual(
            int(contract["product_completeness_estimate_percent"]),
            30,
        )
        self.assertLess(
            int(contract["product_completeness_estimate_percent"]),
            50,
        )

        interpretation = contract["conservative_interpretation"].lower()
        self.assertIn("does not mean", interpretation)
        self.assertIn("ready for final users", interpretation)

    def test_platform_contract_defines_required_layers(self) -> None:
        contract = json.loads(PLATFORM_CONTRACT_PATH.read_text(encoding="utf-8"))

        layer_ids = {layer["id"] for layer in contract["layers"]}

        expected_layers = {
            "core_engine",
            "analysis_pipeline",
            "api_service",
            "web_interface",
            "storage",
            "hosting_deployment",
        }

        self.assertTrue(
            expected_layers.issubset(layer_ids),
            f"Missing platform layers: {sorted(expected_layers - layer_ids)}",
        )

    def test_api_draft_is_read_only_and_structured(self) -> None:
        contract = json.loads(PLATFORM_CONTRACT_PATH.read_text(encoding="utf-8"))
        api_draft = contract["api_draft"]

        self.assertTrue(api_draft["initial_read_only_policy"])

        endpoints = api_draft["endpoints"]
        self.assertGreaterEqual(len(endpoints), 4)

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint.get("id")):
                self.assertIn(endpoint["method"], {"GET"})
                self.assertTrue(endpoint["path"].startswith("/api/v1/"))
                self.assertEqual(endpoint["status"], "planned")
                self.assertTrue(endpoint["purpose"])

    def test_execution_policy_rejects_unsafe_initial_behavior(self) -> None:
        contract = json.loads(PLATFORM_CONTRACT_PATH.read_text(encoding="utf-8"))
        execution_policy = contract["execution_policy"]

        self.assertFalse(execution_policy["arbitrary_shell_execution_allowed"])
        self.assertFalse(execution_policy["write_operations_allowed_initially"])
        self.assertTrue(execution_policy["backend_execution_requires_allowlist"])

        required_before_execution = set(
            execution_policy["required_before_execution_endpoint"]
        )
        self.assertIn("approved command allowlist", required_before_execution)
        self.assertIn("input validation", required_before_execution)
        self.assertIn("tests for rejected unsafe operations", required_before_execution)

    def test_platform_documents_do_not_overstate_scientific_maturity(self) -> None:
        combined_text = "\n".join(
            [
                PLATFORM_PLAN_PATH.read_text(encoding="utf-8"),
                API_README_PATH.read_text(encoding="utf-8"),
                WEB_README_PATH.read_text(encoding="utf-8"),
            ]
        ).lower()

        self.assertIn("does not prove scientific validity", combined_text)
        self.assertIn("diagnostic", combined_text)
        self.assertIn("scientific", combined_text)


if __name__ == "__main__":
    unittest.main()