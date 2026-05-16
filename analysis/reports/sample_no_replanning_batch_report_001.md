# FieldOps Lab batch report

## Sample no-replanning and replanning batch

This report was generated automatically from the batch result JSON.

## Batch overview

| Field | Value |
| --- | --- |
| batch_id | sample_no_replanning_batch_001 |
| configured_experiment_count | 12 |
| completed_experiment_count | 12 |
| completion_percent | 100 |
| is_complete | yes |
| experiment_count | 12 |

## Description

Sample batch comparing no-replanning, threshold decisions with no implemented replanning, and threshold decisions with greedy replanning solver.

## Ranking configuration

Ranking config ID: `default_objective_delta_ranking_v1`

Score definition: Lower is better. Current ranking_score equals mean_delta_objective_value.

| Active weight | Value |
| --- | --- |
| objective_value_weight | 1 |

**Important limitation:** this ranking is currently objective-only. It does not penalize makespan, lateness, travel time, waiting time, or replanning effort.

## Recommendations

| Scenario | Policy | Replanning method | Execution mode | Best score | Second score | Margin | Clear winner | Delta objective | Delta makespan | Delta travel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | no_replanning_policy_v1 | replanning_not_implemented_v1 | no_replanning_execution_baseline | 0 | 0 | 0 | no | 0 | 0 | 10 |
| sample_delay_moderate_001 | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 15 | 67 | yes | -52 | 33 | -17 |
| sample_delay_reassignment_001 | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 65 | 117 | yes | -52 | 3 | -17 |
| sample_delay_severe_001 | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 55 | 107 | yes | -52 | 83 | -17 |

## Trade-off warnings

- sample_delay_moderate_001: objective improves by 52, but makespan increases by 33.
- sample_delay_moderate_001: travel time improves by 17, but makespan still increases by 33.
- sample_delay_reassignment_001: objective improves by 52, but makespan increases by 3.
- sample_delay_reassignment_001: travel time improves by 17, but makespan still increases by 3.
- sample_delay_severe_001: objective improves by 52, but makespan increases by 83.
- sample_delay_severe_001: travel time improves by 17, but makespan still increases by 83.

## Generated files

| Output | Path | Written |
| --- | --- | --- |
| overview_csv_output_path | data/results/sample_no_replanning_batch_overview_001.csv | yes |
| summary_csv_output_path | data/results/sample_no_replanning_batch_summary_001.csv | yes |
| aggregate_csv_output_path | data/results/sample_no_replanning_batch_aggregate_summary_001.csv | yes |
| ranking_csv_output_path | data/results/sample_no_replanning_batch_ranking_001.csv | yes |
| recommendation_csv_output_path | data/results/sample_no_replanning_batch_recommendation_001.csv | yes |
| result_json_output_path | data/results/sample_no_replanning_batch_result_001.json | yes |

## Interpretation

The current batch is useful as a controlled validation example. It shows that the system can execute baseline policies, trigger replanning decisions, apply a greedy replanning method, rank alternatives, recommend options, and export results.

However, this is not yet enough for a research conclusion. The ranking configuration is still objective-only, the sample size is small, and the current scenarios are handcrafted examples rather than a broad experimental campaign.
