import { ReportCard } from "../components/ReportCard";
import type { PlatformReport } from "../domain/platform";
import { formatPercent, formatToken } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function isCampaignReport(report: PlatformReport): boolean {
  return report.id.includes("campaign") || report.category.startsWith("campaign");
}

function qualityStatus(report: PlatformReport): string {
  if (report.qualityPassed === null) {
    return "quality unknown";
  }

  return report.qualityPassed ? "quality passed" : "quality failed";
}

function findReport(
  reports: PlatformReport[],
  reportId: string,
): PlatformReport | undefined {
  return reports.find((report) => report.id === reportId);
}

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Campaign diagnostics</p>
        <h2>Loading campaign diagnostics...</h2>
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
      <p className="eyebrow">Campaign diagnostics</p>
      <h2>Campaign diagnostics unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

function EvidenceCard({
  label,
  report,
  fallback,
}: {
  label: string;
  report: PlatformReport | undefined;
  fallback: string;
}) {
  if (!report) {
    return (
      <article className="report-card">
        <span className="report-category">missing</span>
        <h3>{label}</h3>
        <p>{fallback}</p>
        <strong>not exposed yet</strong>
      </article>
    );
  }

  return (
    <article className="report-card">
      <span className="report-category">{formatToken(report.category)}</span>
      <h3>{label}</h3>
      <p>{report.description}</p>
      <dl>
        <dt>Report</dt>
        <dd>{report.title}</dd>
        <dt>Artifact</dt>
        <dd>{report.artifactPath}</dd>
        <dt>Status</dt>
        <dd>{qualityStatus(report)}</dd>
      </dl>
      <span className={report.available ? "availability-ok" : "availability-bad"}>
        {report.available ? "available" : "missing"}
      </span>
    </article>
  );
}

export function CampaignDiagnosticsPage() {
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
  const campaignReports = snapshot.reports.filter(isCampaignReport);
  const passedQualityChecks = campaignReports.filter(
    (report) => report.qualityPassed === true,
  ).length;

  const finalDiagnosticReport = findReport(
    campaignReports,
    "campaign_final_diagnostic_report",
  );
  const executionIndexReport = findReport(
    campaignReports,
    "campaign_execution_index",
  );
  const resultSummaryReport = findReport(
    campaignReports,
    "campaign_result_summary",
  );
  const decisionMatrixReport = findReport(
    campaignReports,
    "campaign_decision_matrix",
  );

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Campaign diagnostics</p>
          <h2>Campaign diagnostic workspace</h2>
          <p className="hero-copy">
            Focused view for experiment campaign artifacts. This page prepares
            the bridge between batch experimentation, delay-focused analysis,
            and future simulation evidence without enabling remote execution.
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
            <p className="eyebrow">Campaign overview</p>
            <h2>{campaignReports.length} campaign reports exposed</h2>
          </div>
          <span className="source-pill">read-only</span>
        </div>

        <div className="status-grid">
          <article className="metric-card">
            <span>Campaign reports</span>
            <strong>{campaignReports.length}</strong>
            <p>Artifacts related to campaign planning, execution, and analysis.</p>
          </article>

          <article className="metric-card">
            <span>Quality checks passed</span>
            <strong>{passedQualityChecks}</strong>
            <p>Campaign artifacts with an explicitly passing quality check.</p>
          </article>

          <article className="metric-card">
            <span>Execution status</span>
            <strong>{snapshot.status.executionStatus}</strong>
            <p>Execution remains disabled from the web interface.</p>
          </article>

          <article className="metric-card">
            <span>Research scope</span>
            <strong>delays first</strong>
            <p>
              Dissertation scope remains delay-focused, while the platform stays
              extensible to other perturbations.
            </p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Diagnostic evidence map</p>
            <h2>Key campaign artifacts</h2>
          </div>
          <span className="source-pill">inspection only</span>
        </div>

        <div className="report-grid">
          <EvidenceCard
            fallback="The final diagnostic report is not exposed in the current API catalog."
            label="Final diagnostic evidence"
            report={finalDiagnosticReport}
          />

          <EvidenceCard
            fallback="The execution index is not exposed in the current API catalog."
            label="Execution trace index"
            report={executionIndexReport}
          />

          <EvidenceCard
            fallback="The campaign result summary is not exposed in the current API catalog."
            label="Result summary"
            report={resultSummaryReport}
          />

          <EvidenceCard
            fallback="The campaign decision matrix is not exposed in the current API catalog."
            label="Decision matrix"
            report={decisionMatrixReport}
          />
        </div>
      </section>

      <section className="notice-card">
        <p className="eyebrow">Conservative interpretation</p>
        <h2>Diagnostic evidence, not final scientific validity</h2>
        <p>
          These campaign artifacts help inspect consistency, coverage, ranking
          sensitivity, and analysis readiness. They do not yet prove that a
          re-planning policy is scientifically superior for a real company.
        </p>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Campaign report catalog</p>
            <h2>All campaign-related artifacts</h2>
          </div>
          <span className="source-pill">{campaignReports.length} reports</span>
        </div>

        {campaignReports.length > 0 ? (
          <div className="report-grid">
            {campaignReports.map((report) => (
              <ReportCard key={report.id} report={report} />
            ))}
          </div>
        ) : (
          <div className="notice-card">
            <h2>No campaign reports exposed yet</h2>
            <p>
              Run the reporting pipeline and verify that the read-only API
              catalog exposes campaign artifacts.
            </p>
          </div>
        )}
      </section>
    </>
  );
}