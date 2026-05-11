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

    FIELDOPS_EXPECT_EQ(config.experiments.size(), 3);

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].metadata.experiment_id,
        "batch_001_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].metadata.scenario_id,
        "sample_delay_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].metadata.seed,
        101
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].perturbation_plan_path,
        "data/perturbations/sample_perturbations_light_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[1].metadata.experiment_id,
        "batch_001_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[1].metadata.scenario_id,
        "sample_delay_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[1].metadata.seed,
        201
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[1].perturbation_plan_path,
        "data/perturbations/sample_perturbations_moderate_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[2].metadata.experiment_id,
        "batch_001_severe_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[2].metadata.scenario_id,
        "sample_delay_severe_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[2].metadata.seed,
        301
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[2].perturbation_plan_path,
        "data/perturbations/sample_perturbations_severe_001.json"
    );

    FIELDOPS_EXPECT_TRUE(!config.verbose);
    FIELDOPS_EXPECT_TRUE(!config.export_individual_results);
    FIELDOPS_EXPECT_TRUE(config.export_summary_csv);
}