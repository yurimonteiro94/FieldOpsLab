#include "core/replanning/replanning_application/replanning_application.h"

#include <algorithm>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

static std::unordered_map<std::string, Task> build_task_map(
    const Instance& instance
) {
    std::unordered_map<std::string, Task> task_map;

    for (const auto& task : instance.tasks) {
        task_map[task.id] = task;
    }

    return task_map;
}

static std::unordered_map<std::string, Technician> build_technician_map(
    const Instance& instance
) {
    std::unordered_map<std::string, Technician> technician_map;

    for (const auto& technician : instance.technicians) {
        technician_map[technician.id] = technician;
    }

    return technician_map;
}

static std::unordered_map<std::string, int> build_location_index_map(
    const TravelMatrix& matrix
) {
    std::unordered_map<std::string, int> location_index;

    for (int i = 0; i < static_cast<int>(matrix.location_ids.size()); ++i) {
        location_index[matrix.location_ids[i]] = i;
    }

    return location_index;
}

static bool vector_contains(
    const std::vector<std::string>& values,
    const std::string& value
) {
    return std::find(values.begin(), values.end(), value) != values.end();
}

static bool should_keep_original_stop(
    const RouteStop& stop,
    const ReplanningRequest& request
) {
    return vector_contains(request.completed_task_ids, stop.task_id) ||
           vector_contains(request.locked_task_ids, stop.task_id);
}

static bool is_candidate_task(
    const std::string& task_id,
    const ReplanningRequest& request
) {
    return vector_contains(request.candidate_task_ids, task_id);
}

static Route build_route_shell_from_planned_route(
    const Route& planned_route
) {
    Route route;

    route.technician_id = planned_route.technician_id;
    route.start_location_id = planned_route.start_location_id;
    route.end_location_id = planned_route.end_location_id;

    return route;
}

static int find_route_index_by_technician_id(
    const Solution& solution,
    const std::string& technician_id
) {
    for (int i = 0; i < static_cast<int>(solution.routes.size()); ++i) {
        if (solution.routes[i].technician_id == technician_id) {
            return i;
        }
    }

    return -1;
}

static void add_replanned_candidate_stops(
    Solution& applied_solution,
    const ReplanningRequest& request,
    const ReplanningResult& replanning_result
) {
    for (const auto& replanned_route :
         replanning_result.generated_solution.routes) {
        int route_index =
            find_route_index_by_technician_id(
                applied_solution,
                replanned_route.technician_id
            );

        if (route_index < 0) {
            Route new_route;

            new_route.technician_id = replanned_route.technician_id;
            new_route.start_location_id = replanned_route.start_location_id;
            new_route.end_location_id = replanned_route.end_location_id;

            applied_solution.routes.push_back(new_route);
            route_index = static_cast<int>(applied_solution.routes.size()) - 1;
        }

        for (const auto& stop : replanned_route.stops) {
            if (!is_candidate_task(stop.task_id, request)) {
                continue;
            }

            applied_solution.routes[route_index].stops.push_back(stop);
        }
    }
}

static void add_unassigned_tasks(
    Solution& applied_solution,
    const Solution& planned_solution,
    const ReplanningRequest& request,
    const ReplanningResult& replanning_result
) {
    for (const auto& task_id : planned_solution.unassigned_task_ids) {
        if (!is_candidate_task(task_id, request)) {
            applied_solution.unassigned_task_ids.push_back(task_id);
        }
    }

    for (const auto& task_id :
         replanning_result.generated_solution.unassigned_task_ids) {
        if (!vector_contains(applied_solution.unassigned_task_ids, task_id)) {
            applied_solution.unassigned_task_ids.push_back(task_id);
        }
    }
}

