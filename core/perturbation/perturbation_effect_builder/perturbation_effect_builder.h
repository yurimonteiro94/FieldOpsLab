#pragma once

#include <vector>

#include "core/perturbation/effect/effect.h"
#include "core/perturbation/perturbation/perturbation.h"

Effect build_effect_from_perturbation(
    const Perturbation& perturbation
);

std::vector<Effect> build_effects_from_perturbation_plan(
    const PerturbationPlan& plan
);