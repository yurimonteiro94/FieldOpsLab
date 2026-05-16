# FieldOps Lab campaign perturbation plan quality check

Index JSON: `analysis\reports\campaign_perturbation_plan_index.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| checked_plan_count | 12 |
| expected_plan_count | 12 |
| generated_perturbation_count | 15 |
| semantic_status | family_specific_template_based_perturbation_plan |
| fuzzy_logic_status | not_used_in_main_pipeline |

## Plan checks

| Plan | Family | Severity | Exists | Travel delay | Service delay | Problems |
| --- | --- | --- | --- | ---: | ---: | --- |
| campaign_combined_delay_light_perturbation_plan | combined_delay | light | yes | 10 | 7 | none |
| campaign_combined_delay_moderate_perturbation_plan | combined_delay | moderate | yes | 50 | 35 | none |
| campaign_combined_delay_severe_perturbation_plan | combined_delay | severe | yes | 90 | 63 | none |
| campaign_reassignment_opportunity_light_perturbation_plan | reassignment_opportunity | light | yes | 10 | 0 | none |
| campaign_reassignment_opportunity_moderate_perturbation_plan | reassignment_opportunity | moderate | yes | 50 | 0 | none |
| campaign_reassignment_opportunity_severe_perturbation_plan | reassignment_opportunity | severe | yes | 90 | 0 | none |
| campaign_service_delay_only_light_perturbation_plan | service_delay_only | light | yes | 0 | 7 | none |
| campaign_service_delay_only_moderate_perturbation_plan | service_delay_only | moderate | yes | 0 | 35 | none |
| campaign_service_delay_only_severe_perturbation_plan | service_delay_only | severe | yes | 0 | 63 | none |
| campaign_travel_delay_only_light_perturbation_plan | travel_delay_only | light | yes | 10 | 0 | none |
| campaign_travel_delay_only_moderate_perturbation_plan | travel_delay_only | moderate | yes | 50 | 0 | none |
| campaign_travel_delay_only_severe_perturbation_plan | travel_delay_only | severe | yes | 90 | 0 | none |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The campaign perturbation plans passed the structural quality check. They are coherent enough to be connected to executable batch configs.

Passing this check does not prove scientific validity. It only confirms that the generated perturbation plans match the intended family and severity structure.
