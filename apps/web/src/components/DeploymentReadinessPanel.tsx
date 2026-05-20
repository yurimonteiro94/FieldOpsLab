export type DeploymentReadinessStatus = "ready" | "blocked" | "future";

type DeploymentReadinessItem = {
  title: string;
  status: string;
  kind: DeploymentReadinessStatus;
  description: string;
};

const readinessItems: DeploymentReadinessItem[] = [
  {
    title: "Read-only API",
    status: "Ready",
    kind: "ready",
    description:
      "Inspection endpoints are available for contracts, reports, samples, project status, and deployment readiness.",
  },
  {
    title: "Browser-triggered execution",
    status: "Blocked",
    kind: "blocked",
    description:
      "The browser still cannot run solvers, start experiments, mutate schedules, write files, or trigger backend jobs.",
  },
  {
    title: "Cloud Run container scaffold",
    status: "Prepared",
    kind: "ready",
    description:
      "The read-only API has a container scaffold intended for a future Cloud Run service.",
  },
  {
    title: "Local container smoke test",
    status: "Prepared",
    kind: "ready",
    description:
      "The local smoke test validates health, endpoint catalog quality, read-only flags, 404 behavior, and 405 behavior.",
  },
  {
    title: "Solver-backed execution",
    status: "Future work",
    kind: "future",
    description:
      "The real execution layer, OR-Tools-backed solver integration, experiment orchestration, and storage are not production-ready yet.",
  },
  {
    title: "Production deployment",
    status: "Future work",
    kind: "future",
    description:
      "A real Cloud Run deployment still needs project, billing, region, registry, visibility, monitoring, rollback, and smoke-test decisions.",
  },
];

const currentProofPoints = [
  "The platform exposes read-only API contracts and reports.",
  "The dashboard can communicate current platform readiness without enabling execution.",
  "The current web layer remains safe for demonstration because execution is explicitly disabled.",
];

const remainingProductionWork = [
  "Real execution layer for controlled solver-backed jobs.",
  "Experiment orchestration and persistent storage.",
  "Frontend API URL wiring for hosted environments.",
  "Authentication and visibility decisions.",
  "Monitoring, cost controls, rollback procedures, and post-deploy smoke tests.",
];

function statusClassName(kind: DeploymentReadinessStatus): string {
  return `deployment-readiness-panel__status deployment-readiness-panel__status--${kind}`;
}

export function DeploymentReadinessPanel() {
  return (
    <section
      aria-labelledby="deployment-readiness-title"
      className="deployment-readiness-panel"
    >
      <div className="deployment-readiness-panel__header">
        <p className="deployment-readiness-panel__eyebrow">
          Platform readiness
        </p>
        <h2 id="deployment-readiness-title">Deployment readiness</h2>
        <p>
          Current status of the FieldOps Lab hosting and execution boundary. This
          panel is intentionally honest: the API is ready for read-only
          inspection, but real optimization execution is still future work.
        </p>
      </div>

      <div className="deployment-readiness-panel__grid" role="list">
        {readinessItems.map((item) => (
          <article
            className="deployment-readiness-panel__card"
            key={item.title}
            role="listitem"
          >
            <div className="deployment-readiness-panel__card-header">
              <h3>{item.title}</h3>
              <span className={statusClassName(item.kind)}>{item.status}</span>
            </div>
            <p>{item.description}</p>
          </article>
        ))}
      </div>

      <div className="deployment-readiness-panel__details">
        <div>
          <h3>What this proves now</h3>
          <ul>
            {currentProofPoints.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3>What remains before production</h3>
          <ul>
            {remainingProductionWork.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <p className="deployment-readiness-panel__contract">
        Contract source: <code>/api/v1/deployment-readiness-contract</code>
      </p>
    </section>
  );
}

export default DeploymentReadinessPanel;
