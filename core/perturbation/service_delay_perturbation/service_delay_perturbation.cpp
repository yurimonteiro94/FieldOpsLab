#include "core/perturbation/service_delay_perturbation/service_delay_perturbation.h"

#include <stdexcept>
#include <string>

bool is_valid_service_delay_perturbation(
    const Perturbation& perturbation
) {
    if (perturbation.type != PerturbationType::SERVICE_DELAY) {
        return false;
    }

    if (perturbation.perturbation_id.empty()) {
        return false;
    }

    if (perturbation.occurrence_time < 0) {
        return false;
    }

    if (perturbation.technician_id.empty()) {
        return false;
    }

    if (perturbation.task_id.empty()) {
        return false;
    }

    if (perturbation.delay_duration <= 0) {
        return false;
    }

    return true;
}

Effect build_service_delay_effect(
    const Perturbation& perturbation
) {
    if (!is_valid_service_delay_perturbation(perturbation)) {
        throw std::runtime_error(
            "Invalid service delay perturbation: " +
            perturbation.perturbation_id
        );
    }

    return build_effect_from_perturbation_id(
        "effect_from_" + perturbation.perturbation_id,
        EffectType::ADD_SERVICE_DELAY,
        perturbation.occurrence_time,
        perturbation.technician_id,
        perturbation.task_id,
        perturbation.from_location_id,
        perturbation.to_location_id,
        perturbation.delay_duration,
        "Add service delay effect generated from service delay perturbation."
    );
}