# FieldOps Lab full campaign pipeline quality check

Manifest: `analysis\reports\full_campaign_pipeline_manifest.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 1 |
| step_count | 24 |
| failed_step_count | 0 |
| required_output_file_count | 11 |
| required_quality_file_count | 11 |

## Output checks

| Path | Exists | Size bytes |
| --- | --- | ---: |
| `analysis\reports\full_campaign_pipeline_report.md` | yes | 3000 |
| `analysis\reports\full_campaign_pipeline_manifest.json` | yes | 26546 |
| `analysis\reports\full_campaign_pipeline_log.txt` | yes | 23819 |
| `analysis\reports\campaign_execution_index.json` | yes | 51406 |
| `analysis\reports\campaign_result_summary.json` | yes | 19677 |
| `analysis\reports\campaign_result_semantic_inspection.json` | yes | 34722 |
| `analysis\reports\service_delay_impact_audit.json` | yes | 16040 |
| `analysis\reports\policy_trigger_behavior_audit.json` | yes | 32583 |
| `analysis\reports\campaign_decision_matrix.json` | yes | 17591 |
| `analysis\reports\campaign_ranking_profile_sensitivity.json` | yes | 248151 |
| `analysis\reports\campaign_final_diagnostic_report.json` | yes | 20248 |

## Quality file checks

| Path | Passed | Problem count |
| --- | --- | ---: |
| `analysis\reports\experiment_campaign_plan_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_batch_blueprint_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_perturbation_plan_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_executable_batch_config_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_execution_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_result_summary_quality_check.json` | yes | 0 |
| `analysis\reports\service_delay_impact_audit_quality_check.json` | yes | 0 |
| `analysis\reports\policy_trigger_behavior_audit_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_decision_matrix_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_ranking_profile_sensitivity_quality_check.json` | yes | 0 |
| `analysis\reports\campaign_final_diagnostic_report_quality_check.json` | yes | 0 |

## Problems

- None.

## Warnings

- WARNING: Final diagnostic report has 2 methodological warning(s).

## Conservative interpretation

The full campaign pipeline passed the structural quality check. This means the automated campaign flow is reproducible enough to use as the current engineering baseline.

This does not prove final scientific validity. It confirms that the execution and reporting pipeline is internally consistent.
