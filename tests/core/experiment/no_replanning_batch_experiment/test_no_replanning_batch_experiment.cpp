#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

static std::vector<std::string> read_batch_csv_lines(
    const std::string& file_path
) {
    std::ifstream file(file_path);

    std::vector<std::string> lines;
    std::string line;

    while (std::getline(file, line)) {
        lines.push_back(line);
    }

    return lines;
}

void test_no_replanning_batch_experiment() {
    NoReplanningBatchExperimentConfig batch_config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    const std::string summary_csv_path =
        "data/results/test_no_replanning_batch_summary.csv";

    batch_config.summary_csv_output_path = summary_csv_path;
    batch_config.verbose = false;
    batch_config.export_individual_results = false;
    batch_config.export_summary_csv = true;

    std::filesystem::remove(summary_csv_path);

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(batch_config);

    FIELDOPS_EXPECT_EQ(
        batch_result.batch_id,
        "sample_no_replanning_batch_001"
    );

    FIELDOPS_EXPECT_EQ(batch_result.experiment_count(), 3);
    FIELDOPS_EXPECT_EQ(batch_result.results.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[0].validation_result.is_valid()
    );

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[1].validation_result.is_valid()
    );

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[2].validation_result.is_valid()
    );

    FIELDOPS_EXPECT_EQ(
        batch_result.results[0].metadata.experiment_id,
        "batch_001_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        batch_result.results[1].metadata.experiment_id,
        "batch_001_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        batch_result.results[2].metadata.experiment_id,
        "batch_001_severe_001"
    );

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[0].comparison.delta_total_travel_time <
        batch_result.results[1].comparison.delta_total_travel_time
    );

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[1].comparison.delta_total_travel_time <
        batch_result.results[2].comparison.delta_total_travel_time
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(summary_csv_path));

    std::vector<std::string> lines =
        read_batch_csv_lines(summary_csv_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 4);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("experiment_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("batch_001_light_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("batch_001_moderate_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[3].find("batch_001_severe_001") != std::string::npos
    );
}