#pragma once

#include <vector>

#include "core/instance/instance/instance.h"
#include "core/simulation/simulation_event/simulation_event.h"
#include "core/solution/solution/solution.h"

struct SimulationTimeline {
    std::vector<SimulationEvent> events;

    int start_time = 0;
    int end_time = 0;
};

SimulationTimeline build_simulation_timeline_from_solution(
    const Instance& instance,
    const Solution& solution
);

void print_simulation_timeline_summary(const SimulationTimeline& timeline);