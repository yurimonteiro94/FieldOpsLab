#include "core/replanning/replanning_engine/replanning_engine.h"
#include "tests/test_support/test_assertions.h"

static ReplanningRequest make_replanning_engine_test_request() {
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

void test_replanning_engine() {
    ReplanningRequest work_request =
        make_replanning_engine_test_request();

    ReplanningEngineConfig config;

    config.method_id = "replanning_not_implemented_v1";
    config.result_id = "test_replanning_engine_result_001";

    ReplanningResult not_implemented_result =
        run_replanning_engine(work_request, config);

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.result_id,
        "test_replanning_engine_result_001"
    );

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.request_id,
        "test_replanning_request_001"
    );

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.status,
        ReplanningResultStatus::NOT_IMPLEMENTED
    );

    FIELDOPS_EXPECT_EQ(not_implemented_result.completed_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.locked_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.candidate_task_count, 1);
    FIELDOPS_EXPECT_EQ(not_implemented_result.busy_technician_count, 2);

    FIELDOPS_EXPECT_TRUE(!not_implemented_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!not_implemented_result.is_successful());

    ReplanningRequest not_requested_request =
        make_replanning_engine_test_request();

    not_requested_request.should_replan = false;
    not_requested_request.policy_decision = "DO_NOT_REPLAN";

    ReplanningResult not_requested_result =
        run_replanning_engine(not_requested_request, config);

    FIELDOPS_EXPECT_EQ(
        not_requested_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    ReplanningRequest no_work_request =
        make_replanning_engine_test_request();

    no_work_request.candidate_task_ids.clear();

    ReplanningResult no_work_result =
        run_replanning_engine(no_work_request, config);

    FIELDOPS_EXPECT_EQ(
        no_work_result.status,
        ReplanningResultStatus::NO_WORK
    );

    ReplanningEngineConfig unknown_config;

    unknown_config.method_id = "unknown_replanning_method_v1";
    unknown_config.result_id = "test_replanning_engine_unknown_result";

    ReplanningResult unknown_result =
        run_replanning_engine(work_request, unknown_config);

    FIELDOPS_EXPECT_EQ(
        unknown_result.result_id,
        "test_replanning_engine_unknown_result"
    );

    FIELDOPS_EXPECT_EQ(
        unknown_result.method_id,
        "unknown_replanning_method_v1"
    );

    FIELDOPS_EXPECT_EQ(
        unknown_result.status,
        ReplanningResultStatus::FAILED
    );

    FIELDOPS_EXPECT_TRUE(!unknown_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!unknown_result.is_successful());
}