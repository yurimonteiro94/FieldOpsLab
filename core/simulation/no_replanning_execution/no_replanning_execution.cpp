#include "core/simulation/no_replanning_execution/no_replanning_execution.h"

#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>

struct TaskRuntimeAdjustment {
    int additional_service_duration = 0;
};

struct TravelRuntimeAdjustment {
    int additional_travel_duration = 0;
};

static std::unordered_map<std::string, Task> build_task_map(
    const Instance& instance
) {
    std::unordered_map<std::string, Task> task_map;

    for (const auto& task : instance.tasks) {
        task_map[task.id] = task;
    }

    return task_map;
}

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

static std::string make_travel_key(
    const std::string& technician_id,
    const std::string& from_location_id,
    const std::string& to_location_id,
    const std::string& task_id
) {
    return technician_id + "|" +
           from_location_id + "|" +
           to_location_id + "|" +
           task_id;
}

static std::string make_service_key(
    const std::string& technician_id,
    const std::string& task_id
) {
    return technician_id + "|" + task_id;
}

static std::unordered_map<std::string, TravelRuntimeAdjustment>
build_travel_adjustments(
    const std::vector<Effect>& effects
) {
    std::unordered_map<std::string, TravelRuntimeAdjustment> adjustments;

    for (const auto& effect : effects) {
        if (effect.type != EffectType::ADD_TRAVEL_DELAY) {
            continue;
        }

        const std::string key = make_travel_key(
            effect.technician_id,
            effect.from_location_id,
            effect.to_location_id,
            effect.task_id
        );

        adjustments[key].additional_travel_duration += effect.delay_duration;
    }

    return adjustments;
}

static std::unordered_map<std::string, TaskRuntimeAdjustment>
build_service_adjustments(
    const std::vector<Effect>& effects
) {
    std::unordered_map<std::string, TaskRuntimeAdjustment> adjustments;

    for (const auto& effect : effects) {
        if (effect.type != EffectType::ADD_SERVICE_DELAY) {
            continue;
        }

        const std::string key = make_service_key(
            effect.technician_id,
            effect.task_id
        );

        adjustments[key].additional_service_duration += effect.delay_duration;
    }

    return adjustments;
}

static int get_additional_travel_duration(
    const std::unordered_map<std::string, TravelRuntimeAdjustment>& adjustments,
    const std::string& technician_id,
    const std::string& from_location_id,
    const std::string& to_location_id,
    const std::string& task_id
) {
    const std::string key = make_travel_key(
        technician_id,
        from_location_id,
        to_location_id,
        task_id
    );

    auto it = adjustments.find(key);

    if (it == adjustments.end()) {
        return 0;
    }

    return it->second.additional_travel_duration;
}

static int get_additional_service_duration(
    const std::unordered_map<std::string, TaskRuntimeAdjustment>& adjustments,
    const std::string& technician_id,
    const std::string& task_id
) {
    const std::string key = make_service_key(
        technician_id,
        task_id
    );

    auto it = adjustments.find(key);

    if (it == adjustments.end()) {
        return 0;
    }

    return it->second.additional_service_duration;
}

static SolutionStatus determine_status_after_execution(
    const Solution& executed_solution
) {
    if (executed_solution.unassigned_task_ids.empty()) {
        return SolutionStatus::FEASIBLE;
    }

    bool has_assigned_tasks = false;

    for (const auto& route : executed_solution.routes) {
        if (!route.stops.empty()) {
            has_assigned_tasks = true;
            break;
        }
    }

    if (has_assigned_tasks) {
        return SolutionStatus::PARTIAL;
    }

    return SolutionStatus::INFEASIBLE;
}

Solution execute_solution_without_replanning(
    const Instance& instance,
    const Solution& planned_solution,
    const std::vector<Effect>& effects
) {
    Solution executed_solution;

    executed_solution.solution_id =
        planned_solution.solution_id + "_executed_without_replanning";

    executed_solution.method_id =
        planned_solution.method_id + "+no_replanning_execution";

    executed_solution.instance_id = planned_solution.instance_id;
    executed_solution.unassigned_task_ids =
        planned_solution.unassigned_task_ids;

    const auto task_map = build_task_map(instance);
    const auto technician_map = build_technician_map(instance);
    const auto location_index = build_location_index_map(instance.travel_matrix);

    const auto travel_adjustments = build_travel_adjustments(effects);
    const auto service_adjustments = build_service_adjustments(effects);

    for (const auto& planned_route : planned_solution.routes) {
        Route executed_route;

        executed_route.technician_id = planned_route.technician_id;
        executed_route.start_location_id = planned_route.start_location_id;
        executed_route.end_location_id = planned_route.end_location_id;

        const Technician& technician =
            technician_map.at(planned_route.technician_id);

        std::string current_location_id = planned_route.start_location_id;
        int current_location_index = location_index.at(current_location_id);
        int current_time = technician.available_from;

        for (const auto& planned_stop : planned_route.stops) {
            const Task& task = task_map.at(planned_stop.task_id);

            const int stop_location_index =
                location_index.at(planned_stop.location_id);

            const int base_travel_time =
                instance.travel_matrix.duration(
                    current_location_index,
                    stop_location_index
                );

            const int additional_travel_time =
                get_additional_travel_duration(
                    travel_adjustments,
                    planned_route.technician_id,
                    current_location_id,
                    planned_stop.location_id,
                    planned_stop.task_id
                );

            const int travel_time =
                base_travel_time + additional_travel_time;

            const int arrival_time = current_time + travel_time;

            const int start_service_time =
                std::max(arrival_time, task.time_window_start);

            const int waiting_time = start_service_time - arrival_time;

            const int additional_service_duration =
                get_additional_service_duration(
                    service_adjustments,
                    planned_route.technician_id,
                    planned_stop.task_id
                );

            const int service_duration =
                task.service_duration + additional_service_duration;

            const int end_service_time =
                start_service_time + service_duration;

            RouteStop executed_stop;

            executed_stop.task_id = planned_stop.task_id;
            executed_stop.location_id = planned_stop.location_id;
            executed_stop.arrival_time = arrival_time;
            executed_stop.start_service_time = start_service_time;
            executed_stop.end_service_time = end_service_time;
            executed_stop.travel_time_from_previous = travel_time;
            executed_stop.waiting_time = waiting_time;

            executed_route.stops.push_back(executed_stop);

            executed_route.total_travel_time += travel_time;
            executed_route.total_service_time += service_duration;
            executed_route.total_waiting_time += waiting_time;

            current_location_id = planned_stop.location_id;
            current_location_index = stop_location_index;
            current_time = end_service_time;
        }

        const int end_location_index =
            location_index.at(planned_route.end_location_id);

        const int return_travel_time =
            instance.travel_matrix.duration(
                current_location_index,
                end_location_index
            );

        executed_route.total_travel_time += return_travel_time;
        executed_route.end_time = current_time + return_travel_time;

        executed_solution.routes.push_back(executed_route);
    }

    int total_travel_time = 0;
    int total_waiting_time = 0;

    for (const auto& route : executed_solution.routes) {
        total_travel_time += route.total_travel_time;
        total_waiting_time += route.total_waiting_time;
    }

    const double unassigned_penalty = 100000.0;

    executed_solution.objective_value =
        static_cast<double>(total_travel_time + total_waiting_time) +
        unassigned_penalty *
        static_cast<double>(executed_solution.unassigned_task_ids.size());

    executed_solution.status =
        determine_status_after_execution(executed_solution);

    return executed_solution;
}