import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";

const healthPayload = {
  allows_arbitrary_command_execution: false,
  contract: {
    available: true,
    path: "platform/contracts/fieldops_platform_contract.json",
  },
  mode: "read_only",
  read_only: true,
  routes: [
    {
      description: "Return API status and read-only mode.",
      method: "GET",
      path: "/api/v1/health",
    },
    {
      description: "Return simulation state contract.",
      method: "GET",
      path: "/api/v1/simulation-state-contract",
    },
    {
      description: "Return simulation state sample.",
      method: "GET",
      path: "/api/v1/simulation-state-sample",
    },
    {
      description: "Return delay injection request contract.",
      method: "GET",
      path: "/api/v1/delay-injection-request-contract",
    },
  ],
  service: "fieldops_lab_api",
  status: "ok",
};

const projectStatusPayload = {
  conservative_note: "This dashboard does not prove scientific validity.",
  summary_metrics: {
    product_completeness: 56,
    engineering_status: "passed_current_structural_quality_gate",
    scientific_status: "diagnostic_only_with_methodological_warnings",
  },
};

const reportsPayload = {
  read_only: true,
  execution_supported: false,
  reports: [
    {
      id: "project_status",
      title: "Project status",
      category: "engineering",
      description: "Current structural engineering status.",
      artifact_path: "analysis/reports/project_status_report.json",
      markdown_path: "analysis/reports/project_status_report.md",
      quality_path: "analysis/reports/project_status_quality_check.json",
      available: true,
      loaded: true,
      markdown_available: true,
      quality_available: true,
      quality_passed: true,
    },
  ],
};

const experimentalDesignPayload = {
  report: "experimental_design_matrix",
  available: true,
  read_only: true,
  summary: {
    experiment_count: 648,
    scenario_count: 12,
    replication_count: 3,
    factor_count: 4,
    reproducible_from_explicit_factors: true,
  },
  factors: [],
  limitations: [
    "The matrix is a planning artifact, not final scientific validation.",
  ],
  quality_notes: [
    "The design is reproducible from explicit factors and replications.",
  ],
};

const researchMethodPayload = {
  read_only: true,
  available: true,
  contract_path: "platform/contracts/research_method_contract.json",
  framing_path: "platform/research_framing.md",
  framing_markdown: "# FieldOps Lab research framing",
  conservative_interpretation: {
    does_not_claim_final_scientific_validity: true,
    fuzzy_logic_is_optional: true,
    practical_equivalence_must_be_handled: true,
    real_company_data_requires_validation_before_decision_support: true,
  },
  contract: {
    status: "draft",
    scientific_maturity: "diagnostic_foundation",
    project_question: {
      summary:
        "How can a field service operation choose an appropriate replanning policy when operational disruptions occur during execution?",
    },
    research_gap: {
      specific_gap:
        "A replicable experimental and decision framework for comparing replanning policies under controlled dynamic disruptions.",
      primary_dynamic_focus: [
        "delay_propagation",
        "travel_delay",
        "service_delay",
      ],
      secondary_dynamic_focus: [
        "new_requests",
        "cancellations",
        "priority_changes",
      ],
    },
    contribution_claims: {
      claims_policy_decision_framework: true,
      claims_reproducible_experimental_platform: true,
    },
    fuzzy_logic_position: {
      preferred_baseline_alternatives: [
        "statistical_comparison",
        "practical_equivalence_thresholds",
      ],
    },
    current_completed_foundation: ["read_only_local_http_api"],
    missing_major_work: ["statistical_comparison_module"],
  },
};

