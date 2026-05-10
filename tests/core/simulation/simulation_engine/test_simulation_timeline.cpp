#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/simulation/simulation_engine/simulation_engine.h"
#include "tests/test_support/test_assertions.h"

void test_simulation_timeline() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SimulationTimeline timeline =
        build_simulation_timeline_from_solution(instance, solution);

    FIELDOPS_EXPECT_EQ(timeline.start_time, 0);
    FIELDOPS_EXPECT_EQ(timeline.end_time, 270);
    FIELDOPS_EXPECT_EQ(timeline.events.size(), 20);

    FIELDOPS_EXPECT_TRUE(
        timeline.events.front().type == SimulationEventType::ROUTE_STARTED
    );

    FIELDOPS_EXPECT_TRUE(
        timeline.events.back().type == SimulationEventType::ROUTE_COMPLETED
    );

    FIELDOPS_EXPECT_EQ(timeline.events.back().time, 270);
}