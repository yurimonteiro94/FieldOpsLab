#include "core/policy/policy_evaluator/policy_evaluator.h"
#include "tests/test_support/test_assertions.h"

static Effect make_policy_evaluator_delay_effect(
    const std::string& effect_id,
    int occurrence_time,
    int delay_duration
) {
    Effect effect;

    effect.effect_id = effect_id;
    effect.type = EffectType::ADD_TRAVEL_DELAY;
    effect.occurrence_time = occurrence_time;
    effect.technician_id = "tech_1";
    effect.task_id = "task_C";
    effect.from_location_id = "task_A_location";
    effect.to_location_id = "task_C_location";
    effect.delay_duration = delay_duration;
    effect.description = "Policy evaluator test delay effect.";

    return effect;
}

void test_policy_evaluator() {
    FIELDOPS_EXPECT_TRUE(
        is_supported_policy_id("no_replanning_policy_v1")
    );

    FIELDOPS_EXPECT_TRUE(
        is_supported_policy_id("threshold_delay_replanning_policy_v1")
    );

    FIELDOPS_EXPECT_TRUE(
        !is_supported_policy_id("unknown_policy")
    );

    PolicyEvaluationContext context;

    context.current_time = 125;

    context.effects.push_back(
        make_policy_evaluator_delay_effect("delay_001", 125, 50)
    );

    PolicyEvaluationConfig no_replanning_config;

    no_replanning_config.policy_id = "no_replanning_policy_v1";

    PolicyDecision no_replanning_decision =
        evaluate_policy(context, no_replanning_config);

    FIELDOPS_EXPECT_EQ(
        no_replanning_decision.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_TRUE(!no_replanning_decision.should_replan());

    PolicyEvaluationConfig threshold_config;

    threshold_config.policy_id = "threshold_delay_replanning_policy_v1";
    threshold_config.threshold_delay_config.max_single_delay_threshold = 30;
    threshold_config.threshold_delay_config.total_delay_threshold = 60;

    PolicyDecision threshold_decision =
        evaluate_policy(context, threshold_config);

    FIELDOPS_EXPECT_EQ(
        threshold_decision.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_TRUE(threshold_decision.should_replan());

    PolicyEvaluationContext light_context;

    light_context.current_time = 125;

    light_context.effects.push_back(
        make_policy_evaluator_delay_effect("light_delay_001", 125, 10)
    );

    light_context.effects.push_back(
        make_policy_evaluator_delay_effect("light_delay_002", 130, 5)
    );

    PolicyDecision light_threshold_decision =
        evaluate_policy(light_context, threshold_config);

    FIELDOPS_EXPECT_EQ(
        light_threshold_decision.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_TRUE(!light_threshold_decision.should_replan());
}