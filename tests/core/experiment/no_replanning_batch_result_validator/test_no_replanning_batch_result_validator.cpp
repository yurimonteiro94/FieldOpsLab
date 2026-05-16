#include "core/experiment/no_replanning_batch_result_validator/no_replanning_batch_result_validator.h"
#include "tests/test_support/test_assertions.h"

#include <stdexcept>

static NoReplanningBatchExperimentResult build_valid_batch_result() {
    NoReplanningBatchExperimentResult result;

    result.batch_id = "test_batch";
    result.name = "Test batch";
    result.description = "Test batch result validation.";

    result.configured_experiment_count = 1;
    result.completed_experiment_count = 1;
    result.completion_percent = 100.0;
    result.is_complete = true;

    result.results.push_back(NoReplanningExperimentResult{});

    result.overview_csv_output_path =
        "data/results/test_batch_overview.csv";
    result.summary_csv_output_path =
        "data/results/test_batch_summary.csv";
    result.aggregate_csv_output_path =
        "data/results/test_batch_aggregate.csv";
    result.ranking_csv_output_path =
        "data/results/test_batch_ranking.csv";
    result.recommendation_csv_output_path =
        "data/results/test_batch_recommendation.csv";
    result.result_json_output_path =
        "data/results/test_batch_result.json";

    result.overview_csv_was_written = true;
    result.summary_csv_was_written = true;
    result.aggregate_csv_was_written = true;
    result.ranking_csv_was_written = true;
    result.recommendation_csv_was_written = true;
    result.result_json_was_written = true;

    return result;
}

static bool validation_throws(
    const NoReplanningBatchExperimentResult& result
) {
    try {
        validate_no_replanning_batch_result(result);
        return false;
    } catch (const std::runtime_error&) {
        return true;
    }
}

void test_no_replanning_batch_result_validator() {
    NoReplanningBatchExperimentResult valid_result =
        build_valid_batch_result();

    validate_no_replanning_batch_result(valid_result);

    NoReplanningBatchExperimentResult invalid_completed_count =
        valid_result;

    invalid_completed_count.completed_experiment_count = 0;
    invalid_completed_count.completion_percent = 0.0;
    invalid_completed_count.is_complete = false;

    FIELDOPS_EXPECT_TRUE(validation_throws(invalid_completed_count));

    NoReplanningBatchExperimentResult invalid_completion_percent =
        valid_result;

    invalid_completion_percent.completion_percent = 50.0;

    FIELDOPS_EXPECT_TRUE(validation_throws(invalid_completion_percent));

    NoReplanningBatchExperimentResult invalid_is_complete =
        valid_result;

    invalid_is_complete.is_complete = false;

    FIELDOPS_EXPECT_TRUE(validation_throws(invalid_is_complete));

    NoReplanningBatchExperimentResult invalid_output_path =
        valid_result;

    invalid_output_path.result_json_output_path = "";

    FIELDOPS_EXPECT_TRUE(validation_throws(invalid_output_path));
}