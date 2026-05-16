# FieldOps Lab executed campaign batch result path check

Result JSON: `data\results\campaign_batches\campaign_travel_delay_only_light_batch_result.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | no |
| problem_count | 4 |
| expected_result_dir | `data\results\campaign_batches` |

## Output path checks

| Output key | Path | Under expected dir | Written | Problems |
| --- | --- | --- | --- | --- |
| overview_csv_output_path | `data\results\sample_no_replanning_batch_overview_001.csv` | no | yes | Path still points to sample batch output.; Path is not under expected campaign result directory. |
| summary_csv_output_path | `data\results\campaign_batches\campaign_travel_delay_only_light_batch_summary.csv` | yes | yes | none |
| aggregate_csv_output_path | `data\results\campaign_batches\campaign_travel_delay_only_light_batch_aggregate_summary.csv` | yes | yes | none |
| ranking_csv_output_path | `data\results\campaign_batches\campaign_travel_delay_only_light_batch_ranking.csv` | yes | yes | none |
| recommendation_csv_output_path | `data\results\sample_no_replanning_batch_recommendation_001.csv` | no | yes | Path still points to sample batch output.; Path is not under expected campaign result directory. |
| result_json_output_path | `data\results\campaign_batches\campaign_travel_delay_only_light_batch_result.json` | yes | yes | none |

## Conservative interpretation

The executed batch result still reports one or more unsafe or stale output paths. This means the generated config may be correct, but the C++ loader or execution layer is probably not loading every output path field yet.
