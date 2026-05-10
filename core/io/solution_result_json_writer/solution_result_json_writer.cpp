#include "core/io/solution_result_json_writer/solution_result_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static json route_stop_to_json(const RouteStop& stop) {
    return {
        {"task_id", stop.task_id},
        {"location_id", stop.location_id},
        {"arrival_time", stop.arrival_time},
        {"start_service_time", stop.start_service_time},
        {"end_service_time", stop.end_service_time},
        {"travel_time_from_previous", stop.travel_time_from_previous},
        {"waiting_time", stop.waiting_time}
    };
}

static json route_to_json(const Route& route) {
    json stops = json::array();

    for (const auto& stop : route.stops) {
        stops.push_back(route_stop_to_json(stop));
    }

    return {
        {"technician_id", route.technician_id},
        {"start_location_id", route.start_location_id},
        {"end_location_id", route.end_location_id},
        {"stops", stops},
        {"total_travel_time", route.total_travel_time},
        {"total_service_time", route.total_service_time},
        {"total_waiting_time", route.total_waiting_time},
        {"end_time", route.end_time}
    };
}

static json metrics_to_json(const SolutionMetrics& metrics) {
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

void write_solution_result_to_json(
    const Instance& instance,
    const Solution& solution,
    const SolutionMetrics& metrics,
    const std::string& output_path
) {
    json routes = json::array();

    for (const auto& route : solution.routes) {
        routes.push_back(route_to_json(route));
    }

    json result = {
        {"result_type", "initial_solution_result"},
        {"instance_id", instance.instance_id},
        {"instance_name", instance.name},
        {"solution_id", solution.solution_id},
        {"method_id", solution.method_id},
        {"status", solution_status_to_string(solution.status)},
        {"objective_value", solution.objective_value},
        {"routes", routes},
        {"unassigned_task_ids", solution.unassigned_task_ids},
        {"metrics", metrics_to_json(metrics)}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open output file for writing: " + output_path
        );
    }

    file << result.dump(4);
}