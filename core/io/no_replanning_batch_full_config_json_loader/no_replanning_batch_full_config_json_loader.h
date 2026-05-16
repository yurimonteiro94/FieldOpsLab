#pragma once

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

#include <string>

struct NoReplanningBatchFullConfigLoadResult {
    NoReplanningBatchExperimentConfig config;
    bool custom_ranking_config_was_loaded = false;
};

NoReplanningBatchFullConfigLoadResult
load_no_replanning_batch_full_config_from_json(
    const std::string& file_path
);

NoReplanningBatchExperimentConfig
load_no_replanning_batch_config_from_json_with_optional_ranking_config(
    const std::string& file_path
);