#pragma once

#include <string>

#include "core/perturbation/perturbation/perturbation.h"

PerturbationPlan load_perturbation_plan_from_json(
    const std::string& file_path
);