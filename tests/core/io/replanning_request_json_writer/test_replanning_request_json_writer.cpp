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

static Effect make_replanning_request_writer_test_effect() {
    Effect effect;

    effect.effect_id = "test_runtime_effect_001";
    effect.type = EffectType::ADD_TRAVEL_DELAY;
    effect.occurrence_time = 125;
    effect.technician_id = "tech_1";
    effect.task_id = "task_C";
    effect.from_location_id = "task_A_location";
    effect.to_location_id = "task_C_location";
    effect.delay_duration = 50;
    effect.description = "Test runtime effect for request writer.";

    return effect;
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

    request.runtime_effects.push_back(
        make_replanning_request_writer_test_effect()
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

    FIELDOPS_EXPECT_TRUE(
        data.at("has_work").get<bool>()
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
        data.at("counts").at("technician_runtime_state_count").get<int>(),
        2
    );

    FIELDOPS_EXPECT_EQ(
        data.at("counts").at("runtime_effect_count").get<int>(),
        1
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

    FIELDOPS_EXPECT_EQ(
        data.at("technician_runtime_states").size(),
        2
    );

    FIELDOPS_EXPECT_EQ(
        data.at("technician_runtime_states").at(0).at("technician_id").get<std::string>(),
        "tech_1"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("technician_runtime_states").at(0).at("execution_status").get<std::string>(),
        "TRAVELING"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("technician_runtime_states").at(0).at("current_location_id").get<std::string>(),
        "task_A_location"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("technician_runtime_states").at(0).at("next_task_id").get<std::string>(),
        "task_C"
    );

    FIELDOPS_EXPECT_TRUE(
        data.at("technician_runtime_states").at(0).at("can_receive_candidate_tasks").get<bool>()
    );

    FIELDOPS_EXPECT_EQ(
        data.at("runtime_effects").size(),
        1
    );

    FIELDOPS_EXPECT_EQ(
        data.at("runtime_effects").at(0).at("effect_id").get<std::string>(),
        "test_runtime_effect_001"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("runtime_effects").at(0).at("type").get<std::string>(),
        "ADD_TRAVEL_DELAY"
    );

    FIELDOPS_EXPECT_EQ(
        data.at("runtime_effects").at(0).at("delay_duration").get<int>(),
        50
    );
}