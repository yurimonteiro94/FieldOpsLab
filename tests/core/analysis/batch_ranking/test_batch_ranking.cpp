#include "core/analysis/batch_ranking/batch_ranking.h"
#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <string>
#include <vector>

static const BatchRankingRow* find_ranking_row(
    const std::vector<BatchRankingRow>& rows,
    const std::string& scenario_id,
    int rank
) {
    for (const auto& row : rows) {
        if (row.key.scenario_id == scenario_id &&
            row.rank == rank) {
            return &row;
        }
    }

    return nullptr;
}

void test_batch_ranking() {
    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(
            "data/experiments/sample_no_replanning_batch_001.json"
        );

    config.verbose = false;
    config.export_individual_results = false;
    config.export_summary_csv = false;
    config.export_aggregate_csv = false;
    config.export_ranking_csv = false;
    config.export_result_json = false;

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(config);

    std::vector<BatchRankingRow> rows =
        build_batch_ranking_rows(batch_result);

    FIELDOPS_EXPECT_EQ(rows.size(), 12);

    FIELDOPS_EXPECT_TRUE(
        batch_ranking_score_definition().find("Lower is better") !=
        std::string::npos
    );

    FIELDOPS_EXPECT_EQ(
        batch_ranking_tie_breakers().size(),
        5
    );

    const BatchRankingRow* light_winner =
        find_ranking_row(
            rows,
            "sample_delay_light_001",
            1
        );

    FIELDOPS_EXPECT_TRUE(light_winner != nullptr);

    FIELDOPS_EXPECT_EQ(
        light_winner->key.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        light_winner->key.replanning_method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        light_winner->ranking_score,
        0.0
    );

    const BatchRankingRow* moderate_winner =
        find_ranking_row(
            rows,
            "sample_delay_moderate_001",
            1
        );

    FIELDOPS_EXPECT_TRUE(moderate_winner != nullptr);

    FIELDOPS_EXPECT_EQ(
        moderate_winner->key.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_winner->key.replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_winner->key.execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_winner->stats.replanning_applied_count,
        1
    );

    FIELDOPS_EXPECT_EQ(
        moderate_winner->ranking_score,
        -52.0
    );

    FIELDOPS_EXPECT_EQ(
        moderate_winner->mean_delta_total_travel_time,
        -17.0
    );

    const BatchRankingRow* reassignment_winner =
        find_ranking_row(
            rows,
            "sample_delay_reassignment_001",
            1
        );

    FIELDOPS_EXPECT_TRUE(reassignment_winner != nullptr);

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->key.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->key.replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->key.execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->stats.policy_should_replan_count,
        1
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->stats.replanning_request_count,
        1
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->stats.replanning_success_count,
        1
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->stats.replanning_applied_count,
        1
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->ranking_score,
        -52.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->mean_delta_makespan,
        3.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_winner->mean_delta_total_travel_time,
        -17.0
    );

    const BatchRankingRow* reassignment_baseline =
        find_ranking_row(
            rows,
            "sample_delay_reassignment_001",
            2
        );

    FIELDOPS_EXPECT_TRUE(reassignment_baseline != nullptr);

    FIELDOPS_EXPECT_EQ(
        reassignment_baseline->key.policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_baseline->ranking_score,
        65.0
    );

    const BatchRankingRow* severe_winner =
        find_ranking_row(
            rows,
            "sample_delay_severe_001",
            1
        );

    FIELDOPS_EXPECT_TRUE(severe_winner != nullptr);

    FIELDOPS_EXPECT_EQ(
        severe_winner->key.policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        severe_winner->key.replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        severe_winner->ranking_score,
        -52.0
    );
}