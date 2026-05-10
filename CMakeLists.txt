cmake_minimum_required(VERSION 3.20)

project(FieldOpsLab VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(fieldops_lab
    app/main.cpp
    core/instance/instance/instance.cpp
    core/instance/instance_validator/instance_validator.cpp
    core/io/instance_json_loader/instance_json_loader.cpp
    core/io/solution_result_json_writer/solution_result_json_writer.cpp
    core/io/simulation_timeline_json_writer/simulation_timeline_json_writer.cpp
    core/solution/solution/solution.cpp
    core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.cpp
    core/metrics/solution_metrics/solution_metrics.cpp
    core/simulation/simulation_event/simulation_event.cpp
    core/simulation/simulation_engine/simulation_engine.cpp
)

target_include_directories(fieldops_lab PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/external
)