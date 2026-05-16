# FieldOps Lab ranking sensitivity report

Batch ID: `sample_no_replanning_batch_001`

Batch name: Sample no-replanning and replanning batch

## Purpose

This report tests whether the recommended policy changes when the ranking weights change. If the recommendation changes across profiles, the conclusion is sensitive to the decision criteria.

## Ranking profiles

| Profile | Description | Weights |
| --- | --- | --- |
| objective_only | Replicates the current default ranking. Lower objective delta is better. | mean_delta_objective_value=1 |
| balanced_operational | Balances objective value, makespan, travel time, lateness, and small replanning effort. | mean_delta_objective_value=1, mean_delta_makespan=0.50, mean_delta_total_travel_time=0.25, mean_delta_total_lateness=2, mean_delta_late_task_count=100, replanning_applied_rate=5 |
| makespan_priority | Prioritizes finishing earlier. This profile intentionally penalizes makespan strongly. | mean_delta_objective_value=0.25, mean_delta_makespan=1.50, mean_delta_total_travel_time=0.10, mean_delta_total_lateness=2, mean_delta_late_task_count=100, replanning_applied_rate=20 |
| conservative_replanning | Penalizes replanning effort. Useful when operational stability matters. | mean_delta_objective_value=1, mean_delta_makespan=0.50, mean_delta_total_travel_time=0.25, mean_delta_total_lateness=2, mean_delta_late_task_count=100, replanning_request_rate=10, replanning_applied_rate=30 |

## Recommendations by profile

### objective_only

| Scenario | Recommended option | Score | Second score | Margin | Clear winner | Delta objective | Delta makespan | Delta travel | Replanning applied rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 0 | 0 | 0 | no | 0 | 0 | 10 | 0 |
| sample_delay_moderate_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -52 | 15 | 67 | yes | -52 | 33 | -17 | 1 |
| sample_delay_reassignment_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -52 | 65 | 117 | yes | -52 | 3 | -17 | 1 |
| sample_delay_severe_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -52 | 55 | 107 | yes | -52 | 83 | -17 | 1 |

### balanced_operational

| Scenario | Recommended option | Score | Second score | Margin | Clear winner | Delta objective | Delta makespan | Delta travel | Replanning applied rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 2.50 | 2.50 | 0 | no | 0 | 0 | 10 | 0 |
| sample_delay_moderate_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -34.75 | 35 | 69.75 | yes | -52 | 33 | -17 | 1 |
| sample_delay_reassignment_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -49.75 | 122.50 | 172.25 | yes | -52 | 3 | -17 | 1 |
| sample_delay_severe_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -9.75 | 105 | 114.75 | yes | -52 | 83 | -17 | 1 |

### makespan_priority

| Scenario | Recommended option | Score | Second score | Margin | Clear winner | Delta objective | Delta makespan | Delta travel | Replanning applied rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 1 | 1 | 0 | no | 0 | 0 | 10 | 0 |
| sample_delay_moderate_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 31.25 | 31.25 | 0 | no | 15 | 15 | 50 | 0 |
| sample_delay_reassignment_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | 9.80 | 123.75 | 113.95 | yes | -52 | 3 | -17 | 1 |
| sample_delay_severe_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 105.25 | 105.25 | 0 | no | 55 | 55 | 90 | 0 |

### conservative_replanning

| Scenario | Recommended option | Score | Second score | Margin | Clear winner | Delta objective | Delta makespan | Delta travel | Replanning applied rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | 2.50 | 2.50 | 0 | no | 0 | 0 | 10 | 0 |
| sample_delay_moderate_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | 0.25 | 35 | 34.75 | yes | -52 | 33 | -17 | 1 |
| sample_delay_reassignment_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | -14.75 | 122.50 | 137.25 | yes | -52 | 3 | -17 | 1 |
| sample_delay_severe_001 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | 25.25 | 105 | 79.75 | yes | -52 | 83 | -17 | 1 |

## Stability across profiles

| Scenario | Stability | Objective only | Balanced operational | Makespan priority | Conservative replanning |
| --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | stable | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline |
| sample_delay_moderate_001 | sensitive | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |
| sample_delay_reassignment_001 | stable | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |
| sample_delay_severe_001 | sensitive | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |

## Interpretation

- Stable scenarios: 2.
- Sensitive scenarios: 2.
- Some recommendations change when the ranking weights change. These cases should not be treated as final policy conclusions yet.
- Stable recommendations are more promising, but still require more replications and broader scenarios.
- This script is a step toward decision support. It is not fuzzy logic yet, but it prepares the ground for fuzzy rules by showing how scenario recommendations react to different priorities.
