#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

void test_no_replanning_batch_config_json_loader() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    FIELDOPS_EXPECT_EQ(
        config.batch_id,
        "sample_no_replanning_batch_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.summary_csv_output_path,
        "data/results/sample_no_replanning_batch_summary_001.csv"
    );

    FIELDOPS_EXPECT_EQ(config.experiments.size(), 2);

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].instance_path,
        "data/instances/sample_instance_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].perturbation_plan_path,
        "data/perturbations/sample_perturbations_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[1].planned_solution_output_path,
        "data/results/batch_001_planned_solution_002.json"
    );

    FIELDOPS_EXPECT_TRUE(!config.verbose);
    FIELDOPS_EXPECT_TRUE(!config.export_individual_results);
    FIELDOPS_EXPECT_TRUE(config.export_summary_csv);
}