#pragma once

#include <string>

#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

void write_no_replanning_experiment_summary_to_csv(
    const NoReplanningExperimentResult& result,
    const std::string& output_path,
    bool append = false
);