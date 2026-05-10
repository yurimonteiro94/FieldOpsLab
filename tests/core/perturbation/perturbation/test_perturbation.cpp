#include "core/perturbation/perturbation/perturbation.h"
#include "tests/test_support/test_assertions.h"

void test_perturbation() {
    Perturbation perturbation;

    perturbation.perturbation_id = "pert_001";
    perturbation.type = PerturbationType::TRAVEL_DELAY;
    perturbation.occurrence_time = 90;
    perturbation.technician_id = "tech_1";
    perturbation.task_id = "task_A";
    perturbation.from_location_id = "depot";
    perturbation.to_location_id = "task_A_location";
    perturbation.delay_duration = 25;

    FIELDOPS_EXPECT_EQ(
        perturbation_type_to_string(perturbation.type),
        "TRAVEL_DELAY"
    );

    FIELDOPS_EXPECT_TRUE(is_delay_perturbation(perturbation));

    perturbation.type = PerturbationType::TASK_CANCELLATION;

    FIELDOPS_EXPECT_TRUE(!is_delay_perturbation(perturbation));
}