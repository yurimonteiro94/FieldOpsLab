# FieldOps Lab final diagnostic ranking integration quality check

Final JSON: `analysis\reports\campaign_final_diagnostic_report.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| json_row_count | 12 |
| csv_row_count | 12 |
| ranking_profile_count | 4 |
| scenario_summary_count | 12 |
| recommendation_count | 48 |
| ranking_row_count | 144 |
| sensitive_to_ranking_profile_count | 2 |

## Stability counts

| Stability class | Count |
| --- | ---: |
| same_policy_different_class | 2 |
| stable_across_profiles | 10 |

## Problems

- None.

## Warnings

- None.

## Conservative interpretation

The final diagnostic report contains and exposes ranking sensitivity information consistently in JSON, Markdown, and CSV.

This still does not prove the scientific correctness of any ranking profile. It only verifies that the integration layer is present and internally consistent.
