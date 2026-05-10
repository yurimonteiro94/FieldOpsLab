#pragma once

#include "core/perturbation/effect/effect.h"
#include "core/perturbation/perturbation/perturbation.h"

bool is_valid_travel_delay_perturbation(
    const Perturbation& perturbation
);

Effect build_travel_delay_effect(
    const Perturbation& perturbation
);