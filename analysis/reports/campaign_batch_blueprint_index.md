# FieldOps Lab campaign batch blueprint index

This report indexes campaign batch blueprints generated from the experiment campaign plan.

## Source plan

| Field | Value |
| --- | --- |
| source_plan_path | `analysis\reports\experiment_campaign_plan.json` |
| design_status | planning_only |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | campaign_design_only |

## Blueprint overview

| Field | Value |
| --- | --- |
| blueprint_count | 12 |
| total_planned_run_count | 36 |
| total_planned_algorithm_run_count | 108 |
| executable_status | blueprint_not_executable_yet |

## Blueprints

| Batch | Family | Severity | Replications | Planned runs | Algorithm runs | Status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| campaign_combined_delay_light_batch_blueprint | combined_delay | light | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_combined_delay_moderate_batch_blueprint | combined_delay | moderate | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_combined_delay_severe_batch_blueprint | combined_delay | severe | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_reassignment_opportunity_light_batch_blueprint | reassignment_opportunity | light | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_reassignment_opportunity_moderate_batch_blueprint | reassignment_opportunity | moderate | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_reassignment_opportunity_severe_batch_blueprint | reassignment_opportunity | severe | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_service_delay_only_light_batch_blueprint | service_delay_only | light | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_service_delay_only_moderate_batch_blueprint | service_delay_only | moderate | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_service_delay_only_severe_batch_blueprint | service_delay_only | severe | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_travel_delay_only_light_batch_blueprint | travel_delay_only | light | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_travel_delay_only_moderate_batch_blueprint | travel_delay_only | moderate | 3 | 3 | 9 | blueprint_not_executable_yet |
| campaign_travel_delay_only_severe_batch_blueprint | travel_delay_only | severe | 3 | 3 | 9 | blueprint_not_executable_yet |

## Conservative interpretation

These blueprints are an intermediate planning layer. They organize future batches, but they are not executable experiment configs yet.

This is intentional. The project should first preserve a clean separation between campaign design, blueprint organization, executable configs, execution results, and scientific interpretation.
