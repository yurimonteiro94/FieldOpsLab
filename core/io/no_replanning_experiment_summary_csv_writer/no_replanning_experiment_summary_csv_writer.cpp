#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

static std::string bool_to_csv(bool value) {
    return value ? "true" : "false";
}

static std::string csv_escape(const std::string& value) {
    bool must_quote = false;

    for (const char character : value) {
        if (character == ',' ||
            character == '"' ||
            character == '\n' ||
            character == '\r') {
            must_quote = true;
            break;
        }
    }

    if (!must_quote) {
        return value;
    }

    std::string escaped = "\"";

    for (const char character : value) {
        if (character == '"') {
            escaped += "\"\"";
        } else {
            escaped += character;
        }
    }

    escaped += "\"";

    return escaped;
}

static std::string build_header_line() {
    return
        "result_type,"
        "experiment_id,"
        "scenario_id,"
        "replication_id,"
        "seed,"
        "notes,"
        "instance_id,"
        "perturbation_plan_id,"
        "policy_id,"
        "policy_decision,"
        "policy_should_replan,"
        "has_replanning_request,"
        "replanning_request_has_work,"
        "replanning_completed_task_count,"
        "replanning_locked_task_count,"
        "replanning_candidate_task_count,"
        "replanning_available_technician_count,"
        "replanning_busy_technician_count,"
        "replanning_finished_technician_count,"
        "has_replanning_result,"
        "replanning_result_method_id,"
        "replanning_result_status,"
        "replanning_result_has_new_solution,"
        "replanning_result_is_successful,"
        "replanning_result_generated_solution_id,"
        "replanning_result_was_applied_to_execution,"
        "execution_mode,"
        "planned_solution_id,"
        "planned_method_id,"
        "executed_solution_id,"
        "executed_method_id,"
        "planned_objective_value,"
        "executed_objective_value,"
        "delta_objective_value,"
        "percent_objective_value,"
        "planned_makespan,"
        "executed_makespan,"
        "delta_makespan,"
        "percent_makespan,"
        "planned_total_travel_time,"
        "executed_total_travel_time,"
        "delta_total_travel_time,"
        "percent_total_travel_time,"
        "planned_total_service_time,"
        "executed_total_service_time,"
        "delta_total_service_time,"
        "percent_total_service_time,"
        "planned_total_waiting_time,"
        "executed_total_waiting_time,"
        "delta_total_waiting_time,"
        "percent_total_waiting_time,"
        "planned_late_task_count,"
        "executed_late_task_count,"
        "delta_late_task_count,"
        "planned_total_lateness,"
        "executed_total_lateness,"
        "delta_total_lateness,"
        "assigned_task_count,"
        "unassigned_task_count,"
        "effect_count";
}

static int get_replanning_completed_task_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.completed_task_count();
}

static int get_replanning_locked_task_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.locked_task_count();
}

static int get_replanning_candidate_task_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.candidate_task_count();
}

static int get_replanning_available_technician_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.available_technician_count();
}

static int get_replanning_busy_technician_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.busy_technician_count();
}

static int get_replanning_finished_technician_count(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_request) {
        return 0;
    }

    return result.replanning_request.finished_technician_count();
}

static std::string get_replanning_result_method_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.method_id;
}

static std::string get_replanning_result_status(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return replanning_result_status_to_string(
        result.replanning_result.status
    );
}

static bool get_replanning_result_has_new_solution(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return false;
    }

    return result.replanning_result.has_new_solution();
}

static bool get_replanning_result_is_successful(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return false;
    }

    return result.replanning_result.is_successful();
}

static std::string get_replanning_result_generated_solution_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.generated_solution_id;
}

