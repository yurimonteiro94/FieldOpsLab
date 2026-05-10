#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "tests/test_support/test_assertions.h"

void test_solution_metrics() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SolutionMetrics metrics =
        calculate_solution_metrics(instance, solution);

    FIELDOPS_EXPECT_EQ(metrics.route_count, 2);
    FIELDOPS_EXPECT_EQ(metrics.used_route_count, 2);
    FIELDOPS_EXPECT_EQ(metrics.assigned_task_count, 3);
    FIELDOPS_EXPECT_EQ(metrics.unassigned_task_count, 0);
    FIELDOPS_EXPECT_EQ(metrics.total_travel_time, 145);
    FIELDOPS_EXPECT_EQ(metrics.total_service_time, 155);
    FIELDOPS_EXPECT_EQ(metrics.total_waiting_time, 165);
    FIELDOPS_EXPECT_EQ(metrics.late_task_count, 0);
    FIELDOPS_EXPECT_EQ(metrics.total_lateness, 0);
    FIELDOPS_EXPECT_EQ(metrics.makespan, 270);
}