#pragma once

#include <string>

#include "core/simulation/simulation_engine/simulation_engine.h"

void write_simulation_timeline_to_json(
    const SimulationTimeline& timeline,
    const std::string& output_path
);