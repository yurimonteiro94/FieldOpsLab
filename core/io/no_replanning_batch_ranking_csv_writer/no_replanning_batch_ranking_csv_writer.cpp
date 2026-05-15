#include "core/io/no_replanning_batch_ranking_csv_writer/no_replanning_batch_ranking_csv_writer.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct BatchRankingKey {
    std::string scenario_id;
    std::string policy_id;
    std::string replanning_method_id;
    std::string execution_mode;

    bool operator<(const BatchRankingKey& other) const {
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

    double mean_delta_objective_value = 0.0;
    double mean_delta_makespan = 0.0;
    double mean_delta_total_travel_time = 0.0;
    double mean_delta_total_service_time = 0.0;
    double mean_delta_total_waiting_time = 0.0;

    double mean_late_task_count = 0.0;
    double mean_total_lateness = 0.0;
    double mean_effect_count = 0.0;

    double ranking_score = 0.0;
};

static std::string csv_escape(const std::string& value) {
    bool must_quote = false;

    for (const char character : value) {
        if (character == ',' ||
            character == '"' ||
            character == '\n' ||
            character == '\r') {
            must_quote = true;
            break;
        }
    }

    if (!must_quote) {
        return value;
    }

    std::string escaped = "\"";

    for (const char character : value) {
        if (character == '"') {
            escaped += "\"\"";
        } else {
            escaped += character;
        }
    }

    escaped += "\"";

    return escaped;
}

static std::string get_replanning_method_id(
    const NoReplanningExperimentResult& result
) {
    if (!result.has_replanning_result) {
        return "";
    }

    return result.replanning_result.method_id;
}

static BatchRankingKey build_key(
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

static void add_result_to_stats(
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

static double mean(double sum, int count) {
    if (count == 0) {
        return 0.0;
    }

    return sum / static_cast<double>(count);
}

static BatchRankingRow build_row(
    const BatchRankingKey& key,
    const BatchRankingStats& stats
) {
    BatchRankingRow row;

    row.key = key;
    row.stats = stats;

    row.mean_delta_objective_value =
        mean(stats.sum_delta_objective_value, stats.experiment_count);

    row.mean_delta_makespan =
        mean(stats.sum_delta_makespan, stats.experiment_count);

    row.mean_delta_total_travel_time =
        mean(stats.sum_delta_total_travel_time, stats.experiment_count);

    row.mean_delta_total_service_time =
        mean(stats.sum_delta_total_service_time, stats.experiment_count);

    row.mean_delta_total_waiting_time =
        mean(stats.sum_delta_total_waiting_time, stats.experiment_count);

    row.mean_late_task_count =
        mean(stats.sum_late_task_count, stats.experiment_count);

    row.mean_total_lateness =
        mean(stats.sum_total_lateness, stats.experiment_count);

    row.mean_effect_count =
        mean(stats.sum_effect_count, stats.experiment_count);

    row.ranking_score = row.mean_delta_objective_value;

    return row;
}

static std::vector<BatchRankingRow> build_ranking_rows(
    const NoReplanningBatchExperimentResult& batch_result
) {
    std::map<BatchRankingKey, BatchRankingStats> grouped_stats;

    for (const auto& result : batch_result.results) {
        BatchRankingKey key = build_key(result);

        add_result_to_stats(grouped_stats[key], result);
    }

    std::vector<BatchRankingRow> rows;

    for (const auto& entry : grouped_stats) {
        rows.push_back(
            build_row(entry.first, entry.second)
        );
    }

    std::sort(
        rows.begin(),
        rows.end(),
        [](const BatchRankingRow& first, const BatchRankingRow& second) {
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

    return rows;
}

static std::string build_header_line() {
    return
        "scenario_id,"
        "rank,"
        "policy_id,"
        "replanning_method_id,"
        "execution_mode,"
        "experiment_count,"
        "policy_should_replan_count,"
        "replanning_request_count,"
        "replanning_success_count,"
        "replanning_applied_count,"
        "ranking_score,"
        "mean_delta_objective_value,"
        "mean_delta_makespan,"
        "mean_delta_total_travel_time,"
        "mean_delta_total_service_time,"
        "mean_delta_total_waiting_time,"
        "mean_late_task_count,"
        "mean_total_lateness,"
        "mean_effect_count";
}

static std::string build_data_line(const BatchRankingRow& row) {
    std::ostringstream line;

    line << csv_escape(row.key.scenario_id) << ","
         << row.rank << ","
         << csv_escape(row.key.policy_id) << ","
         << csv_escape(row.key.replanning_method_id) << ","
         << csv_escape(row.key.execution_mode) << ","
         << row.stats.experiment_count << ","
         << row.stats.policy_should_replan_count << ","
         << row.stats.replanning_request_count << ","
         << row.stats.replanning_success_count << ","
         << row.stats.replanning_applied_count << ","
         << row.ranking_score << ","
         << row.mean_delta_objective_value << ","
         << row.mean_delta_makespan << ","
         << row.mean_delta_total_travel_time << ","
         << row.mean_delta_total_service_time << ","
         << row.mean_delta_total_waiting_time << ","
         << row.mean_late_task_count << ","
         << row.mean_total_lateness << ","
         << row.mean_effect_count;

    return line.str();
}

void write_no_replanning_batch_ranking_csv(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path
) {
    std::vector<BatchRankingRow> rows =
        build_ranking_rows(batch_result);

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path, std::ios::trunc);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch ranking CSV file: " +
            output_path
        );
    }

    file << build_header_line() << "\n";

    for (const auto& row : rows) {
        file << build_data_line(row) << "\n";
    }
}