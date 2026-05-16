# FieldOps Lab campaign result summary quality check

Summary JSON: `analysis\reports\campaign_result_summary.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 2 |
| batch_count | 12 |
| recommendation_count | 12 |
| total_completed_experiment_count | 108 |
| weak_or_tied_count | 6 |
| tradeoff_count | 6 |
| csv_row_count | 12 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | campaign_result_consolidation_only |

## Problems

- None.

## Warnings

- WARNING: Campaign has 6 weak or tied recommendation(s).
- WARNING: Campaign has 6 trade-off recommendation(s).

## Conservative interpretation

The campaign result summary passed the structural quality check. It is safe to use as a campaign-level consolidation report.

This still does not prove scientific validity. It checks consistency of the consolidation layer.
