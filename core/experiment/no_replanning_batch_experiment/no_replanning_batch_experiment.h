#pragma once

#include <string>
#include <vector>

#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

struct NoReplanningBatchExperimentConfig {
    std::vector<NoReplanningExperimentConfig> experiments;

    std::string summary_csv_output_path =
        "data/results/no_replanning_batch_summary.csv";

    bool verbose = false;
    bool export_individual_results = false;
    bool export_summary_csv = true;
};

struct NoReplanningBatchExperimentResult {
    std::vector<NoReplanningExperimentResult> results;

    int experiment_count() const;
};

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
);