const simulationContractPayload = {
  read_only: true,
  available: true,
  contract_path: "platform/contracts/simulation_state_contract.json",
  conservative_note:
    "Simulation state contract is read-only and does not enable browser-triggered execution.",
  safety_flags: {
    browser_execution_enabled: false,
    arbitrary_command_execution_allowed: false,
    write_operations_supported: false,
    future_job_api_currently_enabled: false,
  },
  contract: {
    modes: [
      {
        id: "optimization_mode",
        label: "Optimization mode",
        purpose:
          "Batch experiments, policy comparison, metrics, ranking, and statistical analysis.",
        execution_enabled: false,
      },
      {
        id: "simulation_mode",
        label: "Simulation mode",
        purpose:
          "Visual map and operational timeline for inspecting technicians, tasks, delays, and re-planning decisions.",
        execution_enabled: false,
      },
    ],
    scope: {
      primary_dissertation_scope: [
        "delay_propagation",
        "travel_delay",
        "service_delay",
      ],
      future_platform_perturbations: [
        "new_requests",
        "cancellations",
        "priority_changes",
      ],
    },
    state_schema: {
      map_entities: ["technicians", "tasks", "depots", "routes"],
      timeline: {
        events: [
          "simulation_started",
          "travel_delay_detected",
          "replanning_evaluation_required",
        ],
      },
    },
    replanning_decision: {
      fields: [
        "policy_id",
        "trigger_reason",
        "delay_minutes",
        "projected_lateness",
      ],
    },
    future_api_endpoints: [
      {
        method: "POST",
        path: "/api/v1/simulation-runs",
        status: "planned_not_enabled",
        execution_enabled: false,
      },
    ],
  },
};

const simulationSamplePayload = {
  schema: "fieldops_lab.simulation_state_sample_endpoint",
  read_only: true,
  available: true,
  execution_enabled: false,
  write_operations_supported: false,
  browser_triggered_execution_enabled: false,
  arbitrary_command_execution_allowed: false,
  artifact_path: "platform/contracts/simulation_state_sample.json",
  simulation_state_sample: {
    schema: "fieldops_lab.simulation_state_sample",
    version: "0.1.0",
    read_only: true,
    execution_enabled: false,
    write_operations_supported: false,
    browser_triggered_execution_enabled: false,
    arbitrary_command_execution_allowed: false,
    purpose:
      "Provide a conservative sample simulation state for future read-only map and timeline rendering.",
    clock: {
      simulation_id: "demo_delay_propagation_001",
      status: "paused",
      time_unit: "minutes",
      start_time: 0,
      current_time: 135,
      end_time: 480,
      speed_multiplier: 1,
      can_user_advance_time: false,
      can_user_inject_delay: false,
    },
    map: {
      coordinate_system: "normalized_demo_coordinates",
      depots: [
        {
          id: "depot_001",
          label: "Main depot",
          x: 10,
          y: 10,
        },
      ],
      technicians: [
        {
          id: "tech_001",
          label: "Technician 1",
          status: "traveling",
          x: 47,
          y: 52,
          current_task_id: "task_003",
          route_id: "route_001",
          delay_minutes: 18,
        },
        {
          id: "tech_002",
          label: "Technician 2",
          status: "servicing",
          x: 72,
          y: 31,
          current_task_id: "task_005",
          route_id: "route_002",
          delay_minutes: 0,
        },
      ],
      tasks: [
        {
          id: "task_001",
          label: "Customer 1",
          status: "completed",
          x: 22,
          y: 20,
          planned_start: 40,
          planned_end: 70,
          actual_start: 42,
          actual_end: 72,
          priority: "normal",
        },
        {
          id: "task_003",
          label: "Customer 3",
          status: "at_risk",
          x: 58,
          y: 68,
          planned_start: 145,
          planned_end: 180,
          actual_start: null,
          actual_end: null,
          priority: "high",
        },
        {
          id: "task_005",
          label: "Customer 5",
          status: "in_service",
          x: 72,
          y: 31,
          planned_start: 120,
          planned_end: 160,
          actual_start: 121,
          actual_end: null,
          priority: "normal",
        },
      ],
      routes: [
        {
          id: "route_001",
          technician_id: "tech_001",
          task_sequence: ["task_001", "task_003"],
          status: "delayed",
          total_delay_minutes: 18,
        },
      ],
    },
    timeline: [
      {
        time: 0,
        type: "simulation_started",
        label: "Simulation initialized",
        affected_entity_id: "demo_delay_propagation_001",
        delay_minutes: 0,
      },
      {
        time: 135,
        type: "travel_delay_detected",
        label: "Travel delay detected before Task 3",
        affected_entity_id: "tech_001",
        delay_minutes: 18,
      },
      {
        time: 135,
        type: "replanning_evaluation_required",
        label: "Delay threshold reached for replanning evaluation",
        affected_entity_id: "route_001",
        delay_minutes: 18,
      },
    ],
    replanning_decision: {
      status: "evaluation_required",
      trigger: "travel_delay_threshold",
      trigger_time: 135,
      affected_route_id: "route_001",
      affected_technician_id: "tech_001",
      primary_delay_type: "travel_delay",
      delay_propagation_detected: true,
      candidate_policies: [
        {
          id: "no_replanning",
          label: "No replanning",
          execution_enabled: false,
        },
        {
          id: "threshold_delay_replanning",
          label: "Threshold delay replanning",
          execution_enabled: false,
        },
      ],
      decision_fields: [
        "policy_id",
        "trigger_reason",
        "delay_minutes",
        "projected_lateness",
      ],
    },
    research_scope: {
      primary_dissertation_scope: [
        "delay_propagation",
        "travel_delay",
        "service_delay",
      ],
      future_platform_perturbations: [
        "new_requests",
        "cancellations",
        "priority_changes",
      ],
    },
    safety_notes: [
      "This sample is static and read-only.",
      "It must not trigger optimization, simulation execution, shell commands, solver calls, file writes, or backend jobs.",
    ],
  },
};

