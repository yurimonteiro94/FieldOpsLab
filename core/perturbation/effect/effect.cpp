#include "core/perturbation/effect/effect.h"

std::string effect_type_to_string(EffectType type) {
    switch (type) {
        case EffectType::ADD_TRAVEL_DELAY:
            return "ADD_TRAVEL_DELAY";

        case EffectType::ADD_SERVICE_DELAY:
            return "ADD_SERVICE_DELAY";

        case EffectType::CANCEL_TASK:
            return "CANCEL_TASK";

        case EffectType::ADD_TASK:
            return "ADD_TASK";

        case EffectType::NONE:
            return "NONE";

        default:
            return "NONE";
    }
}

Effect build_effect_from_perturbation_id(
    const std::string& effect_id,
    EffectType type,
    int occurrence_time,
    const std::string& technician_id,
    const std::string& task_id,
    const std::string& from_location_id,
    const std::string& to_location_id,
    int delay_duration,
    const std::string& description
) {
    Effect effect;

    effect.effect_id = effect_id;
    effect.type = type;
    effect.occurrence_time = occurrence_time;
    effect.technician_id = technician_id;
    effect.task_id = task_id;
    effect.from_location_id = from_location_id;
    effect.to_location_id = to_location_id;
    effect.delay_duration = delay_duration;
    effect.description = description;

    return effect;
}