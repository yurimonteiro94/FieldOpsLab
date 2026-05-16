#include "core/analysis/batch_ranking/batch_ranking_config.h"
#include "core/io/batch_ranking_config_json_loader/batch_ranking_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>

static std::string write_test_json_file(
    const std::string& file_name,
    const std::string& content
) {
    const std::string directory =
        "data/results/test_batch_ranking_config_json_loader";

    std::filesystem::create_directories(directory);

    const std::string path = directory + "/" + file_name;

    std::ofstream output(path);
    output << content;

    return path;
}

static bool ranking_config_loader_throws(
    const std::string& file_path,
    BatchRankingConfig& config
) {
    try {
        try_load_batch_ranking_config_from_json_file(
            file_path,
            config
        );

        return false;
    } catch (const std::runtime_error&) {
        return true;
    }
}

void test_batch_ranking_config_json_loader() {
    BatchRankingConfig config;

    const std::string custom_config_path =
        write_test_json_file(
            "custom_ranking_config.json",
            "{\n"
            "  \"batch_id\": \"test_batch\",\n"
            "  \"ranking_config\": {\n"
            "    \"ranking_config_id\": \"custom_travel_priority_v1\",\n"
            "    \"objective_value_weight\": 0.0,\n"
            "    \"makespan_weight\": 0.25,\n"
            "    \"total_travel_time_weight\": 1.5,\n"
            "    \"replanning_applied_count_weight\": 10.0\n"
            "  }\n"
            "}\n"
        );

    const bool loaded =
        try_load_batch_ranking_config_from_json_file(
            custom_config_path,
            config
        );

    FIELDOPS_EXPECT_TRUE(loaded);
    FIELDOPS_EXPECT_TRUE(
        config.ranking_config_id == "custom_travel_priority_v1"
    );
    FIELDOPS_EXPECT_TRUE(config.objective_value_weight == 0.0);
    FIELDOPS_EXPECT_TRUE(config.makespan_weight == 0.25);
    FIELDOPS_EXPECT_TRUE(config.total_travel_time_weight == 1.5);
    FIELDOPS_EXPECT_TRUE(config.replanning_applied_count_weight == 10.0);

    BatchRankingConfig default_only_config;

    const std::string no_config_path =
        write_test_json_file(
            "no_ranking_config.json",
            "{\n"
            "  \"batch_id\": \"test_batch_without_ranking_config\"\n"
            "}\n"
        );

    const bool no_config_loaded =
        try_load_batch_ranking_config_from_json_file(
            no_config_path,
            default_only_config
        );

    FIELDOPS_EXPECT_TRUE(!no_config_loaded);
    FIELDOPS_EXPECT_TRUE(
        default_only_config.ranking_config_id ==
        "default_objective_delta_ranking_v1"
    );
    FIELDOPS_EXPECT_TRUE(default_only_config.objective_value_weight == 1.0);

    BatchRankingConfig invalid_zero_config;

    const std::string invalid_zero_path =
        write_test_json_file(
            "invalid_zero_ranking_config.json",
            "{\n"
            "  \"ranking_config\": {\n"
            "    \"ranking_config_id\": \"invalid_zero_weights\",\n"
            "    \"objective_value_weight\": 0.0,\n"
            "    \"makespan_weight\": 0.0,\n"
            "    \"total_travel_time_weight\": 0.0,\n"
            "    \"total_service_time_weight\": 0.0,\n"
            "    \"total_waiting_time_weight\": 0.0,\n"
            "    \"late_task_count_weight\": 0.0,\n"
            "    \"total_lateness_weight\": 0.0,\n"
            "    \"effect_count_weight\": 0.0,\n"
            "    \"policy_should_replan_count_weight\": 0.0,\n"
            "    \"replanning_request_count_weight\": 0.0,\n"
            "    \"replanning_success_count_weight\": 0.0,\n"
            "    \"replanning_applied_count_weight\": 0.0\n"
            "  }\n"
            "}\n"
        );

    FIELDOPS_EXPECT_TRUE(
        ranking_config_loader_throws(
            invalid_zero_path,
            invalid_zero_config
        )
    );
}