#pragma once

#include <string>
#include <vector>

enum class SolutionStatus {
    FEASIBLE,
    PARTIAL,
    INFEASIBLE
};

std::string solution_status_to_string(SolutionStatus status);

struct RouteStop {
    std::string task_id;
    std::string location_id;

    int arrival_time = 0;
    int start_service_time = 0;
    int end_service_time = 0;
    int travel_time_from_previous = 0;
    int waiting_time = 0;
};

struct Route {
    std::string technician_id;
    std::string start_location_id;
    std::string end_location_id;

    std::vector<RouteStop> stops;

    int total_travel_time = 0;
    int total_service_time = 0;
    int total_waiting_time = 0;
    int end_time = 0;
};

struct Solution {
    std::string solution_id;
    std::string method_id;
    std::string instance_id;

    SolutionStatus status = SolutionStatus::INFEASIBLE;

    std::vector<Route> routes;
    std::vector<std::string> unassigned_task_ids;

    double objective_value = 0.0;
};

void print_solution_summary(const Solution& solution);