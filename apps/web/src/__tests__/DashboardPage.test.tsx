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
  ],
  service: "fieldops_lab_api",
  status: "ok",
};

const projectStatusPayload = {
  conservative_note: "This dashboard does not prove scientific validity.",
  summary_metrics: {
    product_completeness: 46,
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
      quality_path: "analysis/reports/project_status_quality_check.json",
      available: true,
      loaded: true,
      quality_passed: true,
    },
  ],
};

const experimentalDesignPayload = {
  summary: {
    experiment_count: 648,
    scenario_count: 12,
    replication_count: 3,
    reproducible_from_explicit_factors: true,
  },
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
        "How can a field service operation choose an appropriate replanning policy when operational disruptions occur during the execution of a dynamic TRSP or WSRP schedule?",
    },
    research_gap: {
      specific_gap:
        "A replicable experimental and decision framework for comparing replanning policies under controlled dynamic disruptions and recommending policies by scenario class.",
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
        "dominance_rules",
      ],
    },
    current_completed_foundation: [
      "core_cpp_tests",
      "read_only_local_http_api",
      "web_dashboard_connected_to_api",
    ],
    missing_major_work: [
      "statistical_comparison_module",
      "policy_recommendation_method",
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

      return Promise.resolve(
        new Response(JSON.stringify({ error: "not_found" }), {
          status: 404,
        }),
      );
    }),
  );
}

describe("App dashboard", () => {
  beforeEach(() => {
    installSuccessfulFetchMock();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the dashboard with API-backed data", async () => {
    render(<App />);

    expect(
      await screen.findByText("Experimental platform dashboard"),
    ).not.toBeNull();
    expect(screen.getAllByText("46%")).toHaveLength(2);
    expect(screen.getByText("local http api")).not.toBeNull();
    expect(screen.getByText("Project status")).not.toBeNull();
    expect(screen.getByText("648")).not.toBeNull();
    expect(screen.getByText("disabled")).not.toBeNull();
  });

  it("navigates to report catalog and scientific validation pages", async () => {
    render(<App />);

    expect(
      await screen.findByText("Experimental platform dashboard"),
    ).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Reports" }));

    expect(await screen.findByText("Report catalog")).not.toBeNull();
    expect(screen.getByText("1 reports exposed")).not.toBeNull();

    fireEvent.click(
      screen.getByRole("button", { name: "Scientific validation" }),
    );

    expect(await screen.findByText("Evidence and risk control")).not.toBeNull();
    expect(
      screen.getByText(
        "Generated artifacts are engineering and diagnostic evidence, not final scientific validation.",
      ),
    ).not.toBeNull();
  });

  it("navigates to the research method page", async () => {
    render(<App />);

    expect(
      await screen.findByText("Experimental platform dashboard"),
    ).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Research method" }));

    expect(await screen.findByText("Decision method framing")).not.toBeNull();
    expect(screen.getByText("Research gap")).not.toBeNull();
    expect(screen.getByText("Delay propagation")).not.toBeNull();
    expect(screen.getByText("optional")).not.toBeNull();
    expect(screen.getByText("Practical equivalence")).not.toBeNull();
  });

  it("shows a conservative error state when the API fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(
          new Response(JSON.stringify({ error: "not_found" }), {
            status: 404,
          }),
        ),
      ),
    );

    render(<App />);

    expect(await screen.findByText("Could not load platform data")).not.toBeNull();
    expect(screen.getByText("API unavailable")).not.toBeNull();
  });
});