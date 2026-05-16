#include "core/analysis/batch_recommendation/batch_recommendation.h"
#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"
#include "tests/test_support/test_assertions.h"

#include <string>
#include <vector>

static const BatchScenarioRecommendation* find_recommendation(
    const std::vector<BatchScenarioRecommendation>& recommendations,
    const std::string& scenario_id
) {
    for (const auto& recommendation : recommendations) {
        if (recommendation.scenario_id == scenario_id) {
            return &recommendation;
        }
    }

    return nullptr;
}

void test_batch_recommendation() {
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

    std::vector<BatchScenarioRecommendation> recommendations =
        build_batch_scenario_recommendations(batch_result);

    FIELDOPS_EXPECT_EQ(recommendations.size(), 4);

    FIELDOPS_EXPECT_TRUE(
        batch_recommendation_definition().find("One recommendation") !=
        std::string::npos
    );

    const BatchScenarioRecommendation* light_recommendation =
        find_recommendation(
            recommendations,
            "sample_delay_light_001"
        );

    FIELDOPS_EXPECT_TRUE(light_recommendation != nullptr);

    FIELDOPS_EXPECT_EQ(
        light_recommendation->recommended_policy_id,
        "no_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        light_recommendation->recommended_replanning_method_id,
        "replanning_not_implemented_v1"
    );

    FIELDOPS_EXPECT_EQ(
        light_recommendation->best_score,
        0.0
    );

    FIELDOPS_EXPECT_TRUE(
        light_recommendation->has_second_option
    );

    FIELDOPS_EXPECT_EQ(
        light_recommendation->second_best_score,
        0.0
    );

    FIELDOPS_EXPECT_EQ(
        light_recommendation->score_margin_to_second,
        0.0
    );

    FIELDOPS_EXPECT_TRUE(
        !light_recommendation->has_clear_winner
    );

    const BatchScenarioRecommendation* moderate_recommendation =
        find_recommendation(
            recommendations,
            "sample_delay_moderate_001"
        );

    FIELDOPS_EXPECT_TRUE(moderate_recommendation != nullptr);

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->recommended_policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->recommended_replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->recommended_execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->best_score,
        -52.0
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->second_best_score,
        15.0
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->score_margin_to_second,
        67.0
    );

    FIELDOPS_EXPECT_TRUE(
        moderate_recommendation->has_clear_winner
    );

    FIELDOPS_EXPECT_EQ(
        moderate_recommendation->replanning_applied_count,
        1
    );

    const BatchScenarioRecommendation* reassignment_recommendation =
        find_recommendation(
            recommendations,
            "sample_delay_reassignment_001"
        );

    FIELDOPS_EXPECT_TRUE(reassignment_recommendation != nullptr);

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->recommended_policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->recommended_replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->recommended_execution_mode,
        "replanning_applied_execution"
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->best_score,
        -52.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->second_best_score,
        65.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->score_margin_to_second,
        117.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->mean_delta_makespan,
        3.0
    );

    FIELDOPS_EXPECT_EQ(
        reassignment_recommendation->mean_delta_total_travel_time,
        -17.0
    );

    FIELDOPS_EXPECT_TRUE(
        reassignment_recommendation->recommendation_reason.find(
            "lowest ranking score"
        ) != std::string::npos
    );

    const BatchScenarioRecommendation* severe_recommendation =
        find_recommendation(
            recommendations,
            "sample_delay_severe_001"
        );

    FIELDOPS_EXPECT_TRUE(severe_recommendation != nullptr);

    FIELDOPS_EXPECT_EQ(
        severe_recommendation->recommended_policy_id,
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        severe_recommendation->recommended_replanning_method_id,
        "greedy_replanning_solver_v1"
    );

    FIELDOPS_EXPECT_EQ(
        severe_recommendation->best_score,
        -52.0
    );

    FIELDOPS_EXPECT_EQ(
        severe_recommendation->second_best_score,
        55.0
    );

    FIELDOPS_EXPECT_EQ(
        severe_recommendation->score_margin_to_second,
        107.0
    );
}