# FieldOps Lab campaign batch blueprint quality check

Index JSON: `analysis\reports\campaign_batch_blueprint_index.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| blueprint_count | 12 |
| blueprint_dir | `analysis\reports\campaign_batch_blueprints` |

## Campaign values

| Field | Value |
| --- | --- |
| blueprint_count | 12 |
| total_planned_run_count | 36 |
| total_planned_algorithm_run_count | 108 |
| executable_status | blueprint_not_executable_yet |
| fuzzy_logic_status | not_used_in_main_pipeline |
| scientific_status | campaign_design_only |

## Blueprint checks

| Batch | Exists | Size bytes | Planned runs | Policy options | Algorithm runs | Problems |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| campaign_combined_delay_light_batch_blueprint | yes | 13063 | 3 | 3 | 9 | none |
| campaign_combined_delay_moderate_batch_blueprint | yes | 13232 | 3 | 3 | 9 | none |
| campaign_combined_delay_severe_batch_blueprint | yes | 13329 | 3 | 3 | 9 | none |
| campaign_reassignment_opportunity_light_batch_blueprint | yes | 13449 | 3 | 3 | 9 | none |
| campaign_reassignment_opportunity_moderate_batch_blueprint | yes | 13582 | 3 | 3 | 9 | none |
| campaign_reassignment_opportunity_severe_batch_blueprint | yes | 13499 | 3 | 3 | 9 | none |
| campaign_service_delay_only_light_batch_blueprint | yes | 13187 | 3 | 3 | 9 | none |
| campaign_service_delay_only_moderate_batch_blueprint | yes | 13356 | 3 | 3 | 9 | none |
| campaign_service_delay_only_severe_batch_blueprint | yes | 13285 | 3 | 3 | 9 | none |
| campaign_travel_delay_only_light_batch_blueprint | yes | 13161 | 3 | 3 | 9 | none |
| campaign_travel_delay_only_moderate_batch_blueprint | yes | 13318 | 3 | 3 | 9 | none |
| campaign_travel_delay_only_severe_batch_blueprint | yes | 13247 | 3 | 3 | 9 | none |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The campaign batch blueprints passed the structural quality check. They are coherent enough to be used as input for the next implementation step.

They are still not executable experiment configs. The next step should convert these blueprints into concrete batch configuration JSON files or build a generator for those configs.
