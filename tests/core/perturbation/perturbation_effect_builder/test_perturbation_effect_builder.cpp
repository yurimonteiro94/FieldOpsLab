#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "tests/test_support/test_assertions.h"

#include <stdexcept>
#include <vector>

void test_perturbation_effect_builder() {
    PerturbationPlan plan = load_perturbation_plan_from_json(
        "data/perturbations/sample_perturbations_001.json"
    );

    std::vector<Effect> effects =
        build_effects_from_perturbation_plan(plan);

    FIELDOPS_EXPECT_EQ(effects.size(), 2);

    FIELDOPS_EXPECT_EQ(
        effects[0].effect_id,
        "effect_from_travel_delay_001"
    );

    FIELDOPS_EXPECT_EQ(
        effects[0].type,
        EffectType::ADD_TRAVEL_DELAY
    );

    FIELDOPS_EXPECT_EQ(effects[0].occurrence_time, 125);
    FIELDOPS_EXPECT_EQ(effects[0].from_location_id, "task_A_location");
    FIELDOPS_EXPECT_EQ(effects[0].to_location_id, "task_C_location");
    FIELDOPS_EXPECT_EQ(effects[0].delay_duration, 50);

    FIELDOPS_EXPECT_EQ(
        effects[1].effect_id,
        "effect_from_service_delay_001"
    );

    FIELDOPS_EXPECT_EQ(
        effects[1].type,
        EffectType::ADD_SERVICE_DELAY
    );

    FIELDOPS_EXPECT_EQ(effects[1].occurrence_time, 130);
    FIELDOPS_EXPECT_EQ(effects[1].delay_duration, 30);

    Perturbation unknown_perturbation;

    unknown_perturbation.perturbation_id = "unknown_001";
    unknown_perturbation.type = PerturbationType::UNKNOWN;

    bool threw_exception = false;

    try {
        build_effect_from_perturbation(unknown_perturbation);
    } catch (const std::runtime_error&) {
        threw_exception = true;
    }

    FIELDOPS_EXPECT_TRUE(threw_exception);
}