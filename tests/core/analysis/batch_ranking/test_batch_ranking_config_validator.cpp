#include "core/analysis/batch_ranking/batch_ranking_config.h"
#include "core/analysis/batch_ranking/batch_ranking_config_validator/batch_ranking_config_validator.h"
#include "tests/test_support/test_assertions.h"

#include <limits>
#include <stdexcept>

static BatchRankingConfig build_valid_test_ranking_config() {
    BatchRankingConfig config;

    config.ranking_config_id = "test_ranking_config";
    config.objective_value_weight = 1.0;

    return config;
}

static bool validation_throws(const BatchRankingConfig& config) {
    try {
        validate_batch_ranking_config(config);
        return false;
    } catch (const std::runtime_error&) {
        return true;
    }
}

void test_batch_ranking_config_validator() {
    BatchRankingConfig valid_config =
        build_valid_test_ranking_config();

    validate_batch_ranking_config(valid_config);

    BatchRankingConfig empty_id_config = valid_config;
    empty_id_config.ranking_config_id = "";

    FIELDOPS_EXPECT_TRUE(validation_throws(empty_id_config));

    BatchRankingConfig all_zero_config = valid_config;
    all_zero_config.objective_value_weight = 0.0;
    all_zero_config.makespan_weight = 0.0;
    all_zero_config.total_travel_time_weight = 0.0;
    all_zero_config.total_service_time_weight = 0.0;
    all_zero_config.total_waiting_time_weight = 0.0;
    all_zero_config.late_task_count_weight = 0.0;
    all_zero_config.total_lateness_weight = 0.0;
    all_zero_config.effect_count_weight = 0.0;
    all_zero_config.policy_should_replan_count_weight = 0.0;
    all_zero_config.replanning_request_count_weight = 0.0;
    all_zero_config.replanning_success_count_weight = 0.0;
    all_zero_config.replanning_applied_count_weight = 0.0;

    FIELDOPS_EXPECT_TRUE(validation_throws(all_zero_config));

    BatchRankingConfig infinite_weight_config = valid_config;
    infinite_weight_config.objective_value_weight =
        std::numeric_limits<double>::infinity();

    FIELDOPS_EXPECT_TRUE(validation_throws(infinite_weight_config));

    BatchRankingConfig nan_weight_config = valid_config;
    nan_weight_config.objective_value_weight =
        std::numeric_limits<double>::quiet_NaN();

    FIELDOPS_EXPECT_TRUE(validation_throws(nan_weight_config));

    BatchRankingConfig negative_weight_config = valid_config;
    negative_weight_config.objective_value_weight = 0.0;
    negative_weight_config.total_travel_time_weight = -1.0;

    validate_batch_ranking_config(negative_weight_config);
}