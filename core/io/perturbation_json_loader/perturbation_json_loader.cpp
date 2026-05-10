#include "core/io/perturbation_json_loader/perturbation_json_loader.h"

#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static Perturbation read_perturbation_from_json(const json& item) {
    Perturbation perturbation;

    perturbation.perturbation_id =
        item.at("perturbation_id").get<std::string>();

    perturbation.type =
        perturbation_type_from_string(item.at("type").get<std::string>());

    perturbation.occurrence_time =
        item.at("occurrence_time").get<int>();

    perturbation.technician_id =
        item.value("technician_id", "");

    perturbation.task_id =
        item.value("task_id", "");

    perturbation.from_location_id =
        item.value("from_location_id", "");

    perturbation.to_location_id =
        item.value("to_location_id", "");

    perturbation.delay_duration =
        item.value("delay_duration", 0);

    perturbation.description =
        item.value("description", "");

    return perturbation;
}

PerturbationPlan load_perturbation_plan_from_json(
    const std::string& file_path
) {
    std::ifstream file(file_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open perturbation plan file: " + file_path
        );
    }

    json data;
    file >> data;

    PerturbationPlan plan;

    plan.perturbation_plan_id =
        data.at("perturbation_plan_id").get<std::string>();

    plan.name = data.value("name", "");
    plan.description = data.value("description", "");

    for (const auto& item : data.at("perturbations")) {
        plan.perturbations.push_back(
            read_perturbation_from_json(item)
        );
    }

    return plan;
}