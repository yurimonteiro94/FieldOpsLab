#include "core/replanning/greedy_replanning_solver/greedy_replanning_solver.h"

#include <algorithm>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

static void copy_request_counts_to_result(
    ReplanningResult& result,
    const ReplanningRequest& request
) {
    result.completed_task_count = request.completed_task_count();
    result.locked_task_count = request.locked_task_count();
    result.candidate_task_count = request.candidate_task_count();

    result.available_technician_count =
        request.available_technician_count();

    result.busy_technician_count =
        request.busy_technician_count();

    result.finished_technician_count =
        request.finished_technician_count();
}

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

static bool vector_contains(
    const std::vector<std::string>& values,
    const std::string& value
) {
    return std::find(values.begin(), values.end(), value) != values.end();
}

static bool technician_can_execute_task(
    const Technician& technician,
    const Task& task
) {
    for (const auto& required_skill : task.required_skills) {
        if (!vector_contains(technician.skills, required_skill)) {
            return false;
        }
    }

    return true;
}

static std::vector<std::string> build_active_technician_ids(
    const ReplanningRequest& request
) {
    std::vector<std::string> technician_ids;

    for (const auto& runtime_state :
         request.technician_runtime_states) {
        if (!runtime_state.can_receive_candidate_tasks) {
            continue;
        }

        if (!vector_contains(technician_ids, runtime_state.technician_id)) {
            technician_ids.push_back(runtime_state.technician_id);
        }
    }

    if (!technician_ids.empty()) {
        return technician_ids;
    }

    for (const auto& technician_id : request.available_technician_ids) {
        technician_ids.push_back(technician_id);
    }

    for (const auto& technician_id : request.busy_technician_ids) {
        if (!vector_contains(technician_ids, technician_id)) {
            technician_ids.push_back(technician_id);
        }
    }

    return technician_ids;
}

static std::string technician_start_location_for_replanning(
    const Technician& technician,
    const ReplanningRequest& request
) {
    const ReplanningTechnicianRuntimeState* runtime_state =
        find_replanning_technician_runtime_state_by_id(
            request,
            technician.id
        );

    if (runtime_state == nullptr) {
        return technician.start_location_id;
    }

    if (runtime_state->current_location_id.empty()) {
        return technician.start_location_id;
    }

    return runtime_state->current_location_id;
}

static int technician_start_time_for_replanning(
    const Technician& technician,
    const ReplanningRequest& request
) {
    const ReplanningTechnicianRuntimeState* runtime_state =
        find_replanning_technician_runtime_state_by_id(
            request,
            technician.id
        );

    if (runtime_state == nullptr) {
        return std::max(technician.available_from, request.decision_time);
    }

    return std::max(
        technician.available_from,
        runtime_state->available_from_time
    );
}

static Route build_empty_replanning_route(
    const Technician& technician,
    const ReplanningRequest& request
) {
    Route route;

    route.technician_id = technician.id;
    route.start_location_id =
        technician_start_location_for_replanning(
            technician,
            request
        );

    route.end_location_id = technician.end_location_id;

    route.end_time =
        technician_start_time_for_replanning(
            technician,
            request
        );

    return route;
}

static int route_current_location_index(
    const Route& route,
    const std::unordered_map<std::string, int>& location_index
) {
    if (route.stops.empty()) {
        return location_index.at(route.start_location_id);
    }

    return location_index.at(route.stops.back().location_id);
}

static std::string route_current_location_id(
    const Route& route
) {
    if (route.stops.empty()) {
        return route.start_location_id;
    }

    return route.stops.back().location_id;
}

static int route_current_time(
    const Route& route
) {
    if (route.stops.empty()) {
        return route.end_time;
    }

    return route.stops.back().end_service_time;
}

static int get_runtime_travel_delay(
    const ReplanningRequest& request,
    const std::string& technician_id,
    const std::string& from_location_id,
    const std::string& to_location_id,
    const std::string& task_id
) {
    int delay = 0;

    for (const auto& effect : request.runtime_effects) {
        if (effect.type != EffectType::ADD_TRAVEL_DELAY) {
            continue;
        }

        if (effect.technician_id != technician_id) {
            continue;
        }

        if (effect.from_location_id != from_location_id) {
            continue;
        }

        if (effect.to_location_id != to_location_id) {
            continue;
        }

        if (effect.task_id != task_id) {
            continue;
        }

        delay += effect.delay_duration;
    }

    return delay;
}

