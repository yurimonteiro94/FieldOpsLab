#include "core/experiment/no_replanning_batch_result_validator/no_replanning_batch_result_validator.h"

#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>

static void throw_validation_error(const std::string& message) {
    throw std::runtime_error(
        "Invalid no-replanning batch result: " + message
    );
}

static bool almost_equal(double first, double second) {
    return std::fabs(first - second) < 0.000001;
}

static double expected_completion_percent(
    int completed_experiment_count,
    int configured_experiment_count
) {
    if (configured_experiment_count <= 0) {
        return 100.0;
    }

    return
        100.0 *
        static_cast<double>(completed_experiment_count) /
        static_cast<double>(configured_experiment_count);
}

static void validate_non_negative_counts(
    const NoReplanningBatchExperimentResult& batch_result
) {
    if (batch_result.configured_experiment_count < 0) {
        throw_validation_error(
            "configured_experiment_count cannot be negative."
        );
    }

    if (batch_result.completed_experiment_count < 0) {
        throw_validation_error(
            "completed_experiment_count cannot be negative."
        );
    }

    if (batch_result.experiment_count() < 0) {
        throw_validation_error(
            "experiment_count cannot be negative."
        );
    }
}

static void validate_completion_counts(
    const NoReplanningBatchExperimentResult& batch_result
) {
    if (batch_result.completed_experiment_count !=
        batch_result.experiment_count()) {
        std::ostringstream message;

        message
            << "completed_experiment_count must match experiment_count. "
            << "completed_experiment_count="
            << batch_result.completed_experiment_count
            << ", experiment_count="
            << batch_result.experiment_count()
            << ".";

        throw_validation_error(message.str());
    }

    if (batch_result.completed_experiment_count >
        batch_result.configured_experiment_count) {
        std::ostringstream message;

        message
            << "completed_experiment_count cannot be greater than "
            << "configured_experiment_count. completed_experiment_count="
            << batch_result.completed_experiment_count
            << ", configured_experiment_count="
            << batch_result.configured_experiment_count
            << ".";

        throw_validation_error(message.str());
    }
}

static void validate_completion_percent(
    const NoReplanningBatchExperimentResult& batch_result
) {
    double expected_percent =
        expected_completion_percent(
            batch_result.completed_experiment_count,
            batch_result.configured_experiment_count
        );

    if (!almost_equal(batch_result.completion_percent, expected_percent)) {
        std::ostringstream message;

        message
            << "completion_percent is inconsistent. completion_percent="
            << batch_result.completion_percent
            << ", expected="
            << expected_percent
            << ".";

        throw_validation_error(message.str());
    }
}

static void validate_is_complete(
    const NoReplanningBatchExperimentResult& batch_result
) {
    bool expected_is_complete =
        batch_result.completed_experiment_count >=
        batch_result.configured_experiment_count;

    if (batch_result.is_complete != expected_is_complete) {
        std::ostringstream message;

        message
            << "is_complete is inconsistent. is_complete="
            << batch_result.is_complete
            << ", expected="
            << expected_is_complete
            << ".";

        throw_validation_error(message.str());
    }
}

static void validate_written_output_path(
    bool was_written,
    const std::string& output_path,
    const std::string& output_name
) {
    if (was_written && output_path.empty()) {
        throw_validation_error(
            output_name + " was marked as written, but its output path is empty."
        );
    }
}

static void validate_output_flags(
    const NoReplanningBatchExperimentResult& batch_result
) {
    validate_written_output_path(
        batch_result.overview_csv_was_written,
        batch_result.overview_csv_output_path,
        "overview_csv"
    );

    validate_written_output_path(
        batch_result.summary_csv_was_written,
        batch_result.summary_csv_output_path,
        "summary_csv"
    );

    validate_written_output_path(
        batch_result.aggregate_csv_was_written,
        batch_result.aggregate_csv_output_path,
        "aggregate_csv"
    );

    validate_written_output_path(
        batch_result.ranking_csv_was_written,
        batch_result.ranking_csv_output_path,
        "ranking_csv"
    );

    validate_written_output_path(
        batch_result.recommendation_csv_was_written,
        batch_result.recommendation_csv_output_path,
        "recommendation_csv"
    );

    validate_written_output_path(
        batch_result.result_json_was_written,
        batch_result.result_json_output_path,
        "result_json"
    );
}

void validate_no_replanning_batch_result(
    const NoReplanningBatchExperimentResult& batch_result
) {
    validate_non_negative_counts(batch_result);
    validate_completion_counts(batch_result);
    validate_completion_percent(batch_result);
    validate_is_complete(batch_result);
    validate_output_flags(batch_result);
}