# FieldOps Lab campaign perturbation plan quality check

Index JSON: `analysis\reports\campaign_perturbation_plan_index.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | no |
| problem_count | 12 |
| warning_count | 0 |
| checked_plan_count | 12 |
| expected_plan_count | 12 |
| generated_perturbation_count | 15 |
| semantic_status | family_specific_template_based_perturbation_plan |
| fuzzy_logic_status | not_used_in_main_pipeline |

## Plan checks

| Plan | Family | Severity | Exists | Travel delay | Service delay | Problems |
| --- | --- | --- | --- | ---: | ---: | --- |
| campaign_combined_delay_light_perturbation_plan | combined_delay | light | yes | 17 | 7 | Unexpected travel perturbation count. expected=1; actual=2; Unexpected total travel delay. expected=10; actual=17 |
| campaign_combined_delay_moderate_perturbation_plan | combined_delay | moderate | yes | 85 | 35 | Unexpected travel perturbation count. expected=1; actual=2; Unexpected total travel delay. expected=50; actual=85 |
| campaign_combined_delay_severe_perturbation_plan | combined_delay | severe | yes | 153 | 63 | Unexpected travel perturbation count. expected=1; actual=2; Unexpected total travel delay. expected=90; actual=153 |
| campaign_reassignment_opportunity_light_perturbation_plan | reassignment_opportunity | light | yes | 10 | 0 | none |
| campaign_reassignment_opportunity_moderate_perturbation_plan | reassignment_opportunity | moderate | yes | 50 | 0 | none |
| campaign_reassignment_opportunity_severe_perturbation_plan | reassignment_opportunity | severe | yes | 90 | 0 | none |
| campaign_service_delay_only_light_perturbation_plan | service_delay_only | light | yes | 7 | 7 | Unexpected travel perturbation count. expected=0; actual=1; Unexpected total travel delay. expected=0; actual=7 |
| campaign_service_delay_only_moderate_perturbation_plan | service_delay_only | moderate | yes | 35 | 35 | Unexpected travel perturbation count. expected=0; actual=1; Unexpected total travel delay. expected=0; actual=35 |
| campaign_service_delay_only_severe_perturbation_plan | service_delay_only | severe | yes | 63 | 63 | Unexpected travel perturbation count. expected=0; actual=1; Unexpected total travel delay. expected=0; actual=63 |
| campaign_travel_delay_only_light_perturbation_plan | travel_delay_only | light | yes | 10 | 0 | none |
| campaign_travel_delay_only_moderate_perturbation_plan | travel_delay_only | moderate | yes | 50 | 0 | none |
| campaign_travel_delay_only_severe_perturbation_plan | travel_delay_only | severe | yes | 90 | 0 | none |

## Problems

- ERROR: Unexpected travel perturbation count. expected=1; actual=2
- ERROR: Unexpected total travel delay. expected=10; actual=17
- ERROR: Unexpected travel perturbation count. expected=1; actual=2
- ERROR: Unexpected total travel delay. expected=50; actual=85
- ERROR: Unexpected travel perturbation count. expected=1; actual=2
- ERROR: Unexpected total travel delay. expected=90; actual=153
- ERROR: Unexpected travel perturbation count. expected=0; actual=1
- ERROR: Unexpected total travel delay. expected=0; actual=7
- ERROR: Unexpected travel perturbation count. expected=0; actual=1
- ERROR: Unexpected total travel delay. expected=0; actual=35
- ERROR: Unexpected travel perturbation count. expected=0; actual=1
- ERROR: Unexpected total travel delay. expected=0; actual=63

## Warnings

- None.

## Conservative interpretation

The campaign perturbation plans failed the quality check. Do not connect them to executable batch configs until the listed problems are fixed.

Passing this check does not prove scientific validity. It only confirms that the generated perturbation plans match the intended family and severity structure.
