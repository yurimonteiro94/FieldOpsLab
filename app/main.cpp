#include <exception>
#include <iostream>
#include <string>

#include "core/instance/instance/instance.h"
#include "core/instance/instance_validator/instance_validator.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/solution_result_json_writer/solution_result_json_writer.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/simulation/simulation_engine/simulation_engine.h"
#include "core/simulation/simulation_event/simulation_event.h"
#include "core/solution/solution/solution.h"

int main(int argc, char* argv[]) {
    std::string instance_path = "data/instances/sample_instance_001.json";
    std::string output_path = "data/results/sample_solution_result_001.json";

    if (argc >= 2) {
        instance_path = argv[1];
    }

    if (argc >= 3) {
        output_path = argv[2];
    }

    try {
        std::cout << "FieldOps Lab - simulation engine started.\n";
        std::cout << "Loading instance: " << instance_path << "\n\n";

        Instance instance = load_instance_from_json(instance_path);

        print_instance_summary(instance);

        std::cout << "\n";
        ValidationResult validation = validate_instance(instance);
        print_validation_result(validation);

        if (!validation.is_valid()) {
            return 1;
        }

        std::cout << "\nBuilding initial solution with "
                  << "greedy_earliest_feasible_heuristic_v1"
                  << "...\n\n";

        Solution solution =
            build_initial_solution_greedy_earliest_feasible(instance);

        print_solution_summary(solution);

        std::cout << "\n";
        SolutionMetrics metrics = calculate_solution_metrics(instance, solution);
        print_solution_metrics(metrics);

        std::cout << "\nBuilding simulation timeline...\n\n";

        SimulationTimeline timeline =
            build_simulation_timeline_from_solution(instance, solution);

        print_simulation_timeline_summary(timeline);

        std::cout << "\n";
        print_simulation_events(timeline.events);

        write_solution_result_to_json(
            instance,
            solution,
            metrics,
            output_path
        );

        std::cout << "\nResult written to: " << output_path << "\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}