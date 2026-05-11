cmake_minimum_required(VERSION 3.20)

project(FieldOpsLab VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

enable_testing()

file(GLOB_RECURSE FIELDOPS_CORE_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/core/*.cpp"
)

file(GLOB_RECURSE FIELDOPS_TEST_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/tests/core/*.cpp"
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
    ${FIELDOPS_TEST_SOURCES}
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