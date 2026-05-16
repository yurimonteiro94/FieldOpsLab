#pragma once

#include <string>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

void write_no_replanning_batch_recommendation_csv(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path
);