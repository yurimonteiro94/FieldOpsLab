# FieldOps Lab analysis output quality check

Manifest: `analysis\reports\sample_no_replanning_batch_001_analysis_manifest.json`

## Overall result

| Field | Value |
| --- | --- |
| all_required_checks_passed | no |
| problem_count | 2 |
| warning_count | 1 |
| checked_file_count | 8 |

## File checks

| Label | Exists | Size bytes | Manifest status | Expected text found | Problems |
| --- | --- | ---: | --- | --- | --- |
| summary_text | yes | 2786 | ok | yes | none |
| main_markdown_report | yes | 2559 | ok | no | Expected text not found: # FieldOps Lab batch report |
| recommendation_audit | yes | 2559 | ok | yes | none |
| ranking_sensitivity | yes | 7604 | ok | yes | none |
| scenario_descriptors_markdown | yes | 5158 | ok | yes | none |
| scenario_descriptors_csv | yes | 1552 | ok | yes | none |
| analysis_index | yes | 2238 | ok | yes | none |
| pipeline_log | yes | 5157 | ok | yes | none |

## Duplicate content checks

- ERROR: Duplicate file content detected. labels=['main_markdown_report', 'recommendation_audit']; paths=['analysis\\reports\\sample_no_replanning_batch_001_report.md', 'analysis\\reports\\sample_no_replanning_batch_001_audit.md']

## Same-size warnings

- WARNING: Suspicious same file size detected. size_bytes=2559; labels=['main_markdown_report', 'recommendation_audit']. This is not necessarily wrong, but it should be reviewed.

## Conservative interpretation

The generated analysis outputs did not pass the structural quality check. Do not use these reports as evidence until the listed problems are corrected.
