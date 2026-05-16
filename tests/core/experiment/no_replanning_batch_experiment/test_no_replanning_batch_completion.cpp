#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

void test_no_replanning_batch_completion() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = false;
    config.export_aggregate_csv = false;
    config.export_ranking_csv = false;
    config.export_recommendation_csv = false;
    config.export_result_json = false;

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    FIELDOPS_EXPECT_EQ(result.configured_experiment_count, 12);
    FIELDOPS_EXPECT_EQ(result.completed_experiment_count, 12);
    FIELDOPS_EXPECT_EQ(result.experiment_count(), 12);
    FIELDOPS_EXPECT_TRUE(result.completion_percent == 100.0);
    FIELDOPS_EXPECT_TRUE(result.is_complete);

    NoReplanningBatchExperimentConfig empty_config;

    empty_config.verbose = false;
    empty_config.export_individual_results = false;
    empty_config.export_summary_csv = false;
    empty_config.export_aggregate_csv = false;
    empty_config.export_ranking_csv = false;
    empty_config.export_recommendation_csv = false;
    empty_config.export_result_json = false;
    empty_config.experiments.clear();

    NoReplanningBatchExperimentResult empty_result =
        run_no_replanning_batch_experiment(empty_config);

    FIELDOPS_EXPECT_EQ(empty_result.configured_experiment_count, 0);
    FIELDOPS_EXPECT_EQ(empty_result.completed_experiment_count, 0);
    FIELDOPS_EXPECT_EQ(empty_result.experiment_count(), 0);
    FIELDOPS_EXPECT_TRUE(empty_result.completion_percent == 100.0);
    FIELDOPS_EXPECT_TRUE(empty_result.is_complete);
}