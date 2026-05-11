#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

#include <iostream>
#include <stdexcept>
#include <vector>

#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/no_replanning_experiment_result_json_writer/no_replanning_experiment_result_json_writer.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/io/simulation_timeline_json_writer/simulation_timeline_json_writer.h"
#include "core/io/solution_comparison_json_writer/solution_comparison_json_writer.h"
#include "core/io/solution_result_json_writer/solution_result_json_writer.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/simulation/no_replanning_execution/no_replanning_execution.h"
#include "core/simulation/simulation_state/simulation_state.h"

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

static int get_first_effect_time(const std::vector<Effect>& effects) {
    if (effects.empty()) {
        return 0;
    }

    int first_time = effects.front().occurrence_time;

    for (const auto& effect : effects) {
        if (effect.occurrence_time < first_time) {
            first_time = effect.occurrence_time;
        }
    }

    return first_time;
}

static void print_policy_decision(const PolicyDecision& decision) {
    std::cout << "Policy decision:\n";
    std::cout << "  Policy ID: " << decision.policy_id << "\n";
    std::cout << "  Decision: "
              << policy_decision_type_to_string(decision.type)
              << "\n";
    std::cout << "  Decision time: " << decision.decision_time << "\n";
    std::cout << "  Reason: " << decision.reason << "\n";
}

static std::string build_replanning_request_id(
    const ExperimentMetadata& metadata
) {
    return build_experiment_run_label(metadata) + "_replanning_request";
}

static void maybe_build_replanning_request(
    NoReplanningExperimentResult& result
) {
    if (!result.policy_decision.should_replan()) {
        result.has_replanning_request = false;
        return;
    }

    SimulationSnapshot snapshot =
        build_simulation_snapshot_from_solution(
            result.instance,
            result.planned_solution,
            result.policy_decision.decision_time
        );

    result.replanning_request =
        build_replanning_request_from_snapshot(
            snapshot,
            result.policy_decision,
            build_replanning_request_id(result.metadata)
        );

    result.has_replanning_request = true;
}

static void export_no_replanning_experiment_results(
    const NoReplanningExperimentConfig& config,
    const NoReplanningExperimentResult& result
) {
    write_solution_result_to_json(
        result.instance,
        result.planned_solution,
        result.planned_metrics,
        config.planned_solution_output_path,
        "planned_solution_result"
    );

    write_simulation_timeline_to_json(
        result.planned_timeline,
        config.planned_timeline_output_path
    );

    write_solution_result_to_json(
        result.instance,
        result.executed_solution,
        result.executed_metrics,
        config.executed_solution_output_path,
        "executed_solution_result_no_replanning"
    );

    write_simulation_timeline_to_json(
        result.executed_timeline,
        config.executed_timeline_output_path
    );

    write_solution_comparison_to_json(
        result.instance,
        result.planned_solution,
        result.executed_solution,
        result.comparison,
        config.comparison_output_path,
        "planned_vs_executed_no_replanning_comparison"
    );

    write_no_replanning_experiment_result_to_json(
        result,
        config.experiment_result_output_path,
        "no_replanning_experiment_result"
    );

    write_no_replanning_experiment_summary_to_csv(
        result,
        config.experiment_summary_csv_output_path,
        true
    );
}

