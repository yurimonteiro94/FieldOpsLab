#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

static std::vector<std::string> read_summary_csv_lines(
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

void test_no_replanning_experiment_summary_csv_writer() {
    NoReplanningExperimentConfig no_replanning_config;

    no_replanning_config.metadata.experiment_id =
        "summary_writer_no_replanning_001";

    no_replanning_config.metadata.scenario_id =
        "summary_writer_scenario_001";

    no_replanning_config.metadata.replication_id = 1;
    no_replanning_config.metadata.seed = 1001;
    no_replanning_config.metadata.notes = "CSV writer no-replanning test.";

    no_replanning_config.policy_config.policy_id =
        "no_replanning_policy_v1";

    no_replanning_config.verbose = false;
    no_replanning_config.export_results = false;

    NoReplanningExperimentResult no_replanning_result =
        run_no_replanning_experiment(no_replanning_config);

    NoReplanningExperimentConfig threshold_config;

    threshold_config.metadata.experiment_id =
        "summary_writer_threshold_001";

    threshold_config.metadata.scenario_id =
        "summary_writer_scenario_002";

    threshold_config.metadata.replication_id = 2;
    threshold_config.metadata.seed = 2001;
    threshold_config.metadata.notes = "CSV writer threshold test.";

    threshold_config.policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    threshold_config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    threshold_config.policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    threshold_config.verbose = false;
    threshold_config.export_results = false;

    NoReplanningExperimentResult threshold_result =
        run_no_replanning_experiment(threshold_config);

    const std::string output_path =
        "data/results/test_no_replanning_experiment_summary_writer.csv";

    std::filesystem::remove(output_path);

    write_no_replanning_experiment_summary_to_csv(
        no_replanning_result,
        output_path,
        false
    );

    write_no_replanning_experiment_summary_to_csv(
        threshold_result,
        output_path,
        true
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::vector<std::string> lines =
        read_summary_csv_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("has_replanning_request") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("replanning_candidate_task_count") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("summary_writer_no_replanning_001") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find(",no_replanning_policy_v1,DO_NOT_REPLAN,false,false,false,0,0,0,0,0,0,") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("summary_writer_threshold_001") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find(",threshold_delay_replanning_policy_v1,REPLAN,true,true,true,1,1,1,0,2,0,") !=
        std::string::npos
    );
}