const delayInjectionContractPayload = {
  schema: "fieldops_lab.delay_injection_request_contract_endpoint",
  version: "0.1.0",
  read_only: true,
  execution_enabled: false,
  write_operations_supported: false,
  browser_triggered_execution_enabled: false,
  artifact_path: "platform/contracts/delay_injection_request_contract.json",
  planned_endpoint: {
    method: "POST",
    path: "/api/v1/simulation-runs/{simulation_run_id}/delay-events",
    status: "planned_not_enabled",
    current_behavior: "No write endpoint is currently exposed by the read-only API.",
    execution_enabled: false,
    requires_future_authentication: true,
    requires_future_server_side_validation: true,
    requires_future_audit_log: true,
  },
  delay_injection_request_contract: {
    contract: "delay_injection_request_contract",
    version: "0.1.0",
    status: "planned_disabled",
    read_only: true,
    execution_enabled: false,
    write_operations_supported: false,
    browser_execution_enabled: false,
    primary_purpose:
      "Define the future request shape for injecting delays during visual simulation without enabling execution yet.",
    research_alignment: {
      primary_dissertation_scope: [
        "delay_propagation",
        "travel_delay",
        "service_delay",
      ],
      future_platform_extensions: [
        "new_requests",
        "cancellations",
        "priority_changes",
      ],
      scope_policy:
        "The dissertation should stay focused on delays and delay propagation.",
    },
    planned_endpoint: {
      method: "POST",
      path: "/api/v1/simulation-runs/{simulation_run_id}/delay-events",
      status: "planned_not_enabled",
      current_behavior: "No write endpoint is currently exposed by the read-only API.",
      execution_enabled: false,
      requires_future_authentication: true,
      requires_future_server_side_validation: true,
      requires_future_audit_log: true,
    },
    request_shape: {
      simulation_run_id: {
        type: "string",
        required: true,
        description:
          "Identifier of the future simulation run receiving the delay event.",
      },
      event_type: {
        type: "string",
        required: true,
        allowed_values: ["travel_delay", "service_delay"],
        description: "Primary delay type.",
      },
      target_type: {
        type: "string",
        required: true,
        allowed_values: ["technician", "task", "route_leg"],
        description: "Operational object affected by the injected delay.",
      },
      delay_minutes: {
        type: "number",
        required: true,
        minimum: 0,
        description:
          "Non-negative delay duration added to the affected object.",
      },
      source: {
        type: "string",
        required: true,
        allowed_values: [
          "user_injected",
          "scripted_scenario",
          "imported_scenario",
        ],
        description: "Origin of the delay event.",
      },
      replanning_policy_hint: {
        type: "string",
        required: false,
        allowed_values: [
          "no_replanning",
          "threshold_delay_replanning",
          "periodic_replanning",
          "event_based_replanning",
          "not_specified",
        ],
        description:
          "Optional future hint for selecting or comparing re-planning policies.",
      },
    },
    validation_rules: [
      "event_type must be travel_delay or service_delay for the current dissertation-oriented experiments.",
      "delay injection must not mutate production data.",
      "delay injection must not execute solvers directly from the browser.",
    ],
    expected_future_effects: [
      "Update the simulation timeline.",
      "Track propagated delay across subsequent tasks.",
    ],
    replanning_decision_output: {
      required_future_fields: [
        "decision_id",
        "policy_id",
        "triggered",
        "trigger_reason",
        "stability_delta",
      ],
      current_status: "not_executed_by_this_contract",
    },
    safety_requirements: {
      read_only_contract_only: true,
      no_browser_solver_execution: true,
      no_arbitrary_command_execution: true,
      no_file_system_mutation_from_web: true,
      no_production_data_mutation: true,
    },
    quality_requirements: [
      "The contract must distinguish travel delay from service delay.",
      "The contract must preserve delay propagation as the narrow dissertation scope.",
    ],
    conservative_note:
      "This file is only a read-only planning contract. It does not enable delay injection, simulation execution, solver execution, optimization jobs, or write operations.",
  },
};


