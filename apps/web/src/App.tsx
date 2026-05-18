import { useState } from "react";
import { Layout } from "./components/Layout";
import type { PageId } from "./domain/platform";
import { DashboardPage } from "./pages/DashboardPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ScientificValidationPage } from "./pages/ScientificValidationPage";

function renderPage(page: PageId) {
  if (page === "reports") {
    return <ReportsPage />;
  }

  if (page === "scientific-validation") {
    return <ScientificValidationPage />;
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