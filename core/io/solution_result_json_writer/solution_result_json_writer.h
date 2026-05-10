#pragma once

#include <string>

#include "core/instance/instance/instance.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/solution/solution/solution.h"

void write_solution_result_to_json(
    const Instance& instance,
    const Solution& solution,
    const SolutionMetrics& metrics,
    const std::string& output_path
);