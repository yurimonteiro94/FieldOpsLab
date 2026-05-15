#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/policy/policy/policy.h"
#include "core/replanning/replanning_engine/replanning_engine.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "tests/test_support/test_assertions.h"

static ReplanningRequest build_engine_replanning_request(
    bool should_replan
) {
    ReplanningRequest request;

    request.request_id = "test_engine_replanning_request";
    request.decision_time = 125;
    request.policy_id = "threshold_delay_replanning_policy_v1";
    request.policy_decision =
        policy_decision_type_to_string(
            should_replan ?
            PolicyDecisionType::REPLAN :
            PolicyDecisionType::DO_NOT_REPLAN
        );
    request.should_replan = should_replan;

    request.completed_task_ids.push_back("task_A");
    request.locked_task_ids.push_back("task_B");

    if (should_replan) {
        request.candidate_task_ids.push_back("task_C");
    }

    request.busy_technician_ids.push_back("tech_1");
    request.busy_technician_ids.push_back("tech_2");

    return request;
}

void test_replanning_engine() {
    ReplanningRequest no_replanning_request =
        build_engine_replanning_request(false);

    ReplanningEngineConfig not_implemented_config;

    not_implemented_config.method_id = "replanning_not_implemented_v1";
    not_implemented_config.result_id = "test_not_implemented_result";

    ReplanningResult not_requested_result =
        run_replanning_engine(
            no_replanning_request,
            not_implemented_config
        );

    FIELDOPS_EXPECT_EQ(
        not_requested_result.status,
        ReplanningResultStatus::NOT_REQUESTED
    );

    FIELDOPS_EXPECT_TRUE(!not_requested_result.has_new_solution());

    ReplanningRequest replanning_request =
        build_engine_replanning_request(true);

    ReplanningResult not_implemented_result =
        run_replanning_engine(
            replanning_request,
            not_implemented_config
        );

    FIELDOPS_EXPECT_EQ(
        not_implemented_result.status,
        ReplanningResultStatus::NOT_IMPLEMENTED
    );

    FIELDOPS_EXPECT_TRUE(!not_implemented_result.has_new_solution());

    ReplanningEngineConfig greedy_config;

    greedy_config.method_id = "greedy_replanning_solver_v1";
    greedy_config.result_id = "test_greedy_engine_result";

    ReplanningResult greedy_result_without_instance =
        run_replanning_engine(
            replanning_request,
            greedy_config
        );

    FIELDOPS_EXPECT_EQ(
        greedy_result_without_instance.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(
        !greedy_result_without_instance.has_new_solution()
    );

    Instance instance =
        load_instance_from_json(
            "data/instances/sample_instance_001.json"
        );

    ReplanningResult greedy_result_with_instance =
        run_replanning_engine(
            instance,
            replanning_request,
            greedy_config
        );

    FIELDOPS_EXPECT_EQ(
        greedy_result_with_instance.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_result_with_instance.generated_solution_was_built
    );

    FIELDOPS_EXPECT_TRUE(
        greedy_result_with_instance.has_new_solution()
    );

    FIELDOPS_EXPECT_EQ(
        greedy_result_with_instance.generated_solution.solution_id,
        "test_greedy_engine_result_solution"
    );

    FIELDOPS_EXPECT_EQ(
        greedy_result_with_instance.generated_solution.method_id,
        "greedy_replanning_solver_v1"
    );

    ReplanningEngineConfig unknown_config;

    unknown_config.method_id = "unknown_replanning_method_v1";
    unknown_config.result_id = "test_unknown_result";

    ReplanningResult unknown_result =
        run_replanning_engine(
            replanning_request,
            unknown_config
        );

    FIELDOPS_EXPECT_EQ(
        unknown_result.status,
        ReplanningResultStatus::FAILED
    );

    FIELDOPS_EXPECT_TRUE(!unknown_result.has_new_solution());
}