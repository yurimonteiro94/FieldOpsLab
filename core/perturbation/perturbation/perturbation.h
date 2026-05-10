#pragma once

#include <string>

enum class PerturbationType {
    TRAVEL_DELAY,
    SERVICE_DELAY,
    TASK_CANCELLATION,
    NEW_TASK,
    UNKNOWN
};

std::string perturbation_type_to_string(PerturbationType type);

struct Perturbation {
    std::string perturbation_id;

    PerturbationType type = PerturbationType::UNKNOWN;

    int occurrence_time = 0;

    std::string technician_id;
    std::string task_id;

    std::string from_location_id;
    std::string to_location_id;

    int delay_duration = 0;

    std::string description;
};

bool is_delay_perturbation(const Perturbation& perturbation);