const replanningDecisionResponseContractPayload = {
  schema: "fieldops_lab.replanning_decision_response_contract_endpoint",
  version: "0.1.0",
  read_only: true,
  execution_enabled: false,
  write_operations_supported: false,
  browser_triggered_execution_enabled: false,
  artifact_path: "platform/contracts/replanning_decision_response_contract.json",
  future_endpoint: {
    method: "POST",
    path: "/api/v1/replanning-decisions",
    status: "planned_not_enabled",
    execution_enabled: false,
  },
  replanning_decision_response_contract: {
    contract_name: "replanning_decision_response_contract",
    version: "0.1.0",
    status: "planned_read_only_contract",
    enabled: false,
    execution_enabled: false,
    current_endpoint_enabled: false,
    future_endpoint: {
      method: "POST",
      path: "/api/v1/replanning-decisions",
      status: "planned_not_enabled",
      execution_enabled: false,
    },
    input_references: {
      simulation_id: "Current simulation state identifier.",
      delay_injection_request_id: "Future delay injection request identifier.",
      policy_id: "Candidate policy evaluated by the future engine.",
      baseline_solution_id: "Baseline solution used for comparison.",
    },
    response_shape: {
      feasibility: {
        label: "Feasibility",
        fields: ["is_feasible", "violated_constraints", "infeasibility_reason"],
      },
      performance_delta: {
        label: "Performance delta",
        fields: ["objective_delta", "total_delay_delta", "lateness_delta"],
      },
      stability_delta: {
        label: "Stability delta",
        fields: ["changed_assignments_count", "changed_sequence_count", "stability_score"],
      },
      computational_cost: {
        label: "Computational cost",
        fields: ["solver_time_ms", "wall_time_ms", "iteration_count"],
      },
      delay_propagation: {
        label: "Delay propagation",
        fields: ["affected_tasks_count", "propagated_delay_minutes", "recovered_delay_minutes"],
      },
      explanation: {
        label: "Explanation",
        fields: ["selected_policy_reason", "tradeoff_summary", "conservative_warning"],
      },
    },
    status_values: [
      {
        value: "planned_not_executed",
        description: "Contract shape is visible, but no re-planning is executed.",
      },
      {
        value: "future_decision_ready",
        description: "Reserved for a future validated backend decision.",
      },
    ],
    related_contracts: [
      "simulation_state_contract",
      "simulation_state_sample",
      "delay_injection_request_contract",
    ],
    safety_requirements: {
      no_browser_solver_execution: true,
      no_file_write_from_browser: true,
      no_operational_claim_without_backend_result: true,
    },
    quality_requirements: [
      "The response must preserve feasibility, performance, stability, computational cost, and delay propagation metrics.",
      "The response must support later policy comparison without claiming final scientific validity.",
    ],
    conservative_note:
      "This contract only defines the future response shape. It does not execute re-planning, solvers, optimization, simulation, write operations, or backend jobs.",
  },
};

