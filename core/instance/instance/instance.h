#pragma once

#include <string>
#include <vector>

struct PlanningHorizon {
    int start = 0;
    int end = 0;
};

struct Location {
    std::string id;
    std::string name;
    std::string address;
    double latitude = 0.0;
    double longitude = 0.0;
};

struct Technician {
    std::string id;
    std::string name;
    std::string start_location_id;
    std::string end_location_id;
    int available_from = 0;
    int available_to = 0;
    std::vector<std::string> skills;
};

struct Task {
    std::string id;
    std::string name;
    std::string location_id;
    int service_duration = 0;
    int time_window_start = 0;
    int time_window_end = 0;
    std::vector<std::string> required_skills;
    int priority = 0;
};

struct TravelMatrix {
    std::vector<std::string> location_ids;

    // Internal flattened matrices.
    // Access position: row * size + column.
    std::vector<int> durations;
    std::vector<double> distances;

    int size = 0;

    int index(int from, int to) const;
    int duration(int from, int to) const;
    double distance(int from, int to) const;
};

struct Instance {
    std::string instance_id;
    std::string name;
    std::string description;
    std::string time_unit;

    PlanningHorizon planning_horizon;

    std::vector<Location> locations;
    std::vector<Technician> technicians;
    std::vector<Task> tasks;

    TravelMatrix travel_matrix;
};

void print_instance_summary(const Instance& instance);