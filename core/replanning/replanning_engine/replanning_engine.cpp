#include "core/replanning/replanning_engine/replanning_engine.h"

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

static GreedyReplanningSolverConfig build_greedy_config(
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config
) {
    GreedyReplanningSolverConfig greedy_config;

    greedy_config.method_id = config.method_id;
    greedy_config.result_id = config.result_id;

    if (config.result_id == "replanning_result") {
        greedy_config.generated_solution_id =
            request.request_id + "_greedy_replanned_solution";
    } else {
        greedy_config.generated_solution_id =
            config.result_id + "_solution";
    }

    return greedy_config;
}

static ReplanningResult build_unknown_method_result(
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config
) {
    ReplanningResult result;

    result.result_id = config.result_id;
    result.request_id = request.request_id;
    result.method_id = config.method_id;
    result.status = ReplanningResultStatus::FAILED;
    result.decision_time = request.decision_time;
    result.message =
        "Unknown replanning engine method: " + config.method_id;

    copy_request_counts_to_result(result, request);

    return result;
}

ReplanningResult run_replanning_engine(
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config
) {
    if (config.method_id == "replanning_not_implemented_v1") {
        return build_not_implemented_replanning_result(
            request,
            config.result_id,
            config.method_id
        );
    }

    if (config.method_id == "greedy_replanning_solver_v1") {
        return run_greedy_replanning_solver(
            request,
            build_greedy_config(request, config)
        );
    }

    return build_unknown_method_result(request, config);
}

ReplanningResult run_replanning_engine(
    const Instance& instance,
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config
) {
    if (config.method_id == "replanning_not_implemented_v1") {
        return build_not_implemented_replanning_result(
            request,
            config.result_id,
            config.method_id
        );
    }

    if (config.method_id == "greedy_replanning_solver_v1") {
        return run_greedy_replanning_solver(
            instance,
            request,
            build_greedy_config(request, config)
        );
    }

    return build_unknown_method_result(request, config);
}