# FieldOps Lab campaign ranking profile sensitivity

This report recalculates campaign recommendations using alternative ranking profiles.

## Overview

| Field | Value |
| --- | --- |
| result_file_count | 12 |
| ranking_profile_count | 4 |
| ranking_row_count | 144 |
| recommendation_count | 48 |
| scenario_summary_count | 12 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | ranking_profile_sensitivity_diagnostic_only |

## Ranking profiles

| Profile | Description |
| --- | --- |
| objective_only | Uses only objective delta. This matches the current preliminary ranking. |
| balanced_operational | Balances objective, makespan, travel time, lateness, and replanning effort. |
| makespan_priority | Penalizes makespan strongly and is useful when finishing later is operationally expensive. |
| conservative_replanning | Penalizes replanning effort and favors stability unless benefits are clear. |

## Stability counts

| Stability class | Count |
| --- | ---: |
| same_policy_different_class | 2 |
| stable_across_profiles | 10 |

## Recommended policies

| Policy | Count |
| --- | ---: |
| no_replanning_policy_v1 | 24 |
| threshold_delay_replanning_policy_v1 | 24 |

## Scenario sensitivity summary

| Batch | Family | Severity | Stability | Unique policies | Profile recommendations |
| --- | --- | --- | --- | ---: | --- |
| campaign_combined_delay_light_batch | combined_delay | light | stable_across_profiles | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |
| campaign_combined_delay_severe_batch | combined_delay | severe | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | stable_across_profiles | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |
| campaign_service_delay_only_light_batch | reassignment_opportunity | light | stable_across_profiles | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_service_delay_only_moderate_batch | reassignment_opportunity | moderate | same_policy_different_class | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_service_delay_only_severe_batch | reassignment_opportunity | severe | same_policy_different_class | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_travel_delay_only_light_batch | reassignment_opportunity | light | stable_across_profiles | 1 | balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1 |
| campaign_travel_delay_only_moderate_batch | reassignment_opportunity | moderate | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |
| campaign_travel_delay_only_severe_batch | reassignment_opportunity | severe | stable_across_profiles | 1 | balanced_operational=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; conservative_replanning=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; makespan_priority=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1; objective_only=threshold_delay_replanning_policy_v1+greedy_replanning_solver_v1 |

## Conservative interpretation

If a scenario is stable across profiles, the current recommendation is less sensitive to the ranking formula.

If a scenario is sensitive to ranking profile, it should not be used as a final policy conclusion until ranking criteria are justified and tested on broader instances.
