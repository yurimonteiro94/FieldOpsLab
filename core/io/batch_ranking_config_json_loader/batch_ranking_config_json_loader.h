#pragma once

#include "core/analysis/batch_ranking/batch_ranking_config.h"

#include <string>

bool try_load_batch_ranking_config_from_json_file(
    const std::string& file_path,
    BatchRankingConfig& ranking_config
);

BatchRankingConfig load_batch_ranking_config_from_json_file_or_default(
    const std::string& file_path,
    const BatchRankingConfig& default_ranking_config
);