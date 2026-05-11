#include "core/io/no_replanning_experiment_result_json_writer/no_replanning_experiment_result_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static json metadata_to_json(const ExperimentMetadata& metadata) {
    return {
        {"experiment_id", metadata.experiment_id},
        {"scenario_id", metadata.scenario_id},
        {"replication_id", metadata.replication_id},
        {"seed", metadata.seed},
        {"notes", metadata.notes},
        {"run_label", build_experiment_run_label(metadata)}
    };
}

static json solution_metrics_to_json(const SolutionMetrics& metrics) {
    return {
        {"route_count", metrics.route_count},
        {"used_route_count", metrics.used_route_count},
        {"assigned_task_count", metrics.assigned_task_count},
        {"unassigned_task_count", metrics.unassigned_task_count},
        {"total_travel_time", metrics.total_travel_time},
        {"total_service_time", metrics.total_service_time},
        {"total_waiting_time", metrics.total_waiting_time},
        {"late_task_count", metrics.late_task_count},
        {"total_lateness", metrics.total_lateness},
        {"makespan", metrics.makespan},
        {"objective_value", metrics.objective_value}
    };
}

static json solution_comparison_to_json(const SolutionComparison& comparison) {
    return {
        {"deltas", {
            {"route_count", comparison.delta_route_count},
            {"used_route_count", comparison.delta_used_route_count},
            {"assigned_task_count", comparison.delta_assigned_task_count},
            {"unassigned_task_count", comparison.delta_unassigned_task_count},
            {"total_travel_time", comparison.delta_total_travel_time},
            {"total_service_time", comparison.delta_total_service_time},
            {"total_waiting_time", comparison.delta_total_waiting_time},
            {"late_task_count", comparison.delta_late_task_count},
            {"total_lateness", comparison.delta_total_lateness},
            {"makespan", comparison.delta_makespan},
            {"objective_value", comparison.delta_objective_value}
        }},
        {"percentages", {
            {"total_travel_time", comparison.percent_total_travel_time},
            {"total_service_time", comparison.percent_total_service_time},
            {"total_waiting_time", comparison.percent_total_waiting_time},
            {"makespan", comparison.percent_makespan},
            {"objective_value", comparison.percent_objective_value}
        }}
    };
}

static json policy_decision_to_json(const PolicyDecision& decision) {
    return {
        {"policy_id", decision.policy_id},
        {"decision", policy_decision_type_to_string(decision.type)},
        {"decision_time", decision.decision_time},
        {"reason", decision.reason},
        {"should_replan", decision.should_replan()}
    };
}

static json effects_to_json(const std::vector<Effect>& effects) {
    json data = json::array();

    for (const auto& effect : effects) {
        data.push_back({
            {"effect_id", effect.effect_id},
            {"type", effect_type_to_string(effect.type)},
            {"occurrence_time", effect.occurrence_time},
            {"technician_id", effect.technician_id},
            {"task_id", effect.task_id},
            {"from_location_id", effect.from_location_id},
            {"to_location_id", effect.to_location_id},
            {"delay_duration", effect.delay_duration},
            {"description", effect.description}
        });
    }

    return data;
}

void write_no_replanning_experiment_result_to_json(
    const NoReplanningExperimentResult& result,
    const std::string& output_path,
    const std::string& result_type
) {
    json data = {
        {"result_type", result_type},
        {"metadata", metadata_to_json(result.metadata)},
        {"instance", {
            {"instance_id", result.instance.instance_id},
            {"name", result.instance.name},
            {"description", result.instance.description},
            {"time_unit", result.instance.time_unit}
        }},
        {"perturbation_plan", {
            {"perturbation_plan_id", result.perturbation_plan.perturbation_plan_id},
            {"name", result.perturbation_plan.name},
            {"description", result.perturbation_plan.description},
            {"perturbation_count", result.perturbation_plan.perturbations.size()}
        }},
        {"effects", effects_to_json(result.effects)},
        {"policy_decision", policy_decision_to_json(result.policy_decision)},
        {"planned", {
            {"solution_id", result.planned_solution.solution_id},
            {"method_id", result.planned_solution.method_id},
            {"status", solution_status_to_string(result.planned_solution.status)},
            {"metrics", solution_metrics_to_json(result.planned_metrics)},
            {"timeline", {
                {"start_time", result.planned_timeline.start_time},
                {"end_time", result.planned_timeline.end_time},
                {"event_count", result.planned_timeline.events.size()}
            }}
        }},
        {"executed", {
            {"solution_id", result.executed_solution.solution_id},
            {"method_id", result.executed_solution.method_id},
            {"status", solution_status_to_string(result.executed_solution.status)},
            {"metrics", solution_metrics_to_json(result.executed_metrics)},
            {"timeline", {
                {"start_time", result.executed_timeline.start_time},
                {"end_time", result.executed_timeline.end_time},
                {"event_count", result.executed_timeline.events.size()}
            }}
        }},
        {"comparison", solution_comparison_to_json(result.comparison)}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning experiment result file for writing: " +
            output_path
        );
    }

    file << data.dump(4);
}