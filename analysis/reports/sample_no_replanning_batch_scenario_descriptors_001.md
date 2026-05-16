# FieldOps Lab scenario descriptor report

Batch ID: `sample_no_replanning_batch_001`

Batch name: Sample no-replanning and replanning batch

## Purpose

This report creates scenario descriptors from the batch result. It does not use fuzzy rules. The goal is to describe the operational situation before choosing any final decision model.

## Method

- The no-replanning baseline is used to estimate the operational impact of keeping the original plan.
- The applied greedy replanning option is used as the current candidate when available.
- The descriptor compares candidate gain against makespan risk.
- The result is a conservative scenario classification, not a final scientific conclusion.

## Batch overview

| Field | Value |
| --- | --- |
| configured_experiment_count | 12 |
| completed_experiment_count | 12 |
| completion_percent | 100 |
| ranking_config_id | `default_objective_delta_ranking_v1` |

## Descriptor summary

| Descriptor | Count |
| --- | --- |
| high_impact_controlled_tradeoff | 1 |
| moderate_tradeoff | 1 |
| reassignment_opportunity | 1 |
| stable_low_disruption | 1 |

## Scenario descriptors

| Scenario | Impact score | Impact | Gain | Risk | Descriptor | Conservative action | Objective gain | Travel gain | Makespan risk | Candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_delay_light_001 | 2.50 | negligible | none | none | stable_low_disruption | keep_current_plan | 0 | 0 | 0 | no_replanning_policy_v1 + replanning_not_implemented_v1 + no_replanning_execution_baseline |
| sample_delay_moderate_001 | 35 | low | medium | medium | moderate_tradeoff | keep_current_plan_or_require_manager_review | 67 | 67 | 18 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |
| sample_delay_reassignment_001 | 122.50 | high | high | none | reassignment_opportunity | replan | 117 | 117 | 0 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |
| sample_delay_severe_001 | 105 | high | high | medium | high_impact_controlled_tradeoff | replan_with_makespan_monitoring | 107 | 107 | 28 | threshold_delay_replanning_policy_v1 + greedy_replanning_solver_v1 + replanning_applied_execution |

## Detailed values

### sample_delay_light_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 0 |
| baseline_delta_makespan | 0 |
| baseline_delta_travel | 10 |
| candidate_delta_objective | 0 |
| candidate_delta_makespan | 0 |
| candidate_delta_travel | 10 |
| no_replanning_impact_score | 2.50 |
| objective_gain_if_candidate | 0 |
| travel_gain_if_candidate | 0 |
| makespan_risk_if_candidate | 0 |
| tradeoff_class | no_replanning_gain |
| scenario_descriptor | stable_low_disruption |
| conservative_action | keep_current_plan |

### sample_delay_moderate_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 15 |
| baseline_delta_makespan | 15 |
| baseline_delta_travel | 50 |
| candidate_delta_objective | -52 |
| candidate_delta_makespan | 33 |
| candidate_delta_travel | -17 |
| no_replanning_impact_score | 35 |
| objective_gain_if_candidate | 67 |
| travel_gain_if_candidate | 67 |
| makespan_risk_if_candidate | 18 |
| tradeoff_class | moderate_tradeoff |
| scenario_descriptor | moderate_tradeoff |
| conservative_action | keep_current_plan_or_require_manager_review |

### sample_delay_reassignment_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 65 |
| baseline_delta_makespan | 65 |
| baseline_delta_travel | 100 |
| candidate_delta_objective | -52 |
| candidate_delta_makespan | 3 |
| candidate_delta_travel | -17 |
| no_replanning_impact_score | 122.50 |
| objective_gain_if_candidate | 117 |
| travel_gain_if_candidate | 117 |
| makespan_risk_if_candidate | 0 |
| tradeoff_class | dominant_or_nearly_dominant_replanning |
| scenario_descriptor | reassignment_opportunity |
| conservative_action | replan |

### sample_delay_severe_001

| Feature | Value |
| --- | --- |
| baseline_delta_objective | 55 |
| baseline_delta_makespan | 55 |
| baseline_delta_travel | 90 |
| candidate_delta_objective | -52 |
| candidate_delta_makespan | 83 |
| candidate_delta_travel | -17 |
| no_replanning_impact_score | 105 |
| objective_gain_if_candidate | 107 |
| travel_gain_if_candidate | 107 |
| makespan_risk_if_candidate | 28 |
| tradeoff_class | moderate_tradeoff |
| scenario_descriptor | high_impact_controlled_tradeoff |
| conservative_action | replan_with_makespan_monitoring |

## CSV output

CSV file: `analysis\reports\sample_no_replanning_batch_scenario_descriptors_001.csv`

## Conservative interpretation

This layer is intentionally independent from fuzzy logic. The descriptors can later feed a fuzzy controller, a weighted ranking, a statistical model, or a rule-based decision method.

At this stage, the safest scientific interpretation is that the project can already describe different operational situations, but the conclusions still need broader scenarios, more replications, and stronger validation.
