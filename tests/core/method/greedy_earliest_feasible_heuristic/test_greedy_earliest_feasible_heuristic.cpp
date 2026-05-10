#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "tests/test_support/test_assertions.h"

#include <unordered_set>

void test_greedy_earliest_feasible_heuristic() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    FIELDOPS_EXPECT_TRUE(solution.status == SolutionStatus::FEASIBLE);
    FIELDOPS_EXPECT_EQ(solution.routes.size(), 2);
    FIELDOPS_EXPECT_EQ(solution.unassigned_task_ids.size(), 0);
    FIELDOPS_EXPECT_EQ(solution.method_id, "greedy_earliest_feasible_heuristic_v1");

    int assigned_task_count = 0;
    std::unordered_set<std::string> assigned_task_ids;

    for (const auto& route : solution.routes) {
        for (const auto& stop : route.stops) {
            assigned_task_count += 1;
            assigned_task_ids.insert(stop.task_id);
        }
    }

    FIELDOPS_EXPECT_EQ(assigned_task_count, 3);
    FIELDOPS_EXPECT_EQ(assigned_task_ids.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        assigned_task_ids.find("task_A") != assigned_task_ids.end()
    );

    FIELDOPS_EXPECT_TRUE(
        assigned_task_ids.find("task_B") != assigned_task_ids.end()
    );

    FIELDOPS_EXPECT_TRUE(
        assigned_task_ids.find("task_C") != assigned_task_ids.end()
    );
}