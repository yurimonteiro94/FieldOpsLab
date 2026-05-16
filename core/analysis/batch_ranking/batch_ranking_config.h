#pragma once

#include <string>

struct BatchRankingConfig {
    std::string ranking_config_id = "default_objective_delta_ranking_v1";

    double objective_value_weight = 1.0;
    double makespan_weight = 0.0;
    double total_travel_time_weight = 0.0;
    double total_service_time_weight = 0.0;
    double total_waiting_time_weight = 0.0;

    double late_task_count_weight = 0.0;
    double total_lateness_weight = 0.0;
    double effect_count_weight = 0.0;

    double policy_should_replan_count_weight = 0.0;
    double replanning_request_count_weight = 0.0;
    double replanning_success_count_weight = 0.0;
    double replanning_applied_count_weight = 0.0;
};