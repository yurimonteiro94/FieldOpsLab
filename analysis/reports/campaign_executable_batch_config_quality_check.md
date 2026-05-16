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
| campaign_combined_delay_light_batch | yes | 16793 | 9 | 9 | yes | yes | none |
| campaign_combined_delay_moderate_batch | yes | 17142 | 9 | 9 | yes | yes | none |
| campaign_combined_delay_severe_batch | yes | 16980 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_light_batch | yes | 17765 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_moderate_batch | yes | 18096 | 9 | 9 | yes | yes | none |
| campaign_reassignment_opportunity_severe_batch | yes | 17799 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_light_batch | yes | 16741 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_moderate_batch | yes | 17090 | 9 | 9 | yes | yes | none |
| campaign_service_delay_only_severe_batch | yes | 16802 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_light_batch | yes | 16678 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_moderate_batch | yes | 17027 | 9 | 9 | yes | yes | none |
| campaign_travel_delay_only_severe_batch | yes | 16739 | 9 | 9 | yes | yes | none |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The executable campaign batch config candidates passed the structural quality check. They are coherent enough to be executed for pipeline validation.

This still does not make them final scientific evidence because the perturbation plans are still template-based.
