import { describe, expect, it } from "vitest";
import { createStaticReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";

describe("read-only platform API adapter", () => {
  it("exposes read-only health status", async () => {
    const api = createStaticReadOnlyPlatformApi();

    const health = await api.health();

    expect(health.service).toBe("fieldops_lab_web");
    expect(health.status).toBe("ok");
    expect(health.mode).toBe("read_only_dashboard");
    expect(health.readOnly).toBe(true);
    expect(health.allowsArbitraryCommandExecution).toBe(false);
  });

  it("exposes known report artifacts", async () => {
    const api = createStaticReadOnlyPlatformApi();

    const reports = await api.reports();
    const reportIds = reports.map((report) => report.id);

    expect(reportIds).toContain("project_status");
    expect(reportIds).toContain("scientific_validation_plan");
    expect(reportIds).toContain("experimental_design_matrix");
  });

  it("exposes the current experimental design summary", async () => {
    const api = createStaticReadOnlyPlatformApi();

    const summary = await api.experimentalDesign();

    expect(summary.experimentCount).toBeGreaterThan(0);
    expect(summary.scenarioCount).toBeGreaterThan(0);
    expect(summary.replicationCount).toBeGreaterThan(0);
    expect(summary.reproducibleFromExplicitFactors).toBe(true);
  });

  it("does not claim scientific validity", async () => {
    const api = createStaticReadOnlyPlatformApi();

    const dashboard = await api.dashboard();

    expect(dashboard.status.scientificValidityProven).toBe(false);
    expect(dashboard.status.conservativeNote).toContain(
      "does not prove scientific validity"
    );
  });
});