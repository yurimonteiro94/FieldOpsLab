#include "core/io/no_replanning_batch_overview_csv_writer/no_replanning_batch_overview_csv_writer.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

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

static std::string bool_to_text(bool value) {
    if (value) {
        return "true";
    }

    return "false";
}

static std::string build_header_line() {
    return
        "batch_id,"
        "name,"
        "description,"
        "configured_experiment_count,"
        "completed_experiment_count,"
        "completion_percent,"
        "is_complete,"
        "experiment_count,"
        "summary_csv_was_written,"
        "aggregate_csv_was_written,"
        "ranking_csv_was_written,"
        "recommendation_csv_was_written,"
        "result_json_was_written";
}

static std::string build_data_line(
    const NoReplanningBatchExperimentResult& batch_result
) {
    std::ostringstream line;

    line << csv_escape(batch_result.batch_id) << ","
         << csv_escape(batch_result.name) << ","
         << csv_escape(batch_result.description) << ","
         << batch_result.configured_experiment_count << ","
         << batch_result.completed_experiment_count << ","
         << batch_result.completion_percent << ","
         << bool_to_text(batch_result.is_complete) << ","
         << batch_result.experiment_count() << ","
         << bool_to_text(batch_result.summary_csv_was_written) << ","
         << bool_to_text(batch_result.aggregate_csv_was_written) << ","
         << bool_to_text(batch_result.ranking_csv_was_written) << ","
         << bool_to_text(batch_result.recommendation_csv_was_written) << ","
         << bool_to_text(batch_result.result_json_was_written);

    return line.str();
}

void write_no_replanning_batch_overview_csv(
    const NoReplanningBatchExperimentResult& batch_result,
    const std::string& output_path
) {
    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path, std::ios::trunc);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch overview CSV file: " +
            output_path
        );
    }

    file << build_header_line() << "\n";
    file << build_data_line(batch_result) << "\n";
}