#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "tests/test_support/test_assertions.h"

void test_perturbation_json_loader() {
    PerturbationPlan plan = load_perturbation_plan_from_json(
        "data/perturbations/sample_perturbations_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        plan.perturbation_plan_id,
        "sample_perturbations_001"
    );

    FIELDOPS_EXPECT_EQ(plan.perturbations.size(), 2);

    FIELDOPS_EXPECT_EQ(
        plan.perturbations[0].perturbation_id,
        "travel_delay_001"
    );

    FIELDOPS_EXPECT_TRUE(
        plan.perturbations[0].type == PerturbationType::TRAVEL_DELAY
    );

    FIELDOPS_EXPECT_EQ(
        plan.perturbations[0].delay_duration,
        25
    );

    FIELDOPS_EXPECT_EQ(
        plan.perturbations[1].perturbation_id,
        "service_delay_001"
    );

    FIELDOPS_EXPECT_TRUE(
        plan.perturbations[1].type == PerturbationType::SERVICE_DELAY
    );

    FIELDOPS_EXPECT_EQ(
        plan.perturbations[1].delay_duration,
        30
    );
}