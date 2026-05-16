# FieldOps Lab executable campaign batch config index

This report indexes template-based executable batch config candidates generated from campaign blueprints.

## Overview

| Field | Value |
| --- | --- |
| output_config_dir | `data\experiments\campaign_batches` |
| generated_batch_config_count | 12 |
| generated_experiment_count | 108 |
| semantic_status | template_based_executable_candidate |
| scientific_status | not_final_campaign_semantics |

## Generated configs

| Batch | Family | Severity | Experiments | Config path | Semantic status |
| --- | --- | --- | ---: | --- | --- |
| campaign_combined_delay_light_batch | combined_delay | light | 9 | `data\experiments\campaign_batches\campaign_combined_delay_light_batch.json` | template_based_executable_candidate |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | 9 | `data\experiments\campaign_batches\campaign_combined_delay_moderate_batch.json` | template_based_executable_candidate |
| campaign_combined_delay_severe_batch | combined_delay | severe | 9 | `data\experiments\campaign_batches\campaign_combined_delay_severe_batch.json` | template_based_executable_candidate |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | 9 | `data\experiments\campaign_batches\campaign_reassignment_opportunity_light_batch.json` | template_based_executable_candidate |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | 9 | `data\experiments\campaign_batches\campaign_reassignment_opportunity_moderate_batch.json` | template_based_executable_candidate |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | 9 | `data\experiments\campaign_batches\campaign_reassignment_opportunity_severe_batch.json` | template_based_executable_candidate |
| campaign_service_delay_only_light_batch | service_delay_only | light | 9 | `data\experiments\campaign_batches\campaign_service_delay_only_light_batch.json` | template_based_executable_candidate |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | 9 | `data\experiments\campaign_batches\campaign_service_delay_only_moderate_batch.json` | template_based_executable_candidate |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | 9 | `data\experiments\campaign_batches\campaign_service_delay_only_severe_batch.json` | template_based_executable_candidate |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | 9 | `data\experiments\campaign_batches\campaign_travel_delay_only_light_batch.json` | template_based_executable_candidate |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | 9 | `data\experiments\campaign_batches\campaign_travel_delay_only_moderate_batch.json` | template_based_executable_candidate |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | 9 | `data\experiments\campaign_batches\campaign_travel_delay_only_severe_batch.json` | template_based_executable_candidate |

## Conservative interpretation

These configs are intended to validate the execution pipeline at campaign scale. They deliberately reuse perturbation plan templates inferred from the current sample batch config.

Do not treat results from these generated configs as final scientific evidence yet. The next required step is to generate family-specific perturbation plans so travel-only, service-only, combined-delay, and reassignment scenarios are semantically faithful.
