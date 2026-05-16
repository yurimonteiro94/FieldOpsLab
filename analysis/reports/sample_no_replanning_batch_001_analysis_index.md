# FieldOps Lab batch analysis index

Batch ID: `sample_no_replanning_batch_001`

Batch name: Sample no-replanning and replanning batch

## Purpose

This file is an index for the generated analysis reports. It centralizes the post-processing outputs produced from one batch result JSON.

## Batch status

| Field | Value |
| --- | --- |
| configured_experiment_count | 12 |
| completed_experiment_count | 12 |
| completion_percent | 100.0 |
| is_complete | yes |
| recommendation_count | 4 |

## Ranking status

| Field | Value |
| --- | --- |
| ranking_config_id | `default_objective_delta_ranking_v1` |
| ranking_score_definition | Lower is better. Current ranking_score equals mean_delta_objective_value. |

## Generated reports

| Report | Path | Status |
| --- | --- | --- |
| summary_text | `analysis\reports\sample_no_replanning_batch_001_summary.txt` | ok |
| main_markdown_report | `analysis\reports\sample_no_replanning_batch_001_report.md` | ok |
| recommendation_audit | `analysis\reports\sample_no_replanning_batch_001_audit.md` | ok |
| ranking_sensitivity | `analysis\reports\sample_no_replanning_batch_001_ranking_sensitivity.md` | ok |
| scenario_descriptors_markdown | `analysis\reports\sample_no_replanning_batch_001_scenario_descriptors.md` | ok |
| scenario_descriptors_csv | `analysis\reports\sample_no_replanning_batch_001_scenario_descriptors.csv` | ok |
| analysis_manifest | `analysis\reports\sample_no_replanning_batch_001_analysis_manifest.json` | ok |
| pipeline_log | `analysis\reports\sample_no_replanning_batch_001_pipeline_log.txt` | ok |

## Recommended reading order

1. Summary text
2. Main markdown report
3. Recommendation audit
4. Ranking sensitivity
5. Scenario descriptors
6. Analysis manifest JSON

## Conservative interpretation

This pipeline does not generate a fuzzy decision report. That is intentional. The current recommended direction is to keep fuzzy logic as a possible future decision layer, not as the main method at this stage.

The current analysis is suitable for validating the experimental pipeline and organizing evidence. It is not yet enough for final research conclusions because the batch is still small and handcrafted.
