# FieldOps Lab policy trigger behavior audit

This report checks whether each policy option actually requests replanning under each campaign scenario.

## Overview

| Field | Value |
| --- | --- |
| row_count | 36 |
| threshold_row_count | 24 |
| triggered_threshold_row_count | 16 |
| service_delay_not_triggering_threshold_count | 0 |
| warning_count | 0 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | policy_trigger_behavior_diagnostic_only |

## Trigger behavior by option

| Batch | Family | Severity | Option | Experiments | Should replan | Requests | Applied | Travel delta | Service delta | Trigger class | Warnings |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| campaign_combined_delay_light_batch | combined_delay | light | no_replanning_baseline | 3 | 0 | 0 | 0 | 10 | 7 | baseline_policy | 0 |
| campaign_combined_delay_light_batch | combined_delay | light | threshold_with_greedy_replanning | 3 | 0 | 0 | 0 | 10 | 7 | expected_no_trigger | 0 |
| campaign_combined_delay_light_batch | combined_delay | light | threshold_without_solver | 3 | 0 | 0 | 0 | 10 | 7 | expected_no_trigger | 0 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | no_replanning_baseline | 3 | 0 | 0 | 0 | 50 | 35 | baseline_policy | 0 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 35 | triggered_and_applied | 0 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | threshold_without_solver | 3 | 3 | 3 | 0 | 50 | 35 | triggered_without_solver | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | no_replanning_baseline | 3 | 0 | 0 | 0 | 90 | 63 | baseline_policy | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 63 | triggered_and_applied | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | threshold_without_solver | 3 | 3 | 3 | 0 | 90 | 63 | triggered_without_solver | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | no_replanning_baseline | 3 | 0 | 0 | 0 | 10 | 0 | baseline_policy | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | threshold_with_greedy_replanning | 3 | 0 | 0 | 0 | 10 | 0 | expected_no_trigger | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | threshold_without_solver | 3 | 0 | 0 | 0 | 10 | 0 | expected_no_trigger | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | no_replanning_baseline | 3 | 0 | 0 | 0 | 50 | 0 | baseline_policy | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 0 | triggered_and_applied | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | threshold_without_solver | 3 | 3 | 3 | 0 | 50 | 0 | triggered_without_solver | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | no_replanning_baseline | 3 | 0 | 0 | 0 | 90 | 0 | baseline_policy | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 0 | triggered_and_applied | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | threshold_without_solver | 3 | 3 | 3 | 0 | 90 | 0 | triggered_without_solver | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | no_replanning_baseline | 3 | 0 | 0 | 0 | 0 | 7 | baseline_policy | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | threshold_with_greedy_replanning | 3 | 0 | 0 | 0 | 0 | 7 | expected_no_trigger | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | threshold_without_solver | 3 | 0 | 0 | 0 | 0 | 7 | expected_no_trigger | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | no_replanning_baseline | 3 | 0 | 0 | 0 | 0 | 35 | baseline_policy | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | 0 | 35 | triggered_and_applied | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | threshold_without_solver | 3 | 3 | 3 | 0 | 0 | 35 | triggered_without_solver | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | no_replanning_baseline | 3 | 0 | 0 | 0 | 0 | 63 | baseline_policy | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | 0 | 63 | triggered_and_applied | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | threshold_without_solver | 3 | 3 | 3 | 0 | 0 | 63 | triggered_without_solver | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | no_replanning_baseline | 3 | 0 | 0 | 0 | 10 | 0 | baseline_policy | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | threshold_with_greedy_replanning | 3 | 0 | 0 | 0 | 10 | 0 | expected_no_trigger | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | threshold_without_solver | 3 | 0 | 0 | 0 | 10 | 0 | expected_no_trigger | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | no_replanning_baseline | 3 | 0 | 0 | 0 | 50 | 0 | baseline_policy | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 0 | triggered_and_applied | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | threshold_without_solver | 3 | 3 | 3 | 0 | 50 | 0 | triggered_without_solver | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | no_replanning_baseline | 3 | 0 | 0 | 0 | 90 | 0 | baseline_policy | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | threshold_with_greedy_replanning | 3 | 3 | 3 | 3 | -17 | 0 | triggered_and_applied | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | threshold_without_solver | 3 | 3 | 3 | 0 | 90 | 0 | triggered_without_solver | 0 |

## Warnings

- None.

## Conservative interpretation

This audit classifies trigger behavior using policy decisions, replanning requests, and applied replanning counts. It does not infer triggering from post-replanning metric deltas.

Metric deltas are still shown for context, but a negative travel delta after greedy replanning must not be interpreted as absence of an original travel delay.