static int get_runtime_service_delay(
    const ReplanningRequest& request,
    const std::string& technician_id,
    const std::string& task_id
) {
    int delay = 0;

    for (const auto& effect : request.runtime_effects) {
        if (effect.type != EffectType::ADD_SERVICE_DELAY) {
            continue;
        }

        if (effect.technician_id != technician_id) {
            continue;
        }

        if (effect.task_id != task_id) {
            continue;
        }

        delay += effect.delay_duration;
    }

    return delay;
}

static int calculate_candidate_end_time(
    const Instance& instance,
    const ReplanningRequest& request,
    const std::unordered_map<std::string, int>& location_index,
    const Route& route,
    const Task& task
) {
    const int from_index =
        route_current_location_index(route, location_index);

    const int to_index =
        location_index.at(task.location_id);

    const int base_travel_time =
        instance.travel_matrix.duration(from_index, to_index);

    const int travel_delay =
        get_runtime_travel_delay(
            request,
            route.technician_id,
            route_current_location_id(route),
            task.location_id,
            task.id
        );

    const int travel_time =
        base_travel_time + travel_delay;

    const int arrival_time =
        route_current_time(route) + travel_time;

    const int start_service_time =
        std::max(arrival_time, task.time_window_start);

    const int service_delay =
        get_runtime_service_delay(
            request,
            route.technician_id,
            task.id
        );

    return start_service_time + task.service_duration + service_delay;
}

static RouteStop build_route_stop_for_task(
    const Instance& instance,
    const ReplanningRequest& request,
    const std::unordered_map<std::string, int>& location_index,
    const Route& route,
    const Task& task
) {
    const int from_index =
        route_current_location_index(route, location_index);

    const int to_index =
        location_index.at(task.location_id);

    const int base_travel_time =
        instance.travel_matrix.duration(from_index, to_index);

    const int travel_delay =
        get_runtime_travel_delay(
            request,
            route.technician_id,
            route_current_location_id(route),
            task.location_id,
            task.id
        );

    const int travel_time =
        base_travel_time + travel_delay;

    const int arrival_time =
        route_current_time(route) + travel_time;

    const int start_service_time =
        std::max(arrival_time, task.time_window_start);

    const int waiting_time =
        start_service_time - arrival_time;

    const int service_delay =
        get_runtime_service_delay(
            request,
            route.technician_id,
            task.id
        );

    RouteStop stop;

    stop.task_id = task.id;
    stop.location_id = task.location_id;
    stop.arrival_time = arrival_time;
    stop.start_service_time = start_service_time;
    stop.end_service_time =
        start_service_time + task.service_duration + service_delay;
    stop.travel_time_from_previous = travel_time;
    stop.waiting_time = waiting_time;

    return stop;
}

static void append_stop_to_route(
    Route& route,
    const RouteStop& stop
) {
    route.stops.push_back(stop);
    route.total_travel_time += stop.travel_time_from_previous;
    route.total_service_time +=
        stop.end_service_time - stop.start_service_time;
    route.total_waiting_time += stop.waiting_time;
    route.end_time = stop.end_service_time;
}

static void finalize_route_return_to_depot(
    const Instance& instance,
    const std::unordered_map<std::string, int>& location_index,
    Route& route
) {
    const int from_index =
        route_current_location_index(route, location_index);

    const int to_index =
        location_index.at(route.end_location_id);

    const int return_travel_time =
        instance.travel_matrix.duration(from_index, to_index);

    route.total_travel_time += return_travel_time;
    route.end_time = route_current_time(route) + return_travel_time;
}

static void update_solution_objective_and_status(
    Solution& solution
) {
    int total_travel_time = 0;
    int total_waiting_time = 0;

    for (const auto& route : solution.routes) {
        total_travel_time += route.total_travel_time;
        total_waiting_time += route.total_waiting_time;
    }

    const double unassigned_penalty = 100000.0;

    solution.objective_value =
        static_cast<double>(total_travel_time + total_waiting_time) +
        unassigned_penalty *
        static_cast<double>(solution.unassigned_task_ids.size());

    if (solution.unassigned_task_ids.empty()) {
        solution.status = SolutionStatus::FEASIBLE;
        return;
    }

    bool has_assigned_task = false;

    for (const auto& route : solution.routes) {
        if (!route.stops.empty()) {
            has_assigned_task = true;
            break;
        }
    }

    solution.status =
        has_assigned_task ? SolutionStatus::PARTIAL
                          : SolutionStatus::INFEASIBLE;
}

