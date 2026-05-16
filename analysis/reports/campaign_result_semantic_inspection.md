# FieldOps Lab campaign result semantic inspection

This report checks whether executed campaign results match the intended scenario families.

## Overall result

| Field | Value |
| --- | --- |
| all_semantic_checks_passed | yes |
| semantic_problem_count | 0 |
| semantic_warning_count | 0 |
| batch_count | 12 |

## Batch semantic checks

| Batch | Family | Severity | Baseline travel delta | Baseline service delta | Baseline effect count | Problems | Warnings |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| campaign_combined_delay_light_batch | combined_delay | light | 10 | 7 | 2 | 0 | 0 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | 50 | 35 | 2 | 0 | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | 90 | 63 | 2 | 0 | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | 10 | 0 | 1 | 0 | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | 50 | 0 | 1 | 0 | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | 90 | 0 | 1 | 0 | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | 0 | 7 | 1 | 0 | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | 0 | 35 | 1 | 0 | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | 0 | 63 | 1 | 0 | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | 10 | 0 | 1 | 0 | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | 50 | 0 | 1 | 0 | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | 90 | 0 | 1 | 0 | 0 |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The campaign results passed this semantic diagnostic. The executed perturbation families appear to produce the expected first-order metric effects.