const replanningDecisionResponseSamplePayload = {
  schema: "fieldops_lab.replanning_decision_response_sample_endpoint",
  version: "0.1.0",
  read_only: true,
  execution_enabled: false,
  write_operations_supported: false,
  browser_triggered_execution_enabled: false,
  artifact_path: "platform/contracts/replanning_decision_response_sample.json",
  safety_note:
    "This endpoint exposes a static read-only sample of a future re-planning decision response. It does not execute re-planning, run solvers, start optimization, start simulations, mutate schedules, write files, or trigger backend jobs.",
  replanning_decision_response_sample: {
    schema: "fieldops_lab.replanning_decision_response_sample",
    version: "0.1.0",
    sample_id: "demo_replanning_decision_response_001",
    sample_status: "planned_not_executed",
    read_only: true,
    execution_enabled: false,
    decision_summary: {
      decision_status: "not_executed_by_this_sample",
      decision_enabled: false,
      execution_status: "disabled",
      recommendation: "manual_review_required",
      reason:
        "The sample shows how a future response could compare a baseline and a threshold-delay re-planning candidate without executing a solver.",
    },
    delay_propagation: {
      injected_delay_minutes: 18,
      propagated_delay_minutes_baseline: 42,
      propagated_delay_minutes_candidate: 16,
      recovered_delay_minutes: 26,
    },
    tradeoff_summary: {
      dominant_benefit: "lower_delay_propagation",
      dominant_risk: "schedule_instability",
      policy_comparison_ready: true,
      statistical_claim_ready: false,
      decision_rule_ready: false,
    },
    conservative_note:
      "Sample only. No operational decision is executed, no solver is called, and no schedule is mutated.",
  },
};

function jsonResponse(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

function installSuccessfulFetchMock() {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);

      if (url.endsWith("/api/v1/health")) {
        return Promise.resolve(jsonResponse(healthPayload));
      }

      if (url.endsWith("/api/v1/project-status")) {
        return Promise.resolve(jsonResponse(projectStatusPayload));
      }

      if (url.endsWith("/api/v1/reports")) {
        return Promise.resolve(jsonResponse(reportsPayload));
      }

      if (url.endsWith("/api/v1/experimental-design-matrix")) {
        return Promise.resolve(jsonResponse(experimentalDesignPayload));
      }

      if (url.endsWith("/api/v1/research-method")) {
        return Promise.resolve(jsonResponse(researchMethodPayload));
      }

      if (url.endsWith("/api/v1/simulation-state-contract")) {
        return Promise.resolve(jsonResponse(simulationContractPayload));
      }

      if (url.endsWith("/api/v1/simulation-state-sample")) {
        return Promise.resolve(jsonResponse(simulationSamplePayload));
      }


      if (url.endsWith("/api/v1/replanning-decision-response-contract")) {
        return Promise.resolve(jsonResponse(replanningDecisionResponseContractPayload));
      }
    if (url.endsWith("/api/v1/replanning-decision-response-sample")) {
      return Promise.resolve(jsonResponse(replanningDecisionResponseSamplePayload));
    }

      if (url.endsWith("/api/v1/delay-injection-request-contract")) {
        return Promise.resolve(jsonResponse(delayInjectionContractPayload));
      }

      return Promise.resolve(
        new Response(JSON.stringify({ error: "not_found" }), {
          status: 404,
        }),
      );
    }),
  );
}

