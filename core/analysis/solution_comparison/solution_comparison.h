#pragma once

#include "core/metrics/solution_metrics/solution_metrics.h"

struct SolutionComparison {
    int delta_route_count = 0;
    int delta_used_route_count = 0;

    int delta_assigned_task_count = 0;
    int delta_unassigned_task_count = 0;

    int delta_total_travel_time = 0;
    int delta_total_service_time = 0;
    int delta_total_waiting_time = 0;

    int delta_late_task_count = 0;
    int delta_total_lateness = 0;

    int delta_makespan = 0;

    double delta_objective_value = 0.0;

    double percent_total_travel_time = 0.0;
    double percent_total_service_time = 0.0;
    double percent_total_waiting_time = 0.0;
    double percent_makespan = 0.0;
    double percent_objective_value = 0.0;
};

SolutionComparison compare_solution_metrics(
    const SolutionMetrics& planned,
    const SolutionMetrics& executed
);

void print_solution_comparison(const SolutionComparison& comparison);