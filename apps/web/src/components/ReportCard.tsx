import type { PlatformReport } from "../domain/platform";
import { formatToken } from "../domain/platform";

interface ReportCardProps {
  report: PlatformReport;
}

export function ReportCard({ report }: ReportCardProps) {
  const qualityText =
    report.qualityPassed === null
      ? "quality status not exposed"
      : report.qualityPassed
        ? "quality check passed"
        : "needs review";

  return (
    <article className="report-card">
      <div>
        <span className="report-category">{formatToken(report.category)}</span>
        <h3>{report.title}</h3>
        <p>{report.description}</p>
      </div>

      <dl>
        <dt>Artifact</dt>
        <dd>{report.artifactPath}</dd>

        {report.qualityPath ? (
          <>
            <dt>Quality check</dt>
            <dd>{report.qualityPath}</dd>
          </>
        ) : null}

        <dt>Status</dt>
        <dd>{qualityText}</dd>
      </dl>

      <span className={report.available ? "availability-ok" : "availability-warning"}>
        {report.available ? "available" : "missing"}
      </span>
    </article>
  );
}