describe("Simulation workspace page", () => {
  beforeEach(() => {
    installSuccessfulFetchMock();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads the simulation state sample, delay injection contract, decision response contract, and decision response sample without enabling browser execution", async () => {
    render(<App />);

    expect(await screen.findByText("Experimental platform dashboard")).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Simulation workspace" }));

    expect(await screen.findByText("Visual operation simulation foundation")).not.toBeNull();

    expect(screen.getByText("Read-only contract-backed workspace")).not.toBeNull();
    expect(screen.getAllByText("demo_delay_propagation_001").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Normalized operation map")).not.toBeNull();

    expect(screen.getByRole("heading", { name: "Technician 1" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "Technician 2" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "Customer 3" })).not.toBeNull();

    expect(screen.getByText("Delay propagation events")).not.toBeNull();
    expect(screen.getByText("Travel delay detected before Task 3")).not.toBeNull();
    expect(
      screen.getByText("Delay threshold reached for replanning evaluation"),
    ).not.toBeNull();

    expect(screen.getByText("No replanning")).not.toBeNull();
    expect(screen.getByText("Threshold delay replanning")).not.toBeNull();

    expect(screen.getByText("Delay injection request contract")).not.toBeNull();
    expect(screen.getByText("planned disabled")).not.toBeNull();
    expect(
      screen.getByText("/api/v1/simulation-runs/{simulation_run_id}/delay-events"),
    ).not.toBeNull();
    expect(screen.getByRole("heading", { name: "event_type" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "delay_minutes" })).not.toBeNull();
    expect(screen.getByText("travel delay, service delay")).not.toBeNull();
    expect(screen.getByText("user injected, scripted scenario, imported scenario")).not.toBeNull();
    expect(screen.getByText("not_executed_by_this_contract")).not.toBeNull();

    expect(screen.getByText("Re-planning decision response contract")).not.toBeNull();
    expect(screen.getByText("/api/v1/replanning-decisions")).not.toBeNull();
    expect(screen.getByRole("heading", { name: "performance_delta" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "stability_delta" })).not.toBeNull();
    expect(
      screen.getByText("objective delta, total delay delta, lateness delta"),
    ).not.toBeNull();
    expect(
      screen.getByText("simulation state contract, simulation state sample, delay injection request contract"),
    ).not.toBeNull();



    expect(screen.getAllByText("execution disabled").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Current state is conservative.").length).toBeGreaterThan(0);
    expect(
      screen.getByText(/It must not trigger optimization, simulation execution/),
    ).not.toBeNull();
    expect(
      screen.getByText(/It does not enable delay injection, simulation execution/),
    ).not.toBeNull();

    const fetchMock = globalThis.fetch as unknown as {
      mock: {
        calls: Array<[RequestInfo | URL, RequestInit | undefined]>;
      };
    };

    const requestedUrls = fetchMock.mock.calls.map((call) => String(call[0]));

    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/simulation-state-contract",
    );
    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/simulation-state-sample",
    );
    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/delay-injection-request-contract",
    );

    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/replanning-decision-response-contract",
    );


    expect(
      requestedUrls.some((url) => url.includes("/api/v1/simulation-runs")),
    ).toBe(false);
    expect(
      requestedUrls.some((url) => url.includes("/delay-events")),
    ).toBe(false);
  });
});