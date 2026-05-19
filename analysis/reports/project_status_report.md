# FieldOps Lab project status report

This report summarizes the current engineering and diagnostic status of the project.

## Overall result

| Field | Value |
| --- | --- |
| engineering_status | passed_current_structural_quality_gate |
| scientific_status | diagnostic_only_with_methodological_warnings |
| structural_all_required_checks_passed | yes |

## Summary metrics

| Category | Field | Value |
| --- | --- | ---: |
| overall | engineering_status | passed_current_structural_quality_gate |
| overall | scientific_status | diagnostic_only_with_methodological_warnings |
| overall | structural_all_required_checks_passed | yes |
| tests | analysis_script_count | 54 |
| tests | python_test_count | 46 |
| tests | cpp_test_source_count | 45 |
| tests | script_without_direct_python_test_count | 0 |
| tests | script_needing_test_review_count | 0 |
| pipeline | pipeline_step_count | 26 |
| pipeline | pipeline_failed_step_count | 0 |
| final_diagnostic | final_diagnostic_row_count | 12 |
| ranking_sensitivity | ranking_row_count | 144 |
| ranking_sensitivity | scenario_summary_count | 12 |
| ranking_sensitivity | sensitive_to_ranking_profile_count | 2 |
| ranking_sensitivity | ranking_fragility_status | some_scenarios_sensitive_to_ranking_profile |
| ranking_sensitivity_explanation | ranking_sensitive_scenario_count | 2 |
| ranking_sensitivity_explanation | ranking_sensitivity_explanation_count | 2 |
| ranking_sensitivity_explanation | policy_change_explanation_count | 0 |
| ranking_sensitivity_explanation | class_change_explanation_count | 2 |
| ranking_sensitivity_explanation | all_sensitive_scenarios_have_explanation | yes |
| experimental_design | experimental_design_experiment_count | 648 |
| experimental_design | experimental_design_scenario_count | 108 |
| experimental_design | experimental_design_replication_count | 3 |
| experimental_design | experimental_design_reproducible | yes |
| warnings | methodological_warning_count | 2 |

## Quality summaries

| Quality file | Passed | Problems | Warnings |
| --- | --- | ---: | ---: |
| `analysis/reports/full_campaign_pipeline_quality_check.json` | yes | 0 | 1 |
| `analysis/reports/test_inventory_quality_check.json` | yes | 0 | 0 |
| `analysis/reports/campaign_final_diagnostic_report_quality_check.json` | yes | 0 | 2 |
| `analysis/reports/campaign_ranking_profile_sensitivity_quality_check.json` | yes | 0 | 0 |
| `analysis/reports/campaign_final_ranking_integration_quality_check.json` | yes | 0 | 0 |
| `analysis/reports/ranking_sensitive_scenario_quality_check.json` | yes | 0 | 0 |
| `analysis/reports/ranking_sensitivity_explanation_quality_check.json` | yes | 0 | 0 |
| `analysis/reports/experimental_design_matrix_quality_check.json` | yes | 0 | 0 |

## Conservative interpretation

The project currently passes the structural quality gate.

This does not prove scientific validity. It confirms that the current engineering pipeline, reports, and test inventory are internally consistent.

## Next actions

- Keep strengthening tests when a script receives new behavior.
- Avoid treating diagnostic reports as scientific proof before broader instances and statistical validation.
- Use the full quality gate before important commits or before presenting results.
