#include "core/replanning/replanning_application/replanning_application.h"
#include "tests/test_support/test_assertions.h"

#include "core/instance/instance/instance.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/policy/policy_evaluator/policy_evaluator.h"
#include "core/replanning/replanning_engine/replanning_engine.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/simulation/simulation_state/simulation_state.h"
#include "core/solution/solution/solution.h"

#include <string>
#include <vector>

static int count_task_occurrences(
    const Solution& solution,
    const std::string& task_id
) {
    int count = 0;

    for (const auto& route : solution.routes) {
        for (const auto& stop : route.stops) {
            if (stop.task_id == task_id) {
                ++count;
            }
        }
    }

    return count;
}

static bool task_is_assigned_to_technician(
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

void test_replanning_application() {
    Instance instance =
        load_instance_from_json(
            "data/instances/sample_instance_001.json"
        );

    Solution planned_solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    PerturbationPlan perturbation_plan =
        load_perturbation_plan_from_json(
            "data/perturbations/sample_perturbations_moderate_001.json"
        );

    std::vector<Effect> effects =
        build_effects_from_perturbation_plan(perturbation_plan);

    PolicyEvaluationConfig policy_config;

    policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    PolicyEvaluationContext policy_context;

    policy_context.current_time = 125;
    policy_context.effects = effects;

    PolicyDecision policy_decision =
        evaluate_policy(policy_context, policy_config);

    FIELDOPS_EXPECT_TRUE(policy_decision.should_replan());

    SimulationSnapshot snapshot =
        build_simulation_snapshot_from_solution(
            instance,
            planned_solution,
            policy_decision.decision_time
        );

    ReplanningRequest request =
        build_replanning_request_from_snapshot(
            snapshot,
            policy_decision,
            "test_replanning_application_request"
        );

    FIELDOPS_EXPECT_TRUE(replanning_request_has_work(request));

    FIELDOPS_EXPECT_EQ(request.completed_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.locked_task_count(), 1);
    FIELDOPS_EXPECT_EQ(request.candidate_task_count(), 1);

    ReplanningEngineConfig engine_config;

    engine_config.method_id = "greedy_replanning_solver_v1";
    engine_config.result_id = "test_replanning_application_result";

    ReplanningResult replanning_result =
        run_replanning_engine(
            instance,
            request,
            engine_config
        );

    FIELDOPS_EXPECT_EQ(
        replanning_result.status,
        ReplanningResultStatus::SUCCESS
    );

    FIELDOPS_EXPECT_TRUE(replanning_result.has_new_solution());
    FIELDOPS_EXPECT_TRUE(replanning_result.is_successful());

    Solution applied_solution =
        build_solution_with_applied_replanning_result(
            instance,
            planned_solution,
            request,
            replanning_result
        );

    FIELDOPS_EXPECT_EQ(
        applied_solution.status,
        SolutionStatus::FEASIBLE
    );

    FIELDOPS_EXPECT_TRUE(
        applied_solution.solution_id.find(
            "_with_applied_test_replanning_application_result"
        ) != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        applied_solution.method_id.find(
            "greedy_replanning_solver_v1_applied"
        ) != std::string::npos
    );

    FIELDOPS_EXPECT_EQ(
        count_task_occurrences(applied_solution, "task_A"),
        1
    );

    FIELDOPS_EXPECT_EQ(
        count_task_occurrences(applied_solution, "task_B"),
        1
    );

    FIELDOPS_EXPECT_EQ(
        count_task_occurrences(applied_solution, "task_C"),
        1
    );

    FIELDOPS_EXPECT_TRUE(
        task_is_assigned_to_technician(
            applied_solution,
            "task_A",
            "tech_1"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        task_is_assigned_to_technician(
            applied_solution,
            "task_B",
            "tech_2"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        applied_solution.unassigned_task_ids.empty()
    );

    SolutionMetrics applied_metrics =
        calculate_solution_metrics(
            instance,
            applied_solution
        );

    FIELDOPS_EXPECT_EQ(applied_metrics.assigned_task_count, 3);
    FIELDOPS_EXPECT_EQ(applied_metrics.unassigned_task_count, 0);
    FIELDOPS_EXPECT_EQ(applied_metrics.late_task_count, 0);
}