#include "core/perturbation/travel_delay_perturbation/travel_delay_perturbation.h"
#include "tests/test_support/test_assertions.h"

#include <stdexcept>

void test_travel_delay_perturbation() {
    Perturbation perturbation;

    perturbation.perturbation_id = "travel_delay_001";
    perturbation.type = PerturbationType::TRAVEL_DELAY;
    perturbation.occurrence_time = 90;
    perturbation.technician_id = "tech_1";
    perturbation.task_id = "task_A";
    perturbation.from_location_id = "depot";
    perturbation.to_location_id = "task_A_location";
    perturbation.delay_duration = 25;
    perturbation.description = "Travel delay between depot and task A.";

    FIELDOPS_EXPECT_TRUE(
        is_valid_travel_delay_perturbation(perturbation)
    );

    Effect effect = build_travel_delay_effect(perturbation);

    FIELDOPS_EXPECT_EQ(effect.effect_id, "effect_from_travel_delay_001");
    FIELDOPS_EXPECT_EQ(effect.type, EffectType::ADD_TRAVEL_DELAY);
    FIELDOPS_EXPECT_EQ(effect.occurrence_time, 90);
    FIELDOPS_EXPECT_EQ(effect.technician_id, "tech_1");
    FIELDOPS_EXPECT_EQ(effect.task_id, "task_A");
    FIELDOPS_EXPECT_EQ(effect.from_location_id, "depot");
    FIELDOPS_EXPECT_EQ(effect.to_location_id, "task_A_location");
    FIELDOPS_EXPECT_EQ(effect.delay_duration, 25);

    perturbation.delay_duration = 0;

    FIELDOPS_EXPECT_TRUE(
        !is_valid_travel_delay_perturbation(perturbation)
    );

    bool threw_exception = false;

    try {
        build_travel_delay_effect(perturbation);
    } catch (const std::runtime_error&) {
        threw_exception = true;
    }

    FIELDOPS_EXPECT_TRUE(threw_exception);
}