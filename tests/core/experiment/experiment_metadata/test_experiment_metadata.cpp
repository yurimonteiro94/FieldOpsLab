#include "core/experiment/experiment_metadata/experiment_metadata.h"
#include "tests/test_support/test_assertions.h"

void test_experiment_metadata() {
    ExperimentMetadata metadata;

    metadata.experiment_id = "experiment_001";
    metadata.scenario_id = "scenario_A";
    metadata.replication_id = 3;
    metadata.seed = 42;
    metadata.notes = "Metadata test.";

    FIELDOPS_EXPECT_EQ(metadata.experiment_id, "experiment_001");
    FIELDOPS_EXPECT_EQ(metadata.scenario_id, "scenario_A");
    FIELDOPS_EXPECT_EQ(metadata.replication_id, 3);
    FIELDOPS_EXPECT_EQ(metadata.seed, 42);

    FIELDOPS_EXPECT_EQ(
        build_experiment_run_label(metadata),
        "experiment_001"
    );

    metadata.experiment_id = "";

    FIELDOPS_EXPECT_EQ(
        build_experiment_run_label(metadata),
        "scenario_A_rep_3"
    );

    metadata.scenario_id = "";

    FIELDOPS_EXPECT_EQ(
        build_experiment_run_label(metadata),
        "experiment_rep_3"
    );
}