#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include "core/instance/instance/instance.h"
#include "core/instance/instance_validator/instance_validator.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/io/simulation_timeline_json_writer/simulation_timeline_json_writer.h"
#include "core/io/solution_result_json_writer/solution_result_json_writer.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/effect/effect.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/simulation/no_replanning_execution/no_replanning_execution.h"
#include "core/simulation/simulation_engine/simulation_engine.h"
#include "core/simulation/simulation_event/simulation_event.h"
#include "core/solution/solution/solution.h"
#include "core/analysis/solution_comparison/solution_comparison.h"

static void print_effects_summary(const std::vector<Effect>& effects) {
    std::cout << "Effects summary:\n";
    std::cout << "  Effects: " << effects.size() << "\n";

    for (const auto& effect : effects) {
        std::cout << "  - " << effect.effect_id
                  << " | type=" << effect_type_to_string(effect.type)
                  << " | time=" << effect.occurrence_time
                  << " | technician=" << effect.technician_id
                  << " | task=" << effect.task_id
                  << " | delay=" << effect.delay_duration
                  << "\n";
    }
}

int main(int argc, char* argv[]) {
    std::string instance_path = "data/instances/sample_instance_001.json";
    std::string perturbation_plan_path =
        "data/perturbations/sample_perturbations_001.json";

    std::string planned_solution_output_path =
        "data/results/sample_planned_solution_result_001.json";

    std::string planned_timeline_output_path =
        "data/results/sample_planned_timeline_001.json";

    std::string executed_solution_output_path =
        "data/results/sample_executed_solution_no_replanning_001.json";

    std::string executed_timeline_output_path =
        "data/results/sample_executed_timeline_no_replanning_001.json";

    if (argc >= 2) {
        instance_path = argv[1];
    }

    if (argc >= 3) {
        perturbation_plan_path = argv[2];
    }

    if (argc >= 4) {
        planned_solution_output_path = argv[3];
    }

    if (argc >= 5) {
        planned_timeline_output_path = argv[4];
    }

    if (argc >= 6) {
        executed_solution_output_path = argv[5];
    }

    if (argc >= 7) {
        executed_timeline_output_path = argv[6];
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

        std::cout << "\nBuilding planned solution with "
                  << "greedy_earliest_feasible_heuristic_v1"
                  << "...\n\n";

        Solution planned_solution =
            build_initial_solution_greedy_earliest_feasible(instance);

        print_solution_summary(planned_solution);

        std::cout << "\n";
        SolutionMetrics planned_metrics =
            calculate_solution_metrics(instance, planned_solution);

        print_solution_metrics(planned_metrics);

        std::cout << "\nBuilding planned simulation timeline...\n\n";

        SimulationTimeline planned_timeline =
            build_simulation_timeline_from_solution(
                instance,
                planned_solution
            );

        print_simulation_timeline_summary(planned_timeline);

        write_solution_result_to_json(
            instance,
            planned_solution,
            planned_metrics,
            planned_solution_output_path,
            "planned_solution_result"
        );

        write_simulation_timeline_to_json(
            planned_timeline,
            planned_timeline_output_path
        );

        std::cout << "\nLoading perturbation plan: "
                  << perturbation_plan_path
                  << "\n\n";

        PerturbationPlan perturbation_plan =
            load_perturbation_plan_from_json(perturbation_plan_path);

        std::vector<Effect> effects =
            build_effects_from_perturbation_plan(perturbation_plan);

        print_effects_summary(effects);

        std::cout << "\nExecuting solution without replanning...\n\n";

        Solution executed_solution =
            execute_solution_without_replanning(
                instance,
                planned_solution,
                effects
            );

        print_solution_summary(executed_solution);

        std::cout << "\n";
        SolutionMetrics executed_metrics =
            calculate_solution_metrics(instance, executed_solution);

        print_solution_metrics(executed_metrics);

        std::cout << "\nComparing planned and executed metrics...\n\n";

        SolutionComparison comparison =
            compare_solution_metrics(
                planned_metrics,
                executed_metrics
            );

        print_solution_comparison(comparison);

        std::cout << "\nBuilding executed simulation timeline...\n\n";

        SimulationTimeline executed_timeline =
            build_simulation_timeline_from_solution(
                instance,
                executed_solution
            );

        print_simulation_timeline_summary(executed_timeline);

        write_solution_result_to_json(
            instance,
            executed_solution,
            executed_metrics,
            executed_solution_output_path,
            "executed_solution_result_no_replanning"
        );

        write_simulation_timeline_to_json(
            executed_timeline,
            executed_timeline_output_path
        );

        std::cout << "\nPlanned solution result written to: "
                  << planned_solution_output_path
                  << "\n";

        std::cout << "Planned timeline written to: "
                  << planned_timeline_output_path
                  << "\n";

        std::cout << "Executed solution result written to: "
                  << executed_solution_output_path
                  << "\n";

        std::cout << "Executed timeline written to: "
                  << executed_timeline_output_path
                  << "\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}