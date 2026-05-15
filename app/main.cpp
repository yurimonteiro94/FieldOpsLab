#include <exception>
#include <iostream>
#include <string>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"

static NoReplanningExperimentConfig build_single_experiment_config(
    int argc,
    char* argv[]
) {
    NoReplanningExperimentConfig config;

    if (argc >= 2) {
        config.instance_path = argv[1];
    }

    if (argc >= 3) {
        config.perturbation_plan_path = argv[2];
    }

    if (argc >= 4) {
        config.planned_solution_output_path = argv[3];
    }

    if (argc >= 5) {
        config.planned_timeline_output_path = argv[4];
    }

    if (argc >= 6) {
        config.executed_solution_output_path = argv[5];
    }

    if (argc >= 7) {
        config.executed_timeline_output_path = argv[6];
    }

    if (argc >= 8) {
        config.comparison_output_path = argv[7];
    }

    if (argc >= 9) {
        config.experiment_result_output_path = argv[8];
    }

    if (argc >= 10) {
        config.experiment_summary_csv_output_path = argv[9];
    }

    return config;
}

static int run_batch_mode(int argc, char* argv[]) {
    std::string batch_config_path =
        "data/experiments/sample_no_replanning_batch_001.json";

    if (argc >= 3) {
        batch_config_path = argv[2];
    }

    std::cout << "FieldOps Lab - batch experiment mode started.\n";
    std::cout << "Loading batch config: " << batch_config_path << "\n\n";

    NoReplanningBatchExperimentConfig batch_config =
        load_no_replanning_batch_config_from_json(batch_config_path);

    NoReplanningBatchExperimentResult batch_result =
        run_no_replanning_batch_experiment(batch_config);

    std::cout << "\nBatch experiment finished.\n";
    std::cout << "  Batch ID: " << batch_result.batch_id << "\n";
    std::cout << "  Experiments: " << batch_result.experiment_count() << "\n";

    if (batch_result.summary_csv_was_written) {
        std::cout << "  Summary CSV written to: "
                  << batch_result.summary_csv_output_path << "\n";
    }

    if (batch_result.aggregate_csv_was_written) {
        std::cout << "  Aggregate CSV written to: "
                  << batch_result.aggregate_csv_output_path << "\n";
    }

    if (batch_result.ranking_csv_was_written) {
        std::cout << "  Ranking CSV written to: "
                  << batch_result.ranking_csv_output_path << "\n";
    }

    if (batch_result.result_json_was_written) {
        std::cout << "  Result JSON written to: "
                  << batch_result.result_json_output_path << "\n";
    }

    return 0;
}

static int run_single_experiment_mode(int argc, char* argv[]) {
    NoReplanningExperimentConfig config =
        build_single_experiment_config(argc, argv);

    run_no_replanning_experiment(config);

    return 0;
}

int main(int argc, char* argv[]) {
    try {
        if (argc >= 2 && std::string(argv[1]) == "batch") {
            return run_batch_mode(argc, argv);
        }

        return run_single_experiment_mode(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}