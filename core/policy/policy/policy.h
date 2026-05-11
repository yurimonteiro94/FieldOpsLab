#pragma once

#include <string>
#include <vector>

#include "core/perturbation/effect/effect.h"

enum class PolicyDecisionType {
    DO_NOT_REPLAN,
    REPLAN
};

std::string policy_decision_type_to_string(
    PolicyDecisionType type
);

struct PolicyEvaluationContext {
    int current_time = 0;

    std::vector<Effect> effects;
};

struct PolicyDecision {
    std::string policy_id;

    PolicyDecisionType type = PolicyDecisionType::DO_NOT_REPLAN;

    int decision_time = 0;

    std::string reason;

    bool should_replan() const;
};