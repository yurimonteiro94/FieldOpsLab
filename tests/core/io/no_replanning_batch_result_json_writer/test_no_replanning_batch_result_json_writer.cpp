#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "core/io/no_replanning_batch_result_json_writer/no_replanning_batch_result_json_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

void test_no_replanning_batch_result_json_writer() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = true;
    config.export_aggregate_csv = true;

    config.summary_csv_output_path =
        "data/results/test_batch_result_writer_summary.csv";

    config.aggregate_csv_output_path =
        "data/results/test_batch_result_writer_aggregate.csv";

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(config);

    const std::string output_path =
        "data/results/test_no_replanning_batch_result_writer.json";

    std::filesystem::remove(output_path);

    write_no_replanning_batch_result_to_json(
        batch_result,
        output_path,
        "test_no_replanning_batch_result"
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::ifstream file(output_path);
    json data;
    file >> data;

    FIELDOPS_EXPECT_EQ(
        data.at("result_type").get<std::string>(),
        "test_no_replanning_batch_result"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("batch").at("batch_id").get<std::string>(),
        "sample_no_replanning_batch_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("batch").at("experiment_count").get<int>(),
        9
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("outputs").at("summary_csv_was_written").get<bool>()
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("outputs").at("aggregate_csv_was_written").get<bool>()
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").size(),
        9
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(0).at("experiment_id").get<std::string>(),
        "batch_001_no_replanning_light_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(0).at("policy").at("policy_id").get<std::string>(),
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(0).at("replanning_result").at("status").get<std::string>(),
        "NOT_REQUESTED"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(4).at("experiment_id").get<std::string>(),
        "batch_001_threshold_moderate_001"
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("experiments").at(4).at("policy").at("should_replan").get<bool>()
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(4).at("replanning_result").at("status").get<std::string>(),
        "NOT_IMPLEMENTED"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(7).at("experiment_id").get<std::string>(),
        "batch_001_threshold_greedy_moderate_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(7).at("replanning_result").at("method_id").get<std::string>(),
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(7).at("replanning_result").at("status").get<std::string>(),
        "SUCCESS"
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("experiments").at(7).at("replanning_result").at("has_new_solution").get<bool>()
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("experiments").at(7).at("replanning_result").at("is_successful").get<bool>()
    );

    FIELDOPS_EXPECT_TRUE(
        !data.at("experiments").at(7).at("replanning_result").at("was_applied_to_execution").get<bool>()
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(7).at("execution").at("execution_mode").get<std::string>(),
        "no_replanning_execution_baseline"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(7).at("metrics").at("delta_total_travel_time").get<int>(),
        50
    );

    FIELDOPS_EXPECT_EQ(
        data.at("experiments").at(8).at("metrics").at("delta_makespan").get<int>(),
        55
    );
}