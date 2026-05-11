#pragma once

#include <string>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

NoReplanningBatchExperimentConfig load_no_replanning_batch_config_from_json(
    const std::string& file_path
);