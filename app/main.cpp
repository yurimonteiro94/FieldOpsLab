#include <exception>
#include <iostream>

#include "core/experiment/no_replanning_experiment/no_replanning_experiment.h"

static NoReplanningExperimentConfig build_config_from_arguments(
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

int main(int argc, char* argv[]) {
    try {
        NoReplanningExperimentConfig config =
            build_config_from_arguments(argc, argv);

        run_no_replanning_experiment(config);

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}