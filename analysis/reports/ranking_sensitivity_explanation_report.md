# FieldOps Lab ranking sensitivity explanation report

This report explains the scenarios previously marked as sensitive to ranking profile choice.

It separates policy changes from weaker sensitivity cases where the policy stays the same but the recommendation class changes.

## Input status

| Field | Value |
| --- | --- |
| all_required_inputs_available | yes |
| sensitive_scenario_report_path | analysis\reports\ranking_sensitive_scenario_report.json |
| ranking_sensitivity_source_path | analysis\reports\campaign_ranking_profile_sensitivity.json |
| sensitive_scenario_report_exists | yes |
| ranking_sensitivity_source_exists | yes |
| sensitive_scenario_count | 2 |
| source_ranking_row_count | 144 |
| source_recommended_row_count | 48 |

## Overall result

| Field | Value |
| --- | --- |
| source_sensitive_scenario_count | 2 |
| explanation_count | 2 |
| policy_change_explanation_count | 0 |
| class_change_explanation_count | 2 |
| all_sensitive_scenarios_have_explanation | yes |
| source_ranking_row_count | 144 |
| source_recommended_row_count | 48 |

## Scenario explanations

### `campaign_service_delay_only_moderate_batch`

- Scenario family: `service_delay_only`
- Severity: `moderate`
- Sensitivity reason: `same_policy_but_recommendation_class_changes_across_profiles`
- Recommended policies: `no_replanning_policy_v1`
- Recommendation classes: `keep_plan_candidate; weak_or_tied`
- Investigation status: `requires_recommendation_class_explanation`
- Interpretation: The recommended policy remains the same, but the recommendation class changes under different ranking profiles. This means the policy choice looks stable, but the strength or quality of the recommendation is fragile.

| Profile | Policy | Class | Rank | Score | Dominant metric | Objective delta | Makespan delta | Service delta | Waiting delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| balanced_operational | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 35.0 | 0.0 |
| conservative_replanning | no_replanning_policy_v1 | keep_plan_candidate | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 35.0 | 0.0 |
| makespan_priority | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 35.0 | 0.0 |
| objective_only | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 35.0 | 0.0 |

### `campaign_service_delay_only_severe_batch`

- Scenario family: `service_delay_only`
- Severity: `severe`
- Sensitivity reason: `same_policy_but_recommendation_class_changes_across_profiles`
- Recommended policies: `no_replanning_policy_v1`
- Recommendation classes: `keep_plan_candidate; weak_or_tied`
- Investigation status: `requires_recommendation_class_explanation`
- Interpretation: The recommended policy remains the same, but the recommendation class changes under different ranking profiles. This means the policy choice looks stable, but the strength or quality of the recommendation is fragile.

| Profile | Policy | Class | Rank | Score | Dominant metric | Objective delta | Makespan delta | Service delta | Waiting delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| balanced_operational | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 63.0 | 0.0 |
| conservative_replanning | no_replanning_policy_v1 | keep_plan_candidate | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 63.0 | 0.0 |
| makespan_priority | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 63.0 | 0.0 |
| objective_only | no_replanning_policy_v1 | weak_or_tied | 1 | 0.0 | mean_delta_total_service_time | 0.0 | 0.0 | 63.0 | 0.0 |

## Conservative interpretation

This report explains why the current diagnostic campaign marks some scenarios as ranking-sensitive. It still does not prove statistical significance or scientific generalization.

The next scientific step is to use this explanation as input for broader replicated experiments and statistical comparisons.
