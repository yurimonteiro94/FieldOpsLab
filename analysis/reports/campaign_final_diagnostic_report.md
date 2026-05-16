# FieldOps Lab campaign final diagnostic report

This report consolidates the executed campaign, result summary, semantic inspection, service-delay audit, policy-trigger audit, and campaign decision matrix.

## Overall status

| Field | Value |
| --- | --- |
| decision_row_count | 12 |
| family_count | 4 |
| severity_count | 3 |
| replan_candidate_count | 6 |
| keep_current_plan_candidate_count | 2 |
| service_modeling_review_count | 4 |
| low_evidence_count | 6 |
| medium_evidence_count | 6 |
| semantic_problem_count | 0 |
| service_warning_count | 4 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | final_diagnostic_report_only |
| general_project_completeness_estimate_percent | 30 |
| campaign_pipeline_completeness_estimate_percent | 90 |

## Source files

| Label | Path | Size bytes |
| --- | --- | ---: |
| campaign_execution_index | `analysis\reports\campaign_execution_index.json` | 51404 |
| campaign_result_summary | `analysis\reports\campaign_result_summary.json` | 19677 |
| campaign_result_semantic_inspection | `analysis\reports\campaign_result_semantic_inspection.json` | 34722 |
| service_delay_impact_audit | `analysis\reports\service_delay_impact_audit.json` | 16040 |
| policy_trigger_behavior_audit | `analysis\reports\policy_trigger_behavior_audit.json` | 32583 |
| campaign_decision_matrix | `analysis\reports\campaign_decision_matrix.json` | 17591 |

## Provisional action counts

| Action | Count |
| --- | ---: |
| keep_current_plan_candidate | 2 |
| replan_candidate_with_makespan_monitoring | 6 |
| review_service_delay_modeling_before_concluding | 4 |

## Scientific use status

| Status | Count |
| --- | ---: |
| diagnostic_only_low_evidence | 2 |
| diagnostic_only_requires_modeling_review | 4 |
| preliminary_pattern_candidate | 6 |

## Final diagnostic table

| Batch | Family | Severity | Action | Evidence | Scientific use | Trigger | Service class | Caution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| campaign_combined_delay_light_batch | combined_delay | light | review_service_delay_modeling_before_concluding | low | diagnostic_only_requires_modeling_review | expected_no_trigger | visible_but_neutral_and_kept_plan | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | visible_with_metric_effect | replanning improves objective but increases makespan |
| campaign_combined_delay_severe_batch | combined_delay | severe | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | visible_with_metric_effect | replanning improves objective but increases makespan |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | keep_current_plan_candidate | low | diagnostic_only_low_evidence | expected_no_trigger | not_service_related | weak or tied recommendation |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | not_service_related | replanning improves objective but increases makespan |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | not_service_related | replanning improves objective but increases makespan |
| campaign_service_delay_only_light_batch | service_delay_only | light | review_service_delay_modeling_before_concluding | low | diagnostic_only_requires_modeling_review | expected_no_trigger | visible_but_neutral_and_kept_plan | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | review_service_delay_modeling_before_concluding | low | diagnostic_only_requires_modeling_review | triggered_and_applied | visible_but_neutral_and_kept_plan | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | review_service_delay_modeling_before_concluding | low | diagnostic_only_requires_modeling_review | triggered_and_applied | visible_but_neutral_and_kept_plan | service delay visible but weak under current objective/makespan; weak or tied recommendation |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | keep_current_plan_candidate | low | diagnostic_only_low_evidence | expected_no_trigger | not_service_related | weak or tied recommendation |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | not_service_related | replanning improves objective but increases makespan |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | replan_candidate_with_makespan_monitoring | medium | preliminary_pattern_candidate | triggered_and_applied | not_service_related | replanning improves objective but increases makespan |

## What this report supports

- It supports a demonstrable campaign-level diagnostic pipeline.
- It supports preliminary pattern identification by scenario family and severity.
- It supports identifying weak points in the current model, especially service-delay effects and objective-only ranking.

## What this report does not support yet

- It does not prove a final research conclusion.
- It does not validate the method statistically.
- It does not replace broader instances, richer policies, better ranking criteria, or real-company validation.

## Recommended next implementation priorities

1. Integrate this final diagnostic report into the full campaign pipeline.
2. Replace objective-only ranking with an operational ranking profile.
3. Add at least one stronger replanning policy or method for comparison.
4. Add larger or more varied instances before making scientific claims.
5. Add statistical analysis after enough independent results exist.

## Conservative interpretation

The current project has a working end-to-end experimental campaign pipeline. It is strong as an engineering milestone and still preliminary as scientific evidence.
