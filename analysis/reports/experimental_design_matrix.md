# FieldOps Lab experimental design matrix

This report defines the first broad experimental design matrix for the scientific validation phase.

It converts the current diagnostic state into planned, reproducible experiments.

## Overall result

| Field | Value |
| --- | --- |
| scientific_stage | experimental_design |
| experiment_count | 648 |
| scenario_count | 108 |
| instance_size_level_count | 3 |
| demand_density_level_count | 3 |
| delay_family_count | 4 |
| severity_count | 3 |
| policy_count | 2 |
| replication_count | 3 |
| all_experiments_reproducible_from_explicit_factors | yes |

## Controlled factors

| Factor | Levels |
| --- | --- |
| instance_size | small; medium; large |
| demand_density | sparse; moderate; dense |
| delay_family | travel_delay_only; service_delay_only; combined_delay; reassignment_opportunity |
| delay_severity | light; moderate; severe |
| policy | no_replanning_policy_v1; threshold_delay_replanning_policy_v1 |
| random_seed | 101; 202; 303 |

## Sample planned experiments

| Experiment | Size | Density | Delay family | Severity | Policy | Seed |
| --- | --- | --- | --- | --- | --- | --- |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_no_replanning_policy_v1_replication_01 | small | sparse | travel_delay_only | light | no_replanning_policy_v1 | 101 |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_no_replanning_policy_v1_replication_02 | small | sparse | travel_delay_only | light | no_replanning_policy_v1 | 202 |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_no_replanning_policy_v1_replication_03 | small | sparse | travel_delay_only | light | no_replanning_policy_v1 | 303 |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_threshold_delay_replanning_policy_v1_replication_01 | small | sparse | travel_delay_only | light | threshold_delay_replanning_policy_v1 | 101 |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_threshold_delay_replanning_policy_v1_replication_02 | small | sparse | travel_delay_only | light | threshold_delay_replanning_policy_v1 | 202 |
| size_small_density_sparse_delay_travel_delay_only_severity_light_policy_threshold_delay_replanning_policy_v1_replication_03 | small | sparse | travel_delay_only | light | threshold_delay_replanning_policy_v1 | 303 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_no_replanning_policy_v1_replication_01 | small | sparse | travel_delay_only | moderate | no_replanning_policy_v1 | 101 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_no_replanning_policy_v1_replication_02 | small | sparse | travel_delay_only | moderate | no_replanning_policy_v1 | 202 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_no_replanning_policy_v1_replication_03 | small | sparse | travel_delay_only | moderate | no_replanning_policy_v1 | 303 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_threshold_delay_replanning_policy_v1_replication_01 | small | sparse | travel_delay_only | moderate | threshold_delay_replanning_policy_v1 | 101 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_threshold_delay_replanning_policy_v1_replication_02 | small | sparse | travel_delay_only | moderate | threshold_delay_replanning_policy_v1 | 202 |
| size_small_density_sparse_delay_travel_delay_only_severity_moderate_policy_threshold_delay_replanning_policy_v1_replication_03 | small | sparse | travel_delay_only | moderate | threshold_delay_replanning_policy_v1 | 303 |

## Conservative interpretation

This matrix defines a reproducible experimental design. It does not prove scientific validity by itself. It prepares the project for replicated experiments and later statistical comparison.
