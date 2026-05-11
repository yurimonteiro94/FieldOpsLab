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

    return request;
}

bool replanning_request_has_work(
    const ReplanningRequest& request
) {
    return request.should_replan &&
           request.candidate_task_count() > 0;
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
}