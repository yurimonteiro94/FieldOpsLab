#include <exception>
#include <iostream>
#include <string>

#include "core/instance/instance/instance.h"
#include "core/instance/instance_validator/instance_validator.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/solution/solution/solution.h"

int main(int argc, char* argv[]) {
    std::string instance_path = "data/instances/sample_instance_001.json";

    if (argc >= 2) {
        instance_path = argv[1];
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

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}