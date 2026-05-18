import { ReportCard } from "../components/ReportCard";
import { formatPercent } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

export function ReportsPage() {
  const viewModel = useDashboardViewModel();

  if (viewModel.loading) {
    return (
      <section className="section-card">
        <p className="eyebrow">Reports</p>
        <h2>Loading report catalog...</h2>
      </section>
    );
  }

  if (viewModel.error || !viewModel.snapshot) {
    return (
      <section className="section-card error-card">
        <p className="eyebrow">Reports</p>
        <h2>Report catalog unavailable</h2>
        <p>{viewModel.error ?? "Snapshot unavailable."}</p>
        <button className="primary-action" onClick={viewModel.reload} type="button">
          Retry
        </button>
      </section>
    );
  }

  const { snapshot } = viewModel;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Reports</p>
          <h2>Report catalog</h2>
          <p className="hero-copy">
            Generated artifacts currently exposed by the read-only API. This page
            is a UI foundation for future report detail screens.
          </p>
        </div>

        <div className="completion-panel">
          <span className="completion-number">
            {formatPercent(snapshot.status.productCompleteness)}
          </span>
          <span className="completion-label">overall product completeness</span>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Available artifacts</p>
            <h2>{snapshot.reports.length} reports exposed</h2>
          </div>
          <span className="source-pill">read-only</span>
        </div>

        <div className="report-grid">
          {snapshot.reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      </section>
    </>
  );
}