#pragma once

#include "core/instance/instance/instance.h"
#include "core/solution/solution/solution.h"

struct SolutionMetrics {
    int route_count = 0;
    int used_route_count = 0;

    int assigned_task_count = 0;
    int unassigned_task_count = 0;

    int total_travel_time = 0;
    int total_service_time = 0;
    int total_waiting_time = 0;

    int late_task_count = 0;
    int total_lateness = 0;

    int makespan = 0;

    double objective_value = 0.0;
};

SolutionMetrics calculate_solution_metrics(
    const Instance& instance,
    const Solution& solution
);

void print_solution_metrics(const SolutionMetrics& metrics);