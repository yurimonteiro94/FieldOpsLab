#include "core/solution/solution/solution.h"

#include <iostream>

std::string solution_status_to_string(SolutionStatus status) {
    switch (status) {
        case SolutionStatus::FEASIBLE:
            return "FEASIBLE";

        case SolutionStatus::PARTIAL:
            return "PARTIAL";

        case SolutionStatus::INFEASIBLE:
            return "INFEASIBLE";

        default:
            return "UNKNOWN";
    }
}

void print_solution_summary(const Solution& solution) {
    std::cout << "Solution ID: " << solution.solution_id << "\n";
    std::cout << "Method ID: " << solution.method_id << "\n";
    std::cout << "Instance ID: " << solution.instance_id << "\n";
    std::cout << "Status: " << solution_status_to_string(solution.status) << "\n";
    std::cout << "Objective value: " << solution.objective_value << "\n";
    std::cout << "Routes: " << solution.routes.size() << "\n";
    std::cout << "Unassigned tasks: " << solution.unassigned_task_ids.size() << "\n";

    std::cout << "\nRoutes detail:\n";

    for (const auto& route : solution.routes) {
        std::cout << "  Technician: " << route.technician_id << "\n";
        std::cout << "    Start location: " << route.start_location_id << "\n";
        std::cout << "    End location: " << route.end_location_id << "\n";
        std::cout << "    Stops: " << route.stops.size() << "\n";

        for (const auto& stop : route.stops) {
            std::cout << "      Task: " << stop.task_id
                      << " | arrival: " << stop.arrival_time
                      << " | start: " << stop.start_service_time
                      << " | end: " << stop.end_service_time
                      << " | travel: " << stop.travel_time_from_previous
                      << " | waiting: " << stop.waiting_time
                      << "\n";
        }

        std::cout << "    Total travel time: " << route.total_travel_time << "\n";
        std::cout << "    Total service time: " << route.total_service_time << "\n";
        std::cout << "    Total waiting time: " << route.total_waiting_time << "\n";
        std::cout << "    Route end time: " << route.end_time << "\n";
    }

    if (!solution.unassigned_task_ids.empty()) {
        std::cout << "\nUnassigned tasks:\n";

        for (const auto& task_id : solution.unassigned_task_ids) {
            std::cout << "  - " << task_id << "\n";
        }
    }
}