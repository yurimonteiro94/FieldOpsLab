#include "core/simulation/simulation_event/simulation_event.h"

#include <iostream>

std::string simulation_event_type_to_string(SimulationEventType type) {
    switch (type) {
        case SimulationEventType::ROUTE_STARTED:
            return "ROUTE_STARTED";

        case SimulationEventType::TECHNICIAN_DEPARTED:
            return "TECHNICIAN_DEPARTED";

        case SimulationEventType::TECHNICIAN_ARRIVED:
            return "TECHNICIAN_ARRIVED";

        case SimulationEventType::TASK_STARTED:
            return "TASK_STARTED";

        case SimulationEventType::TASK_COMPLETED:
            return "TASK_COMPLETED";

        case SimulationEventType::ROUTE_COMPLETED:
            return "ROUTE_COMPLETED";

        default:
            return "UNKNOWN";
    }
}

void print_simulation_events(const std::vector<SimulationEvent>& events) {
    std::cout << "Simulation timeline:\n";

    for (const auto& event : events) {
        std::cout << "  t=" << event.time
                  << " | " << simulation_event_type_to_string(event.type)
                  << " | technician=" << event.technician_id;

        if (!event.task_id.empty()) {
            std::cout << " | task=" << event.task_id;
        }

        if (!event.location_id.empty()) {
            std::cout << " | location=" << event.location_id;
        }

        if (!event.message.empty()) {
            std::cout << " | " << event.message;
        }

        std::cout << "\n";
    }
}