#include "core/policy/no_replanning_policy/no_replanning_policy.h"

PolicyDecision evaluate_no_replanning_policy(
    const PolicyEvaluationContext& context
) {
    PolicyDecision decision;

    decision.policy_id = "no_replanning_policy_v1";
    decision.type = PolicyDecisionType::DO_NOT_REPLAN;
    decision.decision_time = context.current_time;
    decision.reason = "No replanning policy always keeps the current plan.";

    return decision;
}