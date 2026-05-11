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

    NoReplanningExperimentConfig greedy_config;

    greedy_config.metadata.experiment_id =
        "summary_writer_greedy_001";

    greedy_config.metadata.scenario_id =
        "summary_writer_scenario_002";

    greedy_config.metadata.replication_id = 2;
    greedy_config.metadata.seed = 2001;
    greedy_config.metadata.notes = "CSV writer greedy test.";

    greedy_config.policy_config.policy_id =
        "threshold_delay_replanning_policy_v1";

    greedy_config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold = 30;

    greedy_config.policy_config
        .threshold_delay_config
        .total_delay_threshold = 60;

    greedy_config.replanning_engine_config.method_id =
        "greedy_replanning_solver_v1";

    greedy_config.verbose = false;
    greedy_config.export_results = false;

    NoReplanningExperimentResult greedy_result =
        run_no_replanning_experiment(greedy_config);

    const std::string output_path =
        "data/results/test_no_replanning_experiment_summary_writer.csv";

    std::filesystem::remove(output_path);

    write_no_replanning_experiment_summary_to_csv(
        no_replanning_result,
        output_path,
        false
    );

    write_no_replanning_experiment_summary_to_csv(
        greedy_result,
        output_path,
        true
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::vector<std::string> lines =
        read_summary_csv_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 3);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("replanning_result_status") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("replanning_result_generated_solution_id") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find("summary_writer_no_replanning_001") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[1].find(",no_replanning_policy_v1,DO_NOT_REPLAN,false,false,false,0,0,0,0,0,0,true,replanning_not_implemented_v1,NOT_REQUESTED,false,false,") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find("summary_writer_greedy_001") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[2].find(",threshold_delay_replanning_policy_v1,REPLAN,true,true,true,1,1,1,0,2,0,true,greedy_replanning_solver_v1,SUCCESS,true,true,") !=
        std::string::npos
    );
}