#include "core/policy/threshold_delay_replanning_policy/threshold_delay_replanning_policy.h"

#include <string>

static int get_max_delay_duration(const std::vector<Effect>& effects) {
    int max_delay = 0;

    for (const auto& effect : effects) {
        if (effect.delay_duration > max_delay) {
            max_delay = effect.delay_duration;
        }
    }

    return max_delay;
}

static int get_total_delay_duration(const std::vector<Effect>& effects) {
    int total_delay = 0;

    for (const auto& effect : effects) {
        if (effect.delay_duration > 0) {
            total_delay += effect.delay_duration;
        }
    }

    return total_delay;
}

PolicyDecision evaluate_threshold_delay_replanning_policy(
    const PolicyEvaluationContext& context,
    const ThresholdDelayReplanningPolicyConfig& config
) {
    PolicyDecision decision;

    decision.policy_id = config.policy_id;
    decision.decision_time = context.current_time;

    const int max_delay = get_max_delay_duration(context.effects);
    const int total_delay = get_total_delay_duration(context.effects);

    if (config.replan_when_single_delay_reaches_threshold &&
        max_delay >= config.max_single_delay_threshold) {
        decision.type = PolicyDecisionType::REPLAN;
        decision.reason =
            "Maximum individual delay reached the replanning threshold. " +
            std::string("max_delay=") +
            std::to_string(max_delay) +
            ", threshold=" +
            std::to_string(config.max_single_delay_threshold) +
            ".";

        return decision;
    }

    if (config.replan_when_total_delay_reaches_threshold &&
        total_delay >= config.total_delay_threshold) {
        decision.type = PolicyDecisionType::REPLAN;
        decision.reason =
            "Total delay reached the replanning threshold. " +
            std::string("total_delay=") +
            std::to_string(total_delay) +
            ", threshold=" +
            std::to_string(config.total_delay_threshold) +
            ".";

        return decision;
    }

    decision.type = PolicyDecisionType::DO_NOT_REPLAN;
    decision.reason =
        "Observed delays did not reach any replanning threshold. " +
        std::string("max_delay=") +
        std::to_string(max_delay) +
        ", total_delay=" +
        std::to_string(total_delay) +
        ".";

    return decision;
}