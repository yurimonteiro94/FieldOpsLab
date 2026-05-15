#include "core/io/no_replanning_batch_aggregate_csv_writer/no_replanning_batch_aggregate_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>

struct BatchAggregateKey {
    std::string scenario_id;
    std::string policy_id;
    std::string replanning_method_id;
    std::string execution_mode;

    bool operator<(const BatchAggregateKey& other) const {
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

struct BatchAggregateStats {
    int experiment_count = 0;

    int policy_should_replan_count = 0;
    int replanning_request_count = 0;
    int replanning_success_count = 0;
    int replanning_applied_count = 0;

    double sum_delta_objective_value = 0.0;
    double sum_percent_objective_value = 0.0;

    double sum_delta_makespan = 0.0;
    double sum_percent_makespan = 0.0;

    double sum_delta_total_travel_time = 0.0;
    double sum_percent_total_travel_time = 0.0;

    double sum_delta_total_service_time = 0.0;
    double sum_percent_total_service_time = 0.0;

    double sum_delta_total_waiting_time = 0.0;
    double sum_percent_total_waiting_time = 0.0;

    double sum_late_task_count = 0.0;
    double sum_total_lateness = 0.0;
    double sum_effect_count = 0.0;
};

static std::string bool_to_csv(bool value) {
    return value ? "true" : "false";
}

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

static BatchAggregateKey build_key(
    const NoReplanningExperimentResult& result
) {
    BatchAggregateKey key;

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
    BatchAggregateStats& stats,
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

    stats.sum_percent_objective_value +=
        result.comparison.percent_objective_value;

    stats.sum_delta_makespan +=
        result.comparison.delta_makespan;

    stats.sum_percent_makespan +=
        result.comparison.percent_makespan;

    stats.sum_delta_total_travel_time +=
        result.comparison.delta_total_travel_time;

    stats.sum_percent_total_travel_time +=
        result.comparison.percent_total_travel_time;

    stats.sum_delta_total_service_time +=
        result.comparison.delta_total_service_time;

    stats.sum_percent_total_service_time +=
        result.comparison.percent_total_service_time;

    stats.sum_delta_total_waiting_time +=
        result.comparison.delta_total_waiting_time;

    stats.sum_percent_total_waiting_time +=
        result.comparison.percent_total_waiting_time;

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

static std::string build_header_line() {
    return
        "scenario_id,"
        "policy_id,"
        "replanning_method_id,"
        "execution_mode,"
        "experiment_count,"
        "policy_should_replan_count,"
        "replanning_request_count,"
        "replanning_success_count,"
        "replanning_applied_count,"
        "mean_delta_objective_value,"
        "mean_percent_objective_value,"
        "mean_delta_makespan,"
        "mean_percent_makespan,"
        "mean_delta_total_travel_time,"
        "mean_percent_total_travel_time,"
        "mean_delta_total_service_time,"
        "mean_percent_total_service_time,"
        "mean_delta_total_waiting_time,"
        "mean_percent_total_waiting_time,"
        "mean_late_task_count,"
        "mean_total_lateness,"
        "mean_effect_count";
}

static std::string build_data_line(
    const BatchAggregateKey& key,
    const BatchAggregateStats& stats
) {
    std::ostringstream line;

    line << csv_escape(key.scenario_id) << ","
         << csv_escape(key.policy_id) << ","
         << csv_escape(key.replanning_method_id) << ","
         << csv_escape(key.execution_mode) << ","
         << stats.experiment_count << ","
         << stats.policy_should_replan_count << ","
         << stats.replanning_request_count << ","
         << stats.replanning_success_count << ","
         << stats.replanning_applied_count << ","
         << mean(stats.sum_delta_objective_value, stats.experiment_count) << ","
         << mean(stats.sum_percent_objective_value, stats.experiment_count) << ","
         << mean(stats.sum_delta_makespan, stats.experiment_count) << ","
         << mean(stats.sum_percent_makespan, stats.experiment_count) << ","
         << mean(stats.sum_delta_total_travel_time, stats.experiment_count) << ","
         << mean(stats.sum_percent_total_travel_time, stats.experiment_count) << ","
         << mean(stats.sum_delta_total_service_time, stats.experiment_count) << ","
         << mean(stats.sum_percent_total_service_time, stats.experiment_count) << ","
         << mean(stats.sum_delta_total_waiting_time, stats.experiment_count) << ","
         << mean(stats.sum_percent_total_waiting_time, stats.experiment_count) << ","
         << mean(stats.sum_late_task_count, stats.experiment_count) << ","
         << mean(stats.sum_total_lateness, stats.experiment_count) << ","
         << mean(stats.sum_effect_count, stats.experiment_count);

    return line.str();
}

void write_no_replanning_batch_aggregate_csv(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path
) {
    std::map<BatchAggregateKey, BatchAggregateStats> grouped_stats;

    for (const auto& result : batch_result.results) {
        BatchAggregateKey key = build_key(result);

        add_result_to_stats(grouped_stats[key], result);
    }

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path, std::ios::trunc);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch aggregate CSV file: " +
            output_path
        );
    }

    file << build_header_line() << "\n";

    for (const auto& entry : grouped_stats) {
        file << build_data_line(entry.first, entry.second) << "\n";
    }
}