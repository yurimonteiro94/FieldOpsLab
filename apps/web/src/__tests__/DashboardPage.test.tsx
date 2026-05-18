import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DashboardPage } from "../pages/DashboardPage";
import { createStaticReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";

describe("DashboardPage", () => {
  it("renders the read-only dashboard with conservative scientific wording", async () => {
    render(<DashboardPage api={createStaticReadOnlyPlatformApi()} />);

    expect(
      await screen.findByRole("heading", {
        name: /read-only research platform dashboard/i
      })
    ).toBeInTheDocument();

    expect(screen.getByText(/39% complete/i)).toBeInTheDocument();
    expect(
      screen.getByText(/does not prove scientific validity/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/No execution exposed/i)).toBeInTheDocument();
  });

  it("renders the main report cards", async () => {
    render(<DashboardPage api={createStaticReadOnlyPlatformApi()} />);

    expect(await screen.findByText("Project status report")).toBeInTheDocument();
    expect(screen.getByText("Scientific validation plan")).toBeInTheDocument();
    expect(screen.getByText("Experimental design matrix")).toBeInTheDocument();
  });

  it("renders safety rules for the current platform stage", async () => {
    render(<DashboardPage api={createStaticReadOnlyPlatformApi()} />);

    expect(
      await screen.findByText("The web dashboard is read-only in this stage.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("No arbitrary command execution is exposed.")
    ).toBeInTheDocument();
  });
});