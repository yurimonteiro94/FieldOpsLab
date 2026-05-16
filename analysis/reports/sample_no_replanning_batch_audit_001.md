# FieldOps Lab recommendation audit

Batch ID: `sample_no_replanning_batch_001`

Ranking config ID: `default_objective_delta_ranking_v1`

## Global findings

- The batch execution is complete. All configured experiments were completed.
- All expected output files were reported as written.
- The ranking is objective-only. This is acceptable for a first validation, but weak for research conclusions because it ignores makespan, lateness, travel time, waiting time, and replanning effort.
- Recommendation audit summary: strong=0, tradeoff=3, weak=1, invalid=0.
- There are trade-off recommendations. These should not be described as absolute improvements.
- There are weak recommendations. These need either better ranking criteria, more replications, or richer scenarios.

## Scenario audit

| Scenario | Audit class | Policy | Method | Execution | Best score | Second score | Margin | Delta objective | Delta makespan | Delta travel | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | weak | no_replanning_policy_v1 | replanning_not_implemented_v1 | no_replanning_execution_baseline | 0 | 0 | 0 | 0 | 0 | 10 | sample_delay_light_001 has no clear winner. The best and second-best scores are tied or too close. |
| sample_delay_moderate_001 | tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 15 | 67 | -52 | 33 | -17 | sample_delay_moderate_001 improves objective and travel time, but increases makespan. |
| sample_delay_reassignment_001 | tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 65 | 117 | -52 | 3 | -17 | sample_delay_reassignment_001 improves objective and travel time, but increases makespan. |
| sample_delay_severe_001 | tradeoff | threshold_delay_replanning_policy_v1 | greedy_replanning_solver_v1 | replanning_applied_execution | -52 | 55 | 107 | -52 | 83 | -17 | sample_delay_severe_001 improves objective and travel time, but increases makespan. |

## Conservative interpretation

This audit should be used as a safety layer before making claims from the batch. A recommendation classified as tradeoff may still be useful, but it must be explained as a compromise, not as an unconditional improvement.

At the current stage, the result is good for validating the pipeline. It is not yet enough to support a final research conclusion because the experiment set is small, the scenarios are handcrafted, and the ranking is still objective-only.
