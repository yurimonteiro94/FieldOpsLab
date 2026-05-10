#include "core/perturbation/service_delay_perturbation/service_delay_perturbation.h"
#include "tests/test_support/test_assertions.h"

#include <stdexcept>

void test_service_delay_perturbation() {
    Perturbation perturbation;

    perturbation.perturbation_id = "service_delay_001";
    perturbation.type = PerturbationType::SERVICE_DELAY;
    perturbation.occurrence_time = 100;
    perturbation.technician_id = "tech_1";
    perturbation.task_id = "task_A";
    perturbation.from_location_id = "";
    perturbation.to_location_id = "task_A_location";
    perturbation.delay_duration = 30;
    perturbation.description = "Service delay during task A.";

    FIELDOPS_EXPECT_TRUE(
        is_valid_service_delay_perturbation(perturbation)
    );

    Effect effect = build_service_delay_effect(perturbation);

    FIELDOPS_EXPECT_EQ(effect.effect_id, "effect_from_service_delay_001");
    FIELDOPS_EXPECT_EQ(effect.type, EffectType::ADD_SERVICE_DELAY);
    FIELDOPS_EXPECT_EQ(effect.occurrence_time, 100);
    FIELDOPS_EXPECT_EQ(effect.technician_id, "tech_1");
    FIELDOPS_EXPECT_EQ(effect.task_id, "task_A");
    FIELDOPS_EXPECT_EQ(effect.to_location_id, "task_A_location");
    FIELDOPS_EXPECT_EQ(effect.delay_duration, 30);

    perturbation.delay_duration = 0;

    FIELDOPS_EXPECT_TRUE(
        !is_valid_service_delay_perturbation(perturbation)
    );

    bool threw_exception = false;

    try {
        build_service_delay_effect(perturbation);
    } catch (const std::runtime_error&) {
        threw_exception = true;
    }

    FIELDOPS_EXPECT_TRUE(threw_exception);
}