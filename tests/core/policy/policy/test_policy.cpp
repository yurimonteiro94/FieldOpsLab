#include "core/policy/policy/policy.h"
#include "tests/test_support/test_assertions.h"

void test_policy() {
    PolicyDecision decision;

    decision.policy_id = "test_policy";
    decision.type = PolicyDecisionType::DO_NOT_REPLAN;
    decision.decision_time = 100;
    decision.reason = "Test decision.";

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(decision.type),
        "DO_NOT_REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(!decision.should_replan());

    decision.type = PolicyDecisionType::REPLAN;

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(decision.type),
        "REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(decision.should_replan());
}