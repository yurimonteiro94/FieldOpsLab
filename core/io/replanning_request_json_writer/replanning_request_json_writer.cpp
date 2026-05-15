#include "core/io/replanning_request_json_writer/replanning_request_json_writer.h"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static json string_vector_to_json(
    const std::vector<std::string>& values
) {
    json data = json::array();

    for (const auto& value : values) {
        data.push_back(value);
    }

    return data;
}

static json effect_to_json(const Effect& effect) {
    return {
        {"effect_id", effect.effect_id},
        {"type", effect_type_to_string(effect.type)},
        {"occurrence_time", effect.occurrence_time},
        {"technician_id", effect.technician_id},
        {"task_id", effect.task_id},
        {"from_location_id", effect.from_location_id},
        {"to_location_id", effect.to_location_id},
        {"delay_duration", effect.delay_duration},
        {"description", effect.description}
    };
}

static json effects_to_json(const std::vector<Effect>& effects) {
    json data = json::array();

    for (const auto& effect : effects) {
        data.push_back(effect_to_json(effect));
    }

    return data;
}

static json technician_runtime_states_to_json(
    const std::vector<ReplanningTechnicianRuntimeState>& runtime_states
) {
    json data = json::array();

    for (const auto& state : runtime_states) {
        data.push_back({
            {"technician_id", state.technician_id},
            {"execution_status", state.execution_status},
            {"current_location_id", state.current_location_id},
            {"current_task_id", state.current_task_id},
            {"next_task_id", state.next_task_id},
            {"available_from_time", state.available_from_time},
            {"can_receive_candidate_tasks",
                state.can_receive_candidate_tasks}
        });
    }

    return data;
}

void write_replanning_request_to_json(
    const ReplanningRequest& request,
    const std::string& output_path,
    const std::string& result_type
) {
    json data = {
        {"result_type", result_type},
        {"request_id", request.request_id},
        {"decision_time", request.decision_time},
        {"policy_id", request.policy_id},
        {"policy_decision", request.policy_decision},
        {"should_replan", request.should_replan},
        {"has_work", replanning_request_has_work(request)},
        {"counts", {
            {"completed_task_count", request.completed_task_count()},
            {"locked_task_count", request.locked_task_count()},
            {"candidate_task_count", request.candidate_task_count()},
            {"available_technician_count", request.available_technician_count()},
            {"busy_technician_count", request.busy_technician_count()},
            {"finished_technician_count", request.finished_technician_count()},
            {"technician_runtime_state_count",
                request.technician_runtime_states.size()},
            {"runtime_effect_count", request.runtime_effects.size()}
        }},
        {"tasks", {
            {"completed_task_ids", string_vector_to_json(request.completed_task_ids)},
            {"locked_task_ids", string_vector_to_json(request.locked_task_ids)},
            {"candidate_task_ids", string_vector_to_json(request.candidate_task_ids)}
        }},
        {"technicians", {
            {"available_technician_ids", string_vector_to_json(request.available_technician_ids)},
            {"busy_technician_ids", string_vector_to_json(request.busy_technician_ids)},
            {"finished_technician_ids", string_vector_to_json(request.finished_technician_ids)}
        }},
        {"technician_runtime_states",
            technician_runtime_states_to_json(
                request.technician_runtime_states
            )},
        {"runtime_effects", effects_to_json(request.runtime_effects)}
    };

    std::filesystem::path path(output_path);

    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }

    std::ofstream file(output_path);

    if (!file.is_open()) {
        throw std::runtime_error(
            "Could not open replanning request JSON file for writing: " +
            output_path
        );
    }

    file << data.dump(4);
}