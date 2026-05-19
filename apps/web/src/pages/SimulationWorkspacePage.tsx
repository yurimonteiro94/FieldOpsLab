import { formatPercent, formatToken } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Simulation workspace</p>
        <h2>Loading simulation workspace...</h2>
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
      <p className="eyebrow">Simulation workspace</p>
      <h2>Simulation workspace unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

function WorkspaceCard({
  title,
  label,
  description,
  status,
}: {
  title: string;
  label: string;
  description: string;
  status: string;
}) {
  return (
    <article className="report-card">
      <span className="report-category">{label}</span>
      <h3>{title}</h3>
      <p>{description}</p>
      <strong>{status}</strong>
    </article>
  );
}

export function SimulationWorkspacePage() {
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
  const primaryFocus = snapshot.researchMethod.contractSummary.primaryDynamicFocus;
  const secondaryFocus =
    snapshot.researchMethod.contractSummary.secondaryDynamicFocus;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Simulation workspace</p>
          <h2>Visual operation simulation foundation</h2>
          <p className="hero-copy">
            Planning page for the future real-time map, operational timeline,
            technician movement, task execution, delay injection, and
            re-planning visualization. This is still read-only and does not
            execute solvers or simulations from the browser.
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
            <p className="eyebrow">Target operating modes</p>
            <h2>Optimization mode and simulation mode</h2>
          </div>
          <span className="source-pill">future execution</span>
        </div>

        <div className="status-grid">
          <article className="metric-card">
            <span>Optimization mode</span>
            <strong>batch experiments</strong>
            <p>
              Data in, many runs out. This mode supports exhaustive experiments,
              policy comparison, metrics, ranking, and statistical analysis.
            </p>
          </article>

          <article className="metric-card">
            <span>Simulation mode</span>
            <strong>visual operation</strong>
            <p>
              A user-facing map and timeline where technicians, tasks, delays,
              and operational events can be inspected over simulated time.
            </p>
          </article>

          <article className="metric-card">
            <span>User interaction</span>
            <strong>delay injection</strong>
            <p>
              Future users should be able to add delays during execution and
              inspect how the policy reacts to disruption propagation.
            </p>
          </article>

          <article className="metric-card">
            <span>Execution boundary</span>
            <strong>{snapshot.status.executionStatus}</strong>
            <p>
              The current web dashboard remains read-only. No browser-triggered
              optimization or simulation execution is exposed yet.
            </p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Simulation surface</p>
            <h2>Future real-time map components</h2>
          </div>
          <span className="source-pill">design contract</span>
        </div>

        <div className="report-grid">
          <WorkspaceCard
            description="Shows customer locations, depot, technicians, current routes, and operation state. This will likely be the main visual layer in simulation mode."
            label="map"
            status="planned"
            title="Real-time operation map"
          />

          <WorkspaceCard
            description="Controls simulated time, replay speed, current event, pending tasks, service start, service finish, and delay propagation."
            label="timeline"
            status="planned"
            title="Operational timeline"
          />

          <WorkspaceCard
            description="Represents technician position, assigned tasks, route progress, current delay, and whether a re-planning trigger has fired."
            label="technicians"
            status="planned"
            title="Technician state cards"
          />

          <WorkspaceCard
            description="Allows controlled user-side insertion of travel delays, service delays, future cancellations, new requests, and priority changes."
            label="events"
            status="delays first"
            title="Perturbation injection panel"
          />
        </div>
      </section>

      <section className="notice-card">
        <p className="eyebrow">Scope control</p>
        <h2>Delays first, platform extensible later</h2>
        <p>
          The dissertation scope should stay focused on delays and delay
          propagation. The platform architecture can still prepare extension
          points for new requests, cancellations, priority changes, and other
          operational disruptions.
        </p>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Dynamic focus</p>
            <h2>Research-aligned perturbation classes</h2>
          </div>
          <span className="source-pill">from research method</span>
        </div>

        <div className="report-grid">
          <article className="report-card">
            <span className="report-category">primary focus</span>
            <h3>Dissertation focus</h3>
            <p>
              {primaryFocus.length > 0
                ? primaryFocus.map(formatToken).join(", ")
                : "delay propagation"}
            </p>
            <strong>narrow and defensible</strong>
          </article>

          <article className="report-card">
            <span className="report-category">secondary focus</span>
            <h3>Future platform extensions</h3>
            <p>
              {secondaryFocus.length > 0
                ? secondaryFocus.map(formatToken).join(", ")
                : "new requests, cancellations, priority changes"}
            </p>
            <strong>extensible architecture</strong>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Implementation roadmap</p>
            <h2>Simulation workspace milestones</h2>
          </div>
          <span className="source-pill">not implemented yet</span>
        </div>

        <div className="report-grid">
          <WorkspaceCard
            description="Define JSON contracts for simulation state, technicians, tasks, events, route segments, and current clock."
            label="contract"
            status="next foundation"
            title="Simulation state schema"
          />

          <WorkspaceCard
            description="Expose a read-only simulation snapshot endpoint before allowing any controlled execution endpoint."
            label="api"
            status="read-only first"
            title="Simulation snapshot API"
          />

          <WorkspaceCard
            description="Render fake/static operation state first, then connect it to backend-generated snapshots."
            label="frontend"
            status="safe prototype"
            title="Visual simulation page"
          />

          <WorkspaceCard
            description="Only after contracts and tests are stable, add controlled execution through queued jobs, never arbitrary subprocess calls."
            label="execution"
            status="future gated step"
            title="Controlled simulation runner"
          />
        </div>
      </section>
    </>
  );
}