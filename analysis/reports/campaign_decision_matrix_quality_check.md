# FieldOps Lab campaign decision matrix quality check

Decision matrix JSON: `analysis\reports\campaign_decision_matrix.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 2 |
| row_count | 12 |
| csv_row_count | 12 |
| low_evidence_count | 6 |
| service_modeling_review_count | 4 |
| replan_candidate_count | 6 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | decision_matrix_diagnostic_only |

## Problems

- None.

## Warnings

- WARNING: Decision matrix contains 6 low-evidence row(s).
- WARNING: Decision matrix contains 4 service-modeling review row(s).

## Conservative interpretation

The decision matrix passed the structural quality check. It can be used as a diagnostic consolidation layer.

Warnings are methodological cautions. They do not necessarily indicate execution failure.
