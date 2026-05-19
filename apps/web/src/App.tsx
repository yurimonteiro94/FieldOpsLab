import { useState } from "react";

import { Layout } from "./components/Layout";
import type { PageId } from "./domain/platform";
import { ApiSafetyPage } from "./pages/ApiSafetyPage";
import { CampaignDiagnosticsPage } from "./pages/CampaignDiagnosticsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ExperimentalDesignPage } from "./pages/ExperimentalDesignPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ResearchMethodPage } from "./pages/ResearchMethodPage";
import { ScientificValidationPage } from "./pages/ScientificValidationPage";
import { SimulationWorkspacePage } from "./pages/SimulationWorkspacePage";

function renderPage(page: PageId) {
  if (page === "simulation-workspace") {
    return <SimulationWorkspacePage />;
  }

  if (page === "reports") {
    return <ReportsPage />;
  }

  if (page === "campaign-diagnostics") {
    return <CampaignDiagnosticsPage />;
  }

  if (page === "experimental-design") {
    return <ExperimentalDesignPage />;
  }

  if (page === "api-safety") {
    return <ApiSafetyPage />;
  }

  if (page === "scientific-validation") {
    return <ScientificValidationPage />;
  }

  if (page === "research-method") {
    return <ResearchMethodPage />;
  }

  return <DashboardPage />;
}

export default function App() {
  const [activePage, setActivePage] = useState<PageId>("dashboard");

  return (
    <Layout activePage={activePage} onNavigate={setActivePage}>
      {renderPage(activePage)}
    </Layout>
  );
}