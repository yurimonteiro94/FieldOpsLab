#include "core/perturbation/perturbation/perturbation.h"

std::string perturbation_type_to_string(PerturbationType type) {
    switch (type) {
        case PerturbationType::TRAVEL_DELAY:
            return "TRAVEL_DELAY";

        case PerturbationType::SERVICE_DELAY:
            return "SERVICE_DELAY";

        case PerturbationType::TASK_CANCELLATION:
            return "TASK_CANCELLATION";

        case PerturbationType::NEW_TASK:
            return "NEW_TASK";

        case PerturbationType::UNKNOWN:
            return "UNKNOWN";

        default:
            return "UNKNOWN";
    }
}

PerturbationType perturbation_type_from_string(
    const std::string& type
) {
    if (type == "TRAVEL_DELAY") {
        return PerturbationType::TRAVEL_DELAY;
    }

    if (type == "SERVICE_DELAY") {
        return PerturbationType::SERVICE_DELAY;
    }

    if (type == "TASK_CANCELLATION") {
        return PerturbationType::TASK_CANCELLATION;
    }

    if (type == "NEW_TASK") {
        return PerturbationType::NEW_TASK;
    }

    return PerturbationType::UNKNOWN;
}

bool is_delay_perturbation(const Perturbation& perturbation) {
    return perturbation.type == PerturbationType::TRAVEL_DELAY ||
           perturbation.type == PerturbationType::SERVICE_DELAY;
}