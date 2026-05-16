# FieldOps Lab service delay impact audit

This report audits whether service-delay scenarios visibly affect the executed campaign metrics and final recommendations.

## Overview

| Field | Value |
| --- | --- |
| batch_count | 12 |
| service_related_batch_count | 6 |
| service_only_batch_count | 3 |
| combined_delay_batch_count | 3 |
| visible_but_neutral_and_kept_plan_count | 4 |
| warning_count | 4 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | service_delay_impact_diagnostic_only |

## Batch diagnostics

| Batch | Family | Severity | Recommended policy | Clear winner | Baseline service | Baseline objective | Baseline makespan | Greedy service | Greedy objective | Greedy makespan | Service effect class | Warnings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| campaign_combined_delay_light_batch | combined_delay | light | no_replanning_policy_v1 | no | 7 | 0 | 0 | 7 | 0 | 0 | visible_but_neutral_and_kept_plan | 1 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | threshold_delay_replanning_policy_v1 | yes | 35 | 15 | 15 | 35 | -52 | 38 | visible_with_metric_effect | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | threshold_delay_replanning_policy_v1 | yes | 63 | 55 | 55 | 63 | -52 | 66 | visible_with_metric_effect | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | no_replanning_policy_v1 | no | 0 | 0 | 0 | 0 | 0 | 0 | not_service_related | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | threshold_delay_replanning_policy_v1 | yes | 0 | 15 | 15 | 0 | -52 | 3 | not_service_related | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | threshold_delay_replanning_policy_v1 | yes | 0 | 55 | 55 | 0 | -52 | 3 | not_service_related | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | no_replanning_policy_v1 | no | 7 | 0 | 0 | 7 | 0 | 0 | visible_but_neutral_and_kept_plan | 1 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | no_replanning_policy_v1 | no | 35 | 0 | 0 | 35 | 0 | 0 | visible_but_neutral_and_kept_plan | 1 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | no_replanning_policy_v1 | no | 63 | 0 | 0 | 63 | 0 | 0 | visible_but_neutral_and_kept_plan | 1 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | no_replanning_policy_v1 | no | 0 | 0 | 0 | 0 | 0 | 0 | not_service_related | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | threshold_delay_replanning_policy_v1 | yes | 0 | 15 | 15 | 0 | -52 | 3 | not_service_related | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | threshold_delay_replanning_policy_v1 | yes | 0 | 55 | 55 | 0 | -52 | 3 | not_service_related | 0 |

## Warnings

- campaign_combined_delay_light_batch: Service delay is visible in service time, but neutral in objective, makespan, and lateness under current metrics.
- campaign_service_delay_only_light_batch: Service delay is visible in service time, but neutral in objective, makespan, and lateness under current metrics.
- campaign_service_delay_only_moderate_batch: Service delay is visible in service time, but neutral in objective, makespan, and lateness under current metrics.
- campaign_service_delay_only_severe_batch: Service delay is visible in service time, but neutral in objective, makespan, and lateness under current metrics.

## Conservative interpretation

This audit does not prove that the service-delay model is wrong. It checks whether service delays are visible in the current metrics and whether the current ranking reacts to them.

If service delays increase service time but do not affect objective, makespan, lateness, or recommendations, then the next modeling question is whether the objective function should penalize service-time disruptions or whether the current behavior is operationally acceptable.
