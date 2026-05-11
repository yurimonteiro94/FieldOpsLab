#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"

#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static NoReplanningExperimentConfig read_experiment_config_from_json(
    const json& data
) {
    NoReplanningExperimentConfig config;

    config.instance_path =
        data.value("instance_path", config.instance_path);

    config.perturbation_plan_path =
        data.value("perturbation_plan_path", config.perturbation_plan_path);

    config.planned_solution_output_path =
        data.value(
            "planned_solution_output_path",
            config.planned_solution_output_path
        );

    config.planned_timeline_output_path =
        data.value(
            "planned_timeline_output_path",
            config.planned_timeline_output_path
        );

    config.executed_solution_output_path =
        data.value(
            "executed_solution_output_path",
            config.executed_solution_output_path
        );

    config.executed_timeline_output_path =
        data.value(
            "executed_timeline_output_path",
            config.executed_timeline_output_path
        );

    config.comparison_output_path =
        data.value("comparison_output_path", config.comparison_output_path);

    config.experiment_result_output_path =
        data.value(
            "experiment_result_output_path",
            config.experiment_result_output_path
        );

    config.experiment_summary_csv_output_path =
        data.value(
            "experiment_summary_csv_output_path",
            config.experiment_summary_csv_output_path
        );

    return config;
}

NoReplanningBatchExperimentConfig load_no_replanning_batch_config_from_json(
    const std::string& file_path
) {
    std::ifstream file(file_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch config file: " + file_path
        );
    }

    json data;
    file >> data;

    NoReplanningBatchExperimentConfig config;

    config.batch_id =
        data.value("batch_id", config.batch_id);

    config.name =
        data.value("name", config.name);

    config.description =
        data.value("description", config.description);

    config.summary_csv_output_path =
        data.value(
            "summary_csv_output_path",
            config.summary_csv_output_path
        );

    config.verbose =
        data.value("verbose", config.verbose);

    config.export_individual_results =
        data.value(
            "export_individual_results",
            config.export_individual_results
        );

    config.export_summary_csv =
        data.value("export_summary_csv", config.export_summary_csv);

    for (const auto& experiment_data : data.at("experiments")) {
        config.experiments.push_back(
            read_experiment_config_from_json(experiment_data)
        );
    }

    return config;
}