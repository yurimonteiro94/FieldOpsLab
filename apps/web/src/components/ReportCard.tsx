import type { ReportArtifact } from "../domain/platform";

interface ReportCardProps {
  report: ReportArtifact;
}

export function ReportCard({ report }: ReportCardProps) {
  const qualityText = report.passed ? "quality check passed" : "needs review";

  return (
    <article className="report-card">
      <div>
        <p className="card-title">{report.category.replace(/_/g, " ")}</p>
        <h3>{report.title}</h3>
      </div>

      <dl>
        <div>
          <dt>Artifact</dt>
          <dd>{report.path}</dd>
        </div>

        {report.qualityCheckPath ? (
          <div>
            <dt>Quality check</dt>
            <dd>{report.qualityCheckPath}</dd>
          </div>
        ) : null}

        <div>
          <dt>Status</dt>
          <dd>{qualityText}</dd>
        </div>
      </dl>
    </article>
  );
}