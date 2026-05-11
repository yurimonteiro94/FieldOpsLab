#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

static std::vector<std::string> read_lines(const std::string& file_path) {
    std::ifstream file(file_path);

    std::vector<std::string> lines;
    std::string line;

    while (std::getline(file, line)) {
        lines.push_back(line);
    }

    return lines;
}

void test_no_replanning_experiment_summary_csv_writer() {
    NoReplanningExperimentConfig config;

    config.metadata.experiment_id = "csv_writer_experiment_001";
    config.metadata.scenario_id = "csv_writer_scenario_001";
    config.metadata.replication_id = 5;
    config.metadata.seed = 5001;

    config.verbose = false;
    config.export_results = false;

    NoReplanningExperimentResult result =
        run_no_replanning_experiment(config);

    const std::string output_path =
        "data/results/test_no_replanning_experiment_summary_writer.csv";

    std::filesystem::remove(output_path);

    write_no_replanning_experiment_summary_to_csv(
        result,
        output_path,
        true,
        false
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::vector<std::string> lines = read_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 2);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("experiment_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("scenario_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("delta_total_travel_time") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("csv_writer_experiment_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("csv_writer_scenario_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("no_replanning_policy_v1") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("50") != std::string::npos
    );

    write_no_replanning_experiment_summary_to_csv(
        result,
        output_path,
        false,
        true
    );

    lines = read_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("csv_writer_experiment_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("no_replanning_policy_v1") != std::string::npos
    );
}