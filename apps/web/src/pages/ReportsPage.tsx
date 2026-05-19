import { useEffect, useMemo, useState } from "react";

import { ReportCard } from "../components/ReportCard";
import type { PlatformReport, ReportDetail } from "../domain/platform";
import { formatPercent } from "../domain/platform";
import { createReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Reports</p>
        <h2>Loading report catalog...</h2>
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
      <p className="eyebrow">Reports</p>
      <h2>Report catalog unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

function ReportPreview({
  detail,
  loading,
  error,
}: {
  detail: ReportDetail | null;
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Report detail</p>
            <h2>Loading selected report...</h2>
          </div>
          <span className="source-pill">read-only</span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="notice-card error-card">
        <p className="eyebrow">Report detail</p>
        <h2>Selected report unavailable</h2>
        <p>{error}</p>
      </section>
    );
  }

  if (!detail) {
    return (
      <section className="notice-card">
        <p className="eyebrow">Report detail</p>
        <h2>Select a report</h2>
        <p>
          Choose one generated artifact from the catalog to inspect its JSON
          artifact, markdown summary, and quality check metadata.
        </p>
      </section>
    );
  }

  const markdownPreview =
    detail.markdown.text.length > 900
      ? `${detail.markdown.text.slice(0, 900)}...`
      : detail.markdown.text;

  const artifactKeys = detail.artifact.data
    ? Object.keys(detail.artifact.data).slice(0, 8)
    : [];

  const qualityKeys = detail.qualityCheck.data
    ? Object.keys(detail.qualityCheck.data).slice(0, 8)
    : [];

  return (
    <>
      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Report detail</p>
            <h2>{detail.title}</h2>
          </div>
          <span className="source-pill">{detail.category}</span>
        </div>

        <p>{detail.description}</p>

        <div className="status-grid">
          <article className="metric-card">
            <span>Artifact</span>
            <strong>{detail.artifact.exists ? "available" : "missing"}</strong>
            <p>{detail.artifact.path}</p>
          </article>

          <article className="metric-card">
            <span>Markdown</span>
            <strong>{detail.markdown.exists ? "available" : "missing"}</strong>
            <p>{detail.markdown.path}</p>
          </article>

          <article className="metric-card">
            <span>Quality check</span>
            <strong>
              {detail.metadata.qualityPassed === null
                ? "unknown"
                : detail.metadata.qualityPassed
                  ? "passed"
                  : "failed"}
            </strong>
            <p>{detail.qualityCheck.path}</p>
          </article>

          <article className="metric-card">
            <span>Execution</span>
            <strong>
              {detail.executionSupported || detail.writeOperationsSupported
                ? "not safe"
                : "disabled"}
            </strong>
            <p>Report details are inspection-only.</p>
          </article>
        </div>
      </section>

      <section className="notice-card">
        <p className="eyebrow">Conservative note</p>
        <p>{detail.conservativeNote}</p>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Markdown preview</p>
            <h2>Generated report summary</h2>
          </div>
          <span className="source-pill">
            {detail.markdown.loaded ? "loaded" : "not loaded"}
          </span>
        </div>

        <pre className="code-preview">
          {markdownPreview || "No markdown text was exposed for this report."}
        </pre>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">JSON inspection</p>
            <h2>Top-level artifact fields</h2>
          </div>
          <span className="source-pill">read-only</span>
        </div>

        <div className="report-grid">
          <article className="report-card">
            <span className="report-category">artifact</span>
            <h3>{detail.artifact.path}</h3>
            <p>
              {artifactKeys.length > 0
                ? artifactKeys.join(", ")
                : "No top-level keys available."}
            </p>
          </article>

          <article className="report-card">
            <span className="report-category">quality</span>
            <h3>{detail.qualityCheck.path}</h3>
            <p>
              {qualityKeys.length > 0
                ? qualityKeys.join(", ")
                : "No top-level quality keys available."}
            </p>
          </article>
        </div>
      </section>
    </>
  );
}

function ReportSelector({
  reports,
  selectedReportId,
  onSelect,
}: {
  reports: PlatformReport[];
  selectedReportId: string | null;
  onSelect: (reportId: string) => void;
}) {
  return (
    <div className="report-grid">
      {reports.map((report) => (
        <button
          className={`report-card ${
            selectedReportId === report.id ? "selected-report-card" : ""
          }`}
          key={report.id}
          onClick={() => onSelect(report.id)}
          type="button"
        >
          <span className="report-category">{report.category}</span>
          <h3>{report.title}</h3>
          <p>{report.description}</p>
          <p>{report.artifactPath}</p>
          <strong>
            {report.qualityPassed === null
              ? "quality unknown"
              : report.qualityPassed
                ? "quality passed"
                : "quality failed"}
          </strong>
        </button>
      ))}
    </div>
  );
}

export function ReportsPage() {
  const viewModel = useDashboardViewModel();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [reportDetail, setReportDetail] = useState<ReportDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const api = useMemo(() => {
    return createReadOnlyPlatformApi(viewModel.snapshot?.apiBaseUrl);
  }, [viewModel.snapshot?.apiBaseUrl]);

  useEffect(() => {
    if (!viewModel.snapshot || selectedReportId !== null) {
      return;
    }

    const firstAvailableReport = viewModel.snapshot.reports.find(
      (report) => report.available,
    );

    if (firstAvailableReport) {
      setSelectedReportId(firstAvailableReport.id);
    }
  }, [selectedReportId, viewModel.snapshot]);

  useEffect(() => {
    if (!selectedReportId) {
      setReportDetail(null);
      return;
    }

    const reportId = selectedReportId;
    let cancelled = false;

    async function loadReportDetail() {
      setDetailLoading(true);
      setDetailError(null);

      try {
        const detail = await api.getReportDetail(reportId);

        if (!cancelled) {
          setReportDetail(detail);
        }
      } catch (error) {
        if (!cancelled) {
          setReportDetail(null);
          setDetailError(
            error instanceof Error
              ? error.message
              : "Could not load report detail.",
          );
        }
      } finally {
        if (!cancelled) {
          setDetailLoading(false);
        }
      }
    }

    void loadReportDetail();

    return () => {
      cancelled = true;
    };
  }, [api, selectedReportId]);

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

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Reports</p>
          <h2>Report catalog</h2>
          <p className="hero-copy">
            Generated artifacts currently exposed by the read-only API. Select a
            report to inspect its detail endpoint without triggering execution.
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

        <ReportSelector
          onSelect={setSelectedReportId}
          reports={snapshot.reports}
          selectedReportId={selectedReportId}
        />
      </section>

      <ReportPreview
        detail={reportDetail}
        error={detailError}
        loading={detailLoading}
      />

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Catalog cards</p>
            <h2>Compact report overview</h2>
          </div>
          <span className="source-pill">legacy view</span>
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