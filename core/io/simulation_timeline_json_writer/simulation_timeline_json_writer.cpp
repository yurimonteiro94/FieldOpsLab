#include "core/io/simulation_timeline_json_writer/simulation_timeline_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static json simulation_event_to_json(const SimulationEvent& event) {
    return {
        {"time", event.time},
        {"type", simulation_event_type_to_string(event.type)},
        {"technician_id", event.technician_id},
        {"task_id", event.task_id},
        {"location_id", event.location_id},
        {"message", event.message}
    };
}

void write_simulation_timeline_to_json(
    const SimulationTimeline& timeline,
    const std::string& output_path
) {
    json events = json::array();

    for (const auto& event : timeline.events) {
        events.push_back(simulation_event_to_json(event));
    }

    json result = {
        {"result_type", "simulation_timeline"},
        {"start_time", timeline.start_time},
        {"end_time", timeline.end_time},
        {"event_count", timeline.events.size()},
        {"events", events}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open timeline output file for writing: " + output_path
        );
    }

    file << result.dump(4);
}