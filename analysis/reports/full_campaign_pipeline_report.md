# FieldOps Lab full campaign pipeline report

This report summarizes the automated execution of the full campaign pipeline.

## Overall result

| Field | Value |
| --- | --- |
| all_steps_passed | yes |
| step_count | 22 |
| failed_step_count | 0 |
| fieldops_exe | `build\fieldops_lab.exe` |

## Pipeline steps

| Step | Status | Return code |
| --- | --- | ---: |
| generate_experiment_campaign_plan | ok | 0 |
| verify_experiment_campaign_plan | ok | 0 |
| generate_campaign_batch_blueprints | ok | 0 |
| verify_campaign_batch_blueprints | ok | 0 |
| generate_campaign_perturbation_plans | ok | 0 |
| verify_campaign_perturbation_plans | ok | 0 |
| generate_executable_campaign_batch_configs | ok | 0 |
| connect_campaign_batch_configs_to_perturbation_plans | ok | 0 |
| verify_executable_campaign_batch_configs | ok | 0 |
| run_executable_campaign_batches | ok | 0 |
| verify_campaign_execution_index | ok | 0 |
| generate_campaign_result_summary | ok | 0 |
| verify_campaign_result_summary | ok | 0 |
| inspect_campaign_result_semantics | ok | 0 |
| audit_service_delay_impact | ok | 0 |
| verify_service_delay_impact_audit | ok | 0 |
| audit_policy_trigger_behavior | ok | 0 |
| verify_policy_trigger_behavior_audit | ok | 0 |
| generate_campaign_decision_matrix | ok | 0 |
| verify_campaign_decision_matrix | ok | 0 |
| generate_campaign_final_diagnostic_report | ok | 0 |
| verify_campaign_final_diagnostic_report | ok | 0 |

## Important outputs

| Output | Path |
| --- | --- |
| campaign_execution_index | `analysis\reports\campaign_execution_index.json` |
| campaign_result_summary | `analysis\reports\campaign_result_summary.json` |
| campaign_result_semantic_inspection | `analysis\reports\campaign_result_semantic_inspection.json` |
| service_delay_impact_audit | `analysis\reports\service_delay_impact_audit.json` |
| policy_trigger_behavior_audit | `analysis\reports\policy_trigger_behavior_audit.json` |
| campaign_decision_matrix | `analysis\reports\campaign_decision_matrix.json` |
| campaign_final_diagnostic_report | `analysis\reports\campaign_final_diagnostic_report.json` |
| campaign_final_diagnostic_quality_check | `analysis\reports\campaign_final_diagnostic_report_quality_check.json` |

## Conservative interpretation

This pipeline is now useful as an engineering automation layer. It reduces manual command errors and creates a repeatable path from campaign design to final diagnostic report.

It still does not prove final scientific validity. Broader instances, stronger ranking profiles, richer policies, and statistical validation are still required.
