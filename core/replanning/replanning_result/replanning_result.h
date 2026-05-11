#pragma once

#include <string>

#include "core/replanning/replanning_request/replanning_request.h"

enum class ReplanningResultStatus {
    NOT_REQUESTED,
    NO_WORK,
    NOT_IMPLEMENTED,
    SUCCESS,
    FAILED
};

struct ReplanningResult {
    std::string result_id = "replanning_result";
    std::string request_id = "replanning_request";

    std::string method_id = "replanning_not_implemented_v1";

    ReplanningResultStatus status =
        ReplanningResultStatus::NOT_IMPLEMENTED;

    std::string message;

    int decision_time = 0;

    int completed_task_count = 0;
    int locked_task_count = 0;
    int candidate_task_count = 0;

    int available_technician_count = 0;
    int busy_technician_count = 0;
    int finished_technician_count = 0;

    std::string generated_solution_id;

    bool has_new_solution() const;
    bool is_successful() const;
};

std::string replanning_result_status_to_string(
    ReplanningResultStatus status
);

ReplanningResult build_not_implemented_replanning_result(
    const ReplanningRequest& request,
    const std::string& result_id = "replanning_result",
    const std::string& method_id = "replanning_not_implemented_v1"
);

void print_replanning_result_summary(
    const ReplanningResult& result
);