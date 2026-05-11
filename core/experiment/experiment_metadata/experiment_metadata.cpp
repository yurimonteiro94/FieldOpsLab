#include "core/experiment/experiment_metadata/experiment_metadata.h"

#include <string>

std::string build_experiment_run_label(
    const ExperimentMetadata& metadata
) {
    if (!metadata.experiment_id.empty()) {
        return metadata.experiment_id;
    }

    if (!metadata.scenario_id.empty()) {
        return metadata.scenario_id +
               "_rep_" +
               std::to_string(metadata.replication_id);
    }

    return "experiment_rep_" + std::to_string(metadata.replication_id);
}