#pragma once

#include <string>

#include "core/replanning/replanning_request/replanning_request.h"
#include "core/replanning/replanning_result/replanning_result.h"

struct GreedyReplanningSolverConfig {
    std::string method_id = "greedy_replanning_solver_v1";
    std::string result_id = "greedy_replanning_result";
    std::string generated_solution_id = "greedy_replanned_solution";
};

ReplanningResult run_greedy_replanning_solver(
    const ReplanningRequest& request,
    const GreedyReplanningSolverConfig& config = GreedyReplanningSolverConfig()
);