#pragma once

#include "core/instance/instance/instance.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/replanning/replanning_result/replanning_result.h"
#include "core/solution/solution/solution.h"

Solution build_solution_with_applied_replanning_result(
    const Instance& instance,
    const Solution& planned_solution,
    const ReplanningRequest& request,
    const ReplanningResult& replanning_result
);