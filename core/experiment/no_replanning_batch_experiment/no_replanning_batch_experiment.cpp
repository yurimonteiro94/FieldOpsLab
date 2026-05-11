#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

#include <filesystem>
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

    if (config.export_summary_csv) {
        std::filesystem::remove(config.summary_csv_output_path);
    }

    if (config.verbose) {
        std::cout << "FieldOps Lab - batch experiment mode started.\n";
        std::cout << "Batch ID: " << config.batch_id << "\n";
        std::cout << "Experiments: " << config.experiments.size() << "\n\n";
    }

    bool is_first_summary_row = true;

    for (auto experiment_config : config.experiments) {
        experiment_config.verbose = config.verbose;
        experiment_config.export_results = config.export_individual_results;

        NoReplanningExperimentResult experiment_result =
            run_no_replanning_experiment(experiment_config);

        batch_result.results.push_back(experiment_result);

        if (config.export_summary_csv) {
            const bool append_to_summary = !is_first_summary_row;

            write_no_replanning_experiment_summary_to_csv(
                experiment_result,
                config.summary_csv_output_path,
                append_to_summary
            );

            is_first_summary_row = false;
        }
    }

    if (config.verbose) {
        std::cout << "\nBatch experiment finished.\n";
        std::cout << "  Batch ID: " << batch_result.batch_id << "\n";
        std::cout << "  Experiments: "
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