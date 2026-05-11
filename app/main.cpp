#include <exception>
#include <iostream>
#include <string>

#include "core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.h"
#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"
#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"

static NoReplanningExperimentConfig build_single_experiment_config_from_arguments(
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

static int run_single_experiment_mode(int argc, char* argv[]) {
    NoReplanningExperimentConfig config =
        build_single_experiment_config_from_arguments(argc, argv);

    run_no_replanning_experiment(config);

    return 0;
}

static int run_batch_experiment_mode(int argc, char* argv[]) {
    std::string batch_config_path =
        "data/experiments/sample_no_replanning_batch_001.json";

    if (argc >= 3) {
        batch_config_path = argv[2];
    }

    std::cout << "FieldOps Lab - batch experiment mode started.\n";
    std::cout << "Loading batch config: " << batch_config_path << "\n\n";

    NoReplanningBatchExperimentConfig config =
        load_no_replanning_batch_config_from_json(batch_config_path);

    NoReplanningBatchExperimentResult result =
        run_no_replanning_batch_experiment(config);

    std::cout << "Batch experiment finished.\n";
    std::cout << "  Batch ID: " << result.batch_id << "\n";
    std::cout << "  Experiments: " << result.experiment_count() << "\n";

    if (config.export_summary_csv) {
        std::cout << "  Summary CSV written to: "
                  << config.summary_csv_output_path
                  << "\n";
    }

    return 0;
}

int main(int argc, char* argv[]) {
    try {
        if (argc >= 2) {
            std::string mode = argv[1];

            if (mode == "batch") {
                return run_batch_experiment_mode(argc, argv);
            }
        }

        return run_single_experiment_mode(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}