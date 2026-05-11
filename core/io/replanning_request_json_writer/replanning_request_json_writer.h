#pragma once

#include <string>

#include "core/replanning/replanning_request/replanning_request.h"

void write_replanning_request_to_json(
    const ReplanningRequest& request,
    const std::string& output_path,
    const std::string& result_type = "replanning_request"
);