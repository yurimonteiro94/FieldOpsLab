#include "core/analysis/solution_comparison/solution_comparison.h"

#include <iostream>

static double percentage_change(double planned_value, double executed_value) {
    if (planned_value == 0.0) {
        if (executed_value == 0.0) {
            return 0.0;
        }

        return 100.0;
    }

    return ((executed_value - planned_value) / planned_value) * 100.0;
}

SolutionComparison compare_solution_metrics(
    const SolutionMetrics& planned,
    const SolutionMetrics& executed
) {
    SolutionComparison comparison;

    comparison.delta_route_count =
        executed.route_count - planned.route_count;

    comparison.delta_used_route_count =
        executed.used_route_count - planned.used_route_count;

    comparison.delta_assigned_task_count =
        executed.assigned_task_count - planned.assigned_task_count;

    comparison.delta_unassigned_task_count =
        executed.unassigned_task_count - planned.unassigned_task_count;

    comparison.delta_total_travel_time =
        executed.total_travel_time - planned.total_travel_time;

    comparison.delta_total_service_time =
        executed.total_service_time - planned.total_service_time;

    comparison.delta_total_waiting_time =
        executed.total_waiting_time - planned.total_waiting_time;

    comparison.delta_late_task_count =
        executed.late_task_count - planned.late_task_count;

    comparison.delta_total_lateness =
        executed.total_lateness - planned.total_lateness;

    comparison.delta_makespan =
        executed.makespan - planned.makespan;

    comparison.delta_objective_value =
        executed.objective_value - planned.objective_value;

    comparison.percent_total_travel_time =
        percentage_change(
            planned.total_travel_time,
            executed.total_travel_time
        );

    comparison.percent_total_service_time =
        percentage_change(
            planned.total_service_time,
            executed.total_service_time
        );

    comparison.percent_total_waiting_time =
        percentage_change(
            planned.total_waiting_time,
            executed.total_waiting_time
        );

    comparison.percent_makespan =
        percentage_change(planned.makespan, executed.makespan);

    comparison.percent_objective_value =
        percentage_change(
            planned.objective_value,
            executed.objective_value
        );

    return comparison;
}

void print_solution_comparison(const SolutionComparison& comparison) {
    std::cout << "Solution comparison:\n";
    std::cout << "  Delta route count: "
              << comparison.delta_route_count << "\n";

    std::cout << "  Delta used route count: "
              << comparison.delta_used_route_count << "\n";

    std::cout << "  Delta assigned tasks: "
              << comparison.delta_assigned_task_count << "\n";

    std::cout << "  Delta unassigned tasks: "
              << comparison.delta_unassigned_task_count << "\n";

    std::cout << "  Delta total travel time: "
              << comparison.delta_total_travel_time
              << " ("
              << comparison.percent_total_travel_time
              << "%)\n";

    std::cout << "  Delta total service time: "
              << comparison.delta_total_service_time
              << " ("
              << comparison.percent_total_service_time
              << "%)\n";

    std::cout << "  Delta total waiting time: "
              << comparison.delta_total_waiting_time
              << " ("
              << comparison.percent_total_waiting_time
              << "%)\n";

    std::cout << "  Delta late tasks: "
              << comparison.delta_late_task_count << "\n";

    std::cout << "  Delta total lateness: "
              << comparison.delta_total_lateness << "\n";

    std::cout << "  Delta makespan: "
              << comparison.delta_makespan
              << " ("
              << comparison.percent_makespan
              << "%)\n";

    std::cout << "  Delta objective value: "
              << comparison.delta_objective_value
              << " ("
              << comparison.percent_objective_value
              << "%)\n";
}