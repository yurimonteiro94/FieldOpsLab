# FieldOps Lab test inventory report

This report audits the structural organization of C++ and Python tests.

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| analysis_script_count | 54 |
| python_test_count | 56 |
| cpp_test_source_count | 45 |
| cpp_test_support_header_count | 1 |
| script_with_direct_python_test_count | 54 |
| script_without_direct_python_test_count | 0 |
| script_needing_test_review_count | 0 |
| patch_script_count | 0 |
| row_count | 54 |

## Problems

- None.

## Warnings

- None.

## Analysis script test signals

| Script | Direct tests | Related tests | Generic tests | Status |
| --- | ---: | ---: | ---: | --- |
| `analysis\scripts\audit_batch_recommendations.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\audit_policy_trigger_behavior.py` | 3 | 7 | 4 | direct_test_found |
| `analysis\scripts\audit_service_delay_impact.py` | 3 | 6 | 4 | direct_test_found |
| `analysis\scripts\connect_campaign_batch_configs_to_perturbation_plans.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\generate_batch_markdown_report.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_batch_blueprints.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_decision_matrix.py` | 4 | 9 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_final_diagnostic_report.py` | 3 | 8 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_index.py` | 1 | 2 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_perturbation_plans.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_ranking_profile_sensitivity.py` | 4 | 9 | 4 | direct_test_found |
| `analysis\scripts\generate_campaign_result_summary.py` | 3 | 7 | 4 | direct_test_found |
| `analysis\scripts\generate_executable_campaign_batch_configs.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\generate_experiment_campaign_plan.py` | 3 | 5 | 4 | direct_test_found |
| `analysis\scripts\generate_experimental_design_matrix.py` | 3 | 5 | 4 | direct_test_found |
| `analysis\scripts\generate_fuzzy_decision_report.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\generate_project_status_report.py` | 9 | 10 | 4 | direct_test_found |
| `analysis\scripts\generate_ranking_sensitive_scenario_report.py` | 4 | 4 | 4 | direct_test_found |
| `analysis\scripts\generate_ranking_sensitivity_explanation_report.py` | 3 | 4 | 4 | direct_test_found |
| `analysis\scripts\generate_scenario_descriptors.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\generate_scientific_validation_plan.py` | 5 | 6 | 4 | direct_test_found |
| `analysis\scripts\generate_test_inventory_report.py` | 4 | 6 | 4 | direct_test_found |
| `analysis\scripts\inspect_batch_config_schema.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\inspect_campaign_result_semantics.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\integrate_ranking_sensitivity_into_final_diagnostic_report.py` | 4 | 4 | 4 | direct_test_found |
| `analysis\scripts\run_batch_analysis_pipeline.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\run_executable_campaign_batches.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\run_full_campaign_pipeline.py` | 5 | 11 | 4 | direct_test_found |
| `analysis\scripts\run_local_platform_smoke_check.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\run_project_quality_gate.py` | 8 | 8 | 4 | direct_test_found |
| `analysis\scripts\run_ranking_sensitivity.py` | 1 | 12 | 4 | direct_test_found |
| `analysis\scripts\summarize_batch_result.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\verify_analysis_outputs.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_batch_blueprints.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_decision_matrix.py` | 6 | 9 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_execution_index.py` | 4 | 5 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_final_diagnostic_report.py` | 4 | 8 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_index.py` | 1 | 2 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_perturbation_plans.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_ranking_profile_sensitivity.py` | 5 | 9 | 4 | direct_test_found |
| `analysis\scripts\verify_campaign_result_summary.py` | 4 | 7 | 4 | direct_test_found |
| `analysis\scripts\verify_executable_campaign_batch_configs.py` | 3 | 3 | 4 | direct_test_found |
| `analysis\scripts\verify_executed_campaign_batch_result_paths.py` | 1 | 1 | 4 | direct_test_found |
| `analysis\scripts\verify_experiment_campaign_plan.py` | 3 | 5 | 4 | direct_test_found |
| `analysis\scripts\verify_experimental_design_matrix.py` | 3 | 5 | 4 | direct_test_found |
| `analysis\scripts\verify_final_diagnostic_ranking_integration.py` | 4 | 4 | 4 | direct_test_found |
| `analysis\scripts\verify_full_campaign_pipeline.py` | 7 | 11 | 4 | direct_test_found |
| `analysis\scripts\verify_policy_trigger_behavior_audit.py` | 4 | 7 | 4 | direct_test_found |
| `analysis\scripts\verify_project_status_report.py` | 5 | 10 | 4 | direct_test_found |
| `analysis\scripts\verify_ranking_sensitive_scenario_report.py` | 4 | 4 | 4 | direct_test_found |
| `analysis\scripts\verify_ranking_sensitivity_explanation_report.py` | 4 | 4 | 4 | direct_test_found |
| `analysis\scripts\verify_scientific_validation_plan.py` | 4 | 6 | 4 | direct_test_found |
| `analysis\scripts\verify_service_delay_impact_audit.py` | 4 | 6 | 4 | direct_test_found |
| `analysis\scripts\verify_test_inventory_report.py` | 5 | 6 | 4 | direct_test_found |

## Conservative interpretation

The project has a centralized Python test tree and no temporary patch scripts were found.

Scripts without direct tests are not automatically wrong, but they should be reviewed over time.
