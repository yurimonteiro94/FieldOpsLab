#pragma once

#include <string>
#include <vector>

#include "core/instance/instance/instance.h"
#include "core/solution/solution/solution.h"

enum class SimulationTaskExecutionStatus {
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED,
    UNASSIGNED
};

enum class SimulationTechnicianExecutionStatus {
    IDLE,
    TRAVELING,
    WAITING,
    SERVICING,
    FINISHED
};

struct SimulationTaskState {
    std::string task_id;
    std::string technician_id;
    std::string location_id;

    SimulationTaskExecutionStatus status =
        SimulationTaskExecutionStatus::NOT_STARTED;

    int planned_start_time = 0;
    int planned_end_time = 0;
};

struct SimulationTechnicianState {
    std::string technician_id;

    SimulationTechnicianExecutionStatus status =
        SimulationTechnicianExecutionStatus::IDLE;

    std::string current_location_id;
    std::string current_task_id;
    std::string next_task_id;
};

struct SimulationSnapshot {
    int current_time = 0;

    std::vector<SimulationTechnicianState> technician_states;
    std::vector<SimulationTaskState> task_states;
};

std::string simulation_task_execution_status_to_string(
    SimulationTaskExecutionStatus status
);

std::string simulation_technician_execution_status_to_string(
    SimulationTechnicianExecutionStatus status
);

SimulationSnapshot build_simulation_snapshot_from_solution(
    const Instance& instance,
    const Solution& solution,
    int current_time
);

const SimulationTechnicianState* find_simulation_technician_state_by_id(
    const SimulationSnapshot& snapshot,
    const std::string& technician_id
);

const SimulationTaskState* find_simulation_task_state_by_id(
    const SimulationSnapshot& snapshot,
    const std::string& task_id
);

void print_simulation_snapshot_summary(
    const SimulationSnapshot& snapshot
);