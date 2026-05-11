#pragma once

#include <string>

#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

void write_no_replanning_experiment_result_to_json(
    const NoReplanningExperimentResult& result,
    const std::string& output_path,
    const std::string& result_type = "no_replanning_experiment_result"
);