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

  it("documents the future visual simulation mode without enabling execution", async () => {
    render(<App />);

    expect(
      await screen.findByText("Experimental platform dashboard"),
    ).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Simulation workspace" }));

    expect(
      await screen.findByText("Visual operation simulation foundation"),
    ).not.toBeNull();

    expect(
      screen.getByText("Optimization mode and simulation mode"),
    ).not.toBeNull();
    expect(screen.getByText("Real-time operation map")).not.toBeNull();
    expect(screen.getByText("Operational timeline")).not.toBeNull();
    expect(screen.getByText("Technician state cards")).not.toBeNull();
    expect(screen.getByText("Perturbation injection panel")).not.toBeNull();
    expect(screen.getByText("Delays first, platform extensible later")).not.toBeNull();
    expect(screen.getByText("Simulation state schema")).not.toBeNull();
    expect(screen.getByText("Controlled simulation runner")).not.toBeNull();
    expect(
      screen.getByText(
        "The current web dashboard remains read-only. No browser-triggered optimization or simulation execution is exposed yet.",
      ),
    ).not.toBeNull();
  });
});