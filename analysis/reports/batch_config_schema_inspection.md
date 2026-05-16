# FieldOps Lab batch config schema inspection

This report inspects the current executable sample batch config and the campaign blueprints.

## Inputs

| Input | Path |
| --- | --- |
| sample_config | `data\experiments\sample_no_replanning_batch_001.json` |
| blueprint_index | `analysis\reports\campaign_batch_blueprint_index.json` |
| blueprint_dir | `analysis\reports\campaign_batch_blueprints` |

## Sample config top-level shape

| Key | Type | Item count |
| --- | --- | ---: |
| aggregate_csv_output_path | str | 1 |
| batch_id | str | 1 |
| description | str | 1 |
| experiments | array | 12 |
| export_aggregate_csv | bool | 1 |
| export_individual_results | bool | 1 |
| export_ranking_csv | bool | 1 |
| export_result_json | bool | 1 |
| export_summary_csv | bool | 1 |
| name | str | 1 |
| ranking_csv_output_path | str | 1 |
| result_json_output_path | str | 1 |
| summary_csv_output_path | str | 1 |
| verbose | bool | 1 |

## Candidate experiment arrays in sample config

| Path | Length | Object count | Candidate score | Sample keys |
| --- | ---: | ---: | ---: | --- |
| experiments | 12 | 12 | 5 | experiment_id, instance_path, notes, perturbation_plan_path, policy_id, replanning_method_id, replication_id, scenario_id, seed |

## Blueprint index summary

| Field | Value |
| --- | --- |
| blueprint_count | 12 |
| total_planned_run_count | 36 |
| total_planned_algorithm_run_count | 108 |

## Blueprint files

| File | Size bytes | Top-level key count | Key path count |
| --- | ---: | ---: | ---: |
| campaign_combined_delay_light_batch_blueprint_blueprint.json | 13063 | 12 | 68 |
| campaign_combined_delay_moderate_batch_blueprint_blueprint.json | 13232 | 12 | 68 |
| campaign_combined_delay_severe_batch_blueprint_blueprint.json | 13329 | 12 | 68 |
| campaign_reassignment_opportunity_light_batch_blueprint_blueprint.json | 13449 | 12 | 68 |
| campaign_reassignment_opportunity_moderate_batch_blueprint_blueprint.json | 13582 | 12 | 68 |
| campaign_reassignment_opportunity_severe_batch_blueprint_blueprint.json | 13499 | 12 | 68 |
| campaign_service_delay_only_light_batch_blueprint_blueprint.json | 13187 | 12 | 68 |
| campaign_service_delay_only_moderate_batch_blueprint_blueprint.json | 13356 | 12 | 68 |
| campaign_service_delay_only_severe_batch_blueprint_blueprint.json | 13285 | 12 | 68 |
| campaign_travel_delay_only_light_batch_blueprint_blueprint.json | 13161 | 12 | 68 |
| campaign_travel_delay_only_moderate_batch_blueprint_blueprint.json | 13318 | 12 | 68 |
| campaign_travel_delay_only_severe_batch_blueprint_blueprint.json | 13247 | 12 | 68 |

## Conservative interpretation

This inspection is a safety step before generating executable campaign configs. The project currently has valid planning blueprints, but they still need to be mapped carefully to the actual batch config schema used by the C++ executable.

The next step should be a generator that creates concrete batch config JSON files from these blueprints, using the current sample config as the structural template.
