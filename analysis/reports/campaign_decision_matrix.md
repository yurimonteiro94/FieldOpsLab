# FieldOps Lab campaign decision matrix

This report consolidates campaign recommendations, semantic checks, service-delay diagnostics, and policy-trigger behavior into one decision-support table.

## Overview

| Field | Value |
| --- | --- |
| matrix_row_count | 12 |
| family_count | 4 |
| low_evidence_count | 6 |
| medium_evidence_count | 6 |
| invalid_evidence_count | 0 |
| service_modeling_review_count | 4 |
| replan_candidate_count | 6 |
| keep_current_plan_candidate_count | 2 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | decision_matrix_diagnostic_only |

## Provisional actions

| Action | Count |
| --- | ---: |
| keep_current_plan_candidate | 2 |
| replan_candidate_with_makespan_monitoring | 6 |
| review_service_delay_modeling_before_concluding | 4 |

## Evidence strength

| Evidence strength | Count |
| --- | ---: |
| low | 6 |
| medium | 6 |

## Decision matrix

| Batch | Family | Severity | Recommendation | Trigger with greedy | Service class | Action | Evidence | Caution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| campaign_combined_delay_light_batch | combined_delay | light | weak_or_tied | expected_no_trigger | visible_but_neutral_and_kept_plan | review_service_delay_modeling_before_concluding | low | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | replanning_tradeoff | triggered_and_applied | visible_with_metric_effect | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |
| campaign_combined_delay_severe_batch | combined_delay | severe | replanning_tradeoff | triggered_and_applied | visible_with_metric_effect | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | weak_or_tied | expected_no_trigger | not_service_related | keep_current_plan_candidate | low | weak or tied recommendation |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | replanning_tradeoff | triggered_and_applied | not_service_related | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | replanning_tradeoff | triggered_and_applied | not_service_related | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |
| campaign_service_delay_only_light_batch | service_delay_only | light | weak_or_tied | expected_no_trigger | visible_but_neutral_and_kept_plan | review_service_delay_modeling_before_concluding | low | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | weak_or_tied | triggered_and_applied | visible_but_neutral_and_kept_plan | review_service_delay_modeling_before_concluding | low | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | weak_or_tied | triggered_and_applied | visible_but_neutral_and_kept_plan | review_service_delay_modeling_before_concluding | low | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | weak_or_tied | expected_no_trigger | not_service_related | keep_current_plan_candidate | low | weak or tied recommendation |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | replanning_tradeoff | triggered_and_applied | not_service_related | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | replanning_tradeoff | triggered_and_applied | not_service_related | replan_candidate_with_makespan_monitoring | medium | replanning improves objective but increases makespan |

## Conservative interpretation

This matrix is a diagnostic decision-support layer. It does not prove the final research method yet.

Rows marked as low evidence, weak/tied, or service-modeling review should not be used as final policy conclusions without broader instances, stronger ranking criteria, and additional validation.

Fuzzy logic remains outside the main pipeline. These descriptors could later feed fuzzy logic, statistical rules, or a deterministic decision framework, but they are not fuzzy rules here.
