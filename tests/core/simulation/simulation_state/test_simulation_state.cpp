#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/simulation/simulation_state/simulation_state.h"
#include "tests/test_support/test_assertions.h"

void test_simulation_state() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SimulationSnapshot snapshot_at_zero =
        build_simulation_snapshot_from_solution(instance, solution, 0);

    FIELDOPS_EXPECT_EQ(snapshot_at_zero.current_time, 0);
    FIELDOPS_EXPECT_EQ(snapshot_at_zero.technician_states.size(), 2);
    FIELDOPS_EXPECT_EQ(snapshot_at_zero.task_states.size(), 3);

    const SimulationTechnicianState* tech_1_at_zero =
        find_simulation_technician_state_by_id(
            snapshot_at_zero,
            "tech_1"
        );

    FIELDOPS_EXPECT_TRUE(tech_1_at_zero != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_technician_execution_status_to_string(
            tech_1_at_zero->status
        ),
        "TRAVELING"
    );

    FIELDOPS_EXPECT_EQ(tech_1_at_zero->next_task_id, "task_A");

    const SimulationTaskState* task_a_at_zero =
        find_simulation_task_state_by_id(snapshot_at_zero, "task_A");

    FIELDOPS_EXPECT_TRUE(task_a_at_zero != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_task_execution_status_to_string(task_a_at_zero->status),
        "NOT_STARTED"
    );

    SimulationSnapshot snapshot_at_100 =
        build_simulation_snapshot_from_solution(instance, solution, 100);

    const SimulationTechnicianState* tech_1_at_100 =
        find_simulation_technician_state_by_id(
            snapshot_at_100,
            "tech_1"
        );

    FIELDOPS_EXPECT_TRUE(tech_1_at_100 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_technician_execution_status_to_string(
            tech_1_at_100->status
        ),
        "SERVICING"
    );

    FIELDOPS_EXPECT_EQ(tech_1_at_100->current_task_id, "task_A");

    const SimulationTaskState* task_a_at_100 =
        find_simulation_task_state_by_id(snapshot_at_100, "task_A");

    FIELDOPS_EXPECT_TRUE(task_a_at_100 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_task_execution_status_to_string(task_a_at_100->status),
        "IN_PROGRESS"
    );

    SimulationSnapshot snapshot_at_125 =
        build_simulation_snapshot_from_solution(instance, solution, 125);

    const SimulationTechnicianState* tech_1_at_125 =
        find_simulation_technician_state_by_id(
            snapshot_at_125,
            "tech_1"
        );

    FIELDOPS_EXPECT_TRUE(tech_1_at_125 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_technician_execution_status_to_string(
            tech_1_at_125->status
        ),
        "TRAVELING"
    );

    FIELDOPS_EXPECT_EQ(tech_1_at_125->next_task_id, "task_C");

    const SimulationTaskState* task_a_at_125 =
        find_simulation_task_state_by_id(snapshot_at_125, "task_A");

    FIELDOPS_EXPECT_TRUE(task_a_at_125 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_task_execution_status_to_string(task_a_at_125->status),
        "COMPLETED"
    );

    const SimulationTaskState* task_c_at_125 =
        find_simulation_task_state_by_id(snapshot_at_125, "task_C");

    FIELDOPS_EXPECT_TRUE(task_c_at_125 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_task_execution_status_to_string(task_c_at_125->status),
        "NOT_STARTED"
    );

    SimulationSnapshot snapshot_at_200 =
        build_simulation_snapshot_from_solution(instance, solution, 200);

    const SimulationTechnicianState* tech_1_at_200 =
        find_simulation_technician_state_by_id(
            snapshot_at_200,
            "tech_1"
        );

    FIELDOPS_EXPECT_TRUE(tech_1_at_200 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_technician_execution_status_to_string(
            tech_1_at_200->status
        ),
        "SERVICING"
    );

    FIELDOPS_EXPECT_EQ(tech_1_at_200->current_task_id, "task_C");

    const SimulationTechnicianState* tech_2_at_200 =
        find_simulation_technician_state_by_id(
            snapshot_at_200,
            "tech_2"
        );

    FIELDOPS_EXPECT_TRUE(tech_2_at_200 != nullptr);

    FIELDOPS_EXPECT_EQ(
        simulation_technician_execution_status_to_string(
            tech_2_at_200->status
        ),
        "FINISHED"
    );
}