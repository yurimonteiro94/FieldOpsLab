#pragma once

#include <string>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

void write_no_replanning_batch_result_to_json(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path,
    const std::string& result_type
);