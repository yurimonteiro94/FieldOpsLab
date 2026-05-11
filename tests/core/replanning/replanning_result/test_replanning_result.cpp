#include "core/replanning/replanning_result/replanning_result.h"
#include "tests/test_support/test_assertions.h"

static ReplanningRequest make_base_replanning_result_test_request() {
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

void test_replanning_result() {
    FIELDOPS_EXPECT_EQ(
        replanning_result_status_to_string(
            ReplanningResultStatus::NOT_REQUESTED
        ),
        "NOT_REQUESTED"
    );

    FIELDOPS_EXPECT_EQ(
        replanning_result_status_to_string(
            ReplanningResultStatus::NO_WORK
        ),
        "NO_WORK"
    );

    FIELDOPS_EXPECT_EQ(
        replanning_result_status_to_string(
            ReplanningResultStatus::NOT_IMPLEMENTED
        ),
        "NOT_IMPLEMENTED"
    );

    FIELDOPS_EXPECT_EQ(
        replanning_result_status_to_string(
            ReplanningResultStatus::SUCCESS
        ),
        "SUCCESS"
    );

    FIELDOPS_EXPECT_EQ(
        replanning_result_status_to_string(
            ReplanningResultStatus::FAILED
        ),
        "FAILED"
    );

    ReplanningRequest not_requested_request =
        make_base_replanning_result_test_request();

    not_requested_request.should_replan = false;
    not_requested_request.policy_decision = "DO_NOT_REPLAN";

    ReplanningResult not_requested_result =
        build_not_implemented_replanning_result(
            not_requested_request,
            "test_replanning_result_not_requested",
            "replanning_not_implemented_v1"
        );

    FIELDOPS_EXPECT_EQ(
        not_requested_result.result_id,
        "test_replanning_result_not_requested"
    );

    FIELDOPS_EXPECT_EQ(
        not_requested_result.request_id,
        "test_replanning_request_001"
    );

    FIELDOPS_EXPECT_EQ(
        not_requested_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    FIELDOPS_EXPECT_TRUE(!not_requested_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!not_requested_result.is_successful());

    ReplanningRequest no_work_request =
        make_base_replanning_result_test_request();

    no_work_request.candidate_task_ids.clear();

    ReplanningResult no_work_result =
        build_not_implemented_replanning_result(
            no_work_request,
            "test_replanning_result_no_work",
            "replanning_not_implemented_v1"
        );

    FIELDOPS_EXPECT_EQ(
        no_work_result.status,
        ReplanningResultStatus::NO_WORK
    );

    FIELDOPS_EXPECT_EQ(no_work_result.candidate_task_count, 0);
    FIELDOPS_EXPECT_TRUE(!no_work_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!no_work_result.is_successful());

    ReplanningRequest work_request =
        make_base_replanning_result_test_request();

    ReplanningResult not_implemented_result =
        build_not_implemented_replanning_result(
            work_request,
            "test_replanning_result_not_implemented",
            "replanning_not_implemented_v1"
        );

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.status,
        ReplanningResultStatus::NOT_IMPLEMENTED
    );

    FIELDOPS_EXPECT_EQ(not_implemented_result.decision_time, 125);
    FIELDOPS_EXPECT_EQ(not_implemented_result.completed_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.locked_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.candidate_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.busy_technician_count, 2);

    FIELDOPS_EXPECT_TRUE(!not_implemented_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!not_implemented_result.is_successful());
}