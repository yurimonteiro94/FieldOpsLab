#pragma once

#include <vector>

#include "core/instance/instance/instance.h"
#include "core/perturbation/effect/effect.h"
#include "core/solution/solution/solution.h"

Solution execute_solution_without_replanning(
    const Instance& instance,
    const Solution& planned_solution,
    const std::vector<Effect>& effects
);