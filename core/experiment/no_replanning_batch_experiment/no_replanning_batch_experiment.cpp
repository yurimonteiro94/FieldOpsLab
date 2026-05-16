#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"

#include <filesystem>
#include <iomanip>
#include <iostream>

#include "core/analysis/batch_ranking/batch_ranking_config_validator/batch_ranking_config_validator.h"
#include "core/experiment/no_replanning_batch_result_validator/no_replanning_batch_result_validator.h"
#include "core/io/no_replanning_batch_aggregate_csv_writer/no_replanning_batch_aggregate_csv_writer.h"
#include "core/io/no_replanning_batch_overview_csv_writer/no_replanning_batch_overview_csv_writer.h"
#include "core/io/no_replanning_batch_ranking_csv_writer/no_replanning_batch_ranking_csv_writer.h"
#include "core/io/no_replanning_batch_recommendation_csv_writer/no_replanning_batch_recommendation_csv_writer.h"
#include "core/io/no_replanning_batch_result_json_writer/no_replanning_batch_result_json_writer.h"
#include "core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.h"

int NoReplanningBatchExperimentResult::experiment_count() const {
    return static_cast<int>(results.size());
}

static void remove_existing_output_file(const std::string& output_path) {
    if (!output_path.empty()) {
        std::filesystem::remove(output_path);
    }
}

static double calculate_completion_percent(
    int completed_experiment_count,
    int configured_experiment_count
) {
    if (configured_experiment_count <= 0) {
        return 100.0;
    }

    return
        100.0 *
        static_cast<double>(completed_experiment_count) /
        static_cast<double>(configured_experiment_count);
}

static bool calculate_is_complete(
    int completed_experiment_count,
    int configured_experiment_count
) {
    return completed_experiment_count >= configured_experiment_count;
}

static void update_batch_completion(
    NoReplanningBatchExperimentResult& batch_result
) {
    batch_result.completed_experiment_count =
        batch_result.experiment_count();

    batch_result.completion_percent =
        calculate_completion_percent(
            batch_result.completed_experiment_count,
            batch_result.configured_experiment_count
        );

    batch_result.is_complete =
        calculate_is_complete(
            batch_result.completed_experiment_count,
            batch_result.configured_experiment_count
        );
}

static void update_batch_output_flags(
    NoReplanningBatchExperimentResult& batch_result,
    const NoReplanningBatchExperimentConfig& config
) {
    batch_result.overview_csv_was_written =
        config.export_overview_csv &&
        !config.overview_csv_output_path.empty();

    batch_result.summary_csv_was_written =
        config.export_summary_csv &&
        !config.summary_csv_output_path.empty();

    batch_result.aggregate_csv_was_written =
        config.export_aggregate_csv &&
        !config.aggregate_csv_output_path.empty();

    batch_result.ranking_csv_was_written =
        config.export_ranking_csv &&
        !config.ranking_csv_output_path.empty();

    batch_result.recommendation_csv_was_written =
        config.export_recommendation_csv &&
        !config.recommendation_csv_output_path.empty();

    batch_result.result_json_was_written =
        config.export_result_json &&
        !config.result_json_output_path.empty();
}

static void print_batch_progress_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& batch_result
) {
    if (!config.verbose) {
        return;
    }

    std::cout
        << "  Progress: "
        << batch_result.completed_experiment_count
        << "/"
        << batch_result.configured_experiment_count
        << " experiments completed ("
        << std::fixed
        << std::setprecision(2)
        << batch_result.completion_percent
        << "%).\n";
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

static void write_batch_overview_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& result
) {
    if (!config.export_overview_csv) {
        return;
    }

    write_no_replanning_batch_overview_csv(
        result,
        config.overview_csv_output_path
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

static void write_batch_ranking_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& result
) {
    if (!config.export_ranking_csv) {
        return;
    }

    write_no_replanning_batch_ranking_csv(
        result,
        config.ranking_csv_output_path
    );
}

static void write_batch_recommendation_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& result
) {
    if (!config.export_recommendation_csv) {
        return;
    }

    write_no_replanning_batch_recommendation_csv(
        result,
        config.recommendation_csv_output_path
    );
}

static void write_batch_result_json_if_enabled(
    const NoReplanningBatchExperimentConfig& config,
    const NoReplanningBatchExperimentResult& result
) {
    if (!config.export_result_json) {
        return;
    }

    write_no_replanning_batch_result_to_json(
        result,
        config.result_json_output_path,
        "no_replanning_batch_result"
    );
}

NoReplanningBatchExperimentResult run_no_replanning_batch_experiment(
    const NoReplanningBatchExperimentConfig& config
) {
    validate_batch_ranking_config(config.ranking_config);

    NoReplanningBatchExperimentResult batch_result;

    batch_result.batch_id = config.batch_id;
    batch_result.name = config.name;
    batch_result.description = config.description;

    batch_result.overview_csv_output_path = config.overview_csv_output_path;
    batch_result.summary_csv_output_path = config.summary_csv_output_path;
    batch_result.aggregate_csv_output_path = config.aggregate_csv_output_path;
    batch_result.ranking_csv_output_path = config.ranking_csv_output_path;
    batch_result.recommendation_csv_output_path =
        config.recommendation_csv_output_path;
    batch_result.result_json_output_path = config.result_json_output_path;

    batch_result.ranking_config = config.ranking_config;

    batch_result.configured_experiment_count =
        static_cast<int>(config.experiments.size());

    update_batch_completion(batch_result);

    if (config.export_overview_csv) {
        remove_existing_output_file(config.overview_csv_output_path);
    }

    if (config.export_summary_csv) {
        remove_existing_output_file(config.summary_csv_output_path);
    }

    if (config.export_aggregate_csv) {
        remove_existing_output_file(config.aggregate_csv_output_path);
    }

    if (config.export_ranking_csv) {
        remove_existing_output_file(config.ranking_csv_output_path);
    }

    if (config.export_recommendation_csv) {
        remove_existing_output_file(config.recommendation_csv_output_path);
    }

    if (config.export_result_json) {
        remove_existing_output_file(config.result_json_output_path);
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

        update_batch_completion(batch_result);

        write_batch_summary_row_if_enabled(
            config,
            experiment_result,
            append_summary_row
        );

        append_summary_row = true;

        print_batch_progress_if_enabled(config, batch_result);
    }

    update_batch_output_flags(batch_result, config);

    validate_no_replanning_batch_result(batch_result);

    write_batch_aggregate_if_enabled(config, batch_result);
    write_batch_ranking_if_enabled(config, batch_result);
    write_batch_recommendation_if_enabled(config, batch_result);
    write_batch_overview_if_enabled(config, batch_result);
    write_batch_result_json_if_enabled(config, batch_result);

    return batch_result;
}