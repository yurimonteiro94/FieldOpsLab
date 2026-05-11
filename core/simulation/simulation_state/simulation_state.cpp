#include "core/simulation/simulation_state/simulation_state.h"

#include <iostream>
#include <stdexcept>

std::string simulation_task_execution_status_to_string(
    SimulationTaskExecutionStatus status
) {
    switch (status) {
        case SimulationTaskExecutionStatus::NOT_STARTED:
            return "NOT_STARTED";

        case SimulationTaskExecutionStatus::IN_PROGRESS:
            return "IN_PROGRESS";

        case SimulationTaskExecutionStatus::COMPLETED:
            return "COMPLETED";

        case SimulationTaskExecutionStatus::UNASSIGNED:
            return "UNASSIGNED";
    }

    return "UNKNOWN";
}

std::string simulation_technician_execution_status_to_string(
    SimulationTechnicianExecutionStatus status
) {
    switch (status) {
        case SimulationTechnicianExecutionStatus::IDLE:
            return "IDLE";

        case SimulationTechnicianExecutionStatus::TRAVELING:
            return "TRAVELING";

        case SimulationTechnicianExecutionStatus::WAITING:
            return "WAITING";

        case SimulationTechnicianExecutionStatus::SERVICING:
            return "SERVICING";

        case SimulationTechnicianExecutionStatus::FINISHED:
            return "FINISHED";
    }

    return "UNKNOWN";
}

static SimulationTaskState build_simulation_task_state_from_stop(
    const Route& route,
    const RouteStop& stop,
    int current_time
) {
    SimulationTaskState task_state;

    task_state.task_id = stop.task_id;
    task_state.technician_id = route.technician_id;
    task_state.location_id = stop.location_id;
    task_state.planned_start_time = stop.start_service_time;
    task_state.planned_end_time = stop.end_service_time;

    if (current_time < stop.start_service_time) {
        task_state.status = SimulationTaskExecutionStatus::NOT_STARTED;
    } else if (current_time < stop.end_service_time) {
        task_state.status = SimulationTaskExecutionStatus::IN_PROGRESS;
    } else {
        task_state.status = SimulationTaskExecutionStatus::COMPLETED;
    }

    return task_state;
}

static SimulationTechnicianState build_simulation_technician_state_from_route(
    const Route& route,
    int current_time
) {
    SimulationTechnicianState technician_state;

    technician_state.technician_id = route.technician_id;
    technician_state.current_location_id = route.start_location_id;

    if (route.stops.empty()) {
        if (current_time >= route.end_time) {
            technician_state.status =
                SimulationTechnicianExecutionStatus::FINISHED;
            technician_state.current_location_id = route.end_location_id;
        } else {
            technician_state.status =
                SimulationTechnicianExecutionStatus::IDLE;
        }

        return technician_state;
    }

    const RouteStop& first_stop = route.stops.front();

    if (current_time < first_stop.arrival_time) {
        technician_state.status =
            SimulationTechnicianExecutionStatus::TRAVELING;
        technician_state.next_task_id = first_stop.task_id;
        technician_state.current_location_id = route.start_location_id;
        return technician_state;
    }

    for (int i = 0; i < static_cast<int>(route.stops.size()); ++i) {
        const RouteStop& stop = route.stops[i];

        if (current_time >= stop.arrival_time &&
            current_time < stop.start_service_time) {
            technician_state.status =
                SimulationTechnicianExecutionStatus::WAITING;
            technician_state.current_location_id = stop.location_id;
            technician_state.current_task_id = stop.task_id;
            return technician_state;
        }

        if (current_time >= stop.start_service_time &&
            current_time < stop.end_service_time) {
            technician_state.status =
                SimulationTechnicianExecutionStatus::SERVICING;
            technician_state.current_location_id = stop.location_id;
            technician_state.current_task_id = stop.task_id;
            return technician_state;
        }

        if (i + 1 < static_cast<int>(route.stops.size())) {
            const RouteStop& next_stop = route.stops[i + 1];

            if (current_time >= stop.end_service_time &&
                current_time < next_stop.arrival_time) {
                technician_state.status =
                    SimulationTechnicianExecutionStatus::TRAVELING;
                technician_state.current_location_id = stop.location_id;
                technician_state.next_task_id = next_stop.task_id;
                return technician_state;
            }
        }
    }

    const RouteStop& last_stop = route.stops.back();

    if (current_time >= last_stop.end_service_time &&
        current_time < route.end_time) {
        technician_state.status =
            SimulationTechnicianExecutionStatus::TRAVELING;
        technician_state.current_location_id = last_stop.location_id;
        technician_state.next_task_id = "";
        return technician_state;
    }

    technician_state.status =
        SimulationTechnicianExecutionStatus::FINISHED;
    technician_state.current_location_id = route.end_location_id;

    return technician_state;
}

