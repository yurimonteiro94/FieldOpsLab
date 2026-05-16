#include "core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.h"

#include <fstream>
#include <stdexcept>
#include <string>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static std::string get_optional_string(
    const json& data,
    const std::string& key,
    const std::string& default_value
) {
    if (!data.contains(key)) {
        return default_value;
    }

    if (data.at(key).is_null()) {
        return default_value;
    }

    return data.at(key).get<std::string>();
}

static int get_optional_int(
    const json& data,
    const std::string& key,
    int default_value
) {
    if (!data.contains(key)) {
        return default_value;
    }

    if (data.at(key).is_null()) {
        return default_value;
    }

    return data.at(key).get<int>();
}

static bool get_optional_bool(
    const json& data,
    const std::string& key,
    bool default_value
) {
    if (!data.contains(key)) {
        return default_value;
    }

    if (data.at(key).is_null()) {
        return default_value;
    }

    return data.at(key).get<bool>();
}

static void load_policy_config(
    NoReplanningExperimentConfig& config,
    const json& experiment_data
) {
    config.policy_config.policy_id =
        get_optional_string(
            experiment_data,
            "policy_id",
            config.policy_config.policy_id
        );

    config.policy_config
        .threshold_delay_config
        .max_single_delay_threshold =
            get_optional_int(
                experiment_data,
                "max_single_delay_threshold",
                config.policy_config
                    .threshold_delay_config
                    .max_single_delay_threshold
            );

    config.policy_config
        .threshold_delay_config
        .total_delay_threshold =
            get_optional_int(
                experiment_data,
                "total_delay_threshold",
                config.policy_config
                    .threshold_delay_config
                    .total_delay_threshold
            );
}

static void load_replanning_engine_config(
    NoReplanningExperimentConfig& config,
    const json& experiment_data
) {
    config.replanning_engine_config.method_id =
        get_optional_string(
            experiment_data,
            "replanning_method_id",
            config.replanning_engine_config.method_id
        );

    config.replanning_engine_config.result_id =
        config.metadata.experiment_id + "_replanning_result";
}

static NoReplanningExperimentConfig load_experiment_config_from_json(
    const json& experiment_data
) {
    NoReplanningExperimentConfig config;

    config.metadata.experiment_id =
        get_optional_string(
            experiment_data,
            "experiment_id",
            config.metadata.experiment_id
        );

    config.metadata.scenario_id =
        get_optional_string(
            experiment_data,
            "scenario_id",
            config.metadata.scenario_id
        );

    config.metadata.replication_id =
        get_optional_int(
            experiment_data,
            "replication_id",
            config.metadata.replication_id
        );

    config.metadata.seed =
        get_optional_int(
            experiment_data,
            "seed",
            config.metadata.seed
        );

    config.metadata.notes =
        get_optional_string(
            experiment_data,
            "notes",
            config.metadata.notes
        );

    config.instance_path =
        get_optional_string(
            experiment_data,
            "instance_path",
            config.instance_path
        );

    config.perturbation_plan_path =
        get_optional_string(
            experiment_data,
            "perturbation_plan_path",
            config.perturbation_plan_path
        );

    load_policy_config(config, experiment_data);
    load_replanning_engine_config(config, experiment_data);

    config.replanning_request_output_path =
        "data/results/" +
        config.metadata.experiment_id +
        "_replanning_request.json";

    config.experiment_result_output_path =
        "data/results/" +
        config.metadata.experiment_id +
        "_experiment_result.json";

    config.experiment_summary_csv_output_path =
        "data/results/" +
        config.metadata.experiment_id +
        "_experiment_summary.csv";

    return config;
}

NoReplanningBatchExperimentConfig load_no_replanning_batch_config_from_json(
    const std::string& file_path
) {
    std::ifstream file(file_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open no-replanning batch config JSON file: " +
            file_path
        );
    }

    json data;
    file >> data;

    NoReplanningBatchExperimentConfig config;

    config.batch_id =
        get_optional_string(
            data,
            "batch_id",
            config.batch_id
        );

    config.name =
        get_optional_string(
            data,
            "name",
            config.name
        );

    config.description =
        get_optional_string(
            data,
            "description",
            config.description
        );

    config.overview_csv_output_path =
        get_optional_string(
            data,
            "overview_csv_output_path",
            config.overview_csv_output_path
        );

    config.summary_csv_output_path =
        get_optional_string(
            data,
            "summary_csv_output_path",
            config.summary_csv_output_path
        );

    config.aggregate_csv_output_path =
        get_optional_string(
            data,
            "aggregate_csv_output_path",
            config.aggregate_csv_output_path
        );

    config.ranking_csv_output_path =
        get_optional_string(
            data,
            "ranking_csv_output_path",
            config.ranking_csv_output_path
        );

    config.recommendation_csv_output_path =
        get_optional_string(
            data,
            "recommendation_csv_output_path",
            config.recommendation_csv_output_path
        );

    config.result_json_output_path =
        get_optional_string(
            data,
            "result_json_output_path",
            config.result_json_output_path
        );

    config.verbose =
        get_optional_bool(
            data,
            "verbose",
            config.verbose
        );

    config.export_individual_results =
        get_optional_bool(
            data,
            "export_individual_results",
            config.export_individual_results
        );

    config.export_summary_csv =
        get_optional_bool(
            data,
            "export_summary_csv",
            config.export_summary_csv
        );

    config.export_aggregate_csv =
        get_optional_bool(
            data,
            "export_aggregate_csv",
            config.export_aggregate_csv
        );

    config.export_ranking_csv =
        get_optional_bool(
            data,
            "export_ranking_csv",
            config.export_ranking_csv
        );

    config.export_result_json =
        get_optional_bool(
            data,
            "export_result_json",
            config.export_result_json
        );

    if (!data.contains("experiments")) {
        throw std::runtime_error(
            "No-replanning batch config JSON must contain an experiments array."
        );
    }

    if (!data.at("experiments").is_array()) {
        throw std::runtime_error(
            "No-replanning batch config experiments field must be an array."
        );
    }

    for (const auto& experiment_data : data.at("experiments")) {
        config.experiments.push_back(
            load_experiment_config_from_json(experiment_data)
        );
    }

    return config;
}