# FieldOps Lab campaign perturbation connection report

This report confirms that executable campaign batch configs were connected to family-specific perturbation plans.

## Overview

| Field | Value |
| --- | --- |
| connected_config_count | 12 |
| total_experiment_count | 108 |
| updated_experiment_count | 108 |
| problem_count | 0 |
| semantic_status | executable_campaign_config_with_family_specific_perturbations |

## Connected configs

| Batch | Family | Severity | Experiments | Perturbation plan | Problems |
| --- | --- | --- | ---: | --- | ---: |
| campaign_combined_delay_light_batch | combined_delay | light | 9 | `data/perturbations/campaign_plans/campaign_combined_delay_light_perturbation_plan.json` | 0 |
| campaign_combined_delay_moderate_batch | combined_delay | moderate | 9 | `data/perturbations/campaign_plans/campaign_combined_delay_moderate_perturbation_plan.json` | 0 |
| campaign_combined_delay_severe_batch | combined_delay | severe | 9 | `data/perturbations/campaign_plans/campaign_combined_delay_severe_perturbation_plan.json` | 0 |
| campaign_reassignment_opportunity_light_batch | reassignment_opportunity | light | 9 | `data/perturbations/campaign_plans/campaign_reassignment_opportunity_light_perturbation_plan.json` | 0 |
| campaign_reassignment_opportunity_moderate_batch | reassignment_opportunity | moderate | 9 | `data/perturbations/campaign_plans/campaign_reassignment_opportunity_moderate_perturbation_plan.json` | 0 |
| campaign_reassignment_opportunity_severe_batch | reassignment_opportunity | severe | 9 | `data/perturbations/campaign_plans/campaign_reassignment_opportunity_severe_perturbation_plan.json` | 0 |
| campaign_service_delay_only_light_batch | service_delay_only | light | 9 | `data/perturbations/campaign_plans/campaign_service_delay_only_light_perturbation_plan.json` | 0 |
| campaign_service_delay_only_moderate_batch | service_delay_only | moderate | 9 | `data/perturbations/campaign_plans/campaign_service_delay_only_moderate_perturbation_plan.json` | 0 |
| campaign_service_delay_only_severe_batch | service_delay_only | severe | 9 | `data/perturbations/campaign_plans/campaign_service_delay_only_severe_perturbation_plan.json` | 0 |
| campaign_travel_delay_only_light_batch | travel_delay_only | light | 9 | `data/perturbations/campaign_plans/campaign_travel_delay_only_light_perturbation_plan.json` | 0 |
| campaign_travel_delay_only_moderate_batch | travel_delay_only | moderate | 9 | `data/perturbations/campaign_plans/campaign_travel_delay_only_moderate_perturbation_plan.json` | 0 |
| campaign_travel_delay_only_severe_batch | travel_delay_only | severe | 9 | `data/perturbations/campaign_plans/campaign_travel_delay_only_severe_perturbation_plan.json` | 0 |

## Conservative interpretation

The executable campaign configs now point to family-specific perturbation plans instead of reusing only the sample perturbation templates.

This is still not the final scientific campaign. It is the next executable validation layer, suitable for checking whether all campaign batches can run without contaminating sample outputs.
