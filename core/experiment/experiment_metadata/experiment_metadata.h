#pragma once

#include <string>

struct ExperimentMetadata {
    std::string experiment_id = "sample_no_replanning_experiment_001";
    std::string scenario_id = "sample_delay_scenario_001";

    int replication_id = 1;
    int seed = 0;

    std::string notes;
};

std::string build_experiment_run_label(
    const ExperimentMetadata& metadata
);