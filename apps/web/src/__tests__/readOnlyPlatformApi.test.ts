import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";

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
  report: "project_status",
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
  report: "experimental_design_matrix",
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

describe("ReadOnlyPlatformApi", () => {
  beforeEach(() => {
    installSuccessfulFetchMock();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads a complete read-only platform snapshot", async () => {
    const api = new ReadOnlyPlatformApi("http://127.0.0.1:8080");

    const snapshot = await api.getSnapshot();

    expect(snapshot.health.service).toBe("fieldops_lab_api");
    expect(snapshot.health.readOnly).toBe(true);
    expect(snapshot.health.allowsArbitraryCommandExecution).toBe(false);
    expect(snapshot.status.productCompleteness).toBe(46);
    expect(snapshot.status.executionStatus).toBe("disabled");
    expect(snapshot.reports).toHaveLength(1);
    expect(snapshot.reports[0]?.title).toBe("Project status");
    expect(snapshot.experimentalDesign.experimentCount).toBe(648);
    expect(snapshot.researchMethod.contractSummary.scientificMaturity).toBe(
      "diagnostic_foundation",
    );
    expect(snapshot.researchMethod.interpretation.fuzzyLogicIsOptional).toBe(
      true,
    );
    expect(snapshot.warnings.join(" ")).toContain(
      "does not prove scientific validity",
    );
    expect(snapshot.warnings.join(" ")).toContain("practical equivalence");
  });

  it("loads the research method endpoint conservatively", async () => {
    const api = new ReadOnlyPlatformApi("http://127.0.0.1:8080");

    const researchMethod = await api.getResearchMethod();

    expect(researchMethod.readOnly).toBe(true);
    expect(researchMethod.available).toBe(true);
    expect(researchMethod.contractPath).toBe(
      "platform/contracts/research_method_contract.json",
    );
    expect(researchMethod.contractSummary.primaryDynamicFocus).toContain(
      "delay_propagation",
    );
    expect(
      researchMethod.contractSummary.preferredBaselineAlternatives,
    ).toContain("statistical_comparison");
    expect(
      researchMethod.interpretation.doesNotClaimFinalScientificValidity,
    ).toBe(true);
    expect(
      researchMethod.interpretation.practicalEquivalenceMustBeHandled,
    ).toBe(true);
  });

  it("uses only read-only API endpoints", async () => {
    const api = new ReadOnlyPlatformApi("http://127.0.0.1:8080");

    await api.getSnapshot();

    const fetchMock = globalThis.fetch as unknown as {
      mock: {
        calls: Array<[RequestInfo | URL, RequestInit | undefined]>;
      };
    };

    const requestedUrls = fetchMock.mock.calls.map((call) => String(call[0]));
    const forbiddenWriteRoute = ["/api", "v1", "execute"].join("/");

    expect(requestedUrls).toContain("http://127.0.0.1:8080/api/v1/health");
    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/project-status",
    );
    expect(requestedUrls).toContain("http://127.0.0.1:8080/api/v1/reports");
    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/experimental-design-matrix",
    );
    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/research-method",
    );
    expect(
      requestedUrls.some((url) => url.includes(forbiddenWriteRoute)),
    ).toBe(false);
  });

  it("throws when the API returns a non-ok response", async () => {
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

    const api = new ReadOnlyPlatformApi("http://127.0.0.1:8080");

    await expect(api.getHealth()).rejects.toThrow("API request failed");
  });

  it("normalizes missing optional report fields conservatively", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);

        if (url.endsWith("/api/v1/reports")) {
          return Promise.resolve(
            jsonResponse({
              reports: [
                {
                  id: "scientific_validation_plan",
                },
              ],
            }),
          );
        }

        return Promise.resolve(jsonResponse(healthPayload));
      }),
    );

    const api = new ReadOnlyPlatformApi("http://127.0.0.1:8080");

    const reports = await api.getReports();

    expect(reports[0]?.title).toBe("Scientific Validation Plan");
    expect(reports[0]?.available).toBe(true);
    expect(reports[0]?.qualityPassed).toBeNull();
  });
});