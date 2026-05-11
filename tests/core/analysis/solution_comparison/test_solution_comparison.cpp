#include "core/analysis/solution_comparison/solution_comparison.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/simulation/no_replanning_execution/no_replanning_execution.h"
#include "tests/test_support/test_assertions.h"

#include <vector>

void test_solution_comparison() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution planned_solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SolutionMetrics planned_metrics =
        calculate_solution_metrics(instance, planned_solution);

    PerturbationPlan perturbation_plan =
        load_perturbation_plan_from_json(
            "data/perturbations/sample_perturbations_001.json"
        );

    std::vector<Effect> effects =
        build_effects_from_perturbation_plan(perturbation_plan);

    Solution executed_solution =
        execute_solution_without_replanning(
            instance,
            planned_solution,
            effects
        );

    SolutionMetrics executed_metrics =
        calculate_solution_metrics(instance, executed_solution);

    SolutionComparison comparison =
        compare_solution_metrics(planned_metrics, executed_metrics);

    FIELDOPS_EXPECT_EQ(comparison.delta_route_count, 0);
    FIELDOPS_EXPECT_EQ(comparison.delta_used_route_count, 0);
    FIELDOPS_EXPECT_EQ(comparison.delta_assigned_task_count, 0);
    FIELDOPS_EXPECT_EQ(comparison.delta_unassigned_task_count, 0);

    FIELDOPS_EXPECT_EQ(comparison.delta_total_travel_time, 50);
    FIELDOPS_EXPECT_EQ(comparison.delta_total_service_time, 30);
    FIELDOPS_EXPECT_EQ(comparison.delta_total_waiting_time, -35);

    FIELDOPS_EXPECT_EQ(comparison.delta_late_task_count, 0);
    FIELDOPS_EXPECT_EQ(comparison.delta_total_lateness, 0);

    FIELDOPS_EXPECT_EQ(comparison.delta_makespan, 15);
    FIELDOPS_EXPECT_TRUE(comparison.delta_objective_value == 15.0);

    FIELDOPS_EXPECT_TRUE(comparison.percent_total_travel_time > 34.0);
    FIELDOPS_EXPECT_TRUE(comparison.percent_total_service_time > 19.0);
    FIELDOPS_EXPECT_TRUE(comparison.percent_total_waiting_time < 0.0);
    FIELDOPS_EXPECT_TRUE(comparison.percent_makespan > 5.0);
    FIELDOPS_EXPECT_TRUE(comparison.percent_objective_value > 4.0);
}