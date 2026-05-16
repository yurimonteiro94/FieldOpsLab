# FieldOps Lab experiment campaign plan

This file defines a planned experimental campaign. It is not an execution result.

## Campaign design overview

| Field | Value |
| --- | --- |
| design_status | planning_only |
| replication_count_per_condition | 3 |
| scenario_family_count | 4 |
| severity_level_count | 3 |
| policy_option_count | 3 |
| ranking_profile_count | 4 |
| planned_condition_count | 12 |
| planned_run_count | 36 |
| planned_algorithm_run_count | 108 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | campaign_design_only |

## Scenario families

| Family | Travel delay | Service delay | Reassignment opportunity | Description |
| --- | --- | --- | --- | --- |
| travel_delay_only | yes | no | no | Only travel time is perturbed. |
| service_delay_only | no | yes | no | Only service time is perturbed. |
| combined_delay | yes | yes | no | Travel and service times are both perturbed. |
| reassignment_opportunity | yes | no | yes | A disruption creates a possible benefit from reassigning remaining work. |

## Severity levels

| Severity | Nominal delay minutes | Description |
| --- | ---: | --- |
| light | 10 | Small disruption. Usually useful to test whether replanning is unnecessary. |
| moderate | 50 | Medium disruption. Useful to test trade-offs between keeping the plan and replanning. |
| severe | 90 | Large disruption. Useful to test robustness, risk, and operational recovery. |

## Policy options

| Option | Policy | Method | Description |
| --- | --- | --- | --- |
| no_replanning_baseline | no_replanning_policy_v1 | replanning_not_implemented_v1 | Baseline option. The original plan is kept. |
| threshold_without_solver | threshold_delay_replanning_policy_v1 | replanning_not_implemented_v1 | Decision policy may request replanning, but no solver is applied. Useful as a control option. |
| threshold_with_greedy_replanning | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | Decision policy may request replanning and applies the current greedy replanning solver. |

## Ranking profiles to test later

| Profile | Status | Description |
| --- | --- | --- |
| objective_only | baseline_only | Preliminary ranking. Optimizes objective delta only. |
| balanced_operational | recommended_for_sensitivity_analysis | Balances objective, makespan, travel time, lateness, and replanning effort. |
| makespan_priority | recommended_for_sensitivity_analysis | Prioritizes finishing earlier and penalizes makespan strongly. |
| conservative_replanning | recommended_for_sensitivity_analysis | Penalizes unnecessary replanning and favors operational stability. |

## Expected descriptor distribution

| Descriptor | Planned run count |
| --- | ---: |
| high_impact_controlled_tradeoff | 3 |
| high_impact_delay | 6 |
| moderate_tradeoff | 9 |
| reassignment_opportunity | 6 |
| stable_low_disruption | 12 |

## Planned runs

| Planned run | Family | Severity | Replication | Travel delay | Service delay | Descriptor | Conservative action |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| planned_travel_delay_only_light_rep001 | travel_delay_only | light | 1 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_travel_delay_only_light_rep002 | travel_delay_only | light | 2 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_travel_delay_only_light_rep003 | travel_delay_only | light | 3 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_travel_delay_only_moderate_rep001 | travel_delay_only | moderate | 1 | 50 | 0 | moderate_tradeoff | compare_policies_before_recommending |
| planned_travel_delay_only_moderate_rep002 | travel_delay_only | moderate | 2 | 50 | 0 | moderate_tradeoff | compare_policies_before_recommending |
| planned_travel_delay_only_moderate_rep003 | travel_delay_only | moderate | 3 | 50 | 0 | moderate_tradeoff | compare_policies_before_recommending |
| planned_travel_delay_only_severe_rep001 | travel_delay_only | severe | 1 | 90 | 0 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_travel_delay_only_severe_rep002 | travel_delay_only | severe | 2 | 90 | 0 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_travel_delay_only_severe_rep003 | travel_delay_only | severe | 3 | 90 | 0 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_service_delay_only_light_rep001 | service_delay_only | light | 1 | 0 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_service_delay_only_light_rep002 | service_delay_only | light | 2 | 0 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_service_delay_only_light_rep003 | service_delay_only | light | 3 | 0 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_service_delay_only_moderate_rep001 | service_delay_only | moderate | 1 | 0 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_service_delay_only_moderate_rep002 | service_delay_only | moderate | 2 | 0 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_service_delay_only_moderate_rep003 | service_delay_only | moderate | 3 | 0 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_service_delay_only_severe_rep001 | service_delay_only | severe | 1 | 0 | 63 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_service_delay_only_severe_rep002 | service_delay_only | severe | 2 | 0 | 63 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_service_delay_only_severe_rep003 | service_delay_only | severe | 3 | 0 | 63 | high_impact_delay | compare_policies_with_risk_monitoring |
| planned_combined_delay_light_rep001 | combined_delay | light | 1 | 10 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_combined_delay_light_rep002 | combined_delay | light | 2 | 10 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_combined_delay_light_rep003 | combined_delay | light | 3 | 10 | 7 | stable_low_disruption | keep_current_plan_or_validate |
| planned_combined_delay_moderate_rep001 | combined_delay | moderate | 1 | 50 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_combined_delay_moderate_rep002 | combined_delay | moderate | 2 | 50 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_combined_delay_moderate_rep003 | combined_delay | moderate | 3 | 50 | 35 | moderate_tradeoff | compare_policies_before_recommending |
| planned_combined_delay_severe_rep001 | combined_delay | severe | 1 | 90 | 63 | high_impact_controlled_tradeoff | compare_policies_with_risk_monitoring |
| planned_combined_delay_severe_rep002 | combined_delay | severe | 2 | 90 | 63 | high_impact_controlled_tradeoff | compare_policies_with_risk_monitoring |
| planned_combined_delay_severe_rep003 | combined_delay | severe | 3 | 90 | 63 | high_impact_controlled_tradeoff | compare_policies_with_risk_monitoring |
| planned_reassignment_opportunity_light_rep001 | reassignment_opportunity | light | 1 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_reassignment_opportunity_light_rep002 | reassignment_opportunity | light | 2 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_reassignment_opportunity_light_rep003 | reassignment_opportunity | light | 3 | 10 | 0 | stable_low_disruption | keep_current_plan_or_validate |
| planned_reassignment_opportunity_moderate_rep001 | reassignment_opportunity | moderate | 1 | 50 | 0 | reassignment_opportunity | test_replanning_opportunity |
| planned_reassignment_opportunity_moderate_rep002 | reassignment_opportunity | moderate | 2 | 50 | 0 | reassignment_opportunity | test_replanning_opportunity |
| planned_reassignment_opportunity_moderate_rep003 | reassignment_opportunity | moderate | 3 | 50 | 0 | reassignment_opportunity | test_replanning_opportunity |
| planned_reassignment_opportunity_severe_rep001 | reassignment_opportunity | severe | 1 | 90 | 0 | reassignment_opportunity | test_replanning_opportunity |
| planned_reassignment_opportunity_severe_rep002 | reassignment_opportunity | severe | 2 | 90 | 0 | reassignment_opportunity | test_replanning_opportunity |
| planned_reassignment_opportunity_severe_rep003 | reassignment_opportunity | severe | 3 | 90 | 0 | reassignment_opportunity | test_replanning_opportunity |

## Conservative interpretation

This plan is a bridge between the current handcrafted validation batch and a broader experimental campaign. It should be used to guide the next implementation step, which is generating or loading concrete batch configuration files from this design.

Fuzzy logic is intentionally not part of the main pipeline here. The campaign first needs broader controlled evidence, sensitivity analysis, and quality checks.
