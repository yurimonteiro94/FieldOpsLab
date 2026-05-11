#include "core/replanning/greedy_replanning_solver/greedy_replanning_solver.h"
#include "tests/test_support/test_assertions.h"

static ReplanningRequest make_greedy_replanning_solver_test_request() {
    ReplanningRequest request;

    request.request_id = "test_replanning_request_001";
    request.decision_time = 125;
    request.policy_id = "threshold_delay_replanning_policy_v1";
    request.policy_decision = "REPLAN";
    request.should_replan = true;

    request.completed_task_ids.push_back("task_A");
    request.locked_task_ids.push_back("task_B");
    request.candidate_task_ids.push_back("task_C");

    request.busy_technician_ids.push_back("tech_1");
    request.busy_technician_ids.push_back("tech_2");

    return request;
}

void test_greedy_replanning_solver() {
    GreedyReplanningSolverConfig config;

    config.result_id = "test_greedy_replanning_result_001";
    config.generated_solution_id = "test_greedy_replanned_solution_001";

    ReplanningRequest work_request =
        make_greedy_replanning_solver_test_request();

    ReplanningResult success_result =
        run_greedy_replanning_solver(work_request, config);

    FIELDOPS_EXPECT_EQ(
        success_result.result_id,
        "test_greedy_replanning_result_001"
    );

    FIELDOPS_EXPECT_EQ(
        success_result.request_id,
        "test_replanning_request_001"
    );

    FIELDOPS_EXPECT_EQ(
        success_result.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        success_result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_EQ(success_result.decision_time, 125);
    FIELDOPS_EXPECT_EQ(success_result.completed_task_count, 1);
    FIELDOPS_EXPECT_EQ(success_result.locked_task_count, 1);
    FIELDOPS_EXPECT_EQ(success_result.candidate_task_count, 1);
    FIELDOPS_EXPECT_EQ(success_result.busy_technician_count, 2);

    FIELDOPS_EXPECT_EQ(
        success_result.generated_solution_id,
        "test_greedy_replanned_solution_001"
    );

    FIELDOPS_EXPECT_TRUE(success_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(success_result.is_successful());

    ReplanningRequest not_requested_request =
        make_greedy_replanning_solver_test_request();

    not_requested_request.should_replan = false;
    not_requested_request.policy_decision = "DO_NOT_REPLAN";

    ReplanningResult not_requested_result =
        run_greedy_replanning_solver(not_requested_request, config);

    FIELDOPS_EXPECT_EQ(
        not_requested_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    FIELDOPS_EXPECT_TRUE(!not_requested_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!not_requested_result.is_successful());

    ReplanningRequest no_work_request =
        make_greedy_replanning_solver_test_request();

    no_work_request.candidate_task_ids.clear();

    ReplanningResult no_work_result =
        run_greedy_replanning_solver(no_work_request, config);

    FIELDOPS_EXPECT_EQ(
        no_work_result.status,
        ReplanningResultStatus::NO_WORK
    );

    FIELDOPS_EXPECT_EQ(no_work_result.candidate_task_count, 0);
    FIELDOPS_EXPECT_TRUE(!no_work_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!no_work_result.is_successful());
}