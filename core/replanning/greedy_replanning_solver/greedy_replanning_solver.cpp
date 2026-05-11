#include "core/replanning/greedy_replanning_solver/greedy_replanning_solver.h"

static void copy_request_counts_to_result(
    ReplanningResult& result,
    const ReplanningRequest& request
) {
    result.completed_task_count = request.completed_task_count();
    result.locked_task_count = request.locked_task_count();
    result.candidate_task_count = request.candidate_task_count();

    result.available_technician_count =
        request.available_technician_count();

    result.busy_technician_count =
        request.busy_technician_count();

    result.finished_technician_count =
        request.finished_technician_count();
}

ReplanningResult run_greedy_replanning_solver(
    const ReplanningRequest& request,
    const GreedyReplanningSolverConfig& config
) {
    ReplanningResult result;

    result.result_id = config.result_id;
    result.request_id = request.request_id;
    result.method_id = config.method_id;
    result.decision_time = request.decision_time;

    copy_request_counts_to_result(result, request);

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

    result.status = ReplanningResultStatus::SUCCESS;
    result.generated_solution_id = config.generated_solution_id;
    result.message =
        "Greedy replanning solver produced a candidate replanned solution identifier.";

    return result;
}