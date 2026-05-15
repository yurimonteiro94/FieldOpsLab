#include "core/replanning/replanning_result/replanning_result.h"

#include <iostream>

bool ReplanningResult::has_new_solution() const {
    return generated_solution_was_built &&
           !generated_solution_id.empty() &&
           !generated_solution.solution_id.empty();
}

bool ReplanningResult::is_successful() const {
    return status == ReplanningResultStatus::SUCCESS;
}

std::string replanning_result_status_to_string(
    ReplanningResultStatus status
) {
    switch (status) {
        case ReplanningResultStatus::NOT_REQUESTED:
            return "NOT_REQUESTED";

        case ReplanningResultStatus::NO_WORK:
            return "NO_WORK";

        case ReplanningResultStatus::NOT_IMPLEMENTED:
            return "NOT_IMPLEMENTED";

        case ReplanningResultStatus::SUCCESS:
            return "SUCCESS";

        case ReplanningResultStatus::FAILED:
            return "FAILED";
    }

    return "UNKNOWN";
}

ReplanningResult build_not_implemented_replanning_result(
    const ReplanningRequest& request,
    const std::string& result_id,
    const std::string& method_id
) {
    ReplanningResult result;

    result.result_id = result_id;
    result.request_id = request.request_id;
    result.method_id = method_id;
    result.decision_time = request.decision_time;

    result.completed_task_count = request.completed_task_count();
    result.locked_task_count = request.locked_task_count();
    result.candidate_task_count = request.candidate_task_count();

    result.available_technician_count =
        request.available_technician_count();

    result.busy_technician_count =
        request.busy_technician_count();

    result.finished_technician_count =
        request.finished_technician_count();

    if (!request.should_replan) {
        result.status = ReplanningResultStatus::NOT_REQUESTED;
        result.message =
            "No replanning was requested by the policy decision.";
        return result;
    }

    if (!replanning_request_has_work(request)) {
        result.status = ReplanningResultStatus::NO_WORK;
        result.message =
            "Replanning was requested, but there are no candidate tasks to replan.";
        return result;
    }

    result.status = ReplanningResultStatus::NOT_IMPLEMENTED;
    result.message =
        "Replanning was requested and work exists, but the replanning engine is not implemented yet.";

    return result;
}

void print_replanning_result_summary(
    const ReplanningResult& result
) {
    std::cout << "Replanning result summary:\n";
    std::cout << "  Result ID: " << result.result_id << "\n";
    std::cout << "  Request ID: " << result.request_id << "\n";
    std::cout << "  Method ID: " << result.method_id << "\n";
    std::cout << "  Status: "
              << replanning_result_status_to_string(result.status)
              << "\n";
    std::cout << "  Decision time: " << result.decision_time << "\n";
    std::cout << "  Completed tasks: "
              << result.completed_task_count
              << "\n";
    std::cout << "  Locked tasks: "
              << result.locked_task_count
              << "\n";
    std::cout << "  Candidate tasks: "
              << result.candidate_task_count
              << "\n";
    std::cout << "  Available technicians: "
              << result.available_technician_count
              << "\n";
    std::cout << "  Busy technicians: "
              << result.busy_technician_count
              << "\n";
    std::cout << "  Finished technicians: "
              << result.finished_technician_count
              << "\n";
    std::cout << "  Generated solution ID: "
              << result.generated_solution_id
              << "\n";
    std::cout << "  Generated solution was built: "
              << (result.generated_solution_was_built ? "true" : "false")
              << "\n";

    if (result.generated_solution_was_built) {
        std::cout << "  Generated solution status: "
                  << solution_status_to_string(result.generated_solution.status)
                  << "\n";
        std::cout << "  Generated solution routes: "
                  << result.generated_solution.routes.size()
                  << "\n";
        std::cout << "  Generated solution unassigned tasks: "
                  << result.generated_solution.unassigned_task_ids.size()
                  << "\n";
    }

    std::cout << "  Message: " << result.message << "\n";
}