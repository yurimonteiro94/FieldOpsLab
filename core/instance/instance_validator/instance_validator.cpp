#include "core/instance/instance_validator/instance_validator.h"

#include <iostream>
#include <string>
#include <unordered_set>

bool ValidationResult::is_valid() const {
    return errors.empty();
}

static bool contains_id(
    const std::unordered_set<std::string>& ids,
    const std::string& id
) {
    return ids.find(id) != ids.end();
}

ValidationResult validate_instance(const Instance& instance) {
    ValidationResult result;

    if (instance.instance_id.empty()) {
        result.errors.push_back("instance_id cannot be empty.");
    }

    if (instance.name.empty()) {
        result.warnings.push_back("Instance name is empty.");
    }

    if (instance.time_unit.empty()) {
        result.errors.push_back("time_unit cannot be empty.");
    }

    if (instance.planning_horizon.end <= instance.planning_horizon.start) {
        result.errors.push_back("Planning horizon end must be greater than start.");
    }

    if (instance.locations.empty()) {
        result.errors.push_back("Instance must have at least one location.");
    }

    if (instance.technicians.empty()) {
        result.errors.push_back("Instance must have at least one technician.");
    }

    if (instance.tasks.empty()) {
        result.warnings.push_back("Instance has no tasks.");
    }

    std::unordered_set<std::string> location_ids;

    for (const auto& location : instance.locations) {
        if (location.id.empty()) {
            result.errors.push_back("Location with empty id found.");
            continue;
        }

        if (contains_id(location_ids, location.id)) {
            result.errors.push_back("Duplicate location id: " + location.id);
        }

        location_ids.insert(location.id);

        if (location.latitude < -90.0 || location.latitude > 90.0) {
            result.errors.push_back(
                "Invalid latitude for location: " + location.id
            );
        }

        if (location.longitude < -180.0 || location.longitude > 180.0) {
            result.errors.push_back(
                "Invalid longitude for location: " + location.id
            );
        }
    }

    std::unordered_set<std::string> technician_ids;
    std::unordered_set<std::string> available_skills;

    for (const auto& technician : instance.technicians) {
        if (technician.id.empty()) {
            result.errors.push_back("Technician with empty id found.");
            continue;
        }

        if (contains_id(technician_ids, technician.id)) {
            result.errors.push_back("Duplicate technician id: " + technician.id);
        }

        technician_ids.insert(technician.id);

        if (!contains_id(location_ids, technician.start_location_id)) {
            result.errors.push_back(
                "Technician " + technician.id +
                " has invalid start_location_id: " +
                technician.start_location_id
            );
        }

        if (!contains_id(location_ids, technician.end_location_id)) {
            result.errors.push_back(
                "Technician " + technician.id +
                " has invalid end_location_id: " +
                technician.end_location_id
            );
        }

        if (technician.available_to <= technician.available_from) {
            result.errors.push_back(
                "Technician " + technician.id +
                " has invalid availability interval."
            );
        }

        for (const auto& skill : technician.skills) {
            available_skills.insert(skill);
        }
    }

    std::unordered_set<std::string> task_ids;

    for (const auto& task : instance.tasks) {
        if (task.id.empty()) {
            result.errors.push_back("Task with empty id found.");
            continue;
        }

        if (contains_id(task_ids, task.id)) {
            result.errors.push_back("Duplicate task id: " + task.id);
        }

        task_ids.insert(task.id);

        if (!contains_id(location_ids, task.location_id)) {
            result.errors.push_back(
                "Task " + task.id +
                " has invalid location_id: " +
                task.location_id
            );
        }

        if (task.service_duration <= 0) {
            result.errors.push_back(
                "Task " + task.id +
                " must have positive service_duration."
            );
        }

        if (task.time_window_end <= task.time_window_start) {
            result.errors.push_back(
                "Task " + task.id +
                " has invalid time window."
            );
        }

        if (task.time_window_start < instance.planning_horizon.start ||
            task.time_window_end > instance.planning_horizon.end) {
            result.warnings.push_back(
                "Task " + task.id +
                " has time window outside the planning horizon."
            );
        }

        for (const auto& required_skill : task.required_skills) {
            if (!contains_id(available_skills, required_skill)) {
                result.errors.push_back(
                    "Task " + task.id +
                    " requires unavailable skill: " +
                    required_skill
                );
            }
        }
    }

    if (instance.travel_matrix.size != static_cast<int>(instance.locations.size())) {
        result.errors.push_back(
            "Travel matrix size must match the number of locations."
        );
    }

    if (instance.travel_matrix.durations.size() !=
        static_cast<size_t>(instance.travel_matrix.size * instance.travel_matrix.size)) {
        result.errors.push_back("Travel matrix durations size is invalid.");
    }

    if (instance.travel_matrix.distances.size() !=
        static_cast<size_t>(instance.travel_matrix.size * instance.travel_matrix.size)) {
        result.errors.push_back("Travel matrix distances size is invalid.");
    }

    for (int i = 0; i < instance.travel_matrix.size; ++i) {
        for (int j = 0; j < instance.travel_matrix.size; ++j) {
            int duration = instance.travel_matrix.duration(i, j);
            double distance = instance.travel_matrix.distance(i, j);

            if (duration < 0) {
                result.errors.push_back("Travel duration cannot be negative.");
            }

            if (distance < 0.0) {
                result.errors.push_back("Travel distance cannot be negative.");
            }

            if (i == j && duration != 0) {
                result.warnings.push_back(
                    "Travel duration from a location to itself should be zero."
                );
            }

            if (i == j && distance != 0.0) {
                result.warnings.push_back(
                    "Travel distance from a location to itself should be zero."
                );
            }
        }
    }

    return result;
}

void print_validation_result(const ValidationResult& result) {
    if (result.errors.empty() && result.warnings.empty()) {
        std::cout << "Instance validation: OK\n";
        return;
    }

    if (!result.errors.empty()) {
        std::cout << "Validation errors:\n";

        for (const auto& error : result.errors) {
            std::cout << "  - " << error << "\n";
        }
    }

    if (!result.warnings.empty()) {
        std::cout << "Validation warnings:\n";

        for (const auto& warning : result.warnings) {
            std::cout << "  - " << warning << "\n";
        }
    }
}