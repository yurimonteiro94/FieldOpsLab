# FieldOps Lab executable campaign batch config quality check

Index JSON: `analysis\reports\campaign_executable_batch_config_index.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| config_count | 12 |
| total_experiment_count | 108 |

## Config checks

| Batch | Exists | Size bytes | Experiments | Unique IDs | Output paths ok | Export flags ok | Problems |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| campaign_combined_delay_light_batch | yes | 18686 | 9 | 9 | yes | yes | none |
| campaign_combined_delay_moderate_batch | yes | 19095 | 9 | 9 | yes | yes | none |
| campaign_combined_delay_severe_batch | yes | 18893 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_light_batch | yes | 19858 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_moderate_batch | yes | 20249 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_severe_batch | yes | 19912 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_light_batch | yes | 18714 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_moderate_batch | yes | 19123 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_severe_batch | yes | 18795 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_light_batch | yes | 18631 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_moderate_batch | yes | 19040 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_severe_batch | yes | 18712 | 9 | 9 | yes | yes | none |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The executable campaign batch config candidates passed the structural quality check. They are coherent enough to be executed for pipeline validation.

This still does not make them final scientific evidence because the perturbation plans are still template-based.
