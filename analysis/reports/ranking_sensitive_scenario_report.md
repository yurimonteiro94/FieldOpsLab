# FieldOps Lab ranking-sensitive scenario report

This report identifies scenarios where the recommendation changes under different ranking profiles.

A change can mean a different recommended policy, or the same policy with a different recommendation class.

This is a diagnostic report. It does not prove statistical validity.

## Input status

| Field | Value |
| --- | --- |
| all_required_inputs_available | yes |
| source_path | analysis\reports\campaign_ranking_profile_sensitivity.json |
| source_exists | yes |
| source_report_type | fieldops_lab_campaign_ranking_profile_sensitivity |
| source_scenario_summary_count | 12 |
| source_ranking_row_count | 144 |
| source_ranking_profile_count | 4 |
| source_has_summary_rows | yes |
| source_has_ranking_rows | yes |

## Overall result

| Field | Value |
| --- | --- |
| scenario_summary_count | 12 |
| ranking_row_count | 144 |
| ranking_profile_count | 4 |
| sensitive_scenario_count | 2 |
| policy_change_sensitive_scenario_count | 0 |
| class_change_sensitive_scenario_count | 2 |
| stable_scenario_count | 10 |
| ranking_fragility_status | some_scenarios_sensitive_to_ranking_profile |

## Sensitive scenarios

| Batch | Family | Severity | Ranking profiles | Reason | Recommended policies | Recommendation classes | Investigation status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | 4 | same_policy_but_recommendation_class_changes_across_profiles | no_replanning_policy_v1 | keep_plan_candidate; weak_or_tied | requires_recommendation_class_explanation |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | 4 | same_policy_but_recommendation_class_changes_across_profiles | no_replanning_policy_v1 | keep_plan_candidate; weak_or_tied | requires_recommendation_class_explanation |

## Required investigation

### `campaign_service_delay_only_moderate_batch`

- Scenario family: `service_delay_only`
- Severity: `moderate`
- Sensitive to ranking profile: `yes`
- Sensitivity reason: `same_policy_but_recommendation_class_changes_across_profiles`
- Recommended policies: `no_replanning_policy_v1`
- Recommendation classes: `keep_plan_candidate; weak_or_tied`
- Investigation status: `requires_recommendation_class_explanation`
- Interpretation: The recommended policy remains the same, but the recommendation class changes under different ranking profiles. This means the policy choice looks stable, but the strength or quality of the recommendation is fragile.
- Profile-policy pairs: `balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1`

### `campaign_service_delay_only_severe_batch`

- Scenario family: `service_delay_only`
- Severity: `severe`
- Sensitive to ranking profile: `yes`
- Sensitivity reason: `same_policy_but_recommendation_class_changes_across_profiles`
- Recommended policies: `no_replanning_policy_v1`
- Recommendation classes: `keep_plan_candidate; weak_or_tied`
- Investigation status: `requires_recommendation_class_explanation`
- Interpretation: The recommended policy remains the same, but the recommendation class changes under different ranking profiles. This means the policy choice looks stable, but the strength or quality of the recommendation is fragile.
- Profile-policy pairs: `balanced_operational=no_replanning_policy_v1+replanning_not_implemented_v1; conservative_replanning=no_replanning_policy_v1+replanning_not_implemented_v1; makespan_priority=no_replanning_policy_v1+replanning_not_implemented_v1; objective_only=no_replanning_policy_v1+replanning_not_implemented_v1`

## Conservative interpretation

Scenarios listed here are fragile recommendations. They need metric-level explanation before being used as scientific evidence.

The next step is to explain which objective components, recommendation classes, and ranking weights caused each sensitivity signal.
