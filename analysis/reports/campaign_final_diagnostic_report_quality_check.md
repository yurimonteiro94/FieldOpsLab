# FieldOps Lab campaign final diagnostic report quality check

Final JSON: `analysis\reports\campaign_final_diagnostic_report.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 2 |
| decision_row_count | 12 |
| csv_row_count | 12 |
| source_file_count | 6 |
| low_evidence_count | 6 |
| service_modeling_review_count | 4 |
| replan_candidate_count | 6 |
| semantic_problem_count | 0 |
| invalid_evidence_count | 0 |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | final_diagnostic_report_only |
| general_project_completeness_estimate_percent | 30 |
| campaign_pipeline_completeness_estimate_percent | 90 |

## Problems

- None.

## Warnings

- WARNING: Final report contains 6 low-evidence row(s).
- WARNING: Final report contains 4 service-modeling review row(s).

## Conservative interpretation

The final diagnostic report passed the structural quality check. It can be used as a consolidated project artifact for the current campaign.

Passing this check does not prove scientific validity. It confirms that the final diagnostic layer is internally consistent.
