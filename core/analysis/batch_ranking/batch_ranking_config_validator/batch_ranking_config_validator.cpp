#include "core/analysis/batch_ranking/batch_ranking_config_validator/batch_ranking_config_validator.h"

#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>

static void throw_ranking_config_validation_error(
    const std::string& message
) {
    throw std::runtime_error(
        "Invalid batch ranking config: " + message
    );
}

static void validate_finite_weight(
    double value,
    const std::string& field_name
) {
    if (!std::isfinite(value)) {
        throw_ranking_config_validation_error(
            field_name + " must be finite."
        );
    }
}

static bool is_non_zero_weight(double value) {
    return std::fabs(value) > 0.000001;
}

static void validate_all_weights_are_finite(
    const BatchRankingConfig& ranking_config
) {
    validate_finite_weight(
        ranking_config.objective_value_weight,
        "objective_value_weight"
    );

    validate_finite_weight(
        ranking_config.makespan_weight,
        "makespan_weight"
    );

    validate_finite_weight(
        ranking_config.total_travel_time_weight,
        "total_travel_time_weight"
    );

    validate_finite_weight(
        ranking_config.total_service_time_weight,
        "total_service_time_weight"
    );

    validate_finite_weight(
        ranking_config.total_waiting_time_weight,
        "total_waiting_time_weight"
    );

    validate_finite_weight(
        ranking_config.late_task_count_weight,
        "late_task_count_weight"
    );

    validate_finite_weight(
        ranking_config.total_lateness_weight,
        "total_lateness_weight"
    );

    validate_finite_weight(
        ranking_config.effect_count_weight,
        "effect_count_weight"
    );

    validate_finite_weight(
        ranking_config.policy_should_replan_count_weight,
        "policy_should_replan_count_weight"
    );

    validate_finite_weight(
        ranking_config.replanning_request_count_weight,
        "replanning_request_count_weight"
    );

    validate_finite_weight(
        ranking_config.replanning_success_count_weight,
        "replanning_success_count_weight"
    );

    validate_finite_weight(
        ranking_config.replanning_applied_count_weight,
        "replanning_applied_count_weight"
    );
}

static bool has_at_least_one_non_zero_weight(
    const BatchRankingConfig& ranking_config
) {
    return
        is_non_zero_weight(ranking_config.objective_value_weight) ||
        is_non_zero_weight(ranking_config.makespan_weight) ||
        is_non_zero_weight(ranking_config.total_travel_time_weight) ||
        is_non_zero_weight(ranking_config.total_service_time_weight) ||
        is_non_zero_weight(ranking_config.total_waiting_time_weight) ||
        is_non_zero_weight(ranking_config.late_task_count_weight) ||
        is_non_zero_weight(ranking_config.total_lateness_weight) ||
        is_non_zero_weight(ranking_config.effect_count_weight) ||
        is_non_zero_weight(
            ranking_config.policy_should_replan_count_weight
        ) ||
        is_non_zero_weight(
            ranking_config.replanning_request_count_weight
        ) ||
        is_non_zero_weight(
            ranking_config.replanning_success_count_weight
        ) ||
        is_non_zero_weight(
            ranking_config.replanning_applied_count_weight
        );
}

void validate_batch_ranking_config(
    const BatchRankingConfig& ranking_config
) {
    if (ranking_config.ranking_config_id.empty()) {
        throw_ranking_config_validation_error(
            "ranking_config_id cannot be empty."
        );
    }

    validate_all_weights_are_finite(ranking_config);

    if (!has_at_least_one_non_zero_weight(ranking_config)) {
        throw_ranking_config_validation_error(
            "at least one ranking weight must be non-zero."
        );
    }
}