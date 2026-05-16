#include "core/io/no_replanning_batch_recommendation_csv_writer/no_replanning_batch_recommendation_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/analysis/batch_recommendation/batch_recommendation.h"

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

static std::string build_header_line() {
    return
        "scenario_id,"
        "recommended_policy_id,"
        "recommended_replanning_method_id,"
        "recommended_execution_mode,"
        "recommended_rank,"
        "experiment_count,"
        "policy_should_replan_count,"
        "replanning_request_count,"
        "replanning_success_count,"
        "replanning_applied_count,"
        "best_score,"
        "second_best_score,"
        "score_margin_to_second,"
        "has_second_option,"
        "has_clear_winner,"
        "mean_delta_objective_value,"
        "mean_delta_makespan,"
        "mean_delta_total_travel_time,"
        "mean_delta_total_service_time,"
        "mean_delta_total_waiting_time,"
        "mean_late_task_count,"
        "mean_total_lateness,"
        "mean_effect_count,"
        "recommendation_reason";
}

static std::string build_data_line(
    const BatchScenarioRecommendation& recommendation
) {
    std::ostringstream line;

    line << csv_escape(recommendation.scenario_id) << ","
         << csv_escape(recommendation.recommended_policy_id) << ","
         << csv_escape(recommendation.recommended_replanning_method_id) << ","
         << csv_escape(recommendation.recommended_execution_mode) << ","
         << recommendation.recommended_rank << ","
         << recommendation.experiment_count << ","
         << recommendation.policy_should_replan_count << ","
         << recommendation.replanning_request_count << ","
         << recommendation.replanning_success_count << ","
         << recommendation.replanning_applied_count << ","
         << recommendation.best_score << ","
         << recommendation.second_best_score << ","
         << recommendation.score_margin_to_second << ","
         << bool_to_csv(recommendation.has_second_option) << ","
         << bool_to_csv(recommendation.has_clear_winner) << ","
         << recommendation.mean_delta_objective_value << ","
         << recommendation.mean_delta_makespan << ","
         << recommendation.mean_delta_total_travel_time << ","
         << recommendation.mean_delta_total_service_time << ","
         << recommendation.mean_delta_total_waiting_time << ","
         << recommendation.mean_late_task_count << ","
         << recommendation.mean_total_lateness << ","
         << recommendation.mean_effect_count << ","
         << csv_escape(recommendation.recommendation_reason);

    return line.str();
}

void write_no_replanning_batch_recommendation_csv(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path
) {
    std::vector<BatchScenarioRecommendation> recommendations =
        build_batch_scenario_recommendations(batch_result);

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path, std::ios::trunc);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch recommendation CSV file: " +
            output_path
        );
    }

    file << build_header_line() << "\n";

    for (const auto& recommendation : recommendations) {
        file << build_data_line(recommendation) << "\n";
    }
}