NoReplanningExperimentResult run_no_replanning_experiment(
    const NoReplanningExperimentConfig& config
) {
    NoReplanningExperimentResult result;

    result.metadata = config.metadata;

    if (config.verbose) {
        std::cout << "FieldOps Lab - simulation engine started.\n";
        std::cout << "Experiment ID: "
                  << result.metadata.experiment_id
                  << "\n";
        std::cout << "Scenario ID: "
                  << result.metadata.scenario_id
                  << "\n";
        std::cout << "Replication ID: "
                  << result.metadata.replication_id
                  << "\n";
        std::cout << "Seed: "
                  << result.metadata.seed
                  << "\n";
        std::cout << "Policy ID: "
                  << config.policy_config.policy_id
                  << "\n";
        std::cout << "Loading instance: " << config.instance_path << "\n\n";
    }

    result.instance = load_instance_from_json(config.instance_path);

    if (config.verbose) {
        print_instance_summary(result.instance);
        std::cout << "\n";
    }

    result.validation_result = validate_instance(result.instance);

    if (config.verbose) {
        print_validation_result(result.validation_result);
    }

    if (!result.validation_result.is_valid()) {
        throw std::runtime_error("Invalid instance.");
    }

    if (config.verbose) {
        std::cout << "\nBuilding planned solution with "
                  << "greedy_earliest_feasible_heuristic_v1"
                  << "...\n\n";
    }

    result.planned_solution =
        build_initial_solution_greedy_earliest_feasible(result.instance);

    if (config.verbose) {
        print_solution_summary(result.planned_solution);
        std::cout << "\n";
    }

    result.planned_metrics =
        calculate_solution_metrics(
            result.instance,
            result.planned_solution
        );

    if (config.verbose) {
        print_solution_metrics(result.planned_metrics);
        std::cout << "\nBuilding planned simulation timeline...\n\n";
    }

    result.planned_timeline =
        build_simulation_timeline_from_solution(
            result.instance,
            result.planned_solution
        );

    if (config.verbose) {
        print_simulation_timeline_summary(result.planned_timeline);

        std::cout << "\nLoading perturbation plan: "
                  << config.perturbation_plan_path
                  << "\n\n";
    }

    result.perturbation_plan =
        load_perturbation_plan_from_json(config.perturbation_plan_path);

    result.effects =
        build_effects_from_perturbation_plan(result.perturbation_plan);

    if (config.verbose) {
        print_effects_summary(result.effects);
        std::cout << "\nEvaluating policy...\n\n";
    }

    PolicyEvaluationContext policy_context;

    policy_context.current_time = get_first_effect_time(result.effects);
    policy_context.effects = result.effects;

    result.policy_decision =
        evaluate_policy(policy_context, config.policy_config);

    if (config.verbose) {
        print_policy_decision(result.policy_decision);
    }

    maybe_build_replanning_request(result);

    if (config.verbose && result.has_replanning_request) {
        std::cout << "\nReplanning request generated.\n";
        print_replanning_request_summary(result.replanning_request);

        std::cout << "\nA replanning execution engine is not implemented yet, "
                  << "so this experiment will continue with "
                  << "the no-replanning execution baseline.\n";
    }

    if (config.verbose) {
        std::cout << "\nExecuting solution without replanning...\n\n";
    }

    result.executed_solution =
        execute_solution_without_replanning(
            result.instance,
            result.planned_solution,
            result.effects
        );

    if (config.verbose) {
        print_solution_summary(result.executed_solution);
        std::cout << "\n";
    }

    result.executed_metrics =
        calculate_solution_metrics(
            result.instance,
            result.executed_solution
        );

    if (config.verbose) {
        print_solution_metrics(result.executed_metrics);

        std::cout << "\nComparing planned and executed metrics...\n\n";
    }

    result.comparison =
        compare_solution_metrics(
            result.planned_metrics,
            result.executed_metrics
        );

    if (config.verbose) {
        print_solution_comparison(result.comparison);

        std::cout << "\nBuilding executed simulation timeline...\n\n";
    }

    result.executed_timeline =
        build_simulation_timeline_from_solution(
            result.instance,
            result.executed_solution
        );

    if (config.verbose) {
        print_simulation_timeline_summary(result.executed_timeline);
    }

    if (config.export_results) {
        export_no_replanning_experiment_results(config, result);
    }

    if (config.verbose && config.export_results) {
        std::cout << "\nPlanned solution result written to: "
                  << config.planned_solution_output_path
                  << "\n";

        std::cout << "Planned timeline written to: "
                  << config.planned_timeline_output_path
                  << "\n";

        std::cout << "Executed solution result written to: "
                  << config.executed_solution_output_path
                  << "\n";

        std::cout << "Executed timeline written to: "
                  << config.executed_timeline_output_path
                  << "\n";

        std::cout << "Solution comparison written to: "
                  << config.comparison_output_path
                  << "\n";

        std::cout << "Experiment result written to: "
                  << config.experiment_result_output_path
                  << "\n";

        std::cout << "Experiment summary CSV written to: "
                  << config.experiment_summary_csv_output_path
                  << "\n";
    }

    return result;
}