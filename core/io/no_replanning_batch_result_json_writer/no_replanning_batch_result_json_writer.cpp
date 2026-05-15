#include "core/io/no_replanning_batch_result_json_writer/no_replanning_batch_result_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static std::string get_replanning_method_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.method_id;
}

static std::string get_replanning_status(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return replanning_result_status_to_string(
        result.replanning_result.status
    );
}

static bool get_replanning_has_new_solution(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return false;
    }

    return result.replanning_result.has_new_solution();
}

static bool get_replanning_is_successful(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return false;
    }

    return result.replanning_result.is_successful();
}

static std::string get_replanning_generated_solution_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.generated_solution_id;
}

static json experiment_result_to_json(
    const NoReplanningExperimentResult& result
) {
    return {
        {"experiment_id", result.metadata.experiment_id},
        {"scenario_id", result.metadata.scenario_id},
        {"replication_id", result.metadata.replication_id},
        {"seed", result.metadata.seed},
        {"notes", result.metadata.notes},

        {"instance_id", result.instance.instance_id},
        {"perturbation_plan_id", result.perturbation_plan.perturbation_plan_id},

        {"policy", {
            {"policy_id", result.policy_decision.policy_id},
            {"decision", policy_decision_type_to_string(result.policy_decision.type)},
            {"should_replan", result.policy_decision.should_replan()},
            {"decision_time", result.policy_decision.decision_time},
            {"reason", result.policy_decision.reason}
        }},

        {"replanning_request", {
            {"has_replanning_request", result.has_replanning_request},
            {"has_work",
                result.has_replanning_request &&
                replanning_request_has_work(result.replanning_request)},
            {"completed_task_count",
                result.has_replanning_request ?
                result.replanning_request.completed_task_count() : 0},
            {"locked_task_count",
                result.has_replanning_request ?
                result.replanning_request.locked_task_count() : 0},
            {"candidate_task_count",
                result.has_replanning_request ?
                result.replanning_request.candidate_task_count() : 0},
            {"available_technician_count",
                result.has_replanning_request ?
                result.replanning_request.available_technician_count() : 0},
            {"busy_technician_count",
                result.has_replanning_request ?
                result.replanning_request.busy_technician_count() : 0},
            {"finished_technician_count",
                result.has_replanning_request ?
                result.replanning_request.finished_technician_count() : 0}
        }},

        {"replanning_result", {
            {"has_replanning_result", result.has_replanning_result},
            {"method_id", get_replanning_method_id(result)},
            {"status", get_replanning_status(result)},
            {"has_new_solution", get_replanning_has_new_solution(result)},
            {"is_successful", get_replanning_is_successful(result)},
            {"generated_solution_id", get_replanning_generated_solution_id(result)},
            {"was_applied_to_execution",
                result.replanning_result_was_applied_to_execution}
        }},

        {"execution", {
            {"execution_mode", result.execution_mode},
            {"planned_solution_id", result.planned_solution.solution_id},
            {"planned_method_id", result.planned_solution.method_id},
            {"executed_solution_id", result.executed_solution.solution_id},
            {"executed_method_id", result.executed_solution.method_id}
        }},

        {"metrics", {
            {"planned_objective_value", result.planned_metrics.objective_value},
            {"executed_objective_value", result.executed_metrics.objective_value},
            {"delta_objective_value", result.comparison.delta_objective_value},
            {"percent_objective_value", result.comparison.percent_objective_value},

            {"planned_makespan", result.planned_metrics.makespan},
            {"executed_makespan", result.executed_metrics.makespan},
            {"delta_makespan", result.comparison.delta_makespan},
            {"percent_makespan", result.comparison.percent_makespan},

            {"planned_total_travel_time", result.planned_metrics.total_travel_time},
            {"executed_total_travel_time", result.executed_metrics.total_travel_time},
            {"delta_total_travel_time", result.comparison.delta_total_travel_time},
            {"percent_total_travel_time", result.comparison.percent_total_travel_time},

            {"planned_total_service_time", result.planned_metrics.total_service_time},
            {"executed_total_service_time", result.executed_metrics.total_service_time},
            {"delta_total_service_time", result.comparison.delta_total_service_time},
            {"percent_total_service_time", result.comparison.percent_total_service_time},

            {"planned_total_waiting_time", result.planned_metrics.total_waiting_time},
            {"executed_total_waiting_time", result.executed_metrics.total_waiting_time},
            {"delta_total_waiting_time", result.comparison.delta_total_waiting_time},
            {"percent_total_waiting_time", result.comparison.percent_total_waiting_time},

            {"planned_late_task_count", result.planned_metrics.late_task_count},
            {"executed_late_task_count", result.executed_metrics.late_task_count},
            {"delta_late_task_count", result.comparison.delta_late_task_count},

            {"planned_total_lateness", result.planned_metrics.total_lateness},
            {"executed_total_lateness", result.executed_metrics.total_lateness},
            {"delta_total_lateness", result.comparison.delta_total_lateness},

            {"assigned_task_count", result.executed_metrics.assigned_task_count},
            {"unassigned_task_count", result.executed_metrics.unassigned_task_count},
            {"effect_count", result.effects.size()}
        }}
    };
}

static json experiment_results_to_json(
    const NoReplanningBatchExperimentResult& batch_result
) {
    json experiments = json::array();

    for (const auto& result : batch_result.results) {
        experiments.push_back(experiment_result_to_json(result));
    }

    return experiments;
}

void write_no_replanning_batch_result_to_json(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path,
    const std::string& result_type
) {
    json data = {
        {"result_type", result_type},
        {"batch", {
            {"batch_id", batch_result.batch_id},
            {"name", batch_result.name},
            {"description", batch_result.description},
            {"experiment_count", batch_result.experiment_count()}
        }},
        {"outputs", {
            {"summary_csv_output_path", batch_result.summary_csv_output_path},
            {"aggregate_csv_output_path", batch_result.aggregate_csv_output_path},
            {"result_json_output_path", batch_result.result_json_output_path},
            {"summary_csv_was_written", batch_result.summary_csv_was_written},
            {"aggregate_csv_was_written", batch_result.aggregate_csv_was_written},
            {"result_json_was_written", batch_result.result_json_was_written}
        }},
        {"experiments", experiment_results_to_json(batch_result)}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch result JSON file: " +
            output_path
        );
    }

    file << data.dump(4);
}