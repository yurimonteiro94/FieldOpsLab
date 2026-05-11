#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
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
    const std::string summary_csv_path =
        "data/results/test_no_replanning_batch_summary.csv";

    std::filesystem::remove(summary_csv_path);

    NoReplanningExperimentConfig experiment_1;

    experiment_1.verbose = false;
    experiment_1.export_results = false;

    NoReplanningExperimentConfig experiment_2;

    experiment_2.verbose = false;
    experiment_2.export_results = false;

    NoReplanningBatchExperimentConfig batch_config;

    batch_config.experiments.push_back(experiment_1);
    batch_config.experiments.push_back(experiment_2);
    batch_config.summary_csv_output_path = summary_csv_path;
    batch_config.verbose = false;
    batch_config.export_individual_results = false;
    batch_config.export_summary_csv = true;

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(batch_config);

    FIELDOPS_EXPECT_EQ(batch_result.experiment_count(), 2);
    FIELDOPS_EXPECT_EQ(batch_result.results.size(), 2);

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[0].validation_result.is_valid()
    );

    FIELDOPS_EXPECT_TRUE(
        batch_result.results[1].validation_result.is_valid()
    );

    FIELDOPS_EXPECT_EQ(
        batch_result.results[0].comparison.delta_total_travel_time,
        50
    );

    FIELDOPS_EXPECT_EQ(
        batch_result.results[1].comparison.delta_total_travel_time,
        50
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(summary_csv_path));

    std::vector<std::string> lines =
        read_batch_csv_lines(summary_csv_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("instance_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("sample_instance_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("sample_instance_001") != std::string::npos
    );
}