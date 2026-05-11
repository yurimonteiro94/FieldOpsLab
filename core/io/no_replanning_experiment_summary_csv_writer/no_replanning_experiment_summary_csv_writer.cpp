#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <ios>
#include <stdexcept>
#include <string>

static std::string csv_escape(const std::string& value) {
    bool needs_quotes = false;

    for (char character : value) {
        if (character == ',' ||
            character == '"' ||
            character == '\n' ||
            character == '\r') {
            needs_quotes = true;
            break;
        }
    }

    if (!needs_quotes) {
        return value;
    }

    std::string escaped = "\"";

    for (char character : value) {
        if (character == '"') {
            escaped += "\"\"";
        } else {
            escaped += character;
        }
    }

    escaped += "\"";

    return escaped;
}

static std::string bool_to_string(bool value) {
    return value ? "true" : "false";
}

static void write_header(std::ofstream& file) {
    file
        << "result_type,"
        << "experiment_id,"
        << "scenario_id,"
        << "replication_id,"
        << "seed,"
        << "notes,"
        << "instance_id,"
        << "perturbation_plan_id,"
        << "policy_id,"
        << "policy_decision,"
        << "policy_should_replan,"
        << "planned_solution_id,"
        << "planned_method_id,"
        << "executed_solution_id,"
        << "executed_method_id,"
        << "planned_objective_value,"
        << "executed_objective_value,"
        << "delta_objective_value,"
        << "percent_objective_value,"
        << "planned_makespan,"
        << "executed_makespan,"
        << "delta_makespan,"
        << "percent_makespan,"
        << "planned_total_travel_time,"
        << "executed_total_travel_time,"
        << "delta_total_travel_time,"
        << "percent_total_travel_time,"
        << "planned_total_service_time,"
        << "executed_total_service_time,"
        << "delta_total_service_time,"
        << "percent_total_service_time,"
        << "planned_total_waiting_time,"
        << "executed_total_waiting_time,"
        << "delta_total_waiting_time,"
        << "percent_total_waiting_time,"
        << "planned_late_task_count,"
        << "executed_late_task_count,"
        << "delta_late_task_count,"
        << "planned_total_lateness,"
        << "executed_total_lateness,"
        << "delta_total_lateness,"
        << "assigned_task_count,"
        << "unassigned_task_count,"
        << "effect_count"
        << "\n";
}

static void write_row(
    std::ofstream& file,
    const NoReplanningExperimentResult& result
) {
    file
        << csv_escape("no_replanning_experiment_result") << ","
        << csv_escape(result.metadata.experiment_id) << ","
        << csv_escape(result.metadata.scenario_id) << ","
        << result.metadata.replication_id << ","
        << result.metadata.seed << ","
        << csv_escape(result.metadata.notes) << ","
        << csv_escape(result.instance.instance_id) << ","
        << csv_escape(result.perturbation_plan.perturbation_plan_id) << ","
        << csv_escape(result.policy_decision.policy_id) << ","
        << csv_escape(policy_decision_type_to_string(result.policy_decision.type)) << ","
        << bool_to_string(result.policy_decision.should_replan()) << ","
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
        << result.effects.size()
        << "\n";
}

void write_no_replanning_experiment_summary_to_csv(
    const NoReplanningExperimentResult& result,
    const std::string& output_path,
    bool write_header_line,
    bool append
) {
    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ios_base::openmode mode = std::ios::out;

    if (append) {
        mode = mode | std::ios::app;
    } else {
        mode = mode | std::ios::trunc;
    }

    std::ofstream file(output_path, mode);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning experiment summary CSV for writing: " +
            output_path
        );
    }

    if (write_header_line) {
        write_header(file);
    }

    write_row(file, result);
}