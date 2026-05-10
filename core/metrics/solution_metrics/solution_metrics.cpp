#include "core/metrics/solution_metrics/solution_metrics.h"

#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>

static std::unordered_map<std::string, Task> build_task_map(
    const Instance& instance
) {
    std::unordered_map<std::string, Task> task_map;

    for (const auto& task : instance.tasks) {
        task_map[task.id] = task;
    }

    return task_map;
}

SolutionMetrics calculate_solution_metrics(
    const Instance& instance,
    const Solution& solution
) {
    SolutionMetrics metrics;

    const auto task_map = build_task_map(instance);

    metrics.route_count = static_cast<int>(solution.routes.size());
    metrics.unassigned_task_count =
        static_cast<int>(solution.unassigned_task_ids.size());

    for (const auto& route : solution.routes) {
        if (!route.stops.empty()) {
            metrics.used_route_count += 1;
        }

        metrics.total_travel_time += route.total_travel_time;
        metrics.total_service_time += route.total_service_time;
        metrics.total_waiting_time += route.total_waiting_time;

        if (route.end_time > metrics.makespan) {
            metrics.makespan = route.end_time;
        }

        for (const auto& stop : route.stops) {
            metrics.assigned_task_count += 1;

            auto task_it = task_map.find(stop.task_id);

            if (task_it == task_map.end()) {
                throw std::runtime_error(
                    "Solution references unknown task_id: " + stop.task_id
                );
            }

            const Task& task = task_it->second;

            if (stop.start_service_time > task.time_window_end) {
                metrics.late_task_count += 1;
                metrics.total_lateness +=
                    stop.start_service_time - task.time_window_end;
            }
        }
    }

    metrics.objective_value = solution.objective_value;

    return metrics;
}

void print_solution_metrics(const SolutionMetrics& metrics) {
    std::cout << "Solution metrics:\n";
    std::cout << "  Route count: " << metrics.route_count << "\n";
    std::cout << "  Used route count: " << metrics.used_route_count << "\n";
    std::cout << "  Assigned tasks: " << metrics.assigned_task_count << "\n";
    std::cout << "  Unassigned tasks: " << metrics.unassigned_task_count << "\n";
    std::cout << "  Total travel time: " << metrics.total_travel_time << "\n";
    std::cout << "  Total service time: " << metrics.total_service_time << "\n";
    std::cout << "  Total waiting time: " << metrics.total_waiting_time << "\n";
    std::cout << "  Late tasks: " << metrics.late_task_count << "\n";
    std::cout << "  Total lateness: " << metrics.total_lateness << "\n";
    std::cout << "  Makespan: " << metrics.makespan << "\n";
    std::cout << "  Objective value: " << metrics.objective_value << "\n";
}