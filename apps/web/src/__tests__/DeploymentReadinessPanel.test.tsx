import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DeploymentReadinessPanel } from "../components/DeploymentReadinessPanel";

describe("DeploymentReadinessPanel", () => {
  it("shows the current read-only platform readiness without enabling execution", () => {
    render(<DeploymentReadinessPanel />);

    expect(
      screen.getByRole("heading", { name: "Deployment readiness" }),
    ).toBeInTheDocument();

    expect(screen.getByText("Read-only API")).toBeInTheDocument();
    expect(screen.getByText("Browser-triggered execution")).toBeInTheDocument();
    expect(screen.getByText("Cloud Run container scaffold")).toBeInTheDocument();
    expect(screen.getByText("Local container smoke test")).toBeInTheDocument();

    expect(
      screen.getByText(/cannot run solvers, start experiments, mutate schedules/i),
    ).toBeInTheDocument();

    expect(
      screen.getByText("/api/v1/deployment-readiness-contract"),
    ).toBeInTheDocument();
  });

  it("is honest about what remains before production", () => {
    render(<DeploymentReadinessPanel />);

    expect(screen.getByText("Solver-backed execution")).toBeInTheDocument();
    expect(screen.getAllByText("Future work").length).toBeGreaterThanOrEqual(2);

    expect(
      screen.getByText(/real execution layer for controlled solver-backed jobs/i),
    ).toBeInTheDocument();

    expect(
      screen.getByText(/authentication and visibility decisions/i),
    ).toBeInTheDocument();

    expect(
      screen.getByText(/monitoring, cost controls, rollback procedures/i),
    ).toBeInTheDocument();
  });
});
