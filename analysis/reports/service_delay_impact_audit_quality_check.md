# FieldOps Lab service delay impact audit quality check

Audit JSON: `analysis\reports\service_delay_impact_audit.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 2 |
| batch_count | 12 |
| csv_row_count | 12 |
| service_only_batch_count | 3 |
| combined_delay_batch_count | 3 |
| visible_but_neutral_and_kept_plan_count | 4 |

## Problems

- None.

## Warnings

- WARNING: Service delay is visible but neutral under current objective/makespan in 4 batch(es).
- WARNING: Audit contains 4 methodological warning(s).

## Conservative interpretation

The service-delay impact audit passed the structural quality check. Any warnings should be treated as methodological findings, not as execution failures.
