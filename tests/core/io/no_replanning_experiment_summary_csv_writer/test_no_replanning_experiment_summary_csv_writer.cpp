#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>

void test_no_replanning_experiment_summary_csv_writer() {
    NoReplanningExperimentConfig config;

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
        true
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::ifstream file(output_path);

    std::string header;
    std::string row;

    std::getline(file, header);
    std::getline(file, row);

    FIELDOPS_EXPECT_TRUE(
        header.find("instance_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        header.find("delta_total_travel_time") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        row.find("sample_instance_001") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        row.find("no_replanning_policy_v1") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        row.find("50") != std::string::npos
    );
}