# FieldOps Lab campaign index

This report consolidates all batch analysis manifests found in the reports directory.

## Campaign overview

| Field | Value |
| --- | --- |
| manifest_count | 1 |
| total_configured_experiment_count | 12 |
| total_completed_experiment_count | 12 |
| global_completion_percent | 100 |
| complete_batch_count | 1 |
| quality_ok_batch_count | 1 |
| incomplete_batch_count | 0 |
| quality_problem_batch_count | 0 |
| objective_only_batch_count | 1 |
| fuzzy_used_batch_count | 0 |

## Batch table

| Batch | Complete | Quality ok | Experiments | Completion | Ranking config | Recommendations | Scientific status |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| sample_no_replanning_batch_001 | yes | yes | 12/12 | 100 | default_objective_delta_ranking_v1 | 4 | pipeline_validation_only |

## Quality notes

No manifest-level quality problems were detected.

All discovered batches are marked as complete.

## Methodological notes

- Only one batch manifest was found. This is enough to validate the reporting pipeline, but not enough for a campaign-level conclusion.
- At least one batch still uses an objective-only ranking configuration. This should be treated as preliminary.
- Fuzzy logic is not being used in the main analysis pipeline. This matches the current conservative project direction.

## Conservative interpretation

This index is a project organization layer. It helps track batches, reports, quality status, and preliminary scientific status. It does not replace statistical validation, broader scenarios, or final methodological justification.
