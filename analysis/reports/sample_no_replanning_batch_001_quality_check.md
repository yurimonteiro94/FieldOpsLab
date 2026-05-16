# FieldOps Lab analysis output quality check

Manifest: `analysis\reports\sample_no_replanning_batch_001_analysis_manifest.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | yes |
| problem_count | 0 |
| warning_count | 0 |
| checked_file_count | 8 |

## File checks

| Label | Exists | Size bytes | Manifest status | Expected text found | Problems |
| --- | --- | ---: | --- | --- | --- |
| summary_text | yes | 2786 | ok | yes | none |
| main_markdown_report | yes | 3632 | ok | yes | none |
| recommendation_audit | yes | 2559 | ok | yes | none |
| ranking_sensitivity | yes | 7604 | ok | yes | none |
| scenario_descriptors_markdown | yes | 5158 | ok | yes | none |
| scenario_descriptors_csv | yes | 1552 | ok | yes | none |
| analysis_index | yes | 2238 | ok | yes | none |
| pipeline_log | yes | 5157 | ok | yes | none |

## Duplicate content checks

- No exact duplicate file content detected.

## Same-size warnings

- No suspicious same-size files detected.

## Conservative interpretation

The generated analysis outputs passed the structural quality check. This does not prove the scientific validity of the experiment, but it reduces the risk of using missing, empty, mislabeled, or accidentally duplicated reports.
