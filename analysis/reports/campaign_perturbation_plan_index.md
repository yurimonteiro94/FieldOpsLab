# FieldOps Lab campaign perturbation plan index

This report indexes family-specific perturbation plans generated for the campaign.

## Overview

| Field | Value |
| --- | --- |
| output_plan_dir | `data\perturbations\campaign_plans` |
| generated_perturbation_plan_count | 12 |
| generated_perturbation_count | 15 |
| travel_perturbation_count | 9 |
| service_perturbation_count | 6 |
| semantic_status | family_specific_template_based_perturbation_plan |
| scientific_status | candidate_campaign_semantics |

## Generated plans

| Plan | Family | Severity | Travel delay | Service delay | Perturbations | Path |
| --- | --- | --- | ---: | ---: | ---: | --- |
| campaign_combined_delay_light_perturbation_plan | combined_delay | light | 10 | 7 | 2 | `data\perturbations\campaign_plans\campaign_combined_delay_light_perturbation_plan.json` |
| campaign_combined_delay_moderate_perturbation_plan | combined_delay | moderate | 50 | 35 | 2 | `data\perturbations\campaign_plans\campaign_combined_delay_moderate_perturbation_plan.json` |
| campaign_combined_delay_severe_perturbation_plan | combined_delay | severe | 90 | 63 | 2 | `data\perturbations\campaign_plans\campaign_combined_delay_severe_perturbation_plan.json` |
| campaign_reassignment_opportunity_light_perturbation_plan | reassignment_opportunity | light | 10 | 0 | 1 | `data\perturbations\campaign_plans\campaign_reassignment_opportunity_light_perturbation_plan.json` |
| campaign_reassignment_opportunity_moderate_perturbation_plan | reassignment_opportunity | moderate | 50 | 0 | 1 | `data\perturbations\campaign_plans\campaign_reassignment_opportunity_moderate_perturbation_plan.json` |
| campaign_reassignment_opportunity_severe_perturbation_plan | reassignment_opportunity | severe | 90 | 0 | 1 | `data\perturbations\campaign_plans\campaign_reassignment_opportunity_severe_perturbation_plan.json` |
| campaign_service_delay_only_light_perturbation_plan | service_delay_only | light | 0 | 7 | 1 | `data\perturbations\campaign_plans\campaign_service_delay_only_light_perturbation_plan.json` |
| campaign_service_delay_only_moderate_perturbation_plan | service_delay_only | moderate | 0 | 35 | 1 | `data\perturbations\campaign_plans\campaign_service_delay_only_moderate_perturbation_plan.json` |
| campaign_service_delay_only_severe_perturbation_plan | service_delay_only | severe | 0 | 63 | 1 | `data\perturbations\campaign_plans\campaign_service_delay_only_severe_perturbation_plan.json` |
| campaign_travel_delay_only_light_perturbation_plan | travel_delay_only | light | 10 | 0 | 1 | `data\perturbations\campaign_plans\campaign_travel_delay_only_light_perturbation_plan.json` |
| campaign_travel_delay_only_moderate_perturbation_plan | travel_delay_only | moderate | 50 | 0 | 1 | `data\perturbations\campaign_plans\campaign_travel_delay_only_moderate_perturbation_plan.json` |
| campaign_travel_delay_only_severe_perturbation_plan | travel_delay_only | severe | 90 | 0 | 1 | `data\perturbations\campaign_plans\campaign_travel_delay_only_severe_perturbation_plan.json` |

## Conservative interpretation

These files improve the campaign structure because each scenario family now has a dedicated perturbation plan instead of blindly reusing the same sample plan.

They are still template-based. This is acceptable as the next development step, but final scientific experiments should later calibrate perturbations against realistic or literature-backed distributions.