SimulationSnapshot build_simulation_snapshot_from_solution(
    const Instance& instance,
    const Solution& solution,
    int current_time
) {
    (void)instance;

    if (current_time < 0) {
        throw std::runtime_error(
            "Simulation snapshot current_time cannot be negative."
        );
    }

    SimulationSnapshot snapshot;

    snapshot.current_time = current_time;

    for (const auto& route : solution.routes) {
        snapshot.technician_states.push_back(
            build_simulation_technician_state_from_route(
                route,
                current_time
            )
        );

        for (const auto& stop : route.stops) {
            snapshot.task_states.push_back(
                build_simulation_task_state_from_stop(
                    route,
                    stop,
                    current_time
                )
            );
        }
    }

    for (const auto& task_id : solution.unassigned_task_ids) {
        SimulationTaskState task_state;

        task_state.task_id = task_id;
        task_state.status = SimulationTaskExecutionStatus::UNASSIGNED;

        snapshot.task_states.push_back(task_state);
    }

    return snapshot;
}

const SimulationTechnicianState* find_simulation_technician_state_by_id(
    const SimulationSnapshot& snapshot,
    const std::string& technician_id
) {
    for (const auto& technician_state : snapshot.technician_states) {
        if (technician_state.technician_id == technician_id) {
            return &technician_state;
        }
    }

    return nullptr;
}

const SimulationTaskState* find_simulation_task_state_by_id(
    const SimulationSnapshot& snapshot,
    const std::string& task_id
) {
    for (const auto& task_state : snapshot.task_states) {
        if (task_state.task_id == task_id) {
            return &task_state;
        }
    }

    return nullptr;
}

void print_simulation_snapshot_summary(
    const SimulationSnapshot& snapshot
) {
    std::cout << "Simulation snapshot summary:\n";
    std::cout << "  Current time: " << snapshot.current_time << "\n";
    std::cout << "  Technicians: "
              << snapshot.technician_states.size()
              << "\n";
    std::cout << "  Tasks: " << snapshot.task_states.size() << "\n";

    std::cout << "\nTechnician states:\n";

    for (const auto& technician_state : snapshot.technician_states) {
        std::cout << "  Technician: "
                  << technician_state.technician_id
                  << " | status="
                  << simulation_technician_execution_status_to_string(
                      technician_state.status
                  )
                  << " | current_location="
                  << technician_state.current_location_id
                  << " | current_task="
                  << technician_state.current_task_id
                  << " | next_task="
                  << technician_state.next_task_id
                  << "\n";
    }

    std::cout << "\nTask states:\n";

    for (const auto& task_state : snapshot.task_states) {
        std::cout << "  Task: "
                  << task_state.task_id
                  << " | status="
                  << simulation_task_execution_status_to_string(
                      task_state.status
                  )
                  << " | technician="
                  << task_state.technician_id
                  << " | location="
                  << task_state.location_id
                  << "\n";
    }
}