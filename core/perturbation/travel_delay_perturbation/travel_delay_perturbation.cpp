#include "core/perturbation/travel_delay_perturbation/travel_delay_perturbation.h"

#include <stdexcept>
#include <string>

bool is_valid_travel_delay_perturbation(
    const Perturbation& perturbation
) {
    if (perturbation.type != PerturbationType::TRAVEL_DELAY) {
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

    if (perturbation.from_location_id.empty()) {
        return false;
    }

    if (perturbation.to_location_id.empty()) {
        return false;
    }

    if (perturbation.delay_duration <= 0) {
        return false;
    }

    return true;
}

Effect build_travel_delay_effect(
    const Perturbation& perturbation
) {
    if (!is_valid_travel_delay_perturbation(perturbation)) {
        throw std::runtime_error(
            "Invalid travel delay perturbation: " +
            perturbation.perturbation_id
        );
    }

    return build_effect_from_perturbation_id(
        "effect_from_" + perturbation.perturbation_id,
        EffectType::ADD_TRAVEL_DELAY,
        perturbation.occurrence_time,
        perturbation.technician_id,
        perturbation.task_id,
        perturbation.from_location_id,
        perturbation.to_location_id,
        perturbation.delay_duration,
        "Add travel delay effect generated from travel delay perturbation."
    );
}