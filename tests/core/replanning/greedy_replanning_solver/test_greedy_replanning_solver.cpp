#include "core/replanning/greedy_replanning_solver/greedy_replanning_solver.h"
#include "tests/test_support/test_assertions.h"

#include "core/instance/instance/instance.h"
#include "core/io/instance_json_loader/instance_json_loader.h"

#include <string>

static bool solution_contains_task_on_technician(
    const Solution& solution,
    const std::string& task_id,
    const std::string& technician_id
) {
    for (const auto& route : solution.routes) {
        if (route.technician_id != technician_id) {
            continue;
        }

        for (const auto& stop : route.stops) {
            if (stop.task_id == task_id) {
                return true;
            }
        }
    }

    return false;
}

static const Route* find_route_by_technician_id(
    const Solution& solution,
    const std::string& technician_id
) {
    for (const auto& route : solution.routes) {
        if (route.technician_id == technician_id) {
            return &route;
        }
    }

    return nullptr;
}

void test_greedy_replanning_solver() {
    Instance instance =
        load_instance_from_json(
            "data/instances/sample_instance_001.json"
        );

    ReplanningRequest request;

    request.request_id = "test_greedy_replanning_request_001";
    request.decision_time = 125;
    request.policy_id = "threshold_delay_replanning_policy_v1";
    request.policy_decision = "REPLAN";
    request.should_replan = true;

    request.completed_task_ids.push_back("task_A");
    request.locked_task_ids.push_back("task_C");
    request.candidate_task_ids.push_back("task_B");

    request.busy_technician_ids.push_back("tech_1");
    request.busy_technician_ids.push_back("tech_2");

    ReplanningTechnicianRuntimeState tech_1_state;

    tech_1_state.technician_id = "tech_1";
    tech_1_state.execution_status = "SERVICING";
    tech_1_state.current_location_id = "task_A_location";
    tech_1_state.current_task_id = "task_A";
    tech_1_state.available_from_time = 180;
    tech_1_state.can_receive_candidate_tasks = false;

    ReplanningTechnicianRuntimeState tech_2_state;

    tech_2_state.technician_id = "tech_2";
    tech_2_state.execution_status = "WAITING";
    tech_2_state.current_location_id = "task_B_location";
    tech_2_state.current_task_id = "task_B";
    tech_2_state.available_from_time = 125;
    tech_2_state.can_receive_candidate_tasks = true;

    request.technician_runtime_states.push_back(tech_1_state);
    request.technician_runtime_states.push_back(tech_2_state);

    GreedyReplanningSolverConfig config;

    config.method_id = "greedy_replanning_solver_v1";
    config.result_id = "test_greedy_replanning_result_001";
    config.generated_solution_id = "test_greedy_replanned_solution_001";

    ReplanningResult result =
        run_greedy_replanning_solver(
            instance,
            request,
            config
        );

    FIELDOPS_EXPECT_EQ(
        result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(result.is_successful());
    FIELDOPS_EXPECT_TRUE(result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(result.generated_solution_was_built);

    FIELDOPS_EXPECT_EQ(
        result.generated_solution.solution_id,
        "test_greedy_replanned_solution_001"
    );

    FIELDOPS_EXPECT_EQ(
        result.generated_solution.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        result.generated_solution.status,
        SolutionStatus::FEASIBLE
    );

    FIELDOPS_EXPECT_TRUE(
        solution_contains_task_on_technician(
            result.generated_solution,
            "task_B",
            "tech_2"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        !solution_contains_task_on_technician(
            result.generated_solution,
            "task_B",
            "tech_1"
        )
    );

    const Route* tech_2_route =
        find_route_by_technician_id(
            result.generated_solution,
            "tech_2"
        );

    FIELDOPS_EXPECT_TRUE(tech_2_route != nullptr);

    FIELDOPS_EXPECT_EQ(
        tech_2_route->start_location_id,
        "task_B_location"
    );

    FIELDOPS_EXPECT_EQ(
        tech_2_route->stops.size(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        tech_2_route->stops[0].task_id,
        "task_B"
    );

    FIELDOPS_EXPECT_TRUE(
        result.generated_solution.unassigned_task_ids.empty()
    );
}