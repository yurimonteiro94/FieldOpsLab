#include "core/perturbation/effect/effect.h"
#include "tests/test_support/test_assertions.h"

void test_effect() {
    Effect effect = build_effect_from_perturbation_id(
        "effect_001",
        EffectType::ADD_TRAVEL_DELAY,
        90,
        "tech_1",
        "task_A",
        "depot",
        "task_A_location",
        25,
        "Add travel delay to technician movement."
    );

    FIELDOPS_EXPECT_EQ(effect.effect_id, "effect_001");
    FIELDOPS_EXPECT_EQ(effect_type_to_string(effect.type), "ADD_TRAVEL_DELAY");
    FIELDOPS_EXPECT_EQ(effect.occurrence_time, 90);
    FIELDOPS_EXPECT_EQ(effect.technician_id, "tech_1");
    FIELDOPS_EXPECT_EQ(effect.task_id, "task_A");
    FIELDOPS_EXPECT_EQ(effect.delay_duration, 25);
}