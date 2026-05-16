#pragma once

#include <string>
#include <vector>

#include "core/analysis/batch_ranking/batch_ranking.h"
#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

struct BatchScenarioRecommendation {
    std::string scenario_id;

    std::string recommended_policy_id;
    std::string recommended_replanning_method_id;
    std::string recommended_execution_mode;

    int recommended_rank = 0;

    int experiment_count = 0;
    int policy_should_replan_count = 0;
    int replanning_request_count = 0;
    int replanning_success_count = 0;
    int replanning_applied_count = 0;

    double best_score = 0.0;
    double second_best_score = 0.0;
    double score_margin_to_second = 0.0;

    bool has_second_option = false;
    bool has_clear_winner = false;

    double mean_delta_objective_value = 0.0;
    double mean_delta_makespan = 0.0;
    double mean_delta_total_travel_time = 0.0;
    double mean_delta_total_service_time = 0.0;
    double mean_delta_total_waiting_time = 0.0;

    double mean_late_task_count = 0.0;
    double mean_total_lateness = 0.0;
    double mean_effect_count = 0.0;

    std::string recommendation_reason;
};

std::string batch_recommendation_definition();

std::vector<BatchScenarioRecommendation> build_batch_scenario_recommendations(
    const NoReplanningBatchExperimentResult& batch_result
);