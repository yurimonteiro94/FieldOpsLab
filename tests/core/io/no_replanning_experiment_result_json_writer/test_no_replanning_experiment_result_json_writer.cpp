#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_experiment_result_json_writer/no_replanning_experiment_result_json_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

void test_no_replanning_experiment_result_json_writer() {
    NoReplanningExperimentConfig config;

    config.metadata.experiment_id = "json_writer_experiment_001";
    config.metadata.scenario_id = "json_writer_scenario_001";
    config.metadata.replication_id = 4;
    config.metadata.seed = 4001;

    config.verbose = false;
    config.export_results = false;

    NoReplanningExperimentResult result =
        run_no_replanning_experiment(config);

    const std::string output_path =
        "data/results/test_no_replanning_experiment_result_writer.json";

    std::filesystem::remove(output_path);

    write_no_replanning_experiment_result_to_json(
        result,
        output_path,
        "test_no_replanning_experiment_result"
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::ifstream file(output_path);
    json data;
    file >> data;

    FIELDOPS_EXPECT_EQ(
        data.at("result_type").get<std::string>(),
        "test_no_replanning_experiment_result"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("metadata").at("experiment_id").get<std::string>(),
        "json_writer_experiment_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("metadata").at("scenario_id").get<std::string>(),
        "json_writer_scenario_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("metadata").at("replication_id").get<int>(),
        4
    );

    FIELDOPS_EXPECT_EQ(
        data.at("metadata").at("seed").get<int>(),
        4001
    );

    FIELDOPS_EXPECT_EQ(
        data.at("instance").at("instance_id").get<std::string>(),
        "sample_instance_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("policy_decision").at("policy_id").get<std::string>(),
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("policy_decision").at("should_replan").get<bool>(),
        false
    );

    FIELDOPS_EXPECT_EQ(
        data.at("planned").at("metrics").at("total_travel_time").get<int>(),
        145
    );

    FIELDOPS_EXPECT_EQ(
        data.at("executed").at("metrics").at("total_travel_time").get<int>(),
        195
    );

    FIELDOPS_EXPECT_EQ(
        data.at("comparison").at("deltas").at("total_travel_time").get<int>(),
        50
    );

    FIELDOPS_EXPECT_EQ(
        data.at("effects").size(),
        2
    );
}