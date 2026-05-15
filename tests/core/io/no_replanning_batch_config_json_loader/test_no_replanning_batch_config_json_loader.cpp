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

    FIELDOPS_EXPECT_EQ(
        config.aggregate_csv_output_path,
        "data/results/sample_no_replanning_batch_aggregate_summary_001.csv"
    );

    FIELDOPS_EXPECT_EQ(
        config.result_json_output_path,
        "data/results/sample_no_replanning_batch_result_001.json"
    );

    FIELDOPS_EXPECT_TRUE(!config.verbose);
    FIELDOPS_EXPECT_TRUE(!config.export_individual_results);
    FIELDOPS_EXPECT_TRUE(config.export_summary_csv);
    FIELDOPS_EXPECT_TRUE(config.export_aggregate_csv);
    FIELDOPS_EXPECT_TRUE(config.export_result_json);

    FIELDOPS_EXPECT_EQ(config.experiments.size(), 12);

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].metadata.experiment_id,
        "batch_001_no_replanning_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].policy_config.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].replanning_engine_config.method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[0].perturbation_plan_path,
        "data/perturbations/sample_perturbations_light_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[3].metadata.experiment_id,
        "batch_001_threshold_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[3].policy_config.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[3].replanning_engine_config.method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[3]
            .policy_config
            .threshold_delay_config
            .max_single_delay_threshold,
        30
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[3]
            .policy_config
            .threshold_delay_config
            .total_delay_threshold,
        60
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[6].metadata.experiment_id,
        "batch_001_threshold_greedy_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[6].replanning_engine_config.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[8].metadata.experiment_id,
        "batch_001_threshold_greedy_severe_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[8].metadata.seed,
        901
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[8].perturbation_plan_path,
        "data/perturbations/sample_perturbations_severe_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[8].replanning_engine_config.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[9].metadata.experiment_id,
        "batch_001_no_replanning_reassignment_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[9].metadata.scenario_id,
        "sample_delay_reassignment_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[9].perturbation_plan_path,
        "data/perturbations/sample_perturbations_reassignment_001.json"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[11].metadata.experiment_id,
        "batch_001_threshold_greedy_reassignment_001"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[11].replanning_engine_config.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        config.experiments[11].metadata.seed,
        1201
    );
}