#include <exception>
#include <iostream>
#include <string>
#include <vector>

void test_travel_matrix();
void test_instance_validator();
void test_experiment_metadata();
void test_greedy_earliest_feasible_heuristic();
void test_solution_metrics();
void test_simulation_timeline();
void test_simulation_state();
void test_replanning_request();
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
void test_no_replanning_experiment();
void test_no_replanning_experiment_result_json_writer();
void test_no_replanning_experiment_summary_csv_writer();
void test_no_replanning_batch_experiment();
void test_no_replanning_batch_config_json_loader();
void test_policy();
void test_no_replanning_policy();
void test_threshold_delay_replanning_policy();
void test_policy_evaluator();

struct TestCase {
    std::string name;
    void (*function)();
};

int main() {
    std::vector<TestCase> tests = {
        {"TravelMatrix", test_travel_matrix},
        {"InstanceValidator", test_instance_validator},
        {"ExperimentMetadata", test_experiment_metadata},
        {"GreedyEarliestFeasibleHeuristic", test_greedy_earliest_feasible_heuristic},
        {"SolutionMetrics", test_solution_metrics},
        {"SimulationTimeline", test_simulation_timeline},
        {"SimulationState", test_simulation_state},
        {"ReplanningRequest", test_replanning_request},
        {"ReplanningRequestJsonWriter", test_replanning_request_json_writer},
        {"Perturbation", test_perturbation},
        {"Effect", test_effect},
        {"TravelDelayPerturbation", test_travel_delay_perturbation},
        {"ServiceDelayPerturbation", test_service_delay_perturbation},
        {"PerturbationJsonLoader", test_perturbation_json_loader},
        {"PerturbationEffectBuilder", test_perturbation_effect_builder},
        {"NoReplanningExecution", test_no_replanning_execution},
        {"SolutionComparison", test_solution_comparison},
        {"SolutionComparisonJsonWriter", test_solution_comparison_json_writer},
        {"NoReplanningExperiment", test_no_replanning_experiment},
        {"NoReplanningExperimentResultJsonWriter", test_no_replanning_experiment_result_json_writer},
        {"NoReplanningExperimentSummaryCsvWriter", test_no_replanning_experiment_summary_csv_writer},
        {"NoReplanningBatchExperiment", test_no_replanning_batch_experiment},
        {"NoReplanningBatchConfigJsonLoader", test_no_replanning_batch_config_json_loader},
        {"Policy", test_policy},
        {"NoReplanningPolicy", test_no_replanning_policy},
        {"ThresholdDelayReplanningPolicy", test_threshold_delay_replanning_policy},
        {"PolicyEvaluator", test_policy_evaluator}
    };

    int failed_tests = 0;

    std::cout << "Running FieldOps Lab tests...\n\n";

    for (const auto& test : tests) {
        try {
            test.function();
            std::cout << "[PASS] " << test.name << "\n";
        } catch (const std::exception& error) {
            failed_tests += 1;
            std::cout << "[FAIL] " << test.name << "\n";
            std::cout << "       " << error.what() << "\n";
        }
    }

    std::cout << "\n";

    if (failed_tests == 0) {
        std::cout << "All tests passed.\n";
        return 0;
    }

    std::cout << failed_tests << " test(s) failed.\n";
    return 1;
}