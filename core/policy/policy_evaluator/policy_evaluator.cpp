#include "core/policy/policy_evaluator/policy_evaluator.h"

#include <stdexcept>
#include <string>

#include "core/policy/no_replanning_policy/no_replanning_policy.h"
#include "core/policy/threshold_delay_replanning_policy/threshold_delay_replanning_policy.h"

bool is_supported_policy_id(const std::string& policy_id) {
    return policy_id == "no_replanning_policy_v1" ||
           policy_id == "threshold_delay_replanning_policy_v1";
}

PolicyDecision evaluate_policy(
    const PolicyEvaluationContext& context,
    const PolicyEvaluationConfig& config
) {
    if (config.policy_id == "no_replanning_policy_v1") {
        return evaluate_no_replanning_policy(context);
    }

    if (config.policy_id == "threshold_delay_replanning_policy_v1") {
        ThresholdDelayReplanningPolicyConfig threshold_config =
            config.threshold_delay_config;

        threshold_config.policy_id = config.policy_id;

        return evaluate_threshold_delay_replanning_policy(
            context,
            threshold_config
        );
    }

    throw std::runtime_error(
        "Unsupported policy_id: " + config.policy_id
    );
}