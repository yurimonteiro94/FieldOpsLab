import type { ReadOnlyPlatformApi } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

interface DashboardPageProps {
  api?: ReadOnlyPlatformApi;
}

function formatStatus(value: string): string {
  return value.split("_").join(" ");
}

export function DashboardPage({ api }: DashboardPageProps) {
  const { loading, errorMessage, snapshot, reload } = useDashboardViewModel(api);

  if (loading) {
    return (
      <main className="page-shell">
        <section className="hero-card">
          <p className="eyebrow">FieldOps Lab</p>
          <h1>Loading platform dashboard</h1>
          <p className="muted">Reading the current platform status.</p>
        </section>
      </main>
    );
  }

  if (errorMessage !== null || snapshot === null) {
    return (
      <main className="page-shell">
        <section className="hero-card">
          <p className="eyebrow">FieldOps Lab</p>
          <h1>Dashboard unavailable</h1>
          <p className="danger-text">{errorMessage ?? "The dashboard could not load platform data."}</p>
          <button className="primary-button" type="button" onClick={reload}>
            Try again
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">FieldOps Lab</p>
          <h1>Dynamic TRSP and WSRP experimental platform</h1>
          <p className="hero-copy">
            Read-only dashboard for inspecting engineering status, diagnostic evidence, generated reports,
            and pending scientific validation work.
          </p>
        </div>

        <div className="completion-panel" aria-label="Product completeness">
          <span className="completion-number">{snapshot.productCompletenessPercent}%</span>
          <span className="completion-label">overall product completeness</span>
        </div>
      </section>

      <section className="notice-card">
        <strong>Conservative interpretation</strong>
        <p>{snapshot.conservativeNote}</p>
      </section>

      <section className="status-grid" aria-label="Platform status">
        <article className="status-card">
          <span className="status-label">Engineering status</span>
          <strong>{formatStatus(snapshot.status.engineeringStatus)}</strong>
        </article>

        <article className="status-card">
          <span className="status-label">Scientific status</span>
          <strong>{formatStatus(snapshot.status.scientificStatus)}</strong>
        </article>

        <article className="status-card">
          <span className="status-label">Data source</span>
          <strong>{formatStatus(snapshot.dataSource)}</strong>
        </article>

        <article className="status-card">
          <span className="status-label">Execution</span>
          <strong>{snapshot.status.executionSupported ? "enabled" : "disabled"}</strong>
        </article>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Metrics</p>
            <h2>Current platform snapshot</h2>
          </div>
          {snapshot.apiBaseUrl !== undefined ? (
            <span className="source-pill">API: {snapshot.apiBaseUrl}</span>
          ) : (
            <span className="source-pill">Static fallback</span>
          )}
        </div>

        <div className="metric-grid">
          {snapshot.metrics.map((item) => (
            <article className="metric-card" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.helperText}</p>
            </article>
          ))}
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
          {snapshot.reports.map((report) => (
            <article className="report-card" key={report.id}>
              <div>
                <span className="report-category">{formatStatus(report.category)}</span>
                <h3>{report.title}</h3>
                <p>{report.description}</p>
              </div>

              <dl>
                <dt>Artifact</dt>
                <dd>{report.path}</dd>
                {report.qualityPath !== undefined ? (
                  <>
                    <dt>Quality check</dt>
                    <dd>{report.qualityPath}</dd>
                  </>
                ) : null}
              </dl>

              <span className={report.available ? "availability-ok" : "availability-missing"}>
                {report.available ? "available" : "missing"}
              </span>
            </article>
          ))}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Risk control</p>
            <h2>Evidence warnings</h2>
          </div>
        </div>

        <div className="warning-list">
          {snapshot.evidenceWarnings.map((warning) => (
            <article className={`warning-card ${warning.severity}`} key={warning.id}>
              <strong>{warning.severity}</strong>
              <p>{warning.message}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}