#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>

void test_no_replanning_batch_experiment() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = true;
    config.export_aggregate_csv = true;
    config.export_ranking_csv = true;
    config.export_result_json = true;

    config.summary_csv_output_path =
        "data/results/test_no_replanning_batch_summary.csv";

    config.aggregate_csv_output_path =
        "data/results/test_no_replanning_batch_aggregate_summary_from_batch.csv";

    config.ranking_csv_output_path =
        "data/results/test_no_replanning_batch_ranking_from_batch.csv";

    config.result_json_output_path =
        "data/results/test_no_replanning_batch_result_from_batch.json";

    std::filesystem::remove(config.summary_csv_output_path);
    std::filesystem::remove(config.aggregate_csv_output_path);
    std::filesystem::remove(config.ranking_csv_output_path);
    std::filesystem::remove(config.result_json_output_path);

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    FIELDOPS_EXPECT_EQ(
        result.batch_id,
        "sample_no_replanning_batch_001"
    );

    FIELDOPS_EXPECT_EQ(result.experiment_count(), 12);
    FIELDOPS_EXPECT_EQ(result.results.size(), 12);

    FIELDOPS_EXPECT_TRUE(result.summary_csv_was_written);
    FIELDOPS_EXPECT_TRUE(result.aggregate_csv_was_written);
    FIELDOPS_EXPECT_TRUE(result.ranking_csv_was_written);
    FIELDOPS_EXPECT_TRUE(result.result_json_was_written);

    FIELDOPS_EXPECT_EQ(
        result.summary_csv_output_path,
        "data/results/test_no_replanning_batch_summary.csv"
    );

    FIELDOPS_EXPECT_EQ(
        result.aggregate_csv_output_path,
        "data/results/test_no_replanning_batch_aggregate_summary_from_batch.csv"
    );

    FIELDOPS_EXPECT_EQ(
        result.ranking_csv_output_path,
        "data/results/test_no_replanning_batch_ranking_from_batch.csv"
    );

    FIELDOPS_EXPECT_EQ(
        result.result_json_output_path,
        "data/results/test_no_replanning_batch_result_from_batch.json"
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.summary_csv_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.aggregate_csv_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.ranking_csv_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.result_json_output_path)
    );

    FIELDOPS_EXPECT_EQ(
        result.results[0].metadata.experiment_id,
        "batch_001_no_replanning_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        result.results[0].policy_decision.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        result.results[0].replanning_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    FIELDOPS_EXPECT_EQ(
        result.results[4].metadata.experiment_id,
        "batch_001_threshold_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        result.results[4].policy_decision.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[4].policy_decision.should_replan()
    );

    FIELDOPS_EXPECT_EQ(
        result.results[4].replanning_result.status,
        ReplanningResultStatus::NOT_IMPLEMENTED
    );

    FIELDOPS_EXPECT_EQ(
        result.results[7].metadata.experiment_id,
        "batch_001_threshold_greedy_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        result.results[7].replanning_result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[7].replanning_result.has_new_solution()
    );

    FIELDOPS_EXPECT_EQ(
        result.results[11].metadata.experiment_id,
        "batch_001_threshold_greedy_reassignment_001"
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].policy_decision.should_replan()
    );

    FIELDOPS_EXPECT_EQ(
        result.results[11].replanning_result.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        result.results[11].replanning_result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].replanning_result.has_new_solution()
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].replanning_result.is_successful()
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].replanning_result_was_applied_to_execution
    );

    FIELDOPS_EXPECT_EQ(
        result.results[11].execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].comparison.delta_total_travel_time <
        result.results[9].comparison.delta_total_travel_time
    );

    FIELDOPS_EXPECT_TRUE(
        result.results[11].comparison.delta_objective_value <
        result.results[9].comparison.delta_objective_value
    );
}