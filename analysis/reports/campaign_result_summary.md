# FieldOps Lab campaign result summary

This report consolidates recommendations from the executed campaign batches.

## Overview

| Field | Value |
| --- | --- |
| batch_count | 12 |
| recommendation_count | 12 |
| total_completed_experiment_count | 108 |
| clear_winner_count | 6 |
| weak_or_tied_count | 6 |
| tradeoff_count | 6 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | campaign_result_consolidation_only |

## Recommendation classes

| Class | Count |
| --- | ---: |
| replanning_tradeoff | 6 |
| weak_or_tied | 6 |

## Recommended policies

| Policy | Count |
| --- | ---: |
| no_replanning_policy_v1 | 6 |
| threshold_delay_replanning_policy_v1 | 6 |

## Recommendations by batch

| Batch | Family | Severity | Recommendation class | Policy | Method | Clear winner | Delta objective | Delta makespan | Delta travel |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| campaign_combined_delay_light_batch | combined_delay | light | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 10 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 38 | -17 |
| campaign_combined_delay_severe_batch | combined_delay | severe | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 66 | -17 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 10 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 3 | -17 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 3 | -17 |
| campaign_service_delay_only_light_batch | service_delay_only | light | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | weak_or_tied | no_replanning_policy_v1 | replanning_not_implemented_v1 | no | 0 | 0 | 10 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 3 | -17 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | replanning_tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | yes | -52 | 3 | -17 |

## Conservative interpretation

This report is useful because it finally summarizes the whole executable campaign, not only one handcrafted sample batch.

However, this is still not a final scientific conclusion. The current campaign is still template-based, uses a small base instance, and depends on preliminary ranking criteria. The next step is to inspect whether the recommendations are meaningful by family and severity.
