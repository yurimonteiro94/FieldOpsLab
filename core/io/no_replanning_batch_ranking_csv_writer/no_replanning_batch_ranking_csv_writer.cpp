#include "core/io/no_replanning_batch_ranking_csv_writer/no_replanning_batch_ranking_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/analysis/batch_ranking/batch_ranking.h"

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
        build_batch_ranking_rows(batch_result);

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