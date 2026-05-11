#pragma once

#include <string>
#include <vector>

#include "core/policy/policy/policy.h"
#include "core/simulation/simulation_state/simulation_state.h"

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

void print_replanning_request_summary(
    const ReplanningRequest& request
);