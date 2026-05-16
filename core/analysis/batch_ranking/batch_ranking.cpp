#include "core/analysis/batch_ranking/batch_ranking.h"

#include <algorithm>
#include <map>

bool BatchRankingKey::operator<(const BatchRankingKey& other) const {
    if (scenario_id != other.scenario_id) {
        return scenario_id < other.scenario_id;
    }

    if (policy_id != other.policy_id) {
        return policy_id < other.policy_id;
    }

    if (replanning_method_id != other.replanning_method_id) {
        return replanning_method_id < other.replanning_method_id;
    }

    return execution_mode < other.execution_mode;
}

std::string batch_ranking_score_definition() {
    return
        "Lower is better. Current ranking_score equals "
        "mean_delta_objective_value.";
}

std::vector<std::string> batch_ranking_tie_breakers() {
    return {
        "mean_delta_makespan",
        "mean_delta_total_travel_time",
        "policy_id",
        "replanning_method_id",
        "execution_mode"
    };
}

static std::string get_replanning_method_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.method_id;
}

static BatchRankingKey build_ranking_key(
    const NoReplanningExperimentResult& result
) {
    BatchRankingKey key;

    key.scenario_id = result.metadata.scenario_id;
    key.policy_id = result.policy_decision.policy_id;
    key.replanning_method_id = get_replanning_method_id(result);
    key.execution_mode = result.execution_mode;

    return key;
}

static bool replanning_was_successful(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return false;
    }

    return result.replanning_result.is_successful();
}

static void add_result_to_ranking_stats(
    BatchRankingStats& stats,
    const NoReplanningExperimentResult& result
) {
    stats.experiment_count += 1;

    if (result.policy_decision.should_replan()) {
        stats.policy_should_replan_count += 1;
    }

    if (result.has_replanning_request) {
        stats.replanning_request_count += 1;
    }

    if (replanning_was_successful(result)) {
        stats.replanning_success_count += 1;
    }

    if (result.replanning_result_was_applied_to_execution) {
        stats.replanning_applied_count += 1;
    }

    stats.sum_delta_objective_value +=
        result.comparison.delta_objective_value;

    stats.sum_delta_makespan +=
        result.comparison.delta_makespan;

    stats.sum_delta_total_travel_time +=
        result.comparison.delta_total_travel_time;

    stats.sum_delta_total_service_time +=
        result.comparison.delta_total_service_time;

    stats.sum_delta_total_waiting_time +=
        result.comparison.delta_total_waiting_time;

    stats.sum_late_task_count +=
        result.executed_metrics.late_task_count;

    stats.sum_total_lateness +=
        result.executed_metrics.total_lateness;

    stats.sum_effect_count +=
        result.effects.size();
}

static double mean_value(double sum, int count) {
    if (count == 0) {
        return 0.0;
    }

    return sum / static_cast<double>(count);
}

static BatchRankingRow build_ranking_row(
    const BatchRankingKey& key,
    const BatchRankingStats& stats
) {
    BatchRankingRow row;

    row.key = key;
    row.stats = stats;

    row.mean_delta_objective_value =
        mean_value(
            stats.sum_delta_objective_value,
            stats.experiment_count
        );

    row.mean_delta_makespan =
        mean_value(
            stats.sum_delta_makespan,
            stats.experiment_count
        );

    row.mean_delta_total_travel_time =
        mean_value(
            stats.sum_delta_total_travel_time,
            stats.experiment_count
        );

    row.mean_delta_total_service_time =
        mean_value(
            stats.sum_delta_total_service_time,
            stats.experiment_count
        );

    row.mean_delta_total_waiting_time =
        mean_value(
            stats.sum_delta_total_waiting_time,
            stats.experiment_count
        );

    row.mean_late_task_count =
        mean_value(
            stats.sum_late_task_count,
            stats.experiment_count
        );

    row.mean_total_lateness =
        mean_value(
            stats.sum_total_lateness,
            stats.experiment_count
        );

    row.mean_effect_count =
        mean_value(
            stats.sum_effect_count,
            stats.experiment_count
        );

    row.ranking_score = row.mean_delta_objective_value;

    return row;
}

static void sort_ranking_rows(std::vector<BatchRankingRow>& rows) {
    std::sort(
        rows.begin(),
        rows.end(),
        [](const BatchRankingRow& first,
           const BatchRankingRow& second) {
            if (first.key.scenario_id != second.key.scenario_id) {
                return first.key.scenario_id < second.key.scenario_id;
            }

            if (first.ranking_score != second.ranking_score) {
                return first.ranking_score < second.ranking_score;
            }

            if (first.mean_delta_makespan != second.mean_delta_makespan) {
                return first.mean_delta_makespan < second.mean_delta_makespan;
            }

            if (first.mean_delta_total_travel_time !=
                second.mean_delta_total_travel_time) {
                return first.mean_delta_total_travel_time <
                       second.mean_delta_total_travel_time;
            }

            if (first.key.policy_id != second.key.policy_id) {
                return first.key.policy_id < second.key.policy_id;
            }

            if (first.key.replanning_method_id !=
                second.key.replanning_method_id) {
                return first.key.replanning_method_id <
                       second.key.replanning_method_id;
            }

            return first.key.execution_mode < second.key.execution_mode;
        }
    );
}

static void assign_ranks(std::vector<BatchRankingRow>& rows) {
    std::string current_scenario_id;
    int current_rank = 0;

    for (auto& row : rows) {
        if (row.key.scenario_id != current_scenario_id) {
            current_scenario_id = row.key.scenario_id;
            current_rank = 1;
        } else {
            current_rank += 1;
        }

        row.rank = current_rank;
    }
}

std::vector<BatchRankingRow> build_batch_ranking_rows(
    const NoReplanningBatchExperimentResult& batch_result
) {
    std::map<BatchRankingKey, BatchRankingStats> grouped_stats;

    for (const auto& result : batch_result.results) {
        BatchRankingKey key = build_ranking_key(result);

        add_result_to_ranking_stats(grouped_stats[key], result);
    }

    std::vector<BatchRankingRow> rows;

    for (const auto& entry : grouped_stats) {
        rows.push_back(
            build_ranking_row(entry.first, entry.second)
        );
    }

    sort_ranking_rows(rows);
    assign_ranks(rows);

    return rows;
}