static std::string build_data_line(
    const NoReplanningExperimentResult& result
) {
    std::ostringstream line;

    line << "no_replanning_experiment_result" << ","
         << csv_escape(result.metadata.experiment_id) << ","
         << csv_escape(result.metadata.scenario_id) << ","
         << result.metadata.replication_id << ","
         << result.metadata.seed << ","
         << csv_escape(result.metadata.notes) << ","
         << csv_escape(result.instance.instance_id) << ","
         << csv_escape(result.perturbation_plan.perturbation_plan_id) << ","
         << csv_escape(result.policy_decision.policy_id) << ","
         << policy_decision_type_to_string(result.policy_decision.type) << ","
         << bool_to_csv(result.policy_decision.should_replan()) << ","
         << bool_to_csv(result.has_replanning_request) << ","
         << bool_to_csv(
                result.has_replanning_request &&
                replanning_request_has_work(result.replanning_request)
            ) << ","
         << get_replanning_completed_task_count(result) << ","
         << get_replanning_locked_task_count(result) << ","
         << get_replanning_candidate_task_count(result) << ","
         << get_replanning_available_technician_count(result) << ","
         << get_replanning_busy_technician_count(result) << ","
         << get_replanning_finished_technician_count(result) << ","
         << bool_to_csv(result.has_replanning_result) << ","
         << csv_escape(get_replanning_result_method_id(result)) << ","
         << csv_escape(get_replanning_result_status(result)) << ","
         << bool_to_csv(get_replanning_result_has_new_solution(result)) << ","
         << bool_to_csv(get_replanning_result_is_successful(result)) << ","
         << csv_escape(get_replanning_result_generated_solution_id(result)) << ","
         << bool_to_csv(result.replanning_result_was_applied_to_execution) << ","
         << csv_escape(result.execution_mode) << ","
         << csv_escape(result.planned_solution.solution_id) << ","
         << csv_escape(result.planned_solution.method_id) << ","
         << csv_escape(result.executed_solution.solution_id) << ","
         << csv_escape(result.executed_solution.method_id) << ","
         << result.planned_metrics.objective_value << ","
         << result.executed_metrics.objective_value << ","
         << result.comparison.delta_objective_value << ","
         << result.comparison.percent_objective_value << ","
         << result.planned_metrics.makespan << ","
         << result.executed_metrics.makespan << ","
         << result.comparison.delta_makespan << ","
         << result.comparison.percent_makespan << ","
         << result.planned_metrics.total_travel_time << ","
         << result.executed_metrics.total_travel_time << ","
         << result.comparison.delta_total_travel_time << ","
         << result.comparison.percent_total_travel_time << ","
         << result.planned_metrics.total_service_time << ","
         << result.executed_metrics.total_service_time << ","
         << result.comparison.delta_total_service_time << ","
         << result.comparison.percent_total_service_time << ","
         << result.planned_metrics.total_waiting_time << ","
         << result.executed_metrics.total_waiting_time << ","
         << result.comparison.delta_total_waiting_time << ","
         << result.comparison.percent_total_waiting_time << ","
         << result.planned_metrics.late_task_count << ","
         << result.executed_metrics.late_task_count << ","
         << result.comparison.delta_late_task_count << ","
         << result.planned_metrics.total_lateness << ","
         << result.executed_metrics.total_lateness << ","
         << result.comparison.delta_total_lateness << ","
         << result.executed_metrics.assigned_task_count << ","
         << result.executed_metrics.unassigned_task_count << ","
         << result.effects.size();

    return line.str();
}

void write_no_replanning_experiment_summary_to_csv(
    const NoReplanningExperimentResult& result,
    const std::string& output_path,
    bool append
) {
    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    const bool file_exists =
        std::filesystem::exists(output_path) &&
        std::filesystem::file_size(output_path) > 0;

    std::ofstream file;

    if (append) {
        file.open(output_path, std::ios::app);
    } else {
        file.open(output_path, std::ios::trunc);
    }

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning experiment summary CSV file: " +
            output_path
        );
    }

    if (!append || !file_exists) {
        file << build_header_line() << "\n";
    }

    file << build_data_line(result) << "\n";
}