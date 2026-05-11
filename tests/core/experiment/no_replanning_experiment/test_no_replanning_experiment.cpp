#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>

void test_no_replanning_experiment() {
    NoReplanningExperimentConfig config;

    config.metadata.experiment_id = "test_experiment_001";
    config.metadata.scenario_id = "test_scenario_001";
    config.metadata.replication_id = 7;
    config.metadata.seed = 7001;
    config.metadata.notes = "No-replanning experiment metadata test.";

    config.policy_config.policy_id = "no_replanning_policy_v1";

    config.planned_solution_output_path =
        "data/results/test_no_replanning_planned_solution.json";

    config.planned_timeline_output_path =
        "data/results/test_no_replanning_planned_timeline.json";

    config.executed_solution_output_path =
        "data/results/test_no_replanning_executed_solution.json";

    config.executed_timeline_output_path =
        "data/results/test_no_replanning_executed_timeline.json";

    config.comparison_output_path =
        "data/results/test_no_replanning_comparison.json";

    config.experiment_result_output_path =
        "data/results/test_no_replanning_experiment_result.json";

    config.experiment_summary_csv_output_path =
        "data/results/test_no_replanning_experiment_summary.csv";

    config.verbose = false;
    config.export_results = true;

    std::filesystem::remove(config.planned_solution_output_path);
    std::filesystem::remove(config.planned_timeline_output_path);
    std::filesystem::remove(config.executed_solution_output_path);
    std::filesystem::remove(config.executed_timeline_output_path);
    std::filesystem::remove(config.comparison_output_path);
    std::filesystem::remove(config.experiment_result_output_path);
    std::filesystem::remove(config.experiment_summary_csv_output_path);

    NoReplanningExperimentResult result =
        run_no_replanning_experiment(config);

    FIELDOPS_EXPECT_TRUE(result.validation_result.is_valid());

    FIELDOPS_EXPECT_EQ(result.metadata.experiment_id, "test_experiment_001");
    FIELDOPS_EXPECT_EQ(result.metadata.scenario_id, "test_scenario_001");
    FIELDOPS_EXPECT_EQ(result.metadata.replication_id, 7);
    FIELDOPS_EXPECT_EQ(result.metadata.seed, 7001);

    FIELDOPS_EXPECT_EQ(result.planned_solution.status, SolutionStatus::FEASIBLE);
    FIELDOPS_EXPECT_EQ(result.executed_solution.status, SolutionStatus::FEASIBLE);

    FIELDOPS_EXPECT_EQ(
        result.policy_decision.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_TRUE(!result.policy_decision.should_replan());
    FIELDOPS_EXPECT_TRUE(!result.has_replanning_request);

    FIELDOPS_EXPECT_EQ(
        policy_decision_type_to_string(result.policy_decision.type),
        "DO_NOT_REPLAN"
    );

    FIELDOPS_EXPECT_EQ(result.policy_decision.decision_time, 125);

    FIELDOPS_EXPECT_EQ(result.planned_metrics.total_travel_time, 145);
    FIELDOPS_EXPECT_EQ(result.executed_metrics.total_travel_time, 195);

    FIELDOPS_EXPECT_EQ(result.comparison.delta_total_travel_time, 50);
    FIELDOPS_EXPECT_EQ(result.comparison.delta_total_service_time, 30);
    FIELDOPS_EXPECT_EQ(result.comparison.delta_total_waiting_time, -35);
    FIELDOPS_EXPECT_EQ(result.comparison.delta_makespan, 15);

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.planned_solution_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.planned_timeline_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.executed_solution_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.executed_timeline_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.comparison_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.experiment_result_output_path)
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(config.experiment_summary_csv_output_path)
    );

    NoReplanningExperimentConfig threshold_config;

    threshold_config.metadata.experiment_id = "test_threshold_experiment_001";
    threshold_config.metadata.scenario_id = "test_threshold_scenario_001";
    threshold_config.metadata.replication_id = 1;
    threshold_config.metadata.seed = 9001;

    threshold_config.policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    threshold_config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    threshold_config.policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    threshold_config.verbose = false;
    threshold_config.export_results = false;

    NoReplanningExperimentResult threshold_result =
        run_no_replanning_experiment(threshold_config);

    FIELDOPS_EXPECT_TRUE(threshold_result.policy_decision.should_replan());
    FIELDOPS_EXPECT_TRUE(threshold_result.has_replanning_request);

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.request_id,
        "test_threshold_experiment_001_replanning_request"
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.policy_decision,
        "REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(
        replanning_request_has_work(
            threshold_result.replanning_request
        )
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.completed_task_count(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.locked_task_count(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_request.candidate_task_count(),
        1
    );
}