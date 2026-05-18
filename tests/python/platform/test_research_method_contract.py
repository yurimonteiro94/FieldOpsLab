from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESEARCH_FRAMING_PATH = PROJECT_ROOT / "platform" / "research_framing.md"
RESEARCH_METHOD_CONTRACT_PATH = (
    PROJECT_ROOT / "platform" / "contracts" / "research_method_contract.json"
)


class ResearchMethodContractTests(unittest.TestCase):
    def load_contract(self) -> dict[str, Any]:
        self.assertTrue(RESEARCH_METHOD_CONTRACT_PATH.exists())

        return json.loads(
            RESEARCH_METHOD_CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def test_research_framing_document_exists_and_names_core_elements(self) -> None:
        self.assertTrue(RESEARCH_FRAMING_PATH.exists())

        text = RESEARCH_FRAMING_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("project question", text)
        self.assertIn("research gap", text)
        self.assertIn("what the master's work does", text)
        self.assertIn("what the system does", text)
        self.assertIn("what has already been done", text)
        self.assertIn("what still needs to be done", text)
        self.assertIn("practical equivalence", text)
        self.assertIn("fuzzy logic is not mandatory", text)

    def test_research_contract_is_conservative_about_contribution(self) -> None:
        contract = self.load_contract()

        self.assertEqual(
            contract["contract"],
            "fieldops_lab_research_method_contract",
        )
        self.assertEqual(contract["scientific_maturity"], "diagnostic_foundation")
        self.assertTrue(contract["read_only"])

        claims = contract["contribution_claims"]

        self.assertFalse(claims["claims_new_algorithm_as_primary_contribution"])
        self.assertFalse(claims["claims_finished_scientific_validation"])
        self.assertTrue(claims["claims_policy_decision_framework"])
        self.assertTrue(claims["claims_reproducible_experimental_platform"])

    def test_research_gap_focuses_on_policy_decision_framework(self) -> None:
        contract = self.load_contract()

        question = contract["project_question"]
        gap = contract["research_gap"]

        self.assertTrue(question["decision_focus"])
        self.assertFalse(question["solver_only_focus"])
        self.assertTrue(gap["general_area_already_studied"])

        specific_gap = gap["specific_gap"].lower()

        self.assertIn("replicable", specific_gap)
        self.assertIn("decision framework", specific_gap)
        self.assertIn("replanning policies", specific_gap)
        self.assertIn("scenario class", specific_gap)

    def test_decision_method_requires_practical_equivalence(self) -> None:
        contract = self.load_contract()

        requirements = contract["decision_method_requirements"]

        self.assertTrue(requirements["compare_multiple_policies"])
        self.assertTrue(requirements["use_common_scenario_set"])
        self.assertTrue(requirements["use_common_perturbation_set"])
        self.assertTrue(requirements["consider_performance_metrics"])
        self.assertTrue(requirements["consider_stability_metrics"])
        self.assertTrue(requirements["consider_computational_cost"])
        self.assertTrue(requirements["identify_practical_equivalence"])
        self.assertTrue(requirements["avoid_overclaiming_small_average_differences"])
        self.assertTrue(requirements["prefer_simpler_policy_when_practically_equivalent"])

    def test_fuzzy_logic_is_allowed_but_not_forced(self) -> None:
        contract = self.load_contract()

        fuzzy = contract["fuzzy_logic_position"]

        self.assertFalse(fuzzy["mandatory"])
        self.assertTrue(fuzzy["allowed"])
        self.assertTrue(fuzzy["use_only_if_defensible"])

        alternatives = fuzzy["preferred_baseline_alternatives"]

        self.assertIn("statistical_comparison", alternatives)
        self.assertIn("practical_equivalence_thresholds", alternatives)
        self.assertIn("dominance_rules", alternatives)
        self.assertIn("multi_criteria_scoring", alternatives)

    def test_risk_controls_prevent_overclaiming_and_unsafe_execution(self) -> None:
        contract = self.load_contract()

        risk_controls = contract["risk_controls"]

        self.assertTrue(risk_controls["must_not_expose_execution_from_web_dashboard_yet"])
        self.assertTrue(risk_controls["must_not_claim_scientific_validity_from_tests_only"])
        self.assertTrue(
            risk_controls[
                "must_not_store_real_company_sensitive_data_without_access_control"
            ]
        )
        self.assertTrue(risk_controls["must_keep_generated_reports_reproducible"])


if __name__ == "__main__":
    unittest.main()