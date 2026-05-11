#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

#include <iostream>

#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"

int NoReplanningBatchExperimentResult::experiment_count() const {
    return static_cast<int>(results.size());
}

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
) {
    NoReplanningBatchExperimentResult batch_result;

    batch_result.batch_id = config.batch_id;
    batch_result.name = config.name;
    batch_result.description = config.description;

    if (config.verbose) {
        std::cout << "Running no-replanning batch experiment...\n";
        std::cout << "  Batch ID: " << config.batch_id << "\n";
        std::cout << "  Experiments: " << config.experiments.size() << "\n";
    }

    bool is_first_summary_row = true;

    for (int i = 0; i < static_cast<int>(config.experiments.size()); ++i) {
        NoReplanningExperimentConfig experiment_config =
            config.experiments[i];

        experiment_config.verbose = config.verbose;
        experiment_config.export_results = config.export_individual_results;

        if (config.verbose) {
            std::cout << "\nRunning batch item "
                      << (i + 1)
                      << " of "
                      << config.experiments.size()
                      << "...\n\n";
        }

        NoReplanningExperimentResult result =
            run_no_replanning_experiment(experiment_config);

        if (config.export_summary_csv) {
            write_no_replanning_experiment_summary_to_csv(
                result,
                config.summary_csv_output_path,
                is_first_summary_row,
                !is_first_summary_row
            );

            is_first_summary_row = false;
        }

        batch_result.results.push_back(result);
    }

    if (config.verbose) {
        std::cout << "\nNo-replanning batch experiment finished.\n";
        std::cout << "  Completed experiments: "
                  << batch_result.experiment_count()
                  << "\n";

        if (config.export_summary_csv) {
            std::cout << "  Summary CSV written to: "
                      << config.summary_csv_output_path
                      << "\n";
        }
    }

    return batch_result;
}