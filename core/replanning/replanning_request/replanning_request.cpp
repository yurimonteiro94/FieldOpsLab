#include "core/replanning/replanning_request/replanning_request.h"

#include <iostream>

int ReplanningRequest::completed_task_count() const {
    return static_cast<int>(completed_task_ids.size());
}

int ReplanningRequest::locked_task_count() const {
    return static_cast<int>(locked_task_ids.size());
}

int ReplanningRequest::candidate_task_count() const {
    return static_cast<int>(candidate_task_ids.size());
}

int ReplanningRequest::available_technician_count() const {
    return static_cast<int>(available_technician_ids.size());
}

int ReplanningRequest::busy_technician_count() const {
    return static_cast<int>(busy_technician_ids.size());
}

int ReplanningRequest::finished_technician_count() const {
    return static_cast<int>(finished_technician_ids.size());
}

static void add_task_to_replanning_request(
    ReplanningRequest& request,
    const SimulationTaskState& task_state
) {
    if (task_state.status == SimulationTaskExecutionStatus::COMPLETED) {
        request.completed_task_ids.push_back(task_state.task_id);
        return;
    }

    if (task_state.status == SimulationTaskExecutionStatus::IN_PROGRESS) {
        request.locked_task_ids.push_back(task_state.task_id);
        return;
    }

    if (task_state.status == SimulationTaskExecutionStatus::NOT_STARTED ||
        task_state.status == SimulationTaskExecutionStatus::UNASSIGNED) {
        request.candidate_task_ids.push_back(task_state.task_id);
        return;
    }
}

static void add_technician_to_replanning_request(
    ReplanningRequest& request,
    const SimulationTechnicianState& technician_state
) {
    if (technician_state.status ==
        SimulationTechnicianExecutionStatus::IDLE) {
        request.available_technician_ids.push_back(
            technician_state.technician_id
        );
        return;
    }

    if (technician_state.status ==
        SimulationTechnicianExecutionStatus::FINISHED) {
        request.finished_technician_ids.push_back(
            technician_state.technician_id
        );
        return;
    }

    request.busy_technician_ids.push_back(
        technician_state.technician_id
    );
}

static const SimulationTaskState* find_task_state_by_id(
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

static int estimate_technician_available_from_time(
    const SimulationSnapshot& snapshot,
    const SimulationTechnicianState& technician_state
) {
    if (technician_state.status ==
        SimulationTechnicianExecutionStatus::SERVICING) {
        const SimulationTaskState* task_state =
            find_task_state_by_id(
                snapshot,
                technician_state.current_task_id
            );

        if (task_state != nullptr) {
            return task_state->planned_end_time;
        }
    }

    return snapshot.current_time;
}

static bool technician_can_receive_candidate_tasks(
    const SimulationTechnicianState& technician_state
) {
    return technician_state.status !=
           SimulationTechnicianExecutionStatus::FINISHED;
}

static ReplanningTechnicianRuntimeState
build_technician_runtime_state(
    const SimulationSnapshot& snapshot,
    const SimulationTechnicianState& technician_state
) {
    ReplanningTechnicianRuntimeState runtime_state;

    runtime_state.technician_id = technician_state.technician_id;

    runtime_state.execution_status =
        simulation_technician_execution_status_to_string(
            technician_state.status
        );

    runtime_state.current_location_id =
        technician_state.current_location_id;

    runtime_state.current_task_id =
        technician_state.current_task_id;

    runtime_state.next_task_id =
        technician_state.next_task_id;

    runtime_state.available_from_time =
        estimate_technician_available_from_time(
            snapshot,
            technician_state
        );

    runtime_state.can_receive_candidate_tasks =
        technician_can_receive_candidate_tasks(technician_state);

    return runtime_state;
}

static void add_runtime_states_to_replanning_request(
    ReplanningRequest& request,
    const SimulationSnapshot& snapshot
) {
    for (const auto& technician_state : snapshot.technician_states) {
        request.technician_runtime_states.push_back(
            build_technician_runtime_state(
                snapshot,
                technician_state
            )
        );
    }
}

ReplanningRequest build_replanning_request_from_snapshot(
    const SimulationSnapshot& snapshot,
    const PolicyDecision& policy_decision,
    const std::string& request_id
) {
    ReplanningRequest request;

    request.request_id = request_id;
    request.decision_time = policy_decision.decision_time;
    request.policy_id = policy_decision.policy_id;
    request.policy_decision =
        policy_decision_type_to_string(policy_decision.type);
    request.should_replan = policy_decision.should_replan();

    for (const auto& task_state : snapshot.task_states) {
        add_task_to_replanning_request(request, task_state);
    }

    for (const auto& technician_state : snapshot.technician_states) {
        add_technician_to_replanning_request(
            request,
            technician_state
        );
    }

    add_runtime_states_to_replanning_request(request, snapshot);

    return request;
}

bool replanning_request_has_work(
    const ReplanningRequest& request
) {
    return request.should_replan &&
           request.candidate_task_count() > 0;
}

const ReplanningTechnicianRuntimeState*
find_replanning_technician_runtime_state_by_id(
    const ReplanningRequest& request,
    const std::string& technician_id
) {
    for (const auto& runtime_state :
         request.technician_runtime_states) {
        if (runtime_state.technician_id == technician_id) {
            return &runtime_state;
        }
    }

    return nullptr;
}

static void print_string_vector(
    const std::string& label,
    const std::vector<std::string>& values
) {
    std::cout << "  " << label << ": ";

    if (values.empty()) {
        std::cout << "(none)\n";
        return;
    }

    for (int i = 0; i < static_cast<int>(values.size()); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }

        std::cout << values[i];
    }

    std::cout << "\n";
}

static void print_runtime_states(
    const ReplanningRequest& request
) {
    std::cout << "  Technician runtime states:\n";

    if (request.technician_runtime_states.empty()) {
        std::cout << "    (none)\n";
        return;
    }

    for (const auto& runtime_state :
         request.technician_runtime_states) {
        std::cout << "    Technician: "
                  << runtime_state.technician_id
                  << " | status="
                  << runtime_state.execution_status
                  << " | current_location="
                  << runtime_state.current_location_id
                  << " | current_task="
                  << runtime_state.current_task_id
                  << " | next_task="
                  << runtime_state.next_task_id
                  << " | available_from="
                  << runtime_state.available_from_time
                  << " | can_receive_candidate_tasks="
                  << (
                      runtime_state.can_receive_candidate_tasks
                          ? "true"
                          : "false"
                  )
                  << "\n";
    }
}

void print_replanning_request_summary(
    const ReplanningRequest& request
) {
    std::cout << "Replanning request summary:\n";
    std::cout << "  Request ID: " << request.request_id << "\n";
    std::cout << "  Decision time: " << request.decision_time << "\n";
    std::cout << "  Policy ID: " << request.policy_id << "\n";
    std::cout << "  Policy decision: " << request.policy_decision << "\n";
    std::cout << "  Should replan: "
              << (request.should_replan ? "true" : "false")
              << "\n";

    print_string_vector("Completed tasks", request.completed_task_ids);
    print_string_vector("Locked tasks", request.locked_task_ids);
    print_string_vector("Candidate tasks", request.candidate_task_ids);

    print_string_vector(
        "Available technicians",
        request.available_technician_ids
    );

    print_string_vector(
        "Busy technicians",
        request.busy_technician_ids
    );

    print_string_vector(
        "Finished technicians",
        request.finished_technician_ids
    );

    print_runtime_states(request);
}