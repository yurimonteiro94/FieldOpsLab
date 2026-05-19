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
      description: "Return generated report catalog.",
      method: "GET",
      path: "/api/v1/reports",
    },
    {
      description: "Return research method framing.",
      method: "GET",
      path: "/api/v1/research-method",
    },
    {
      description: "Return simulation state contract.",
      method: "GET",
      path: "/api/v1/simulation-state-contract",
    },
  ],
  service: "fieldops_lab_api",
  status: "ok",
};

const projectStatusPayload = {
  conservative_note: "This dashboard does not prove scientific validity.",
  summary_metrics: {
    product_completeness: 59,
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

const simulationStateContractPayload = {
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
    state_schema: {
      map_entities: [
        "technicians",
        "tasks",
        "depots",
        "routes",
        "operational_events",
      ],
      timeline: {
        event_types: [
          "planned_start",
          "arrival",
          "service_start",
          "delay",
          "replanning_decision",
        ],
      },
    },
    replanning_decision: {
      decision_fields: [
        "policy_id",
        "trigger_reason",
        "computational_cost",
        "route_stability",
        "practical_equivalence_status",
      ],
    },
    future_api_endpoints: [
      {
        method: "POST",
        path: "/api/v1/simulation-jobs",
        status: "planned_not_enabled",
        execution_enabled: false,
      },
    ],
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
        return Promise.resolve(jsonResponse(simulationStateContractPayload));
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

  it("loads the simulation state contract without enabling browser execution", async () => {
    render(<App />);

    expect(await screen.findByText("Experimental platform dashboard")).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Simulation workspace" }));

    expect(
      await screen.findByText("Visual operation simulation foundation"),
    ).not.toBeNull();

    expect(
      await screen.findByText("Read-only contract-backed workspace"),
    ).not.toBeNull();

    expect(screen.getByText("Optimization mode and simulation mode")).not.toBeNull();
    expect(screen.getByText("Future real-time map components")).not.toBeNull();
    expect(screen.getByText("Timeline events and delay propagation")).not.toBeNull();
    expect(screen.getByText("Delays first, platform extensible later")).not.toBeNull();
    expect(screen.getByText("Decision fields to preserve cost and stability evidence")).not.toBeNull();
    expect(screen.getByText("Browser-triggered execution remains disabled")).not.toBeNull();
    expect(screen.getByText("Planned endpoints are visible but not enabled")).not.toBeNull();

    expect(screen.getByText("platform/contracts/simulation_state_contract.json")).not.toBeNull();
    expect(screen.getByText("technicians")).not.toBeNull();
    expect(screen.getByText("replanning decision")).not.toBeNull();
    expect(screen.getByText("computational cost")).not.toBeNull();
    expect(screen.getByText("/api/v1/simulation-jobs")).not.toBeNull();

    expect(screen.getByText("Browser execution")).not.toBeNull();
    expect(screen.getByText("Arbitrary command execution")).not.toBeNull();
    expect(screen.getByText("Write operations")).not.toBeNull();
    expect(screen.getByText("Future job API")).not.toBeNull();

    expect(
      screen.getByText(
        "Simulation state contract is read-only and does not enable browser-triggered execution.",
      ),
    ).not.toBeNull();
  });
});