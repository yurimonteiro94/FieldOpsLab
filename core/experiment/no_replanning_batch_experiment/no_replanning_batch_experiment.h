#pragma once

#include <string>
#include <vector>

#include "core/analysis/batch_ranking/batch_ranking_config.h"
#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

struct NoReplanningBatchExperimentConfig {
    std::string batch_id = "sample_no_replanning_batch";
    std::string name = "Sample no-replanning batch";
    std::string description = "Sample no-replanning batch experiment.";

    std::string overview_csv_output_path =
        "data/results/sample_no_replanning_batch_overview_001.csv";

    std::string summary_csv_output_path =
        "data/results/sample_no_replanning_batch_summary_001.csv";

    std::string aggregate_csv_output_path =
        "data/results/sample_no_replanning_batch_aggregate_summary_001.csv";

    std::string ranking_csv_output_path =
        "data/results/sample_no_replanning_batch_ranking_001.csv";

    std::string recommendation_csv_output_path =
        "data/results/sample_no_replanning_batch_recommendation_001.csv";

    std::string result_json_output_path =
        "data/results/sample_no_replanning_batch_result_001.json";

    bool verbose = true;
    bool export_individual_results = false;
    bool export_overview_csv = true;
    bool export_summary_csv = true;
    bool export_aggregate_csv = true;
    bool export_ranking_csv = true;
    bool export_recommendation_csv = true;
    bool export_result_json = true;

    BatchRankingConfig ranking_config;

    std::vector<NoReplanningExperimentConfig> experiments;
};

struct NoReplanningBatchExperimentResult {
    std::string batch_id;
    std::string name;
    std::string description;

    std::string overview_csv_output_path;
    std::string summary_csv_output_path;
    std::string aggregate_csv_output_path;
    std::string ranking_csv_output_path;
    std::string recommendation_csv_output_path;
    std::string result_json_output_path;

    bool overview_csv_was_written = false;
    bool summary_csv_was_written = false;
    bool aggregate_csv_was_written = false;
    bool ranking_csv_was_written = false;
    bool recommendation_csv_was_written = false;
    bool result_json_was_written = false;

    BatchRankingConfig ranking_config;

    int configured_experiment_count = 0;
    int completed_experiment_count = 0;
    double completion_percent = 0.0;
    bool is_complete = false;

    std::vector<NoReplanningExperimentResult> results;

    int experiment_count() const;
};

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
);