#include "core/io/instance_json_loader.h"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static std::vector<std::string> read_string_vector(const json& value) {
    std::vector<std::string> result;

    for (const auto& item : value) {
        result.push_back(item.get<std::string>());
    }

    return result;
}

static void validate_square_matrix_size(
    const json& matrix,
    int expected_size,
    const std::string& matrix_name
) {
    if (!matrix.is_array()) {
        throw std::runtime_error(matrix_name + " must be an array.");
    }

    if (static_cast<int>(matrix.size()) != expected_size) {
        std::ostringstream message;
        message << matrix_name
                << " must have "
                << expected_size
                << " rows.";
        throw std::runtime_error(message.str());
    }

    for (int row = 0; row < expected_size; ++row) {
        if (!matrix.at(row).is_array()) {
            std::ostringstream message;
            message << matrix_name << " row " << row << " must be an array.";
            throw std::runtime_error(message.str());
        }

        if (static_cast<int>(matrix.at(row).size()) != expected_size) {
            std::ostringstream message;
            message << matrix_name
                    << " row "
                    << row
                    << " must have "
                    << expected_size
                    << " columns.";
            throw std::runtime_error(message.str());
        }
    }
}

static std::vector<int> read_flattened_int_matrix(
    const json& matrix,
    int size
) {
    std::vector<int> result;
    result.reserve(size * size);

    for (int row = 0; row < size; ++row) {
        for (int column = 0; column < size; ++column) {
            result.push_back(matrix.at(row).at(column).get<int>());
        }
    }

    return result;
}

static std::vector<double> read_flattened_double_matrix(
    const json& matrix,
    int size
) {
    std::vector<double> result;
    result.reserve(size * size);

    for (int row = 0; row < size; ++row) {
        for (int column = 0; column < size; ++column) {
            result.push_back(matrix.at(row).at(column).get<double>());
        }
    }

    return result;
}

Instance load_instance_from_json(const std::string& file_path) {
    std::ifstream file(file_path);

    if (!file.is_open()) {
        throw std::runtime_error("Could not open instance file: " + file_path);
    }

    json data;
    file >> data;

    Instance instance;

    instance.instance_id = data.at("instance_id").get<std::string>();
    instance.name = data.at("name").get<std::string>();
    instance.description = data.value("description", "");
    instance.time_unit = data.at("time_unit").get<std::string>();

    instance.planning_horizon.start =
        data.at("planning_horizon").at("start").get<int>();

    instance.planning_horizon.end =
        data.at("planning_horizon").at("end").get<int>();

    for (const auto& item : data.at("locations")) {
        Location location;

        location.id = item.at("id").get<std::string>();
        location.name = item.at("name").get<std::string>();
        location.address = item.value("address", "");
        location.latitude = item.at("latitude").get<double>();
        location.longitude = item.at("longitude").get<double>();

        instance.locations.push_back(location);
    }

    for (const auto& item : data.at("technicians")) {
        Technician technician;

        technician.id = item.at("id").get<std::string>();
        technician.name = item.at("name").get<std::string>();
        technician.start_location_id =
            item.at("start_location_id").get<std::string>();
        technician.end_location_id =
            item.at("end_location_id").get<std::string>();
        technician.available_from = item.at("available_from").get<int>();
        technician.available_to = item.at("available_to").get<int>();
        technician.skills = read_string_vector(item.at("skills"));

        instance.technicians.push_back(technician);
    }

    for (const auto& item : data.at("tasks")) {
        Task task;

        task.id = item.at("id").get<std::string>();
        task.name = item.at("name").get<std::string>();
        task.location_id = item.at("location_id").get<std::string>();
        task.service_duration = item.at("service_duration").get<int>();
        task.time_window_start = item.at("time_window_start").get<int>();
        task.time_window_end = item.at("time_window_end").get<int>();
        task.required_skills = read_string_vector(item.at("required_skills"));
        task.priority = item.at("priority").get<int>();

        instance.tasks.push_back(task);
    }

    const auto& matrix = data.at("travel_matrix");

    instance.travel_matrix.location_ids =
        read_string_vector(matrix.at("location_ids"));

    instance.travel_matrix.size =
        static_cast<int>(instance.travel_matrix.location_ids.size());

    if (instance.travel_matrix.size == 0) {
        throw std::runtime_error("travel_matrix.location_ids cannot be empty.");
    }

    if (instance.travel_matrix.size != static_cast<int>(instance.locations.size())) {
        throw std::runtime_error(
            "travel_matrix.location_ids size must match locations size."
        );
    }

    validate_square_matrix_size(
        matrix.at("durations"),
        instance.travel_matrix.size,
        "travel_matrix.durations"
    );

    validate_square_matrix_size(
        matrix.at("distances"),
        instance.travel_matrix.size,
        "travel_matrix.distances"
    );

    instance.travel_matrix.durations =
        read_flattened_int_matrix(
            matrix.at("durations"),
            instance.travel_matrix.size
        );

    instance.travel_matrix.distances =
        read_flattened_double_matrix(
            matrix.at("distances"),
            instance.travel_matrix.size
        );

    return instance;
}