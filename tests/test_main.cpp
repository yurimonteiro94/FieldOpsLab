#include <exception>
#include <iostream>
#include <string>
#include <vector>

void test_travel_matrix();
void test_instance_validator();
void test_greedy_earliest_feasible_heuristic();
void test_solution_metrics();
void test_simulation_timeline();

struct TestCase {
    std::string name;
    void (*function)();
};

int main() {
    std::vector<TestCase> tests = {
        {"TravelMatrix", test_travel_matrix},
        {"InstanceValidator", test_instance_validator},
        {"GreedyEarliestFeasibleHeuristic", test_greedy_earliest_feasible_heuristic},
        {"SolutionMetrics", test_solution_metrics},
        {"SimulationTimeline", test_simulation_timeline}
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