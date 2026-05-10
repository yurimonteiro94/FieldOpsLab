#pragma once

#include <string>

enum class EffectType {
    ADD_TRAVEL_DELAY,
    ADD_SERVICE_DELAY,
    CANCEL_TASK,
    ADD_TASK,
    NONE
};

std::string effect_type_to_string(EffectType type);

struct Effect {
    std::string effect_id;

    EffectType type = EffectType::NONE;

    int occurrence_time = 0;

    std::string technician_id;
    std::string task_id;

    std::string from_location_id;
    std::string to_location_id;

    int delay_duration = 0;

    std::string description;
};

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
);