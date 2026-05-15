#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

#include <filesystem>
#include <iostream>

#include "core/io/no_replanning_batch_aggregate_csv_writer/no_replanning_batch_aggregate_csv_writer.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"

int NoReplanningBatchExperimentResult::experiment_count() const {
    return static_cast<int>(results.size());
}

static void remove_existing_output_file(const std::string& output_path) {
    if (!output_path.empty()) {
        std::filesystem::remove(output_path);
    }
}

static NoReplanningExperimentConfig prepare_experiment_config_for_batch(
    const NoReplanningBatchExperimentConfig& batch_config,
    const NoReplanningExperimentConfig& experiment_config
) {
    NoReplanningExperimentConfig prepared_config = experiment_config;

    prepared_config.verbose = batch_config.verbose;
    prepared_config.export_results = batch_config.export_individual_results;

    return prepared_config;
}

static void write_batch_summary_row_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningExperimentResult& result,
    bool append
) {
    if (!config.export_summary_csv) {
        return;
    }

    write_no_replanning_experiment_summary_to_csv(
        result,
        config.summary_csv_output_path,
        append
    );
}

static void write_batch_aggregate_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& result
) {
    if (!config.export_aggregate_csv) {
        return;
    }

    write_no_replanning_batch_aggregate_csv(
        result,
        config.aggregate_csv_output_path
    );
}

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
) {
    NoReplanningBatchExperimentResult batch_result;

    batch_result.batch_id = config.batch_id;
    batch_result.name = config.name;
    batch_result.description = config.description;
    batch_result.summary_csv_output_path = config.summary_csv_output_path;
    batch_result.aggregate_csv_output_path = config.aggregate_csv_output_path;

    if (config.export_summary_csv) {
        remove_existing_output_file(config.summary_csv_output_path);
    }

    if (config.export_aggregate_csv) {
        remove_existing_output_file(config.aggregate_csv_output_path);
    }

    bool append_summary_row = false;

    for (const auto& experiment_config : config.experiments) {
        NoReplanningExperimentConfig prepared_config =
            prepare_experiment_config_for_batch(
                config,
                experiment_config
            );

        NoReplanningExperimentResult experiment_result =
            run_no_replanning_experiment(prepared_config);

        batch_result.results.push_back(experiment_result);

        write_batch_summary_row_if_enabled(
            config,
            experiment_result,
            append_summary_row
        );

        append_summary_row = true;
    }

    batch_result.summary_csv_was_written =
        config.export_summary_csv &&
        !config.summary_csv_output_path.empty();

    write_batch_aggregate_if_enabled(config, batch_result);

    batch_result.aggregate_csv_was_written =
        config.export_aggregate_csv &&
        !config.aggregate_csv_output_path.empty();

    if (config.verbose) {
        std::cout << "Batch experiment finished.\n";
        std::cout << "  Batch ID: " << batch_result.batch_id << "\n";
        std::cout << "  Experiments: "
                  << batch_result.experiment_count() << "\n";

        if (batch_result.summary_csv_was_written) {
            std::cout << "  Summary CSV written to: "
                      << batch_result.summary_csv_output_path << "\n";
        }

        if (batch_result.aggregate_csv_was_written) {
            std::cout << "  Aggregate CSV written to: "
                      << batch_result.aggregate_csv_output_path << "\n";
        }
    }

    return batch_result;
}