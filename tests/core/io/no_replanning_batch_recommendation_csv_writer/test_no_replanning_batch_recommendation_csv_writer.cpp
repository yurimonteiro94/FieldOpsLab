#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "core/io/no_replanning_batch_recommendation_csv_writer/no_replanning_batch_recommendation_csv_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

static std::vector<std::string> read_recommendation_csv_lines(
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

static bool any_line_contains(
    const std::vector<std::string>& lines,
    const std::string& text
) {
    for (const auto& line : lines) {
        if (line.find(text) != std::string::npos) {
            return true;
        }
    }

    return false;
}

void test_no_replanning_batch_recommendation_csv_writer() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = false;
    config.export_aggregate_csv = false;
    config.export_ranking_csv = false;
    config.export_recommendation_csv = false;
    config.export_result_json = false;

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(config);

    const std::string output_path =
        "data/results/test_no_replanning_batch_recommendation.csv";

    std::filesystem::remove(output_path);

    write_no_replanning_batch_recommendation_csv(
        batch_result,
        output_path
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::vector<std::string> lines =
        read_recommendation_csv_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 5);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("scenario_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("recommended_policy_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("score_margin_to_second") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("recommendation_reason") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_light_001,"
            "no_replanning_policy_v1,"
            "replanning_not_implemented_v1,"
            "no_replanning_execution_baseline,"
            "1,1,0,0,0,0,0,0,0,true,false"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_moderate_001,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,"
            "1,1,1,1,1,1,-52,15,67,true,true"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_reassignment_001,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,"
            "1,1,1,1,1,1,-52,65,117,true,true"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_severe_001,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,"
            "1,1,1,1,1,1,-52,55,107,true,true"
        )
    );
}