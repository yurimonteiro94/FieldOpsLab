#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/io/no_replanning_batch_full_config_json_loader/no_replanning_batch_full_config_json_loader.h"

#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

static void print_usage() {
    std::cout
        << "FieldOps Lab\n"
        << "\n"
        << "Usage:\n"
        << "  fieldops_lab.exe batch <batch_config_json_path>\n";
}

static void print_written_output(
    const std::string& label,
    const std::string& output_path
) {
    std::cout
        << "  "
        << label
        << " written to: "
        << output_path
        << "\n";
}

static int run_batch_mode(const std::string& config_path) {
    std::cout << "FieldOps Lab - batch experiment mode started.\n";
    std::cout << "Loading batch config: " << config_path << "\n\n";

    NoReplanningBatchFullConfigLoadResult config_load_result =
        load_no_replanning_batch_full_config_from_json(config_path);

    NoReplanningBatchExperimentConfig config =
        config_load_result.config;

    if (
        config_load_result.custom_ranking_config_was_loaded &&
        config.verbose
    ) {
        std::cout
            << "Custom ranking config loaded: "
            << config.ranking_config.ranking_config_id
            << "\n\n";
    }

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    std::cout << "\n";
    std::cout << "Batch experiment finished.\n";
    std::cout << "  Batch ID: " << result.batch_id << "\n";
    std::cout << "  Experiments: " << result.experiment_count() << "\n";
    std::cout
        << "  Completed: "
        << result.completed_experiment_count
        << "/"
        << result.configured_experiment_count
        << " ("
        << std::fixed
        << std::setprecision(2)
        << result.completion_percent
        << "%)\n";

    if (result.overview_csv_was_written) {
        print_written_output(
            "Overview CSV",
            result.overview_csv_output_path
        );
    }

    if (result.summary_csv_was_written) {
        print_written_output(
            "Summary CSV",
            result.summary_csv_output_path
        );
    }

    if (result.aggregate_csv_was_written) {
        print_written_output(
            "Aggregate CSV",
            result.aggregate_csv_output_path
        );
    }

    if (result.ranking_csv_was_written) {
        print_written_output(
            "Ranking CSV",
            result.ranking_csv_output_path
        );
    }

    if (result.recommendation_csv_was_written) {
        print_written_output(
            "Recommendation CSV",
            result.recommendation_csv_output_path
        );
    }

    if (result.result_json_was_written) {
        print_written_output(
            "Result JSON",
            result.result_json_output_path
        );
    }

    return 0;
}

int main(int argc, char* argv[]) {
    try {
        if (argc < 2) {
            print_usage();
            return 1;
        }

        const std::string mode = argv[1];

        if (mode == "batch") {
            if (argc < 3) {
                print_usage();
                return 1;
            }

            return run_batch_mode(argv[2]);
        }

        std::cout << "Unknown mode: " << mode << "\n\n";
        print_usage();

        return 1;
    } catch (const std::exception& exception) {
        std::cout << "Error: " << exception.what() << "\n";
        return 1;
    }
}