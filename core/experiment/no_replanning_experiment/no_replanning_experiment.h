#pragma once

#include <string>
#include <vector>

#include "core/analysis/solution_comparison/solution_comparison.h"
#include "core/experiment/experiment_metadata/experiment_metadata.h"
#include "core/instance/instance/instance.h"
#include "core/instance/instance_validator/instance_validator.h"
#include "core/metrics/solution_metrics/solution_metrics.h"
#include "core/perturbation/effect/effect.h"
#include "core/perturbation/perturbation/perturbation.h"
#include "core/policy/policy/policy.h"
#include "core/policy/policy_evaluator/policy_evaluator.h"
#include "core/replanning/replanning_request/replanning_request.h"
#include "core/replanning/replanning_result/replanning_result.h"
#include "core/simulation/simulation_engine/simulation_engine.h"
#include "core/solution/solution/solution.h"

struct NoReplanningExperimentConfig {
    ExperimentMetadata metadata;

    PolicyEvaluationConfig policy_config;

    std::string instance_path = "data/instances/sample_instance_001.json";

    std::string perturbation_plan_path =
        "data/perturbations/sample_perturbations_001.json";

    std::string planned_solution_output_path =
        "data/results/sample_planned_solution_result_001.json";

    std::string planned_timeline_output_path =
        "data/results/sample_planned_timeline_001.json";

    std::string executed_solution_output_path =
        "data/results/sample_executed_solution_no_replanning_001.json";

    std::string executed_timeline_output_path =
        "data/results/sample_executed_timeline_no_replanning_001.json";

    std::string comparison_output_path =
        "data/results/sample_solution_comparison_no_replanning_001.json";

    std::string experiment_result_output_path =
        "data/results/sample_no_replanning_experiment_result_001.json";

    std::string experiment_summary_csv_output_path =
        "data/results/sample_no_replanning_experiment_summary_001.csv";

    std::string replanning_request_output_path =
        "data/results/sample_replanning_request_001.json";

    bool verbose = true;
    bool export_results = true;
};

struct NoReplanningExperimentResult {
    ExperimentMetadata metadata;

    Instance instance;
    ValidationResult validation_result;

    Solution planned_solution;
    SolutionMetrics planned_metrics;
    SimulationTimeline planned_timeline;

    PerturbationPlan perturbation_plan;
    std::vector<Effect> effects;

    PolicyDecision policy_decision;

    bool has_replanning_request = false;
    ReplanningRequest replanning_request;

    bool has_replanning_result = false;
    ReplanningResult replanning_result;

    Solution executed_solution;
    SolutionMetrics executed_metrics;
    SimulationTimeline executed_timeline;

    SolutionComparison comparison;
};

NoReplanningExperimentResult run_no_replanning_experiment(
    const NoReplanningExperimentConfig& config
);