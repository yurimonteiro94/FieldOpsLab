#pragma once

#include <string>
#include <vector>

#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

struct NoReplanningBatchExperimentConfig {
    std::string batch_id = "sample_no_replanning_batch";
    std::string name = "Sample no-replanning batch";
    std::string description = "Sample no-replanning batch experiment.";

    std::string summary_csv_output_path =
        "data/results/sample_no_replanning_batch_summary_001.csv";

    std::string aggregate_csv_output_path =
        "data/results/sample_no_replanning_batch_aggregate_summary_001.csv";

    std::string result_json_output_path =
        "data/results/sample_no_replanning_batch_result_001.json";

    bool verbose = true;
    bool export_individual_results = false;
    bool export_summary_csv = true;
    bool export_aggregate_csv = true;
    bool export_result_json = true;

    std::vector<NoReplanningExperimentConfig> experiments;
};

struct NoReplanningBatchExperimentResult {
    std::string batch_id;
    std::string name;
    std::string description;

    std::string summary_csv_output_path;
    std::string aggregate_csv_output_path;
    std::string result_json_output_path;

    bool summary_csv_was_written = false;
    bool aggregate_csv_was_written = false;
    bool result_json_was_written = false;

    std::vector<NoReplanningExperimentResult> results;

    int experiment_count() const;
};

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
);