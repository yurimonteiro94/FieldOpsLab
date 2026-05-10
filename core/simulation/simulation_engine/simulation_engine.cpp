#include "core/simulation/simulation_engine/simulation_engine.h"

#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>

static std::unordered_map<std::string, Technician> build_technician_map(
    const Instance& instance
) {
    std::unordered_map<std::string, Technician> technician_map;

    for (const auto& technician : instance.technicians) {
        technician_map[technician.id] = technician;
    }

    return technician_map;
}

static std::unordered_map<std::string, int> build_location_index_map(
    const TravelMatrix& matrix
) {
    std::unordered_map<std::string, int> location_index;

    for (int i = 0; i < static_cast<int>(matrix.location_ids.size()); ++i) {
        location_index[matrix.location_ids[i]] = i;
    }

    return location_index;
}

static SimulationEvent make_event(
    int time,
    SimulationEventType type,
    const std::string& technician_id,
    const std::string& task_id,
    const std::string& location_id,
    const std::string& message
) {
    SimulationEvent event;

    event.time = time;
    event.type = type;
    event.technician_id = technician_id;
    event.task_id = task_id;
    event.location_id = location_id;
    event.message = message;

    return event;
}

static std::string get_last_location_id_before_return(const Route& route) {
    if (!route.stops.empty()) {
        return route.stops.back().location_id;
    }

    return route.start_location_id;
}

static int get_last_time_before_return(
    const Technician& technician,
    const Route& route
) {
    if (!route.stops.empty()) {
        return route.stops.back().end_service_time;
    }

    return technician.available_from;
}

static int simulation_event_type_priority(SimulationEventType type) {
    switch (type) {
        case SimulationEventType::ROUTE_STARTED:
            return 0;

        case SimulationEventType::TECHNICIAN_ARRIVED:
            return 1;

        case SimulationEventType::TASK_STARTED:
            return 2;

        case SimulationEventType::TASK_COMPLETED:
            return 3;

        case SimulationEventType::TECHNICIAN_DEPARTED:
            return 4;

        case SimulationEventType::ROUTE_COMPLETED:
            return 5;

        default:
            return 100;
    }
}

SimulationTimeline build_simulation_timeline_from_solution(
    const Instance& instance,
    const Solution& solution
) {
    SimulationTimeline timeline;

    timeline.start_time = instance.planning_horizon.start;
    timeline.end_time = instance.planning_horizon.start;

    const auto technician_map = build_technician_map(instance);
    const auto location_index = build_location_index_map(instance.travel_matrix);

    for (const auto& route : solution.routes) {
        auto technician_it = technician_map.find(route.technician_id);

        if (technician_it == technician_map.end()) {
            throw std::runtime_error(
                "Solution references unknown technician_id: " +
                route.technician_id
            );
        }

        const Technician& technician = technician_it->second;

        timeline.events.push_back(
            make_event(
                technician.available_from,
                SimulationEventType::ROUTE_STARTED,
                route.technician_id,
                "",
                route.start_location_id,
                "Technician route started."
            )
        );

        for (const auto& stop : route.stops) {
            int departure_time =
                stop.arrival_time - stop.travel_time_from_previous;

            timeline.events.push_back(
                make_event(
                    departure_time,
                    SimulationEventType::TECHNICIAN_DEPARTED,
                    route.technician_id,
                    stop.task_id,
                    stop.location_id,
                    "Technician departed to task location."
                )
            );

            timeline.events.push_back(
                make_event(
                    stop.arrival_time,
                    SimulationEventType::TECHNICIAN_ARRIVED,
                    route.technician_id,
                    stop.task_id,
                    stop.location_id,
                    "Technician arrived at task location."
                )
            );

            timeline.events.push_back(
                make_event(
                    stop.start_service_time,
                    SimulationEventType::TASK_STARTED,
                    route.technician_id,
                    stop.task_id,
                    stop.location_id,
                    "Task service started."
                )
            );

            timeline.events.push_back(
                make_event(
                    stop.end_service_time,
                    SimulationEventType::TASK_COMPLETED,
                    route.technician_id,
                    stop.task_id,
                    stop.location_id,
                    "Task service completed."
                )
            );
        }

        const std::string last_location_id =
            get_last_location_id_before_return(route);

        const int last_time_before_return =
            get_last_time_before_return(technician, route);

        const int last_location_index =
            location_index.at(last_location_id);

        const int end_location_index =
            location_index.at(route.end_location_id);

        const int return_travel_time =
            instance.travel_matrix.duration(
                last_location_index,
                end_location_index
            );

        if (return_travel_time > 0) {
            timeline.events.push_back(
                make_event(
                    last_time_before_return,
                    SimulationEventType::TECHNICIAN_DEPARTED,
                    route.technician_id,
                    "",
                    route.end_location_id,
                    "Technician departed to end location."
                )
            );

            timeline.events.push_back(
                make_event(
                    last_time_before_return + return_travel_time,
                    SimulationEventType::TECHNICIAN_ARRIVED,
                    route.technician_id,
                    "",
                    route.end_location_id,
                    "Technician arrived at end location."
                )
            );
        }

        timeline.events.push_back(
            make_event(
                route.end_time,
                SimulationEventType::ROUTE_COMPLETED,
                route.technician_id,
                "",
                route.end_location_id,
                "Technician route completed."
            )
        );

        if (route.end_time > timeline.end_time) {
            timeline.end_time = route.end_time;
        }
    }

    std::sort(
        timeline.events.begin(),
        timeline.events.end(),
        [](const SimulationEvent& a, const SimulationEvent& b) {
            if (a.time != b.time) {
                return a.time < b.time;
            }

            return simulation_event_type_priority(a.type) <
                simulation_event_type_priority(b.type);
        }
    );

    return timeline;
}

void print_simulation_timeline_summary(const SimulationTimeline& timeline) {
    std::cout << "Simulation timeline summary:\n";
    std::cout << "  Start time: " << timeline.start_time << "\n";
    std::cout << "  End time: " << timeline.end_time << "\n";
    std::cout << "  Events: " << timeline.events.size() << "\n";
}