# FieldOps Lab campaign quality check

Campaign JSON: `analysis\reports\campaign_index.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 1 |
| batch_count | 1 |
| campaign_markdown | `analysis\reports\campaign_index.md` |
| campaign_csv | `analysis\reports\campaign_index.csv` |

## Campaign values

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

## Problems

- None.

## Warnings

- WARNING: Campaign contains 1 objective-only batch(es). Treat conclusions as preliminary.

## Conservative interpretation

The campaign index passed the structural quality check. This does not prove scientific validity, but it reduces the risk of using missing, inconsistent, or accidentally contaminated campaign outputs.
