#pragma once

#include "core/policy/policy/policy.h"

struct ThresholdDelayReplanningPolicyConfig {
    std::string policy_id = "threshold_delay_replanning_policy_v1";

    int max_single_delay_threshold = 30;
    int total_delay_threshold = 60;

    bool replan_when_single_delay_reaches_threshold = true;
    bool replan_when_total_delay_reaches_threshold = true;
};

PolicyDecision evaluate_threshold_delay_replanning_policy(
    const PolicyEvaluationContext& context,
    const ThresholdDelayReplanningPolicyConfig& config =
        ThresholdDelayReplanningPolicyConfig()
);