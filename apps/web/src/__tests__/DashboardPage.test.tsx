import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { DashboardSnapshot, ReadOnlyPlatformApi } from "../domain/platform";
import { DashboardPage } from "../pages/DashboardPage";

function snapshot(): DashboardSnapshot {
  return {
    productCompletenessPercent: 46,
    dataSource: "local_http_api",
    apiBaseUrl: "http://127.0.0.1:8080",
    status: {
      engineeringStatus: "passed_current_structural_quality_gate",
      scientificStatus: "diagnostic_only_with_methodological_warnings",
      structuralChecksPassed: true,
      readOnly: true,
      executionSupported: false,
      arbitraryCommandExecutionAllowed: false,
    },
    metrics: [
      {
        label: "Product completeness",
        value: "46%",
        helperText: "Complete application estimate.",
      },
      {
        label: "Planned experiments",
        value: "648",
        helperText: "Experiment count exposed by the API.",
      },
    ],
    reports: [
      {
        id: "project_status",
        title: "Project status",
        category: "engineering",
        description: "Current structural engineering status.",
        path: "analysis/reports/project_status_report.json",
        qualityPath: "analysis/reports/project_status_quality_check.json",
        available: true,
      },
    ],
    evidenceWarnings: [
      {
        id: "scientific_validity",
        severity: "warning",
        message: "The current platform does not prove scientific validity.",
      },
    ],
    conservativeNote: "This dashboard does not prove scientific validity.",
  };
}

function successfulApi(): ReadOnlyPlatformApi {
  return {
    getDashboardSnapshot: async () => snapshot(),
  };
}

function failingApi(): ReadOnlyPlatformApi {
  return {
    getDashboardSnapshot: async () => {
      throw new Error("API unavailable");
    },
  };
}

describe("DashboardPage", () => {
  it("renders the dashboard with API-backed data", async () => {
    render(<DashboardPage api={successfulApi()} />);

    expect(await screen.findByText("Dynamic TRSP and WSRP experimental platform")).not.toBeNull();
    expect(screen.getAllByText("46%")).toHaveLength(2);
    expect(screen.getByText("local http api")).not.toBeNull();
    expect(screen.getByText("Project status")).not.toBeNull();
    expect(screen.getByText("API: http://127.0.0.1:8080")).not.toBeNull();
  });

  it("keeps execution disabled in the rendered status", async () => {
    render(<DashboardPage api={successfulApi()} />);

    expect(await screen.findByText("Execution")).not.toBeNull();
    expect(screen.getByText("disabled")).not.toBeNull();
  });

  it("shows a conservative error state when the API fails", async () => {
    render(<DashboardPage api={failingApi()} />);

    expect(await screen.findByText("Dashboard unavailable")).not.toBeNull();
    expect(screen.getByText("API unavailable")).not.toBeNull();
    expect(screen.getByRole("button", { name: "Try again" })).not.toBeNull();
  });
});