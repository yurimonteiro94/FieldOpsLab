import { StatusCard } from "../components/StatusCard";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">API safety</p>
        <h2>Loading API contract...</h2>
        <p className="hero-copy">
          The dashboard is waiting for the local read-only API.
        </p>
      </div>
    </section>
  );
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <section className="notice-card error-card">
      <p className="eyebrow">API safety</p>
      <h2>API safety unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

export function ApiSafetyPage() {
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

  const { health, apiBaseUrl } = viewModel.snapshot;
  const writeRoutes = health.routes.filter((route) => route.method !== "GET");

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">API safety</p>
          <h2>Read-only API boundary</h2>
          <p className="hero-copy">
            This page exposes the current HTTP API boundary used by the web
            dashboard. It is a safety inspection page, not an execution panel.
          </p>
        </div>

        <div className="completion-panel">
          <span className="completion-number">
            {health.readOnly ? "RO" : "RW"}
          </span>
          <span className="completion-label">current API mode</span>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Safety guarantees</p>
            <h2>Execution is intentionally unavailable</h2>
          </div>
          <span className="source-pill">{health.mode}</span>
        </div>

        <div className="status-grid">
          <StatusCard
            detail="The web dashboard must not expose backend execution while the project is still a local read-only platform."
            label="Read-only mode"
            value={health.readOnly ? "enabled" : "disabled"}
          />
          <StatusCard
            detail="No arbitrary subprocess or command execution should be reachable from this dashboard."
            label="Arbitrary command execution"
            value={
              health.allowsArbitraryCommandExecution ? "allowed" : "blocked"
            }
          />
          <StatusCard
            detail="The current local API base URL used by the frontend."
            label="API base URL"
            value={apiBaseUrl}
          />
          <StatusCard
            detail="Routes advertised by the health endpoint."
            label="Advertised routes"
            value={String(health.routes.length)}
          />
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Route catalog</p>
            <h2>Routes exposed to the dashboard</h2>
          </div>
          <span className="source-pill">
            {writeRoutes.length === 0 ? "GET-only" : "write routes detected"}
          </span>
        </div>

        <div className="report-grid">
          {health.routes.map((route) => (
            <article className="report-card" key={`${route.method}-${route.path}`}>
              <span className="report-category">{route.method}</span>
              <h3>{route.path}</h3>
              <p>{route.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Risk control</p>
            <h2>What must stay true before execution features exist</h2>
          </div>
          <span className="source-pill">conservative</span>
        </div>

        <div className="warning-list">
          <article className="warning-card warning">
            <strong>No POST execution panel</strong>
            <p>
              The frontend must not expose a button or form that launches
              experiments, solvers, scripts, or arbitrary commands.
            </p>
          </article>

          <article className="warning-card warning">
            <strong>No hidden write route dependency</strong>
            <p>
              All current frontend data should come from explicit read-only GET
              endpoints.
            </p>
          </article>

          <article className="warning-card warning">
            <strong>Future execution requires a separate design</strong>
            <p>
              Controlled execution should be designed later with job contracts,
              validation, authentication, logs, and safe rollback assumptions.
            </p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Contract traceability</p>
            <h2>Platform contract source</h2>
          </div>
          <span className="source-pill">
            {health.contractAvailable ? "available" : "missing"}
          </span>
        </div>

        <div className="metric-grid">
          <article className="metric-card">
            <span>Contract path</span>
            <strong>{health.contractPath}</strong>
            <p>
              Contract advertised by the API health endpoint and inspected by
              the dashboard.
            </p>
          </article>

          <article className="metric-card">
            <span>Service</span>
            <strong>{health.service}</strong>
            <p>Local HTTP service used as the read-only dashboard adapter.</p>
          </article>

          <article className="metric-card">
            <span>Status</span>
            <strong>{health.status}</strong>
            <p>Health status returned by the local API server.</p>
          </article>
        </div>
      </section>
    </>
  );
}