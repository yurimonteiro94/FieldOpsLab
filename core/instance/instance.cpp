#include "core/instance/instance.h"

#include <iostream>
#include <stdexcept>

int TravelMatrix::index(int from, int to) const {
    if (from < 0 || to < 0 || from >= size || to >= size) {
        throw std::out_of_range("TravelMatrix index out of range.");
    }

    return from * size + to;
}

int TravelMatrix::duration(int from, int to) const {
    return durations.at(index(from, to));
}

double TravelMatrix::distance(int from, int to) const {
    return distances.at(index(from, to));
}

void print_instance_summary(const Instance& instance) {
    std::cout << "Instance ID: " << instance.instance_id << "\n";
    std::cout << "Name: " << instance.name << "\n";
    std::cout << "Description: " << instance.description << "\n";
    std::cout << "Time unit: " << instance.time_unit << "\n";

    std::cout << "Planning horizon: "
              << instance.planning_horizon.start
              << " to "
              << instance.planning_horizon.end
              << "\n";

    std::cout << "Locations: " << instance.locations.size() << "\n";
    std::cout << "Technicians: " << instance.technicians.size() << "\n";
    std::cout << "Tasks: " << instance.tasks.size() << "\n";

    std::cout << "Travel matrix size: "
              << instance.travel_matrix.size
              << " x "
              << instance.travel_matrix.size
              << "\n";

    if (instance.travel_matrix.size >= 2) {
        std::cout << "Sample duration from location 0 to 1: "
                  << instance.travel_matrix.duration(0, 1)
                  << " "
                  << instance.time_unit
                  << "\n";

        std::cout << "Sample distance from location 0 to 1: "
                  << instance.travel_matrix.distance(0, 1)
                  << "\n";
    }
}