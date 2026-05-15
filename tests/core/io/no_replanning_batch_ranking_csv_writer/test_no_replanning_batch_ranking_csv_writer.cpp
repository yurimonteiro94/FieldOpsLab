#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "core/io/no_replanning_batch_ranking_csv_writer/no_replanning_batch_ranking_csv_writer.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

static std::vector<std::string> read_ranking_csv_lines(
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

void test_no_replanning_batch_ranking_csv_writer() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = false;
    config.export_aggregate_csv = false;
    config.export_result_json = false;

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    FIELDOPS_EXPECT_EQ(result.results.size(), 12);

    const std::string output_path =
        "data/results/test_no_replanning_batch_ranking.csv";

    std::filesystem::remove(output_path);

    write_no_replanning_batch_ranking_csv(result, output_path);

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::vector<std::string> lines =
        read_ranking_csv_lines(output_path);

    FIELDOPS_EXPECT_EQ(lines.size(), 13);

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("scenario_id") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("rank") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("ranking_score") != std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        lines[0].find("mean_delta_objective_value") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_moderate_001,1,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,1,1,1,1,1,-52"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_severe_001,1,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,1,1,1,1,1,-52"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_reassignment_001,1,"
            "threshold_delay_replanning_policy_v1,"
            "greedy_replanning_solver_v1,"
            "replanning_applied_execution,1,1,1,1,1,-52"
        )
    );

    FIELDOPS_EXPECT_TRUE(
        any_line_contains(
            lines,
            "sample_delay_light_001,1,"
        )
    );
}