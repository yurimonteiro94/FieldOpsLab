#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/simulation/simulation_engine/simulation_engine.h"
#include "tests/test_support/test_assertions.h"

static int find_event_index(
    const SimulationTimeline& timeline,
    int time,
    SimulationEventType type,
    const std::string& technician_id,
    const std::string& task_id
) {
    for (int i = 0; i < static_cast<int>(timeline.events.size()); ++i) {
        const auto& event = timeline.events[i];

        if (event.time == time &&
            event.type == type &&
            event.technician_id == technician_id &&
            event.task_id == task_id) {
            return i;
        }
    }

    return -1;
}

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

    int task_a_completed_index = find_event_index(
        timeline,
        120,
        SimulationEventType::TASK_COMPLETED,
        "tech_1",
        "task_A"
    );

    int tech_1_departed_to_task_c_index = find_event_index(
        timeline,
        120,
        SimulationEventType::TECHNICIAN_DEPARTED,
        "tech_1",
        "task_C"
    );

    FIELDOPS_EXPECT_TRUE(task_a_completed_index >= 0);
    FIELDOPS_EXPECT_TRUE(tech_1_departed_to_task_c_index >= 0);
    FIELDOPS_EXPECT_TRUE(task_a_completed_index < tech_1_departed_to_task_c_index);

    int tech_2_arrived_depot_index = find_event_index(
        timeline,
        195,
        SimulationEventType::TECHNICIAN_ARRIVED,
        "tech_2",
        ""
    );

    int tech_2_route_completed_index = find_event_index(
        timeline,
        195,
        SimulationEventType::ROUTE_COMPLETED,
        "tech_2",
        ""
    );

    FIELDOPS_EXPECT_TRUE(tech_2_arrived_depot_index >= 0);
    FIELDOPS_EXPECT_TRUE(tech_2_route_completed_index >= 0);
    FIELDOPS_EXPECT_TRUE(tech_2_arrived_depot_index < tech_2_route_completed_index);
}