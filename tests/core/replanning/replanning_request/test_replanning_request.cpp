#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/simulation/simulation_state/simulation_state.h"
#include "tests/test_support/test_assertions.h"

#include <string>
#include <vector>

static bool contains_string(
    const std::vector<std::string>& values,
    const std::string& target
) {
    for (const auto& value : values) {
        if (value == target) {
            return true;
        }
    }

    return false;
}

static PolicyDecision make_test_replan_decision(int decision_time) {
    PolicyDecision decision;

    decision.policy_id = "threshold_delay_replanning_policy_v1";
    decision.type = PolicyDecisionType::REPLAN;
    decision.decision_time = decision_time;
    decision.reason = "Test replanning request decision.";

    return decision;
}

static PolicyDecision make_test_do_not_replan_decision(int decision_time) {
    PolicyDecision decision;

    decision.policy_id = "threshold_delay_replanning_policy_v1";
    decision.type = PolicyDecisionType::DO_NOT_REPLAN;
    decision.decision_time = decision_time;
    decision.reason = "Test do-not-replan request decision.";

    return decision;
}

void test_replanning_request() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SimulationSnapshot snapshot_at_125 =
        build_simulation_snapshot_from_solution(instance, solution, 125);

    PolicyDecision replan_decision =
        make_test_replan_decision(125);

    ReplanningRequest request =
        build_replanning_request_from_snapshot(
            snapshot_at_125,
            replan_decision,
            "test_replanning_request_001"
        );

    FIELDOPS_EXPECT_EQ(
        request.request_id,
        "test_replanning_request_001"
    );

    FIELDOPS_EXPECT_EQ(request.decision_time, 125);

    FIELDOPS_EXPECT_EQ(
        request.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(request.policy_decision, "REPLAN");

    FIELDOPS_EXPECT_TRUE(request.should_replan);

    FIELDOPS_EXPECT_EQ(request.completed_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.locked_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.candidate_task_count(), 1);

    FIELDOPS_EXPECT_TRUE(
        contains_string(request.completed_task_ids, "task_A")
    );

    FIELDOPS_EXPECT_TRUE(
        contains_string(request.locked_task_ids, "task_B")
    );

    FIELDOPS_EXPECT_TRUE(
        contains_string(request.candidate_task_ids, "task_C")
    );

    FIELDOPS_EXPECT_EQ(request.available_technician_count(), 0);
    FIELDOPS_EXPECT_EQ(request.busy_technician_count(), 2);
    FIELDOPS_EXPECT_EQ(request.finished_technician_count(), 0);

    FIELDOPS_EXPECT_TRUE(
        contains_string(request.busy_technician_ids, "tech_1")
    );

    FIELDOPS_EXPECT_TRUE(
        contains_string(request.busy_technician_ids, "tech_2")
    );

    FIELDOPS_EXPECT_TRUE(replanning_request_has_work(request));

    PolicyDecision do_not_replan_decision =
        make_test_do_not_replan_decision(125);

    ReplanningRequest no_work_request =
        build_replanning_request_from_snapshot(
            snapshot_at_125,
            do_not_replan_decision,
            "test_replanning_request_002"
        );

    FIELDOPS_EXPECT_TRUE(!no_work_request.should_replan);
    FIELDOPS_EXPECT_TRUE(!replanning_request_has_work(no_work_request));

    SimulationSnapshot snapshot_at_300 =
        build_simulation_snapshot_from_solution(instance, solution, 300);

    ReplanningRequest finished_request =
        build_replanning_request_from_snapshot(
            snapshot_at_300,
            replan_decision,
            "test_replanning_request_003"
        );

    FIELDOPS_EXPECT_EQ(finished_request.completed_task_count(), 3);
    FIELDOPS_EXPECT_EQ(finished_request.candidate_task_count(), 0);
    FIELDOPS_EXPECT_EQ(finished_request.finished_technician_count(), 2);

    FIELDOPS_EXPECT_TRUE(
        !replanning_request_has_work(finished_request)
    );
}