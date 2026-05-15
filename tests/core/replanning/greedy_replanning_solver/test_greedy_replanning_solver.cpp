#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/policy/policy/policy.h"
#include "core/replanning/greedy_replanning_solver/greedy_replanning_solver.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "tests/test_support/test_assertions.h"

static ReplanningRequest build_sample_greedy_replanning_request() {
    ReplanningRequest request;

    request.request_id = "test_greedy_replanning_request";
    request.decision_time = 125;
    request.policy_id = "threshold_delay_replanning_policy_v1";
    request.policy_decision =
        policy_decision_type_to_string(PolicyDecisionType::REPLAN);
    request.should_replan = true;

    request.completed_task_ids.push_back("task_A");
    request.locked_task_ids.push_back("task_B");
    request.candidate_task_ids.push_back("task_C");

    request.busy_technician_ids.push_back("tech_1");
    request.busy_technician_ids.push_back("tech_2");

    return request;
}

void test_greedy_replanning_solver() {
    ReplanningRequest request =
        build_sample_greedy_replanning_request();

    GreedyReplanningSolverConfig config;

    config.result_id = "test_greedy_replanning_result";
    config.generated_solution_id = "test_greedy_replanned_solution";

    ReplanningResult result =
        run_greedy_replanning_solver(request, config);

    FIELDOPS_EXPECT_EQ(
        result.result_id,
        "test_greedy_replanning_result"
    );

    FIELDOPS_EXPECT_EQ(
        result.request_id,
        "test_greedy_replanning_request"
    );

    FIELDOPS_EXPECT_EQ(
        result.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_EQ(
        result.generated_solution_id,
        "test_greedy_replanned_solution"
    );

    FIELDOPS_EXPECT_TRUE(!result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(!result.generated_solution_was_built);

    Instance instance =
        load_instance_from_json(
            "data/instances/sample_instance_001.json"
        );

    ReplanningResult result_with_solution =
        run_greedy_replanning_solver(
            instance,
            request,
            config
        );

    FIELDOPS_EXPECT_EQ(
        result_with_solution.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(result_with_solution.generated_solution_was_built);
    FIELDOPS_EXPECT_TRUE(result_with_solution.has_new_solution());
    FIELDOPS_EXPECT_TRUE(result_with_solution.is_successful());

    FIELDOPS_EXPECT_EQ(
        result_with_solution.generated_solution.solution_id,
        "test_greedy_replanned_solution"
    );

    FIELDOPS_EXPECT_EQ(
        result_with_solution.generated_solution.method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        result_with_solution.generated_solution.instance_id,
        "sample_instance_001"
    );

    FIELDOPS_EXPECT_TRUE(
        result_with_solution.generated_solution.status ==
        SolutionStatus::FEASIBLE ||
        result_with_solution.generated_solution.status ==
        SolutionStatus::PARTIAL
    );

    FIELDOPS_EXPECT_TRUE(
        !result_with_solution.generated_solution.routes.empty()
    );
}