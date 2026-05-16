#include "core/analysis/batch_ranking/batch_ranking.h"

#include <algorithm>
#include <map>
#include <sstream>

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

static bool is_default_ranking_config(
    const BatchRankingConfig& config
) {
    return
        config.ranking_config_id == "default_objective_delta_ranking_v1" &&
        config.objective_value_weight == 1.0 &&
        config.makespan_weight == 0.0 &&
        config.total_travel_time_weight == 0.0 &&
        config.total_service_time_weight == 0.0 &&
        config.total_waiting_time_weight == 0.0 &&
        config.late_task_count_weight == 0.0 &&
        config.total_lateness_weight == 0.0 &&
        config.effect_count_weight == 0.0 &&
        config.policy_should_replan_count_weight == 0.0 &&
        config.replanning_request_count_weight == 0.0 &&
        config.replanning_success_count_weight == 0.0 &&
        config.replanning_applied_count_weight == 0.0;
}

std::string batch_ranking_score_definition(
    const BatchRankingConfig& config
) {
    if (is_default_ranking_config(config)) {
        return
            "Lower is better. Current ranking_score equals "
            "mean_delta_objective_value.";
    }

    std::ostringstream text;

    text
        << "Lower is better. Current ranking_score is a weighted sum. "
        << "ranking_config_id="
        << config.ranking_config_id
        << ".";

    return text.str();
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

static double count_mean_value(int value, int count) {
    if (count == 0) {
        return 0.0;
    }

    return static_cast<double>(value) / static_cast<double>(count);
}

static double calculate_ranking_score(
    const BatchRankingRow& row,
    const BatchRankingConfig& config
) {
    const int count = row.stats.experiment_count;

    return
        config.objective_value_weight *
            row.mean_delta_objective_value +

        config.makespan_weight *
            row.mean_delta_makespan +

        config.total_travel_time_weight *
            row.mean_delta_total_travel_time +

        config.total_service_time_weight *
            row.mean_delta_total_service_time +

        config.total_waiting_time_weight *
            row.mean_delta_total_waiting_time +

        config.late_task_count_weight *
            row.mean_late_task_count +

        config.total_lateness_weight *
            row.mean_total_lateness +

        config.effect_count_weight *
            row.mean_effect_count +

        config.policy_should_replan_count_weight *
            count_mean_value(
                row.stats.policy_should_replan_count,
                count
            ) +

        config.replanning_request_count_weight *
            count_mean_value(
                row.stats.replanning_request_count,
                count
            ) +

        config.replanning_success_count_weight *
            count_mean_value(
                row.stats.replanning_success_count,
                count
            ) +

        config.replanning_applied_count_weight *
            count_mean_value(
                row.stats.replanning_applied_count,
                count
            );
}

static BatchRankingRow build_ranking_row(
    const BatchRankingKey& key,
    const BatchRankingStats& stats,
    const BatchRankingConfig& config
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

    row.ranking_score = calculate_ranking_score(row, config);

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
                return first.mean_delta_makespan <
                       second.mean_delta_makespan;
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
    return build_batch_ranking_rows(
        batch_result,
        batch_result.ranking_config
    );
}

std::vector<BatchRankingRow> build_batch_ranking_rows(
    const NoReplanningBatchExperimentResult& batch_result,
    const BatchRankingConfig& ranking_config
) {
    std::map<BatchRankingKey, BatchRankingStats> grouped_stats;

    for (const auto& result : batch_result.results) {
        BatchRankingKey key = build_ranking_key(result);

        add_result_to_ranking_stats(grouped_stats[key], result);
    }

    std::vector<BatchRankingRow> rows;

    for (const auto& entry : grouped_stats) {
        rows.push_back(
            build_ranking_row(
                entry.first,
                entry.second,
                ranking_config
            )
        );
    }

    sort_ranking_rows(rows);
    assign_ranks(rows);

    return rows;
}