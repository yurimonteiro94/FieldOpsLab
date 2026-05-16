#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>

static std::string read_text_file(const std::string& path) {
    std::ifstream file(path);

    FIELDOPS_EXPECT_TRUE(file.is_open());

    std::ostringstream content;
    content << file.rdbuf();

    return content.str();
}

void test_no_replanning_batch_overview_csv_writer() {
    const std::string output_path =
        "data/results/test_no_replanning_batch_overview.csv";

    std::filesystem::remove(output_path);

    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;

    config.export_overview_csv = true;
    config.overview_csv_output_path = output_path;

    config.export_summary_csv = false;
    config.export_aggregate_csv = false;
    config.export_ranking_csv = false;
    config.export_recommendation_csv = false;
    config.export_result_json = false;

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    FIELDOPS_EXPECT_TRUE(result.overview_csv_was_written);
    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::string content = read_text_file(output_path);

    FIELDOPS_EXPECT_TRUE(
        content.find(
            "batch_id,name,description,configured_experiment_count"
        ) != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        content.find("sample_no_replanning_batch_001") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        content.find(",12,12,100,true,12,") !=
        std::string::npos
    );

    std::filesystem::remove(output_path);
}