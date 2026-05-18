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

    expect(await screen.findByText("Experimental platform dashboard")).not.toBeNull();
    expect(screen.getAllByText("46%")).toHaveLength(2);
    expect(screen.getByText("local http api")).not.toBeNull();
    expect(screen.getByText("Project status")).not.toBeNull();
    expect(screen.getByText("648")).not.toBeNull();
    expect(screen.getByText("disabled")).not.toBeNull();
  });

  it("navigates to report catalog and scientific validation pages", async () => {
    render(<App />);

    expect(await screen.findByText("Experimental platform dashboard")).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Reports" }));

    expect(await screen.findByText("Report catalog")).not.toBeNull();
    expect(screen.getByText("1 reports exposed")).not.toBeNull();

    fireEvent.click(
      screen.getByRole("button", { name: "Scientific validation" }),
    );

    expect(await screen.findByText("Evidence and risk control")).not.toBeNull();
    expect(
      screen.getByText("Generated artifacts are engineering and diagnostic evidence, not final scientific validation."),
    ).not.toBeNull();
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