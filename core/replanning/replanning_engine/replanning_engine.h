#pragma once

#include <string>

#include "core/instance/instance/instance.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/replanning/replanning_result/replanning_result.h"

struct ReplanningEngineConfig {
    std::string method_id = "replanning_not_implemented_v1";
    std::string result_id = "replanning_result";
};

ReplanningResult run_replanning_engine(
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config = ReplanningEngineConfig()
);

ReplanningResult run_replanning_engine(
    const Instance& instance,
    const ReplanningRequest& request,
    const ReplanningEngineConfig& config = ReplanningEngineConfig()
);