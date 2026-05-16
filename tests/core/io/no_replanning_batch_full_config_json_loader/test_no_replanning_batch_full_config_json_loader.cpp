#include "core/io/no_replanning_batch_full_config_json_loader/no_replanning_batch_full_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

static std::string read_text_file_for_full_config_test(
    const std::string& file_path
) {
    std::ifstream input(file_path);

    if (!input.is_open()) {
        throw std::runtime_error(
            "Could not open test JSON file: " + file_path
        );
    }

    std::ostringstream buffer;
    buffer << input.rdbuf();

    return buffer.str();
}

static std::string write_text_file_for_full_config_test(
    const std::string& file_name,
    const std::string& content
) {
    const std::string directory =
        "data/results/test_no_replanning_batch_full_config_json_loader";

    std::filesystem::create_directories(directory);

    const std::string file_path = directory + "/" + file_name;

    std::ofstream output(file_path);
    output << content;

    return file_path;
}

static std::string add_ranking_config_to_root_json_object(
    const std::string& json_text
) {
    const std::size_t final_brace_position =
        json_text.find_last_of('}');

    if (final_brace_position == std::string::npos) {
        throw std::runtime_error(
            "Invalid test JSON. Missing final root object brace."
        );
    }

    const std::string ranking_config_text =
        ",\n"
        "  \"ranking_config\": {\n"
        "    \"ranking_config_id\": \"custom_full_loader_makespan_v1\",\n"
        "    \"objective_value_weight\": 0.0,\n"
        "    \"makespan_weight\": 1.0,\n"
        "    \"total_travel_time_weight\": 0.5,\n"
        "    \"replanning_request_count_weight\": 2.0\n"
        "  }\n";

    std::string result = json_text;
    result.insert(final_brace_position, ranking_config_text);

    return result;
}

void test_no_replanning_batch_full_config_json_loader() {
    const std::string sample_path =
        "data/experiments/sample_no_replanning_batch_001.json";

    NoReplanningBatchFullConfigLoadResult default_result =
        load_no_replanning_batch_full_config_from_json(sample_path);

    FIELDOPS_EXPECT_TRUE(
        !default_result.custom_ranking_config_was_loaded
    );

    FIELDOPS_EXPECT_TRUE(
        default_result.config.ranking_config.ranking_config_id ==
        "default_objective_delta_ranking_v1"
    );

    FIELDOPS_EXPECT_TRUE(
        default_result.config.ranking_config.objective_value_weight == 1.0
    );

    FIELDOPS_EXPECT_TRUE(
        default_result.config.ranking_config.makespan_weight == 0.0
    );

    const std::string sample_json =
        read_text_file_for_full_config_test(sample_path);

    const std::string custom_json =
        add_ranking_config_to_root_json_object(sample_json);

    const std::string custom_path =
        write_text_file_for_full_config_test(
            "sample_batch_with_custom_ranking_config.json",
            custom_json
        );

    NoReplanningBatchFullConfigLoadResult custom_result =
        load_no_replanning_batch_full_config_from_json(custom_path);

    FIELDOPS_EXPECT_TRUE(
        custom_result.custom_ranking_config_was_loaded
    );

    FIELDOPS_EXPECT_TRUE(
        custom_result.config.ranking_config.ranking_config_id ==
        "custom_full_loader_makespan_v1"
    );

    FIELDOPS_EXPECT_TRUE(
        custom_result.config.ranking_config.objective_value_weight == 0.0
    );

    FIELDOPS_EXPECT_TRUE(
        custom_result.config.ranking_config.makespan_weight == 1.0
    );

    FIELDOPS_EXPECT_TRUE(
        custom_result.config.ranking_config.total_travel_time_weight == 0.5
    );

    FIELDOPS_EXPECT_TRUE(
        custom_result.config.ranking_config.replanning_request_count_weight
        == 2.0
    );

    NoReplanningBatchExperimentConfig config_only =
        load_no_replanning_batch_config_from_json_with_optional_ranking_config(
            custom_path
        );

    FIELDOPS_EXPECT_TRUE(
        config_only.ranking_config.ranking_config_id ==
        "custom_full_loader_makespan_v1"
    );
}