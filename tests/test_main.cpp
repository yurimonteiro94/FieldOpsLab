#include "tests/test_support/test_assertions.h"

#include <exception>
#include <iostream>
#include <string>

void test_travel_matrix();
void test_instance_validator();
void test_experiment_metadata();

void test_greedy_earliest_feasible_heuristic();

void test_solution_metrics();
void test_simulation_timeline();
void test_simulation_state();

void test_replanning_request();
void test_replanning_result();
void test_greedy_replanning_solver();
void test_replanning_engine();
void test_replanning_application();

void test_replanning_request_json_writer();

void test_perturbation();
void test_effect();
void test_travel_delay_perturbation();
void test_service_delay_perturbation();
void test_perturbation_json_loader();
void test_perturbation_effect_builder();

void test_no_replanning_execution();

void test_solution_comparison();
void test_solution_comparison_json_writer();

void test_batch_ranking();
void test_batch_ranking_config();
void test_batch_recommendation();

void test_no_replanning_experiment();
void test_no_replanning_experiment_result_json_writer();
void test_no_replanning_experiment_summary_csv_writer();

void test_no_replanning_batch_experiment();
void test_no_replanning_batch_completion();
void test_no_replanning_batch_config_json_loader();
void test_no_replanning_batch_aggregate_csv_writer();
void test_no_replanning_batch_overview_csv_writer();
void test_no_replanning_batch_ranking_csv_writer();
void test_no_replanning_batch_recommendation_csv_writer();
void test_no_replanning_batch_result_json_writer();

void test_policy();
void test_no_replanning_policy();
void test_threshold_delay_replanning_policy();
void test_policy_evaluator();

static int run_test(
    const std::string& test_name,
    void (*test_function)()
) {
    try {
        test_function();
        std::cout << "[PASS] " << test_name << "\n";
        return 0;
    } catch (const std::exception& exception) {
        std::cout << "[FAIL] " << test_name << "\n";
        std::cout << "       " << exception.what() << "\n";
        return 1;
    } catch (...) {
        std::cout << "[FAIL] " << test_name << "\n";
        std::cout << "       Unknown exception.\n";
        return 1;
    }
}

int main() {
    std::cout << "Running FieldOps Lab tests...\n\n";

    int failed_tests = 0;

    failed_tests += run_test("TravelMatrix", test_travel_matrix);
    failed_tests += run_test("InstanceValidator", test_instance_validator);
    failed_tests += run_test("ExperimentMetadata", test_experiment_metadata);

    failed_tests += run_test(
        "GreedyEarliestFeasibleHeuristic",
        test_greedy_earliest_feasible_heuristic
    );

    failed_tests += run_test("SolutionMetrics", test_solution_metrics);
    failed_tests += run_test("SimulationTimeline", test_simulation_timeline);
    failed_tests += run_test("SimulationState", test_simulation_state);

    failed_tests += run_test("ReplanningRequest", test_replanning_request);
    failed_tests += run_test("ReplanningResult", test_replanning_result);

    failed_tests += run_test(
        "GreedyReplanningSolver",
        test_greedy_replanning_solver
    );

    failed_tests += run_test("ReplanningEngine", test_replanning_engine);

    failed_tests += run_test(
        "ReplanningApplication",
        test_replanning_application
    );

    failed_tests += run_test(
        "ReplanningRequestJsonWriter",
        test_replanning_request_json_writer
    );

    failed_tests += run_test("Perturbation", test_perturbation);
    failed_tests += run_test("Effect", test_effect);

    failed_tests += run_test(
        "TravelDelayPerturbation",
        test_travel_delay_perturbation
    );

    failed_tests += run_test(
        "ServiceDelayPerturbation",
        test_service_delay_perturbation
    );

    failed_tests += run_test(
        "PerturbationJsonLoader",
        test_perturbation_json_loader
    );

    failed_tests += run_test(
        "PerturbationEffectBuilder",
        test_perturbation_effect_builder
    );

    failed_tests += run_test(
        "NoReplanningExecution",
        test_no_replanning_execution
    );

    failed_tests += run_test(
        "SolutionComparison",
        test_solution_comparison
    );

    failed_tests += run_test(
        "SolutionComparisonJsonWriter",
        test_solution_comparison_json_writer
    );

    failed_tests += run_test(
        "BatchRanking",
        test_batch_ranking
    );

    failed_tests += run_test(
        "BatchRankingConfig",
        test_batch_ranking_config
    );

    failed_tests += run_test(
        "BatchRecommendation",
        test_batch_recommendation
    );

    failed_tests += run_test(
        "NoReplanningExperiment",
        test_no_replanning_experiment
    );

    failed_tests += run_test(
        "NoReplanningExperimentResultJsonWriter",
        test_no_replanning_experiment_result_json_writer
    );

    failed_tests += run_test(
        "NoReplanningExperimentSummaryCsvWriter",
        test_no_replanning_experiment_summary_csv_writer
    );

    failed_tests += run_test(
        "NoReplanningBatchExperiment",
        test_no_replanning_batch_experiment
    );

    failed_tests += run_test(
        "NoReplanningBatchCompletion",
        test_no_replanning_batch_completion
    );

    failed_tests += run_test(
        "NoReplanningBatchConfigJsonLoader",
        test_no_replanning_batch_config_json_loader
    );

    failed_tests += run_test(
        "NoReplanningBatchAggregateCsvWriter",
        test_no_replanning_batch_aggregate_csv_writer
    );

    failed_tests += run_test(
        "NoReplanningBatchOverviewCsvWriter",
        test_no_replanning_batch_overview_csv_writer
    );

    failed_tests += run_test(
        "NoReplanningBatchRankingCsvWriter",
        test_no_replanning_batch_ranking_csv_writer
    );

    failed_tests += run_test(
        "NoReplanningBatchRecommendationCsvWriter",
        test_no_replanning_batch_recommendation_csv_writer
    );

    failed_tests += run_test(
        "NoReplanningBatchResultJsonWriter",
        test_no_replanning_batch_result_json_writer
    );

    failed_tests += run_test("Policy", test_policy);

    failed_tests += run_test(
        "NoReplanningPolicy",
        test_no_replanning_policy
    );

    failed_tests += run_test(
        "ThresholdDelayReplanningPolicy",
        test_threshold_delay_replanning_policy
    );

    failed_tests += run_test(
        "PolicyEvaluator",
        test_policy_evaluator
    );

    if (failed_tests == 0) {
        std::cout << "\nAll tests passed.\n";
        return 0;
    }

    std::cout << "\n" << failed_tests << " test(s) failed.\n";
    return 1;
}