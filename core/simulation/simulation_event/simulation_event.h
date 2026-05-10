#pragma once

#include <string>
#include <vector>

enum class SimulationEventType {
    ROUTE_STARTED,
    TECHNICIAN_DEPARTED,
    TECHNICIAN_ARRIVED,
    TASK_STARTED,
    TASK_COMPLETED,
    ROUTE_COMPLETED
};

std::string simulation_event_type_to_string(SimulationEventType type);

struct SimulationEvent {
    int time = 0;

    SimulationEventType type = SimulationEventType::ROUTE_STARTED;

    std::string technician_id;
    std::string task_id;
    std::string location_id;
    std::string message;
};

void print_simulation_events(const std::vector<SimulationEvent>& events);