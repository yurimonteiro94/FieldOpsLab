#pragma once

#include <string>

#include "core/analysis/solution_comparison/solution_comparison.h"
#include "core/instance/instance/instance.h"
#include "core/solution/solution/solution.h"

void write_solution_comparison_to_json(
    const Instance& instance,
    const Solution& planned_solution,
    const Solution& executed_solution,
    const SolutionComparison& comparison,
    const std::string& output_path,
    const std::string& result_type = "solution_comparison"
);