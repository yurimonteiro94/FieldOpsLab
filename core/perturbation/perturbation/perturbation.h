#pragma once

#include <string>
#include <vector>

enum class PerturbationType {
    TRAVEL_DELAY,
    SERVICE_DELAY,
    TASK_CANCELLATION,
    NEW_TASK,
    UNKNOWN
};

std::string perturbation_type_to_string(PerturbationType type);

PerturbationType perturbation_type_from_string(
    const std::string& type
);

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

struct PerturbationPlan {
    std::string perturbation_plan_id;
    std::string name;
    std::string description;

    std::vector<Perturbation> perturbations;
};

bool is_delay_perturbation(const Perturbation& perturbation);