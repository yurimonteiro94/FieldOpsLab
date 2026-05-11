cmake_minimum_required(VERSION 3.20)

project(FieldOpsLab VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

enable_testing()

set(FIELDOPS_CORE_SOURCES
    core/analysis/solution_comparison/solution_comparison.cpp
    core/experiment/no_replanning_batch_experiment/no_replanning_batch_experiment.cpp
    core/experiment/no_replanning_experiment/no_replanning_experiment.cpp
    core/instance/instance/instance.cpp
    core/instance/instance_validator/instance_validator.cpp
    core/io/instance_json_loader/instance_json_loader.cpp
    core/io/no_replanning_batch_config_json_loader/no_replanning_batch_config_json_loader.cpp
    core/io/no_replanning_experiment_result_json_writer/no_replanning_experiment_result_json_writer.cpp
    core/io/no_replanning_experiment_summary_csv_writer/no_replanning_experiment_summary_csv_writer.cpp
    core/io/perturbation_json_loader/perturbation_json_loader.cpp
    core/io/solution_comparison_json_writer/solution_comparison_json_writer.cpp
    core/io/solution_result_json_writer/solution_result_json_writer.cpp
    core/io/simulation_timeline_json_writer/simulation_timeline_json_writer.cpp
    core/solution/solution/solution.cpp
    core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.cpp
    core/metrics/solution_metrics/solution_metrics.cpp
    core/simulation/simulation_event/simulation_event.cpp
    core/simulation/simulation_engine/simulation_engine.cpp
    core/simulation/no_replanning_execution/no_replanning_execution.cpp
    core/perturbation/perturbation/perturbation.cpp
    core/perturbation/effect/effect.cpp
    core/perturbation/travel_delay_perturbation/travel_delay_perturbation.cpp
    core/perturbation/service_delay_perturbation/service_delay_perturbation.cpp
    core/perturbation/perturbation_effect_builder/perturbation_effect_builder.cpp
    core/policy/policy/policy.cpp
    core/policy/no_replanning_policy/no_replanning_policy.cpp
)

add_library(fieldops_core STATIC
    ${FIELDOPS_CORE_SOURCES}
)

target_include_directories(fieldops_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/external
)

add_executable(fieldops_lab
    app/main.cpp
)

target_link_libraries(fieldops_lab PRIVATE
    fieldops_core
)

add_executable(fieldops_tests
    tests/test_main.cpp
    tests/core/analysis/solution_comparison/test_solution_comparison.cpp
    tests/core/experiment/no_replanning_batch_experiment/test_no_replanning_batch_experiment.cpp
    tests/core/experiment/no_replanning_experiment/test_no_replanning_experiment.cpp
    tests/core/instance/instance/test_travel_matrix.cpp
    tests/core/instance/instance_validator/test_instance_validator.cpp
    tests/core/io/no_replanning_batch_config_json_loader/test_no_replanning_batch_config_json_loader.cpp
    tests/core/io/no_replanning_experiment_result_json_writer/test_no_replanning_experiment_result_json_writer.cpp
    tests/core/io/no_replanning_experiment_summary_csv_writer/test_no_replanning_experiment_summary_csv_writer.cpp
    tests/core/io/perturbation_json_loader/test_perturbation_json_loader.cpp
    tests/core/io/solution_comparison_json_writer/test_solution_comparison_json_writer.cpp
    tests/core/method/greedy_earliest_feasible_heuristic/test_greedy_earliest_feasible_heuristic.cpp
    tests/core/metrics/solution_metrics/test_solution_metrics.cpp
    tests/core/simulation/simulation_engine/test_simulation_timeline.cpp
    tests/core/simulation/no_replanning_execution/test_no_replanning_execution.cpp
    tests/core/perturbation/perturbation/test_perturbation.cpp
    tests/core/perturbation/effect/test_effect.cpp
    tests/core/perturbation/travel_delay_perturbation/test_travel_delay_perturbation.cpp
    tests/core/perturbation/service_delay_perturbation/test_service_delay_perturbation.cpp
    tests/core/perturbation/perturbation_effect_builder/test_perturbation_effect_builder.cpp
    tests/core/policy/policy/test_policy.cpp
    tests/core/policy/no_replanning_policy/test_no_replanning_policy.cpp
)

target_link_libraries(fieldops_tests PRIVATE
    fieldops_core
)

add_test(
    NAME fieldops_tests
    COMMAND fieldops_tests
)

set_tests_properties(fieldops_tests PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)