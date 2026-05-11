#include "core/io/instance_json_loader/instance_json_loader.h"
#include "core/io/replanning_request_json_writer/replanning_request_json_writer.h"
#include "core/method/greedy_earliest_feasible_heuristic/greedy_earliest_feasible_heuristic.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/simulation/simulation_state/simulation_state.h"
#include "tests/test_support/test_assertions.h"

#include <filesystem>
#include <fstream>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

static PolicyDecision make_replanning_request_writer_test_decision() {
    PolicyDecision decision;

    decision.policy_id = "threshold_delay_replanning_policy_v1";
    decision.type = PolicyDecisionType::REPLAN;
    decision.decision_time = 125;
    decision.reason = "Test replanning request JSON writer decision.";

    return decision;
}

void test_replanning_request_json_writer() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    Solution solution =
        build_initial_solution_greedy_earliest_feasible(instance);

    SimulationSnapshot snapshot =
        build_simulation_snapshot_from_solution(instance, solution, 125);

    PolicyDecision decision =
        make_replanning_request_writer_test_decision();

    ReplanningRequest request =
        build_replanning_request_from_snapshot(
            snapshot,
            decision,
            "test_replanning_request_writer_001"
        );

    const std::string output_path =
        "data/results/test_replanning_request_writer.json";

    std::filesystem::remove(output_path);

    write_replanning_request_to_json(
        request,
        output_path,
        "test_replanning_request"
    );

    FIELDOPS_EXPECT_TRUE(std::filesystem::exists(output_path));

    std::ifstream file(output_path);
    json data;
    file >> data;

    FIELDOPS_EXPECT_EQ(
        data.at("result_type").get<std::string>(),
        "test_replanning_request"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("request_id").get<std::string>(),
        "test_replanning_request_writer_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("decision_time").get<int>(),
        125
    );

    FIELDOPS_EXPECT_EQ(
        data.at("policy_id").get<std::string>(),
        "threshold_delay_replanning_policy_v1"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("policy_decision").get<std::string>(),
        "REPLAN"
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("should_replan").get<bool>()
    );

    FIELDOPS_EXPECT_EQ(
        data.at("counts").at("completed_task_count").get<int>(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        data.at("counts").at("locked_task_count").get<int>(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        data.at("counts").at("candidate_task_count").get<int>(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        data.at("counts").at("busy_technician_count").get<int>(),
        2
    );

    FIELDOPS_EXPECT_EQ(
        data.at("tasks").at("completed_task_ids").at(0).get<std::string>(),
        "task_A"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("tasks").at("locked_task_ids").at(0).get<std::string>(),
        "task_B"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("tasks").at("candidate_task_ids").at(0).get<std::string>(),
        "task_C"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("technicians").at("busy_technician_ids").size(),
        2
    );
}