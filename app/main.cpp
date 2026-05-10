#include <exception>
#include <iostream>
#include <string>

#include "core/instance/instance.h"
#include "core/io/instance_json_loader.h"

int main(int argc, char* argv[]) {
    std::string instance_path = "data/instances/sample_instance_001.json";

    if (argc >= 2) {
        instance_path = argv[1];
    }

    try {
        std::cout << "FieldOps Lab - simulation engine started.\n";
        std::cout << "Loading instance: " << instance_path << "\n\n";

        Instance instance = load_instance_from_json(instance_path);

        print_instance_summary(instance);

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}