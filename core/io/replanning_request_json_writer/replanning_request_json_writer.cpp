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
        {"counts", {
            {"completed_task_count", request.completed_task_count()},
            {"locked_task_count", request.locked_task_count()},
            {"candidate_task_count", request.candidate_task_count()},
            {"available_technician_count", request.available_technician_count()},
            {"busy_technician_count", request.busy_technician_count()},
            {"finished_technician_count", request.finished_technician_count()}
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
        }}
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