static void recalculate_route_times(
    const Instance& instance,
    const std::unordered_map<std::string, Task>& task_map,
    const std::unordered_map<std::string, Technician>& technician_map,
    const std::unordered_map<std::string, int>& location_index,
    Route& route
) {
    if (technician_map.find(route.technician_id) == technician_map.end()) {
        throw std::runtime_error(
            "Unknown technician in replanning application: " +
            route.technician_id
        );
    }

    const Technician& technician =
        technician_map.at(route.technician_id);

    std::string current_location_id = route.start_location_id;
    int current_location_index = location_index.at(current_location_id);
    int current_time = technician.available_from;

    route.total_travel_time = 0;
    route.total_service_time = 0;
    route.total_waiting_time = 0;

    for (auto& stop : route.stops) {
        if (task_map.find(stop.task_id) == task_map.end()) {
            throw std::runtime_error(
                "Unknown task in replanning application: " +
                stop.task_id
            );
        }

        const Task& task = task_map.at(stop.task_id);

        stop.location_id = task.location_id;

        const int stop_location_index =
            location_index.at(stop.location_id);

        const int travel_time =
            instance.travel_matrix.duration(
                current_location_index,
                stop_location_index
            );

        const int arrival_time = current_time + travel_time;

        const int start_service_time =
            std::max(arrival_time, task.time_window_start);

        const int waiting_time = start_service_time - arrival_time;

        const int end_service_time =
            start_service_time + task.service_duration;

        stop.arrival_time = arrival_time;
        stop.start_service_time = start_service_time;
        stop.end_service_time = end_service_time;
        stop.travel_time_from_previous = travel_time;
        stop.waiting_time = waiting_time;

        route.total_travel_time += travel_time;
        route.total_service_time += task.service_duration;
        route.total_waiting_time += waiting_time;

        current_location_id = stop.location_id;
        current_location_index = stop_location_index;
        current_time = end_service_time;
    }

    const int end_location_index =
        location_index.at(route.end_location_id);

    const int return_travel_time =
        instance.travel_matrix.duration(
            current_location_index,
            end_location_index
        );

    route.total_travel_time += return_travel_time;
    route.end_time = current_time + return_travel_time;
}

static void recalculate_solution_objective_and_status(
    Solution& solution
) {
    int total_travel_time = 0;
    int total_waiting_time = 0;

    bool has_assigned_task = false;

    for (const auto& route : solution.routes) {
        total_travel_time += route.total_travel_time;
        total_waiting_time += route.total_waiting_time;

        if (!route.stops.empty()) {
            has_assigned_task = true;
        }
    }

    const double unassigned_penalty = 100000.0;

    solution.objective_value =
        static_cast<double>(total_travel_time + total_waiting_time) +
        unassigned_penalty *
        static_cast<double>(solution.unassigned_task_ids.size());

    if (solution.unassigned_task_ids.empty()) {
        solution.status = SolutionStatus::FEASIBLE;
        return;
    }

    solution.status =
        has_assigned_task ? SolutionStatus::PARTIAL
                          : SolutionStatus::INFEASIBLE;
}

Solution build_solution_with_applied_replanning_result(
    const Instance& instance,
    const Solution& planned_solution,
    const ReplanningRequest& request,
    const ReplanningResult& replanning_result
) {
    if (!replanning_result.has_new_solution()) {
        throw std::runtime_error(
            "Cannot apply replanning result without a generated solution."
        );
    }

    Solution applied_solution;

    applied_solution.solution_id =
        planned_solution.solution_id + "_with_applied_" +
        replanning_result.result_id;

    applied_solution.method_id =
        planned_solution.method_id + "+" +
        replanning_result.method_id + "_applied";

    applied_solution.instance_id = planned_solution.instance_id;

    for (const auto& planned_route : planned_solution.routes) {
        Route applied_route =
            build_route_shell_from_planned_route(planned_route);

        for (const auto& stop : planned_route.stops) {
            if (should_keep_original_stop(stop, request)) {
                applied_route.stops.push_back(stop);
            }
        }

        applied_solution.routes.push_back(applied_route);
    }

    add_replanned_candidate_stops(
        applied_solution,
        request,
        replanning_result
    );

    add_unassigned_tasks(
        applied_solution,
        planned_solution,
        request,
        replanning_result
    );

    const auto task_map = build_task_map(instance);
    const auto technician_map = build_technician_map(instance);
    const auto location_index = build_location_index_map(instance.travel_matrix);

    for (auto& route : applied_solution.routes) {
        recalculate_route_times(
            instance,
            task_map,
            technician_map,
            location_index,
            route
        );
    }

    recalculate_solution_objective_and_status(applied_solution);

    return applied_solution;
}