#include "core/analysis/batch_recommendation/batch_recommendation.h"

#include <sstream>
#include <string>
#include <vector>

std::string batch_recommendation_definition() {
    return
        "One recommendation is produced for each scenario. "
        "The recommended option is the rank-1 option from the batch ranking. "
        "Lower ranking_score is better. "
        "score_margin_to_second equals second_best_score minus best_score.";
}

static std::string build_clear_winner_reason(
    const BatchRankingRow& best_row,
    const BatchRankingRow& second_row
) {
    std::ostringstream reason;

    reason
        << "Recommended because it has the lowest ranking score for scenario "
        << best_row.key.scenario_id
        << ". The best score is "
        << best_row.ranking_score
        << " and the second-best score is "
        << second_row.ranking_score
        << ".";

    return reason.str();
}

static std::string build_tie_break_reason(
    const BatchRankingRow& best_row,
    const BatchRankingRow& second_row
) {
    std::ostringstream reason;

    reason
        << "Recommended by deterministic tie-breakers. "
        << "The best and second-best options have the same ranking score of "
        << best_row.ranking_score
        << " for scenario "
        << best_row.key.scenario_id
        << ".";

    (void)second_row;

    return reason.str();
}

static std::string build_single_option_reason(
    const BatchRankingRow& best_row
) {
    std::ostringstream reason;

    reason
        << "Recommended because it is the only evaluated option for scenario "
        << best_row.key.scenario_id
        << ".";

    return reason.str();
}

static BatchScenarioRecommendation build_recommendation_from_best_row(
    const BatchRankingRow& best_row
) {
    BatchScenarioRecommendation recommendation;

    recommendation.scenario_id = best_row.key.scenario_id;
    recommendation.recommended_policy_id = best_row.key.policy_id;
    recommendation.recommended_replanning_method_id =
        best_row.key.replanning_method_id;
    recommendation.recommended_execution_mode =
        best_row.key.execution_mode;

    recommendation.recommended_rank = best_row.rank;

    recommendation.experiment_count = best_row.stats.experiment_count;
    recommendation.policy_should_replan_count =
        best_row.stats.policy_should_replan_count;
    recommendation.replanning_request_count =
        best_row.stats.replanning_request_count;
    recommendation.replanning_success_count =
        best_row.stats.replanning_success_count;
    recommendation.replanning_applied_count =
        best_row.stats.replanning_applied_count;

    recommendation.best_score = best_row.ranking_score;

    recommendation.mean_delta_objective_value =
        best_row.mean_delta_objective_value;
    recommendation.mean_delta_makespan =
        best_row.mean_delta_makespan;
    recommendation.mean_delta_total_travel_time =
        best_row.mean_delta_total_travel_time;
    recommendation.mean_delta_total_service_time =
        best_row.mean_delta_total_service_time;
    recommendation.mean_delta_total_waiting_time =
        best_row.mean_delta_total_waiting_time;

    recommendation.mean_late_task_count =
        best_row.mean_late_task_count;
    recommendation.mean_total_lateness =
        best_row.mean_total_lateness;
    recommendation.mean_effect_count =
        best_row.mean_effect_count;

    return recommendation;
}

static void complete_recommendation_with_second_option(
    BatchScenarioRecommendation& recommendation,
    const BatchRankingRow& best_row,
    const BatchRankingRow& second_row
) {
    recommendation.has_second_option = true;
    recommendation.second_best_score = second_row.ranking_score;
    recommendation.score_margin_to_second =
        second_row.ranking_score - best_row.ranking_score;

    recommendation.has_clear_winner =
        recommendation.score_margin_to_second > 0.0;

    if (recommendation.has_clear_winner) {
        recommendation.recommendation_reason =
            build_clear_winner_reason(best_row, second_row);
    } else {
        recommendation.recommendation_reason =
            build_tie_break_reason(best_row, second_row);
    }
}

static void complete_recommendation_without_second_option(
    BatchScenarioRecommendation& recommendation,
    const BatchRankingRow& best_row
) {
    recommendation.has_second_option = false;
    recommendation.second_best_score = 0.0;
    recommendation.score_margin_to_second = 0.0;
    recommendation.has_clear_winner = false;
    recommendation.recommendation_reason =
        build_single_option_reason(best_row);
}

std::vector<BatchScenarioRecommendation> build_batch_scenario_recommendations(
    const NoReplanningBatchExperimentResult& batch_result
) {
    std::vector<BatchRankingRow> ranking_rows =
        build_batch_ranking_rows(batch_result);

    std::vector<BatchScenarioRecommendation> recommendations;

    for (int i = 0; i < static_cast<int>(ranking_rows.size()); ++i) {
        const BatchRankingRow& row = ranking_rows[i];

        if (row.rank != 1) {
            continue;
        }

        BatchScenarioRecommendation recommendation =
            build_recommendation_from_best_row(row);

        bool found_second_option = false;

        for (int j = i + 1; j < static_cast<int>(ranking_rows.size()); ++j) {
            const BatchRankingRow& candidate_second = ranking_rows[j];

            if (candidate_second.key.scenario_id != row.key.scenario_id) {
                break;
            }

            if (candidate_second.rank == 2) {
                complete_recommendation_with_second_option(
                    recommendation,
                    row,
                    candidate_second
                );

                found_second_option = true;
                break;
            }
        }

        if (!found_second_option) {
            complete_recommendation_without_second_option(
                recommendation,
                row
            );
        }

        recommendations.push_back(recommendation);
    }

    return recommendations;
}