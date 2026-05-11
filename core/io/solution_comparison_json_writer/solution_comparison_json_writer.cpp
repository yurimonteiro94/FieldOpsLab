#include "core/io/solution_comparison_json_writer/solution_comparison_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static json deltas_to_json(const SolutionComparison& comparison) {
    return {
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
    };
}

static json percentages_to_json(const SolutionComparison& comparison) {
    return {
        {"total_travel_time", comparison.percent_total_travel_time},
        {"total_service_time", comparison.percent_total_service_time},
        {"total_waiting_time", comparison.percent_total_waiting_time},
        {"makespan", comparison.percent_makespan},
        {"objective_value", comparison.percent_objective_value}
    };
}

void write_solution_comparison_to_json(
    const Instance& instance,
    const Solution& planned_solution,
    const Solution& executed_solution,
    const SolutionComparison& comparison,
    const std::string& output_path,
    const std::string& result_type
) {
    json result = {
        {"result_type", result_type},
        {"instance_id", instance.instance_id},
        {"instance_name", instance.name},
        {"planned_solution_id", planned_solution.solution_id},
        {"planned_method_id", planned_solution.method_id},
        {"executed_solution_id", executed_solution.solution_id},
        {"executed_method_id", executed_solution.method_id},
        {"deltas", deltas_to_json(comparison)},
        {"percentages", percentages_to_json(comparison)}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open comparison output file for writing: " + output_path
        );
    }

    file << result.dump(4);
}