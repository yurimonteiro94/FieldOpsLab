#include "core/io/no_replanning_batch_result_json_writer/no_replanning_batch_result_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "core/analysis/batch_ranking/batch_ranking.h"

using json = nlohmann::json;

static json string_vector_to_json(
    const std::vector<std::string>& values
) {
    json data = json::array();

    for (const auto& value : values) {
        data.push_back(value);
    }

    return data;
}

static json effect_to_json(const Effect& effect) {
    return {
        {"effect_id", effect.effect_id},
        {"type", effect_type_to_string(effect.type)},
        {"occurrence_time", effect.occurrence_time},
        {"technician_id", effect.technician_id},
        {"task_id", effect.task_id},
        {"from_location_id", effect.from_location_id},
        {"to_location_id", effect.to_location_id},
        {"delay_duration", effect.delay_duration},
        {"description", effect.description}
    };
}

static json effects_to_json(const std::vector<Effect>& effects) {
    json data = json::array();

    for (const auto& effect : effects) {
        data.push_back(effect_to_json(effect));
    }

    return data;
}

static json technician_runtime_states_to_json(
    const std::vector<ReplanningTechnicianRuntimeState>& runtime_states
) {
    json data = json::array();

    for (const auto& state : runtime_states) {
        data.push_back({
            {"technician_id", state.technician_id},
            {"execution_status", state.execution_status},
            {"current_location_id", state.current_location_id},
            {"current_task_id", state.current_task_id},
            {"next_task_id", state.next_task_id},
            {"available_from_time", state.available_from_time},
            {"can_receive_candidate_tasks",
                state.can_receive_candidate_tasks}
        });
    }

    return data;
}

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

static json replanning_request_to_json(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return {
            {"has_replanning_request", false},
            {"has_work", false},
            {"completed_task_count", 0},
            {"locked_task_count", 0},
            {"candidate_task_count", 0},
            {"available_technician_count", 0},
            {"busy_technician_count", 0},
            {"finished_technician_count", 0},
            {"technician_runtime_state_count", 0},
            {"runtime_effect_count", 0},
            {"technician_runtime_states", json::array()},
            {"runtime_effects", json::array()}
        };
    }

    const ReplanningRequest& request = result.replanning_request;

    return {
        {"has_replanning_request", true},
        {"request_id", request.request_id},
        {"decision_time", request.decision_time},
        {"policy_id", request.policy_id},
        {"policy_decision", request.policy_decision},
        {"should_replan", request.should_replan},
        {"has_work", replanning_request_has_work(request)},
        {"completed_task_count", request.completed_task_count()},
        {"locked_task_count", request.locked_task_count()},
        {"candidate_task_count", request.candidate_task_count()},
        {"available_technician_count", request.available_technician_count()},
        {"busy_technician_count", request.busy_technician_count()},
        {"finished_technician_count", request.finished_technician_count()},
        {"technician_runtime_state_count",
            request.technician_runtime_states.size()},
        {"runtime_effect_count", request.runtime_effects.size()},
        {"tasks", {
            {"completed_task_ids", string_vector_to_json(request.completed_task_ids)},
            {"locked_task_ids", string_vector_to_json(request.locked_task_ids)},
            {"candidate_task_ids", string_vector_to_json(request.candidate_task_ids)}
        }},
        {"technicians", {
            {"available_technician_ids", string_vector_to_json(request.available_technician_ids)},
            {"busy_technician_ids", string_vector_to_json(request.busy_technician_ids)},
            {"finished_technician_ids", string_vector_to_json(request.finished_technician_ids)}
        }},
        {"technician_runtime_states",
            technician_runtime_states_to_json(
                request.technician_runtime_states
            )},
        {"runtime_effects", effects_to_json(request.runtime_effects)}
    };
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

        {"replanning_request", replanning_request_to_json(result)},

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

static json ranking_tie_breakers_to_json() {
    json data = json::array();

    for (const auto& tie_breaker : batch_ranking_tie_breakers()) {
        data.push_back(tie_breaker);
    }

    return data;
}

static json ranking_row_to_json(const BatchRankingRow& row) {
    return {
        {"scenario_id", row.key.scenario_id},
        {"rank", row.rank},
        {"policy_id", row.key.policy_id},
        {"replanning_method_id", row.key.replanning_method_id},
        {"execution_mode", row.key.execution_mode},
        {"experiment_count", row.stats.experiment_count},
        {"policy_should_replan_count", row.stats.policy_should_replan_count},
        {"replanning_request_count", row.stats.replanning_request_count},
        {"replanning_success_count", row.stats.replanning_success_count},
        {"replanning_applied_count", row.stats.replanning_applied_count},
        {"ranking_score", row.ranking_score},
        {"mean_delta_objective_value", row.mean_delta_objective_value},
        {"mean_delta_makespan", row.mean_delta_makespan},
        {"mean_delta_total_travel_time", row.mean_delta_total_travel_time},
        {"mean_delta_total_service_time", row.mean_delta_total_service_time},
        {"mean_delta_total_waiting_time", row.mean_delta_total_waiting_time},
        {"mean_late_task_count", row.mean_late_task_count},
        {"mean_total_lateness", row.mean_total_lateness},
        {"mean_effect_count", row.mean_effect_count}
    };
}

static json rankings_to_json(
    const NoReplanningBatchExperimentResult& batch_result
) {
    std::vector<BatchRankingRow> rows =
        build_batch_ranking_rows(batch_result);

    json ranking_rows = json::array();

    for (const auto& row : rows) {
        ranking_rows.push_back(ranking_row_to_json(row));
    }

    return {
        {"ranking_score_definition", batch_ranking_score_definition()},
        {"tie_breakers", ranking_tie_breakers_to_json()},
        {"row_count", rows.size()},
        {"rows", ranking_rows}
    };
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
            {"ranking_csv_output_path", batch_result.ranking_csv_output_path},
            {"result_json_output_path", batch_result.result_json_output_path},
            {"summary_csv_was_written", batch_result.summary_csv_was_written},
            {"aggregate_csv_was_written", batch_result.aggregate_csv_was_written},
            {"ranking_csv_was_written", batch_result.ranking_csv_was_written},
            {"result_json_was_written", batch_result.result_json_was_written}
        }},
        {"experiments", experiment_results_to_json(batch_result)},
        {"rankings", rankings_to_json(batch_result)}
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