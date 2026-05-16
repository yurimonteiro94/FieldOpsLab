#pragma once

#include <string>
#include <vector>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

struct BatchRankingKey {
    std::string scenario_id;
    std::string policy_id;
    std::string replanning_method_id;
    std::string execution_mode;

    bool operator<(const BatchRankingKey& other) const;
};

struct BatchRankingStats {
    int experiment_count = 0;

    int policy_should_replan_count = 0;
    int replanning_request_count = 0;
    int replanning_success_count = 0;
    int replanning_applied_count = 0;

    double sum_delta_objective_value = 0.0;
    double sum_delta_makespan = 0.0;
    double sum_delta_total_travel_time = 0.0;
    double sum_delta_total_service_time = 0.0;
    double sum_delta_total_waiting_time = 0.0;

    double sum_late_task_count = 0.0;
    double sum_total_lateness = 0.0;
    double sum_effect_count = 0.0;
};

struct BatchRankingRow {
    BatchRankingKey key;
    BatchRankingStats stats;

    int rank = 0;

    double ranking_score = 0.0;

    double mean_delta_objective_value = 0.0;
    double mean_delta_makespan = 0.0;
    double mean_delta_total_travel_time = 0.0;
    double mean_delta_total_service_time = 0.0;
    double mean_delta_total_waiting_time = 0.0;

    double mean_late_task_count = 0.0;
    double mean_total_lateness = 0.0;
    double mean_effect_count = 0.0;
};

std::string batch_ranking_score_definition();

std::vector<std::string> batch_ranking_tie_breakers();

std::vector<BatchRankingRow> build_batch_ranking_rows(
    const NoReplanningBatchExperimentResult& batch_result
);