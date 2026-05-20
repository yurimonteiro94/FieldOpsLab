import { ReportCard } from "../components/ReportCard";
import { StatusCard } from "../components/StatusCard";
import { formatPercent, formatToken } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";
import { DeploymentReadinessPanel } from "../components/DeploymentReadinessPanel";

function LoadingState() {
  return (
    <section className="section-card">
      <p className="eyebrow">Loading</p>
      <h2>Loading platform data...</h2>
      <p>The dashboard is waiting for the local read-only API.</p>
    </section>
  );
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <section className="section-card error-card">
      <p className="eyebrow">API unavailable</p>
      <h2>Could not load platform data</h2>
      <p>{message}</p>
      <p>
        Start the local API server with{" "}
        <code>py -3 services\api\fieldops_http_server.py --host 127.0.0.1 --port 8080</code>
        .
      </p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

export function DashboardPage() {
  const viewModel = useDashboardViewModel();

  if (viewModel.loading) {
    return <LoadingState />;
  }

  if (viewModel.error || !viewModel.snapshot) {
    return (
      <ErrorState
        message={viewModel.error ?? "Snapshot unavailable."}
        onRetry={viewModel.reload}
      />
    );
  }

  const { snapshot } = viewModel;
  const mainReports = snapshot.reports.slice(0, 3);

  return (
    <>
      <section className="hero-card">
        <div>
          <p className="eyebrow">Dynamic TRSP and WSRP</p>
          <h2>Experimental platform dashboard</h2>
          <p className="hero-copy">
            Read-only view of engineering status, diagnostic evidence, generated
            reports, and pending scientific validation work.
          </p>
        </div>

        <div aria-label="Product completeness" className="completion-panel">
          <span className="completion-number">
            {formatPercent(snapshot.status.productCompleteness)}
          </span>
          <span className="completion-label">overall product completeness</span>
        </div>
      </section>

      <section className="notice-card">
        <strong>Conservative interpretation</strong>
        <p>{snapshot.status.conservativeNote}</p>
      </section>

      <section aria-label="Platform status" className="status-grid">
        <StatusCard
          detail="Current structural checks are passing."
          label="Engineering status"
          value={formatToken(snapshot.status.engineeringStatus)}
        />
        <StatusCard
          detail="Scientific evidence still needs validation."
          label="Scientific status"
          value={formatToken(snapshot.status.scientificStatus)}
        />
        <StatusCard
          detail={`API base URL: ${snapshot.apiBaseUrl}`}
          label="Data source"
          value={snapshot.status.dataSource}
        />
        <StatusCard
          detail="The interface is inspection-only."
          label="Execution"
          value={snapshot.status.executionStatus}
        />
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Metrics</p>
            <h2>Current platform snapshot</h2>
          </div>
          <span className="source-pill">API: {snapshot.apiBaseUrl}</span>
        </div>

        <div className="metric-grid">
          <article className="metric-card">
            <span>Product completeness</span>
            <strong>{formatPercent(snapshot.status.productCompleteness)}</strong>
            <p>Complete application estimate.</p>
          </article>

          <article className="metric-card">
            <span>Planned experiments</span>
            <strong>{snapshot.experimentalDesign.experimentCount}</strong>
            <p>Experiment count exposed by the API.</p>
          </article>

          <article className="metric-card">
            <span>Scenario groups</span>
            <strong>{snapshot.experimentalDesign.scenarioCount}</strong>
            <p>Scenario count exposed by the experimental design matrix.</p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Reports</p>
            <h2>Generated artifacts</h2>
          </div>
        </div>

        <div className="report-grid">
          {mainReports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        
      <DeploymentReadinessPanel />
</div>
      </section>
    </>
  );
}
