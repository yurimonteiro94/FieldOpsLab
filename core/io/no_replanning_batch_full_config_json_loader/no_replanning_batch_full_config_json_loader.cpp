#include "core/io/no_replanning_batch_full_config_json_loader/no_replanning_batch_full_config_json_loader.h"

#include "core/io/batch_ranking_config_json_loader/batch_ranking_config_json_loader.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"

NoReplanningBatchFullConfigLoadResult
load_no_replanning_batch_full_config_from_json(
    const std::string& file_path
) {
    NoReplanningBatchFullConfigLoadResult result;

    result.config =
        load_no_replanning_batch_config_from_json(file_path);

    result.custom_ranking_config_was_loaded =
        try_load_batch_ranking_config_from_json_file(
            file_path,
            result.config.ranking_config
        );

    return result;
}

NoReplanningBatchExperimentConfig
load_no_replanning_batch_config_from_json_with_optional_ranking_config(
    const std::string& file_path
) {
    return load_no_replanning_batch_full_config_from_json(file_path).config;
}