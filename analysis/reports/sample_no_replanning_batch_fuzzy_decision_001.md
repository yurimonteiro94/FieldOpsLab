# FieldOps Lab fuzzy decision prototype report

Batch ID: `sample_no_replanning_batch_001`

Batch name: Sample no-replanning and replanning batch

## Purpose

This report converts batch results into fuzzy-style linguistic variables and preliminary decision rules. It is an analysis prototype, not the final fuzzy decision module.

## Fuzzy inputs

- no_replanning_impact_score: estimated operational damage when the current plan is kept.
- objective_gain_if_replan: objective improvement obtained by using the greedy replanning option instead of the no-replanning baseline.
- travel_gain_if_replan: travel-time improvement obtained by using the greedy replanning option.
- makespan_risk_if_replan: additional makespan caused by using the greedy replanning option.

## Decision summary

| Scenario | Fuzzy decision | Impact label | Gain label | Risk label | Objective gain | Makespan risk | Do not replan strength | Replan strength | Conditional strength |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | DO_NOT_REPLAN | low | low | low | 0 | 0 | 1 | 0 | 0 |
| sample_delay_moderate_001 | DO_NOT_REPLAN | low | medium | low | 67 | 18 | 0.56 | 0.42 | 0.12 |
| sample_delay_reassignment_001 | REPLAN | medium | high | low | 117 | 0 | 0 | 0.62 | 0 |
| sample_delay_severe_001 | CONDITIONAL_REPLAN | medium | high | medium | 107 | 28 | 0 | 0.36 | 0.45 |

## Scenario details

### sample_delay_light_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 0 |
| baseline_delta_makespan | 0 |
| baseline_delta_travel | 10 |
| greedy_delta_objective | 0 |
| greedy_delta_makespan | 0 |
| greedy_delta_travel | 10 |
| no_replanning_impact_score | 2.50 |
| objective_gain_if_replan | 0 |
| travel_gain_if_replan | 0 |
| makespan_risk_if_replan | 0 |

| Membership group | Low | Medium | High | Strongest label |
| --- | --- | --- | --- | --- |
| no_replanning_impact | 1 | 0 | 0 | low |
| objective_gain_if_replan | 1 | 0 | 0 | low |
| makespan_risk_if_replan | 1 | 0 | 0 | low |
| travel_gain_if_replan | 1 | 0 | 0 | low |

| Rule | Strength |
| --- | --- |
| do_not_replan | 1 |
| replan | 0 |
| conditional_replan | 0 |

Decision: `DO_NOT_REPLAN`

### sample_delay_moderate_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 15 |
| baseline_delta_makespan | 15 |
| baseline_delta_travel | 50 |
| greedy_delta_objective | -52 |
| greedy_delta_makespan | 33 |
| greedy_delta_travel | -17 |
| no_replanning_impact_score | 35 |
| objective_gain_if_replan | 67 |
| travel_gain_if_replan | 67 |
| makespan_risk_if_replan | 18 |

| Membership group | Low | Medium | High | Strongest label |
| --- | --- | --- | --- | --- |
| no_replanning_impact | 0.56 | 0.08 | 0 | low |
| objective_gain_if_replan | 0 | 0.94 | 0 | medium |
| makespan_risk_if_replan | 0.60 | 0.12 | 0 | low |
| travel_gain_if_replan | 0 | 0.94 | 0 | medium |

| Rule | Strength |
| --- | --- |
| do_not_replan | 0.56 |
| replan | 0.42 |
| conditional_replan | 0.12 |

Decision: `DO_NOT_REPLAN`

### sample_delay_reassignment_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 65 |
| baseline_delta_makespan | 65 |
| baseline_delta_travel | 100 |
| greedy_delta_objective | -52 |
| greedy_delta_makespan | 3 |
| greedy_delta_travel | -17 |
| no_replanning_impact_score | 122.50 |
| objective_gain_if_replan | 117 |
| travel_gain_if_replan | 117 |
| makespan_risk_if_replan | 0 |

| Membership group | Low | Medium | High | Strongest label |
| --- | --- | --- | --- | --- |
| no_replanning_impact | 0 | 0.46 | 0.28 | medium |
| objective_gain_if_replan | 0 | 0.06 | 0.62 | high |
| makespan_risk_if_replan | 1 | 0 | 0 | low |
| travel_gain_if_replan | 0 | 0.06 | 0.62 | high |

| Rule | Strength |
| --- | --- |
| do_not_replan | 0 |
| replan | 0.62 |
| conditional_replan | 0 |

Decision: `REPLAN`

### sample_delay_severe_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 55 |
| baseline_delta_makespan | 55 |
| baseline_delta_travel | 90 |
| greedy_delta_objective | -52 |
| greedy_delta_makespan | 83 |
| greedy_delta_travel | -17 |
| no_replanning_impact_score | 105 |
| objective_gain_if_replan | 107 |
| travel_gain_if_replan | 107 |
| makespan_risk_if_replan | 28 |

| Membership group | Low | Medium | High | Strongest label |
| --- | --- | --- | --- | --- |
| no_replanning_impact | 0 | 0.75 | 0.06 | medium |
| objective_gain_if_replan | 0 | 0.26 | 0.45 | high |
| makespan_risk_if_replan | 0.10 | 0.52 | 0 | medium |
| travel_gain_if_replan | 0 | 0.26 | 0.45 | high |

| Rule | Strength |
| --- | --- |
| do_not_replan | 0 |
| replan | 0.36 |
| conditional_replan | 0.45 |

Decision: `CONDITIONAL_REPLAN`

## Conservative interpretation

- CONDITIONAL_REPLAN: 1 scenario(s).
- DO_NOT_REPLAN: 2 scenario(s).
- REPLAN: 1 scenario(s).
- This is a fuzzy decision prototype, not the final fuzzy controller. It is useful for checking whether the current experimental outputs can be translated into linguistic decision rules.
- The rules are intentionally conservative. A scenario with good objective gain but meaningful makespan risk may become CONDITIONAL_REPLAN instead of a simple REPLAN.
- The next scientific step is to calibrate these membership functions and rule weights using broader experiments, not only this handcrafted sample batch.
