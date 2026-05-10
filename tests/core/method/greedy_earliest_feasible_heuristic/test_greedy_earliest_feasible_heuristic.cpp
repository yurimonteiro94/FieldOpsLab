#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "tests/test_support/test_assertions.h"

void test_greedy_earliest_feasible_heuristic() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    FIELDOPS_EXPECT_TRUE(solution.status == SolutionStatus::FEASIBLE);
    FIELDOPS_EXPECT_EQ(solution.routes.size(), 2);
    FIELDOPS_EXPECT_EQ(solution.unassigned_task_ids.size(), 0);
    FIELDOPS_EXPECT_EQ(solution.method_id, "greedy_earliest_feasible_heuristic_v1");
}