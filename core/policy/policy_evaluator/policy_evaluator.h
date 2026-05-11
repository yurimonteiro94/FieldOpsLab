#pragma once

#include <string>

#include "core/policy/policy/policy.h"
#include "core/policy/threshold_delay_replanning_policy/threshold_delay_replanning_policy.h"

struct PolicyEvaluationConfig {
    std::string policy_id = "no_replanning_policy_v1";

    ThresholdDelayReplanningPolicyConfig threshold_delay_config;
};

bool is_supported_policy_id(const std::string& policy_id);

PolicyDecision evaluate_policy(
    const PolicyEvaluationContext& context,
    const PolicyEvaluationConfig& config = PolicyEvaluationConfig()
);