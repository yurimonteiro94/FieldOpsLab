import { StatusCard } from "../components/StatusCard";
import { formatToken } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Experimental design</p>
        <h2>Loading experimental matrix...</h2>
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
      <p className="eyebrow">Experimental design</p>
      <h2>Experimental design unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

function EmptyFactorState() {
  return (
    <article className="warning-card warning">
      <strong>No factor details exposed yet</strong>
      <p>
        The API exposed the experimental design summary, but not a detailed
        factor list. This page can display richer factors when the report grows.
      </p>
    </article>
  );
}

export function ExperimentalDesignPage() {
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

  const design = viewModel.snapshot.experimentalDesign;
  const factorCount =
    design.factorCount > 0 ? design.factorCount : design.factors.length;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Experimental design</p>
          <h2>Experimental design matrix</h2>
          <p className="hero-copy">
            Read-only view of the experimental campaign structure used to plan
            scenario groups, replications, and controlled perturbation tests.
          </p>
        </div>

        <div className="completion-panel">
          <span className="completion-number">
            {design.readOnly ? "RO" : "RW"}
          </span>
          <span className="completion-label">
            API mode for experimental design inspection
          </span>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Design summary</p>
            <h2>Current experiment structure</h2>
          </div>
          <span className="source-pill">
            {design.available ? "available" : "unavailable"}
          </span>
        </div>

        <div className="status-grid">
          <StatusCard
            detail="Total planned experiments exposed by the design matrix summary."
            label="Planned experiments"
            value={String(design.experimentCount)}
          />
          <StatusCard
            detail="Scenario groups currently represented by the experimental design."
            label="Scenario groups"
            value={String(design.scenarioCount)}
          />
          <StatusCard
            detail="Replication count exposed by the current matrix."
            label="Replications"
            value={String(design.replicationCount)}
          />
          <StatusCard
            detail="Whether the matrix can be reproduced from explicit factors."
            label="Reproducibility"
            value={
              design.reproducibleFromExplicitFactors
                ? "explicit factors"
                : "not confirmed"
            }
          />
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Factors</p>
            <h2>Experimental factors exposed by the report</h2>
          </div>
          <span className="source-pill">{factorCount} factors</span>
        </div>

        {design.factors.length === 0 ? (
          <div className="warning-list">
            <EmptyFactorState />
          </div>
        ) : (
          <div className="report-grid">
            {design.factors.map((factor) => (
              <article className="report-card" key={factor.id}>
                <span className="report-category">{factor.id}</span>
                <h3>{factor.label}</h3>
                <p>{factor.description}</p>

                {factor.levels.length > 0 ? (
                  <div className="warning-list">
                    {factor.levels.slice(0, 6).map((level) => (
                      <article className="warning-card" key={level}>
                        <strong>{formatToken(level)}</strong>
                        <p>{level}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p>No explicit levels exposed yet.</p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Methodological boundary</p>
            <h2>What the design matrix means</h2>
          </div>
          <span className="source-pill">{design.report}</span>
        </div>

        <div className="metric-grid">
          <article className="metric-card">
            <span>Dissertation focus</span>
            <strong>Delays</strong>
            <p>
              The platform may support many perturbation types, but the
              dissertation and presentation should keep the scientific focus on
              delays and delay propagation.
            </p>
          </article>

          <article className="metric-card">
            <span>Platform scope</span>
            <strong>Extensible</strong>
            <p>
              New demands, cancellations, priority changes, and other
              perturbations can remain part of the platform architecture.
            </p>
          </article>

          <article className="metric-card">
            <span>Decision claim</span>
            <strong>Not final yet</strong>
            <p>
              This matrix supports controlled experiments, but it does not
              prove the final policy recommendation method by itself.
            </p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Warnings</p>
            <h2>Current limitations and quality notes</h2>
          </div>
          <span className="source-pill">conservative</span>
        </div>

        <div className="warning-list">
          {design.limitations.length === 0 && design.qualityNotes.length === 0 ? (
            <article className="warning-card warning">
              <strong>No detailed notes exposed yet</strong>
              <p>
                The current endpoint exposes the matrix summary. Detailed
                limitations can be added later without breaking this page.
              </p>
            </article>
          ) : null}

          {design.limitations.map((item) => (
            <article className="warning-card warning" key={item}>
              <strong>Limitation</strong>
              <p>{item}</p>
            </article>
          ))}

          {design.qualityNotes.map((item) => (
            <article className="warning-card" key={item}>
              <strong>Quality note</strong>
              <p>{item}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}