#include "core/policy/threshold_delay_replanning_policy/threshold_delay_replanning_policy.h"
#include "tests/test_support/test_assertions.h"

static Effect make_delay_effect(
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
    effect.description = "Test delay effect.";

    return effect;
}

void test_threshold_delay_replanning_policy() {
    ThresholdDelayReplanningPolicyConfig config;

    config.max_single_delay_threshold = 30;
    config.total_delay_threshold = 60;

    PolicyEvaluationContext light_context;

    light_context.current_time = 125;
    light_context.effects.push_back(
        make_delay_effect("light_delay_001", 125, 10)
    );

    light_context.effects.push_back(
        make_delay_effect("light_delay_002", 130, 5)
    );

    PolicyDecision light_decision =
        evaluate_threshold_delay_replanning_policy(
            light_context,
            config
        );

    FIELDOPS_EXPECT_EQ(
        light_decision.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(light_decision.decision_time, 125);

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(light_decision.type),
        "DO_NOT_REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(!light_decision.should_replan());

    PolicyEvaluationContext single_delay_context;

    single_delay_context.current_time = 125;
    single_delay_context.effects.push_back(
        make_delay_effect("moderate_delay_001", 125, 50)
    );

    PolicyDecision single_delay_decision =
        evaluate_threshold_delay_replanning_policy(
            single_delay_context,
            config
        );

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(single_delay_decision.type),
        "REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(single_delay_decision.should_replan());

    PolicyEvaluationContext total_delay_context;

    total_delay_context.current_time = 140;
    total_delay_context.effects.push_back(
        make_delay_effect("total_delay_001", 140, 25)
    );

    total_delay_context.effects.push_back(
        make_delay_effect("total_delay_002", 145, 20)
    );

    ThresholdDelayReplanningPolicyConfig total_delay_config;

    total_delay_config.max_single_delay_threshold = 30;
    total_delay_config.total_delay_threshold = 40;

    PolicyDecision total_delay_decision =
        evaluate_threshold_delay_replanning_policy(
            total_delay_context,
            total_delay_config
        );

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(total_delay_decision.type),
        "REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(total_delay_decision.should_replan());
}