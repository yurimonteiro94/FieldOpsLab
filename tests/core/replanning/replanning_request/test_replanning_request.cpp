#include "core/replanning/replanning_request/replanning_request.h"
#include "tests/test_support/test_assertions.h"

#include "core/instance/instance/instance.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/policy/policy/policy.h"
#include "core/simulation/simulation_state/simulation_state.h"

void test_replanning_request() {
    Instance instance =
        load_instance_from_json(
            "data/instances/sample_instance_001.json"
        );

    Solution planned_solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SimulationSnapshot snapshot =
        build_simulation_snapshot_from_solution(
            instance,
            planned_solution,
            125
        );

    PolicyDecision decision;

    decision.policy_id = "threshold_delay_replanning_policy_v1";
    decision.type = PolicyDecisionType::REPLAN;
    decision.decision_time = 125;
    decision.reason = "Unit test replanning decision.";

    ReplanningRequest request =
        build_replanning_request_from_snapshot(
            snapshot,
            decision,
            "test_replanning_request_001"
        );

    FIELDOPS_EXPECT_EQ(request.request_id, "test_replanning_request_001");
    FIELDOPS_EXPECT_EQ(request.decision_time, 125);
    FIELDOPS_EXPECT_EQ(request.policy_id, "threshold_delay_replanning_policy_v1");
    FIELDOPS_EXPECT_EQ(request.policy_decision, "REPLAN");
    FIELDOPS_EXPECT_TRUE(request.should_replan);

    FIELDOPS_EXPECT_EQ(request.completed_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.locked_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.candidate_task_count(), 1);

    FIELDOPS_EXPECT_EQ(request.available_technician_count(), 0);
    FIELDOPS_EXPECT_EQ(request.busy_technician_count(), 2);
    FIELDOPS_EXPECT_EQ(request.finished_technician_count(), 0);

    FIELDOPS_EXPECT_TRUE(replanning_request_has_work(request));

    FIELDOPS_EXPECT_EQ(
        request.technician_runtime_states.size(),
        2
    );

    const ReplanningTechnicianRuntimeState* tech_1_state =
        find_replanning_technician_runtime_state_by_id(
            request,
            "tech_1"
        );

    FIELDOPS_EXPECT_TRUE(tech_1_state != nullptr);
    FIELDOPS_EXPECT_EQ(
        tech_1_state->execution_status,
        "TRAVELING"
    );

    FIELDOPS_EXPECT_EQ(
        tech_1_state->current_location_id,
        "task_A_location"
    );

    FIELDOPS_EXPECT_EQ(
        tech_1_state->next_task_id,
        "task_C"
    );

    FIELDOPS_EXPECT_EQ(
        tech_1_state->available_from_time,
        125
    );

    FIELDOPS_EXPECT_TRUE(
        tech_1_state->can_receive_candidate_tasks
    );

    const ReplanningTechnicianRuntimeState* tech_2_state =
        find_replanning_technician_runtime_state_by_id(
            request,
            "tech_2"
        );

    FIELDOPS_EXPECT_TRUE(tech_2_state != nullptr);
    FIELDOPS_EXPECT_EQ(
        tech_2_state->execution_status,
        "SERVICING"
    );

    FIELDOPS_EXPECT_EQ(
        tech_2_state->current_location_id,
        "task_B_location"
    );

    FIELDOPS_EXPECT_EQ(
        tech_2_state->current_task_id,
        "task_B"
    );

    FIELDOPS_EXPECT_EQ(
        tech_2_state->available_from_time,
        165
    );

    FIELDOPS_EXPECT_TRUE(
        tech_2_state->can_receive_candidate_tasks
    );
}