#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"

#include <algorithm>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/perturbation/service_delay_perturbation/service_delay_perturbation.h"
#include "core/perturbation/travel_delay_perturbation/travel_delay_perturbation.h"

Effect build_effect_from_perturbation(
    const Perturbation& perturbation
) {
    switch (perturbation.type) {
        case PerturbationType::TRAVEL_DELAY:
            return build_travel_delay_effect(perturbation);

        case PerturbationType::SERVICE_DELAY:
            return build_service_delay_effect(perturbation);

        case PerturbationType::TASK_CANCELLATION:
            throw std::runtime_error(
                "TASK_CANCELLATION perturbation is not implemented yet: " +
                perturbation.perturbation_id
            );

        case PerturbationType::NEW_TASK:
            throw std::runtime_error(
                "NEW_TASK perturbation is not implemented yet: " +
                perturbation.perturbation_id
            );

        case PerturbationType::UNKNOWN:
        default:
            throw std::runtime_error(
                "Unknown perturbation type: " +
                perturbation.perturbation_id
            );
    }
}

std::vector<Effect> build_effects_from_perturbation_plan(
    const PerturbationPlan& plan
) {
    std::vector<Effect> effects;

    effects.reserve(plan.perturbations.size());

    for (const auto& perturbation : plan.perturbations) {
        effects.push_back(
            build_effect_from_perturbation(perturbation)
        );
    }

    std::stable_sort(
        effects.begin(),
        effects.end(),
        [](const Effect& a, const Effect& b) {
            if (a.occurrence_time != b.occurrence_time) {
                return a.occurrence_time < b.occurrence_time;
            }

            return a.effect_id < b.effect_id;
        }
    );

    return effects;
}