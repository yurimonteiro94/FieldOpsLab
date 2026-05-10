#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"

#include <algorithm>
#include <limits>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct TechnicianState {
    int current_location_index = 0;
    int current_time = 0;
};

static std::unordered_map<std::string, int> build_location_index_map(
    const TravelMatrix& matrix
) {
    std::unordered_map<std::string, int> index_map;

    for (int i = 0; i < static_cast<int>(matrix.location_ids.size()); ++i) {
        index_map[matrix.location_ids[i]] = i;
    }

    return index_map;
}

static bool technician_has_required_skills(
    const Technician& technician,
    const Task& task
) {
    std::unordered_set<std::string> technician_skills;

    for (const auto& skill : technician.skills) {
        technician_skills.insert(skill);
    }

    for (const auto& required_skill : task.required_skills) {
        if (technician_skills.find(required_skill) == technician_skills.end()) {
            return false;
        }
    }

    return true;
}

static std::vector<Task> sort_tasks_by_time_window(
    const std::vector<Task>& tasks
) {
    std::vector<Task> sorted_tasks = tasks;

    std::sort(
        sorted_tasks.begin(),
        sorted_tasks.end(),
        [](const Task& a, const Task& b) {
            if (a.time_window_start != b.time_window_start) {
                return a.time_window_start < b.time_window_start;
            }

            return a.time_window_end < b.time_window_end;
        }
    );

    return sorted_tasks;
}

Solution build_initial_solution_greedy_earliest_feasible(
    const Instance& instance
) {
    Solution solution;

    solution.solution_id = "initial_solution_greedy_earliest_feasible_v1";
    solution.method_id = "greedy_earliest_feasible_heuristic_v1";
    solution.instance_id = instance.instance_id;

    const auto location_index = build_location_index_map(instance.travel_matrix);

    std::vector<TechnicianState> technician_states;
    technician_states.reserve(instance.technicians.size());

    solution.routes.reserve(instance.technicians.size());

    for (const auto& technician : instance.technicians) {
        Route route;

        route.technician_id = technician.id;
        route.start_location_id = technician.start_location_id;
        route.end_location_id = technician.end_location_id;
        route.end_time = technician.available_from;

        solution.routes.push_back(route);

        TechnicianState state;

        state.current_location_index =
            location_index.at(technician.start_location_id);

        state.current_time = technician.available_from;

        technician_states.push_back(state);
    }

    std::vector<Task> sorted_tasks = sort_tasks_by_time_window(instance.tasks);

    for (const auto& task : sorted_tasks) {
        int best_technician_index = -1;
        int best_start_time = 0;
        int best_arrival_time = 0;
        int best_end_time = 0;
        int best_travel_time = 0;
        int best_waiting_time = 0;
        int best_score = std::numeric_limits<int>::max();

        int task_location_index = location_index.at(task.location_id);

        for (int tech_index = 0;
             tech_index < static_cast<int>(instance.technicians.size());
             ++tech_index) {
            const Technician& technician = instance.technicians[tech_index];

            if (!technician_has_required_skills(technician, task)) {
                continue;
            }

            const TechnicianState& state = technician_states[tech_index];

            int travel_time = instance.travel_matrix.duration(
                state.current_location_index,
                task_location_index
            );

            int arrival_time = state.current_time + travel_time;

            int start_service_time = std::max(
                arrival_time,
                task.time_window_start
            );

            int waiting_time = start_service_time - arrival_time;

            int end_service_time =
                start_service_time + task.service_duration;

            int end_location_index =
                location_index.at(technician.end_location_id);

            int return_time = instance.travel_matrix.duration(
                task_location_index,
                end_location_index
            );

            int projected_route_end_time = end_service_time + return_time;

            if (start_service_time > task.time_window_end) {
                continue;
            }

            if (projected_route_end_time > technician.available_to) {
                continue;
            }

            int score = end_service_time;

            if (score < best_score) {
                best_score = score;
                best_technician_index = tech_index;
                best_start_time = start_service_time;
                best_arrival_time = arrival_time;
                best_end_time = end_service_time;
                best_travel_time = travel_time;
                best_waiting_time = waiting_time;
            }
        }

        if (best_technician_index < 0) {
            solution.unassigned_task_ids.push_back(task.id);
            continue;
        }

        RouteStop stop;

        stop.task_id = task.id;
        stop.location_id = task.location_id;
        stop.arrival_time = best_arrival_time;
        stop.start_service_time = best_start_time;
        stop.end_service_time = best_end_time;
        stop.travel_time_from_previous = best_travel_time;
        stop.waiting_time = best_waiting_time;

        Route& route = solution.routes[best_technician_index];

        route.stops.push_back(stop);
        route.total_travel_time += best_travel_time;
        route.total_service_time += task.service_duration;
        route.total_waiting_time += best_waiting_time;
        route.end_time = best_end_time;

        technician_states[best_technician_index].current_location_index =
            task_location_index;

        technician_states[best_technician_index].current_time = best_end_time;
    }

    for (int tech_index = 0;
         tech_index < static_cast<int>(instance.technicians.size());
         ++tech_index) {
        const Technician& technician = instance.technicians[tech_index];
        Route& route = solution.routes[tech_index];
        TechnicianState& state = technician_states[tech_index];

        int end_location_index = location_index.at(technician.end_location_id);

        int return_travel_time = instance.travel_matrix.duration(
            state.current_location_index,
            end_location_index
        );

        route.total_travel_time += return_travel_time;
        route.end_time = state.current_time + return_travel_time;
    }

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
    } else if (solution.unassigned_task_ids.size() < instance.tasks.size()) {
        solution.status = SolutionStatus::PARTIAL;
    } else {
        solution.status = SolutionStatus::INFEASIBLE;
    }

    return solution;
}