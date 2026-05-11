#include "core/policy/policy/policy.h"

std::string policy_decision_type_to_string(
    PolicyDecisionType type
) {
    switch (type) {
        case PolicyDecisionType::DO_NOT_REPLAN:
            return "DO_NOT_REPLAN";

        case PolicyDecisionType::REPLAN:
            return "REPLAN";

        default:
            return "DO_NOT_REPLAN";
    }
}

bool PolicyDecision::should_replan() const {
    return type == PolicyDecisionType::REPLAN;
}