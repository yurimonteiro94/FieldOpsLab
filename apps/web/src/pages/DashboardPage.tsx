import { Layout } from "../components/Layout";
import { ReportCard } from "../components/ReportCard";
import { StatusCard } from "../components/StatusCard";
import type { ReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

interface DashboardPageProps {
  api?: ReadOnlyPlatformApi;
}

export function DashboardPage({ api }: DashboardPageProps) {
  const state = useDashboardViewModel(api);

  if (state.kind === "loading") {
    return (
      <Layout>
        <section className="panel">
          <p>Loading FieldOps Lab dashboard...</p>
        </section>
      </Layout>
    );
  }

  if (state.kind === "error") {
    return (
      <Layout>
        <section className="panel panel-danger">
          <h2>Dashboard loading failed</h2>
          <p>{state.message}</p>
        </section>
      </Layout>
    );
  }

  const { snapshot } = state;

  return (
    <Layout>
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Product maturity</p>
          <h2>{snapshot.status.completionPercent}% complete</h2>
          <p>{snapshot.status.conservativeNote}</p>
        </div>

        <div className="hero-metrics">
          <span>{state.reportCount} reports</span>
          <span>{state.passedReportCount} passed checks</span>
          <span>{state.hasScientificProof ? "validated" : "diagnostic only"}</span>
        </div>
      </section>

      <section className="status-grid" aria-label="Current platform status">
        <StatusCard
          title="Engineering"
          value={snapshot.status.engineeringStatus.replace(/_/g, " ")}
          description="The local structural quality gate is passing in the current pipeline."
        />

        <StatusCard
          title="Scientific status"
          value={snapshot.status.scientificStatus.replace(/_/g, " ")}
          description="Current evidence is diagnostic and still requires broader experiments and statistical validation."
        />

        <StatusCard
          title="Experimental design"
          value={`${snapshot.experimentalDesign.experimentCount} planned experiments`}
          description={`${snapshot.experimentalDesign.scenarioCount} scenarios with ${snapshot.experimentalDesign.replicationCount} replications per scenario-policy combination.`}
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Reports</p>
            <h2>Available generated artifacts</h2>
          </div>
          <span className="mode-badge">No execution exposed</span>
        </div>

        <div className="report-grid">
          {snapshot.reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Safety rules</p>
            <h2>Current operating limits</h2>
          </div>
        </div>

        <ul className="safety-list">
          {snapshot.safetyRules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      </section>
    </Layout>
  );
}