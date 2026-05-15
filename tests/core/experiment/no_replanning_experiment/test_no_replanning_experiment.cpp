#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <string>

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

    config.replanning_request_output_path =
        "data/results/test_no_replanning_replanning_request.json";

    config.verbose = false;
    config.export_results = true;

    std::filesystem::remove(config.planned_solution_output_path);
    std::filesystem::remove(config.planned_timeline_output_path);
    std::filesystem::remove(config.executed_solution_output_path);
    std::filesystem::remove(config.executed_timeline_output_path);
    std::filesystem::remove(config.comparison_output_path);
    std::filesystem::remove(config.experiment_result_output_path);
    std::filesystem::remove(config.experiment_summary_csv_output_path);
    std::filesystem::remove(config.replanning_request_output_path);

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
    FIELDOPS_EXPECT_TRUE(result.has_replanning_result);

    FIELDOPS_EXPECT_EQ(
        result.replanning_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    FIELDOPS_EXPECT_EQ(
        result.replanning_result.method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_TRUE(!result.replanning_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!result.replanning_result.is_successful());

    FIELDOPS_EXPECT_TRUE(
        !result.replanning_result_was_applied_to_execution
    );

    FIELDOPS_EXPECT_EQ(
        result.execution_mode,
        "no_replanning_execution_baseline"
    );

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

    FIELDOPS_EXPECT_TRUE(
        !std::filesystem::exists(config.replanning_request_output_path)
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

    threshold_config.replanning_engine_config.method_id =
        "replanning_not_implemented_v1";

    threshold_config.replanning_request_output_path =
        "data/results/test_threshold_replanning_request.json";

    threshold_config.verbose = false;
    threshold_config.export_results = true;

    std::filesystem::remove(
        threshold_config.replanning_request_output_path
    );

    NoReplanningExperimentResult threshold_result =
        run_no_replanning_experiment(threshold_config);

    FIELDOPS_EXPECT_TRUE(threshold_result.policy_decision.should_replan());
    FIELDOPS_EXPECT_TRUE(threshold_result.has_replanning_request);
    FIELDOPS_EXPECT_TRUE(threshold_result.has_replanning_result);

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_result.status,
        ReplanningResultStatus::NOT_IMPLEMENTED
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_result.method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_result.request_id,
        "test_threshold_experiment_001_replanning_request"
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.replanning_result.result_id,
        "test_threshold_experiment_001_replanning_result"
    );

    FIELDOPS_EXPECT_TRUE(
        !threshold_result.replanning_result.has_new_solution()
    );

    FIELDOPS_EXPECT_TRUE(
        !threshold_result.replanning_result.is_successful()
    );

    FIELDOPS_EXPECT_TRUE(
        !threshold_result.replanning_result_was_applied_to_execution
    );

    FIELDOPS_EXPECT_EQ(
        threshold_result.execution_mode,
        "no_replanning_execution_baseline"
    );

    FIELDOPS_EXPECT_TRUE(
        std::filesystem::exists(
            threshold_config.replanning_request_output_path
        )
    );

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

    NoReplanningExperimentConfig greedy_apply_config;

    greedy_apply_config.metadata.experiment_id =
        "test_greedy_applied_experiment_001";

    greedy_apply_config.metadata.scenario_id =
        "test_greedy_applied_scenario_001";

    greedy_apply_config.metadata.replication_id = 1;
    greedy_apply_config.metadata.seed = 9201;

    greedy_apply_config.policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    greedy_apply_config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    greedy_apply_config.policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    greedy_apply_config.replanning_engine_config.method_id =
        "greedy_replanning_solver_v1";

    greedy_apply_config.verbose = false;
    greedy_apply_config.export_results = false;

    NoReplanningExperimentResult greedy_apply_result =
        run_no_replanning_experiment(greedy_apply_config);

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.policy_decision.should_replan()
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.has_replanning_request
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.has_replanning_result
    );

    FIELDOPS_EXPECT_EQ(
        greedy_apply_result.replanning_result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.replanning_result.has_new_solution()
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.replanning_result.is_successful()
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.replanning_result_was_applied_to_execution
    );

    FIELDOPS_EXPECT_EQ(
        greedy_apply_result.execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.executed_solution.solution_id.find(
            "_with_applied_"
        ) != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_apply_result.executed_solution.method_id.find(
            "greedy_replanning_solver_v1_applied"
        ) != std::string::npos
    );

    FIELDOPS_EXPECT_EQ(
        greedy_apply_result.executed_solution.status,
        SolutionStatus::FEASIBLE
    );

    NoReplanningExperimentConfig unknown_method_config;

    unknown_method_config.metadata.experiment_id =
        "test_unknown_replanning_method_001";

    unknown_method_config.metadata.scenario_id =
        "test_unknown_replanning_method_scenario_001";

    unknown_method_config.metadata.replication_id = 1;
    unknown_method_config.metadata.seed = 9101;

    unknown_method_config.policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    unknown_method_config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    unknown_method_config.policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    unknown_method_config.replanning_engine_config.method_id =
        "unknown_replanning_method_v1";

    unknown_method_config.verbose = false;
    unknown_method_config.export_results = false;

    NoReplanningExperimentResult unknown_method_result =
        run_no_replanning_experiment(unknown_method_config);

    FIELDOPS_EXPECT_TRUE(
        unknown_method_result.policy_decision.should_replan()
    );

    FIELDOPS_EXPECT_TRUE(
        unknown_method_result.has_replanning_request
    );

    FIELDOPS_EXPECT_TRUE(
        unknown_method_result.has_replanning_result
    );

    FIELDOPS_EXPECT_EQ(
        unknown_method_result.replanning_result.status,
        ReplanningResultStatus::FAILED
    );

    FIELDOPS_EXPECT_EQ(
        unknown_method_result.replanning_result.method_id,
        "unknown_replanning_method_v1"
    );

    FIELDOPS_EXPECT_EQ(
        unknown_method_result.replanning_result.result_id,
        "test_unknown_replanning_method_001_replanning_result"
    );

    FIELDOPS_EXPECT_TRUE(
        !unknown_method_result.replanning_result_was_applied_to_execution
    );

    FIELDOPS_EXPECT_EQ(
        unknown_method_result.execution_mode,
        "no_replanning_execution_baseline"
    );
}