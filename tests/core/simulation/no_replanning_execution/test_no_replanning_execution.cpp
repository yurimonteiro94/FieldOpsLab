#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/simulation/no_replanning_execution/no_replanning_execution.h"
#include "tests/test_support/test_assertions.h"

#include <vector>

static const Route& find_route_by_technician(
    const Solution& solution,
    const std::string& technician_id
) {
    for (const auto& route : solution.routes) {
        if (route.technician_id == technician_id) {
            return route;
        }
    }

    throw std::runtime_error("Route not found for technician: " + technician_id);
}

void test_no_replanning_execution() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution planned_solution =
        build_initial_solution_greedy_earliest_feasible(instance);

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

    FIELDOPS_EXPECT_TRUE(
        executed_solution.status == SolutionStatus::FEASIBLE
    );

    const Route& tech_1_route =
        find_route_by_technician(executed_solution, "tech_1");

    const Route& tech_2_route =
        find_route_by_technician(executed_solution, "tech_2");

    FIELDOPS_EXPECT_EQ(tech_1_route.end_time, 285);
    FIELDOPS_EXPECT_EQ(tech_2_route.end_time, 225);

    FIELDOPS_EXPECT_EQ(tech_1_route.total_travel_time, 135);
    FIELDOPS_EXPECT_EQ(tech_2_route.total_service_time, 75);

    SolutionMetrics metrics =
        calculate_solution_metrics(instance, executed_solution);

    FIELDOPS_EXPECT_EQ(metrics.assigned_task_count, 3);
    FIELDOPS_EXPECT_EQ(metrics.unassigned_task_count, 0);
    FIELDOPS_EXPECT_EQ(metrics.total_travel_time, 195);
    FIELDOPS_EXPECT_EQ(metrics.total_service_time, 185);
    FIELDOPS_EXPECT_EQ(metrics.total_waiting_time, 130);
    FIELDOPS_EXPECT_EQ(metrics.makespan, 285);
}