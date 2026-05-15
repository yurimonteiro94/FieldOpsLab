#pragma once

#include <string>
#include <vector>

#include "core/policy/policy/policy.h"
#include "core/simulation/simulation_state/simulation_state.h"

struct ReplanningTechnicianRuntimeState {
    std::string technician_id;

    std::string execution_status;

    std::string current_location_id;
    std::string current_task_id;
    std::string next_task_id;

    int available_from_time = 0;

    bool can_receive_candidate_tasks = false;
};

struct ReplanningRequest {
    std::string request_id = "replanning_request";

    int decision_time = 0;

    std::string policy_id;
    std::string policy_decision;

    bool should_replan = false;

    std::vector<std::string> completed_task_ids;
    std::vector<std::string> locked_task_ids;
    std::vector<std::string> candidate_task_ids;

    std::vector<std::string> available_technician_ids;
    std::vector<std::string> busy_technician_ids;
    std::vector<std::string> finished_technician_ids;

    std::vector<ReplanningTechnicianRuntimeState>
        technician_runtime_states;

    int completed_task_count() const;
    int locked_task_count() const;
    int candidate_task_count() const;

    int available_technician_count() const;
    int busy_technician_count() const;
    int finished_technician_count() const;
};

ReplanningRequest build_replanning_request_from_snapshot(
    const SimulationSnapshot& snapshot,
    const PolicyDecision& policy_decision,
    const std::string& request_id = "replanning_request"
);

bool replanning_request_has_work(
    const ReplanningRequest& request
);

const ReplanningTechnicianRuntimeState*
find_replanning_technician_runtime_state_by_id(
    const ReplanningRequest& request,
    const std::string& technician_id
);

void print_replanning_request_summary(
    const ReplanningRequest& request
);