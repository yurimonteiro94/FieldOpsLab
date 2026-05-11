#include "core/policy/no_replanning_policy/no_replanning_policy.h"
#include "tests/test_support/test_assertions.h"

void test_no_replanning_policy() {
    PolicyEvaluationContext context;

    context.current_time = 125;

    Effect effect;

    effect.effect_id = "effect_001";
    effect.type = EffectType::ADD_TRAVEL_DELAY;
    effect.occurrence_time = 125;
    effect.technician_id = "tech_1";
    effect.task_id = "task_C";
    effect.delay_duration = 50;

    context.effects.push_back(effect);

    PolicyDecision decision =
        evaluate_no_replanning_policy(context);

    FIELDOPS_EXPECT_EQ(decision.policy_id, "no_replanning_policy_v1");
    FIELDOPS_EXPECT_EQ(decision.decision_time, 125);
    FIELDOPS_EXPECT_TRUE(!decision.should_replan());

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(decision.type),
        "DO_NOT_REPLAN"
    );
}