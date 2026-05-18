import { afterEach, describe, expect, it, vi } from "vitest";
import {
  HttpReadOnlyPlatformApi,
  StaticReadOnlyPlatformApi,
} from "../services/readOnlyPlatformApi";

describe("read-only platform API adapters", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns a conservative static fallback snapshot", async () => {
    const api = new StaticReadOnlyPlatformApi();

    const snapshot = await api.getDashboardSnapshot();

    expect(snapshot.productCompletenessPercent).toBe(46);
    expect(snapshot.dataSource).toBe("static_fallback");
    expect(snapshot.status.readOnly).toBe(true);
    expect(snapshot.status.executionSupported).toBe(false);
    expect(snapshot.status.arbitraryCommandExecutionAllowed).toBe(false);
    expect(snapshot.conservativeNote).toContain("does not prove scientific validity");
  });

  it("loads dashboard data from the local HTTP API", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith("/api/v1/health")) {
        return Response.json({
          read_only: true,
          allows_arbitrary_command_execution: false,
        });
      }

      if (url.endsWith("/api/v1/project-status")) {
        return Response.json({
          summary_metrics: {
            engineering_status: "passed_current_structural_quality_gate",
            structural_all_required_checks_passed: true,
          },
          conservative_note: "This API response does not prove scientific validity.",
        });
      }

      if (url.endsWith("/api/v1/reports")) {
        return Response.json({
          reports: [
            {
              id: "project_status",
              title: "Project status",
              category: "engineering",
              description: "Project status report.",
              path: "analysis/reports/project_status_report.json",
              quality_path: "analysis/reports/project_status_quality_check.json",
              available: true,
            },
          ],
        });
      }

      if (url.endsWith("/api/v1/experimental-design-matrix")) {
        return Response.json({
          summary: {
            experiment_count: 648,
            scenario_count: 108,
            replication_count: 3,
            reproducible_from_explicit_factors: true,
          },
        });
      }

      return new Response("not found", { status: 404 });
    });

    vi.stubGlobal("fetch", fetchMock);

    const api = new HttpReadOnlyPlatformApi("http://127.0.0.1:8080");
    const snapshot = await api.getDashboardSnapshot();

    expect(snapshot.dataSource).toBe("local_http_api");
    expect(snapshot.apiBaseUrl).toBe("http://127.0.0.1:8080");
    expect(snapshot.status.readOnly).toBe(true);
    expect(snapshot.status.executionSupported).toBe(false);
    expect(snapshot.status.arbitraryCommandExecutionAllowed).toBe(false);
    expect(snapshot.metrics.some((item) => item.value === "648")).toBe(true);
    expect(snapshot.reports[0].id).toBe("project_status");
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it("removes trailing slashes from the configured HTTP base URL", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      void url;
      return Response.json({});
    });

    vi.stubGlobal("fetch", fetchMock);

    const api = new HttpReadOnlyPlatformApi("http://127.0.0.1:8080///");
    await api.getDashboardSnapshot();

    const requestedUrls = fetchMock.mock.calls.map((call) => String(call[0]));

    expect(requestedUrls.every((url) => url.startsWith("http://127.0.0.1:8080/api/v1/"))).toBe(true);
  });

  it("rejects failed HTTP responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string) => new Response("server error", { status: 500 })),
    );

    const api = new HttpReadOnlyPlatformApi("http://127.0.0.1:8080");

    await expect(api.getDashboardSnapshot()).rejects.toThrow("API request failed");
  });
});