static Solution build_greedy_replanned_solution(
    const Instance& instance,
    const ReplanningRequest& request,
    const GreedyReplanningSolverConfig& config
) {
    Solution solution;

    solution.solution_id = config.generated_solution_id;
    solution.method_id = config.method_id;
    solution.instance_id = instance.instance_id;

    const auto task_map = build_task_map(instance);
    const auto technician_map = build_technician_map(instance);
    const auto location_index = build_location_index_map(instance.travel_matrix);

    std::vector<std::string> active_technician_ids =
        build_active_technician_ids(request);

    for (const auto& technician_id : active_technician_ids) {
        if (technician_map.find(technician_id) == technician_map.end()) {
            continue;
        }

        solution.routes.push_back(
            build_empty_replanning_route(
                technician_map.at(technician_id),
                request
            )
        );
    }

    for (const auto& task_id : request.candidate_task_ids) {
        if (task_map.find(task_id) == task_map.end()) {
            solution.unassigned_task_ids.push_back(task_id);
            continue;
        }

        const Task& task = task_map.at(task_id);

        int best_route_index = -1;
        int best_end_time = std::numeric_limits<int>::max();

        for (int i = 0; i < static_cast<int>(solution.routes.size()); ++i) {
            const Route& route = solution.routes[i];

            if (technician_map.find(route.technician_id) ==
                technician_map.end()) {
                continue;
            }

            const Technician& technician =
                technician_map.at(route.technician_id);

            if (!technician_can_execute_task(technician, task)) {
                continue;
            }

            const int candidate_end_time =
                calculate_candidate_end_time(
                    instance,
                    request,
                    location_index,
                    route,
                    task
                );

            if (candidate_end_time > task.time_window_end) {
                continue;
            }

            if (candidate_end_time < best_end_time) {
                best_end_time = candidate_end_time;
                best_route_index = i;
            }
        }

        if (best_route_index < 0) {
            solution.unassigned_task_ids.push_back(task_id);
            continue;
        }

        RouteStop stop =
            build_route_stop_for_task(
                instance,
                request,
                location_index,
                solution.routes[best_route_index],
                task
            );

        append_stop_to_route(solution.routes[best_route_index], stop);
    }

    for (auto& route : solution.routes) {
        finalize_route_return_to_depot(
            instance,
            location_index,
            route
        );
    }

    update_solution_objective_and_status(solution);

    return solution;
}

ReplanningResult run_greedy_replanning_solver(
    const ReplanningRequest& request,
    const GreedyReplanningSolverConfig& config
) {
    ReplanningResult result;

    result.result_id = config.result_id;
    result.request_id = request.request_id;
    result.method_id = config.method_id;
    result.decision_time = request.decision_time;

    copy_request_counts_to_result(result, request);

    if (!request.should_replan) {
        result.status = ReplanningResultStatus::NOT_REQUESTED;
        result.message =
            "No replanning was requested by the policy decision.";
        return result;
    }

    if (!replanning_request_has_work(request)) {
        result.status = ReplanningResultStatus::NO_WORK;
        result.message =
            "Replanning was requested, but there are no candidate tasks to replan.";
        return result;
    }

    result.status = ReplanningResultStatus::SUCCESS;
    result.generated_solution_id = config.generated_solution_id;
    result.message =
        "Greedy replanning solver produced a candidate replanned solution identifier.";

    return result;
}

ReplanningResult run_greedy_replanning_solver(
    const Instance& instance,
    const ReplanningRequest& request,
    const GreedyReplanningSolverConfig& config
) {
    ReplanningResult result =
        run_greedy_replanning_solver(request, config);

    if (result.status != ReplanningResultStatus::SUCCESS) {
        return result;
    }

    result.generated_solution =
        build_greedy_replanned_solution(
            instance,
            request,
            config
        );

    result.generated_solution_was_built = true;

    if (result.generated_solution.status == SolutionStatus::INFEASIBLE) {
        result.status = ReplanningResultStatus::FAILED;
        result.message =
            "Greedy replanning solver could not build a feasible replanned solution.";
        return result;
    }

    result.message =
        "Greedy replanning solver built a candidate replanned solution.";

    return result;
}