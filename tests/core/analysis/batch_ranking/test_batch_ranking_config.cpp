#include "core/analysis/batch_ranking/batch_ranking.h"
#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <string>
#include <vector>

static const BatchRankingRow* find_batch_ranking_config_test_row(
    const std::vector<BatchRankingRow>& rows,
    const std::string& scenario_id,
    const std::string& policy_id,
    const std::string& replanning_method_id
) {
    for (const auto& row : rows) {
        if (row.key.scenario_id == scenario_id &&
            row.key.policy_id == policy_id &&
            row.key.replanning_method_id == replanning_method_id) {
            return &row;
        }
    }

    return nullptr;
}

void test_batch_ranking_config() {
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

    std::vector<BatchRankingRow> default_rows =
        build_batch_ranking_rows(batch_result);

    const BatchRankingRow* default_greedy_moderate =
        find_batch_ranking_config_test_row(
            default_rows,
            "sample_delay_moderate_001",
            "threshold_delay_replanning_policy_v1",
            "greedy_replanning_solver_v1"
        );

    const BatchRankingRow* default_no_replanning_moderate =
        find_batch_ranking_config_test_row(
            default_rows,
            "sample_delay_moderate_001",
            "no_replanning_policy_v1",
            "replanning_not_implemented_v1"
        );

    FIELDOPS_EXPECT_TRUE(default_greedy_moderate != nullptr);
    FIELDOPS_EXPECT_TRUE(default_no_replanning_moderate != nullptr);

    FIELDOPS_EXPECT_EQ(default_greedy_moderate->rank, 1);
    FIELDOPS_EXPECT_TRUE(
        default_greedy_moderate->ranking_score <
        default_no_replanning_moderate->ranking_score
    );

    FIELDOPS_EXPECT_EQ(
        batch_ranking_score_definition(),
        "Lower is better. Current ranking_score equals "
        "mean_delta_objective_value."
    );

    BatchRankingConfig makespan_config;

    makespan_config.ranking_config_id = "makespan_delta_ranking_v1";
    makespan_config.objective_value_weight = 0.0;
    makespan_config.makespan_weight = 1.0;

    std::vector<BatchRankingRow> makespan_rows =
        build_batch_ranking_rows(batch_result, makespan_config);

    const BatchRankingRow* makespan_greedy_moderate =
        find_batch_ranking_config_test_row(
            makespan_rows,
            "sample_delay_moderate_001",
            "threshold_delay_replanning_policy_v1",
            "greedy_replanning_solver_v1"
        );

    const BatchRankingRow* makespan_no_replanning_moderate =
        find_batch_ranking_config_test_row(
            makespan_rows,
            "sample_delay_moderate_001",
            "no_replanning_policy_v1",
            "replanning_not_implemented_v1"
        );

    FIELDOPS_EXPECT_TRUE(makespan_greedy_moderate != nullptr);
    FIELDOPS_EXPECT_TRUE(makespan_no_replanning_moderate != nullptr);

    FIELDOPS_EXPECT_EQ(makespan_no_replanning_moderate->rank, 1);

    FIELDOPS_EXPECT_TRUE(
        makespan_no_replanning_moderate->ranking_score <
        makespan_greedy_moderate->ranking_score
    );

    FIELDOPS_EXPECT_TRUE(
        batch_ranking_score_definition(makespan_config)
            .find("makespan_delta_ranking_v1") != std::string::npos
    );
}