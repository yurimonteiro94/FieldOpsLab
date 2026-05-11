#include "core/analysis/solution_comparison/solution_comparison.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/perturbation_json_loader/perturbation_json_loader.h"
#include "core/io/solution_comparison_json_writer/solution_comparison_json_writer.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/perturbation_effect_builder/perturbation_effect_builder.h"
#include "core/simulation/no_replanning_execution/no_replanning_execution.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>
#include <vector>

using json = nlohmann::json;

void test_solution_comparison_json_writer() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution planned_solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SolutionMetrics planned_metrics =
        calculate_solution_metrics(instance, planned_solution);

    PerturbationPlan perturbation_plan =
        load_perturbation_plan_from_json(
            "data/perturbations/sample_perturbations_001.json"
        );

    std::vector<Effect> effects =
        build_effects_from_perturbation_plan(perturbation_plan);

    Solution executed_solution =
        execute_solution_without_replanning(
            instance,
            planned_solution,
            effects
        );

    SolutionMetrics executed_metrics =
        calculate_solution_metrics(instance, executed_solution);

    SolutionComparison comparison =
        compare_solution_metrics(planned_metrics, executed_metrics);

    const std::string output_path =
        "data/results/test_solution_comparison_writer.json";

    std::filesystem::remove(output_path);

    write_solution_comparison_to_json(
        instance,
        planned_solution,
        executed_solution,
        comparison,
        output_path,
        "test_solution_comparison"
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::ifstream file(output_path);
    json data;
    file >> data;

    FIELDOPS_EXPECT_EQ(
        data.at("result_type").get<std::string>(),
        "test_solution_comparison"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("instance_id").get<std::string>(),
        "sample_instance_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("deltas").at("total_travel_time").get<int>(),
        50
    );

    FIELDOPS_EXPECT_EQ(
        data.at("deltas").at("total_service_time").get<int>(),
        30
    );

    FIELDOPS_EXPECT_EQ(
        data.at("deltas").at("total_waiting_time").get<int>(),
        -35
    );

    FIELDOPS_EXPECT_EQ(
        data.at("deltas").at("makespan").get<int>(),
        15
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("percentages").at("objective_value").get<double>() > 4.0
    );
}