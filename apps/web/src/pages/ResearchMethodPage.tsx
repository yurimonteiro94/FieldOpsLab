import { StatusCard } from "../components/StatusCard";
import { formatToken } from "../domain/platform";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

function LoadingState() {
  return (
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Research method</p>
        <h2>Loading research framing...</h2>
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
      <p className="eyebrow">Research method</p>
      <h2>Research method unavailable</h2>
      <p>{message}</p>
      <button className="primary-action" onClick={onRetry} type="button">
        Retry
      </button>
    </section>
  );
}

function LimitedList({
  items,
  emptyText,
  limit = 6,
}: {
  items: string[];
  emptyText: string;
  limit?: number;
}) {
  const visibleItems = items.slice(0, limit);

  if (visibleItems.length === 0) {
    return <p>{emptyText}</p>;
  }

  return (
    <div className="warning-list">
      {visibleItems.map((item) => (
        <article className="warning-card" key={item}>
          <strong>{formatToken(item)}</strong>
          <p>{item}</p>
        </article>
      ))}
    </div>
  );
}

export function ResearchMethodPage() {
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

  const { researchMethod } = viewModel.snapshot;
  const { contractSummary, interpretation } = researchMethod;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Research method</p>
          <h2>Decision method framing</h2>
          <p className="hero-copy">{contractSummary.projectQuestion}</p>
        </div>

        <div className="completion-panel">
          <span className="completion-number">
            {researchMethod.readOnly ? "RO" : "RW"}
          </span>
          <span className="completion-label">
            API mode for research method inspection
          </span>
        </div>
      </section>

      <section className="notice-card">
        <p className="eyebrow">Research gap</p>
        <p>{contractSummary.researchGap}</p>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Scientific posture</p>
            <h2>Conservative interpretation</h2>
          </div>
          <span className="source-pill">{contractSummary.status}</span>
        </div>

        <div className="status-grid">
          <StatusCard
            detail="Current maturity level exposed by the research method contract."
            label="Scientific maturity"
            value={formatToken(contractSummary.scientificMaturity)}
          />
          <StatusCard
            detail="The system supports the experiments. It is not the final contribution by itself."
            label="Decision framework"
            value={
              contractSummary.claimsPolicyDecisionFramework
                ? "claimed as target"
                : "not claimed"
            }
          />
          <StatusCard
            detail="Fuzzy logic is allowed only if it becomes defensible."
            label="Fuzzy logic"
            value={
              interpretation.fuzzyLogicIsOptional ? "optional" : "required"
            }
          />
          <StatusCard
            detail="Small average differences must not be overclaimed."
            label="Practical equivalence"
            value={
              interpretation.practicalEquivalenceMustBeHandled
                ? "required"
                : "not confirmed"
            }
          />
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Dynamic focus</p>
            <h2>Dissertation focus and platform extensions</h2>
          </div>
          <span className="source-pill">delay-first</span>
        </div>

        <div className="report-grid">
          <article className="report-card">
            <span className="report-category">Primary focus</span>
            <h3>Delay propagation</h3>
            <p>
              The dissertation and presentation should focus on delays,
              especially delay propagation, travel delay, and service delay.
            </p>
            <LimitedList
              emptyText="No primary focus items were exposed by the contract."
              items={contractSummary.primaryDynamicFocus}
              limit={4}
            />
          </article>

          <article className="report-card">
            <span className="report-category">Platform extension</span>
            <h3>Other perturbations</h3>
            <p>
              The platform can remain extensible beyond the dissertation scope.
            </p>
            <LimitedList
              emptyText="No secondary focus items were exposed by the contract."
              items={contractSummary.secondaryDynamicFocus}
              limit={4}
            />
          </article>

          <article className="report-card">
            <span className="report-category">Decision alternatives</span>
            <h3>Defensible baselines</h3>
            <p>
              Standard statistical comparison and simpler decision rules should
              remain valid alternatives before adding fuzzy logic.
            </p>
            <LimitedList
              emptyText="No baseline alternatives were exposed by the contract."
              items={contractSummary.preferredBaselineAlternatives}
              limit={5}
            />
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Evidence boundary</p>
            <h2>What the page must not overclaim</h2>
          </div>
          <span className="source-pill">
            {researchMethod.available ? "available" : "contract missing"}
          </span>
        </div>

        <div className="warning-list">
          <article className="warning-card warning">
            <strong>Scientific validity</strong>
            <p>
              Passing engineering tests does not prove the final scientific
              contribution.
            </p>
          </article>

          <article className="warning-card warning">
            <strong>Company data</strong>
            <p>
              Real company data still requires validation, access control, and
              careful interpretation before decision support.
            </p>
          </article>

          <article className="warning-card warning">
            <strong>Execution safety</strong>
            <p>
              The web dashboard remains read-only and does not expose backend
              execution.
            </p>
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Traceability</p>
            <h2>Source artifacts</h2>
          </div>
          <span className="source-pill">read-only</span>
        </div>

        <div className="metric-grid">
          <article className="metric-card">
            <span>Contract</span>
            <strong>{researchMethod.contractPath}</strong>
            <p>Research method contract consumed through the local API.</p>
          </article>

          <article className="metric-card">
            <span>Framing</span>
            <strong>{researchMethod.framingPath}</strong>
            <p>Markdown framing used to explain the research logic.</p>
          </article>

          <article className="metric-card">
            <span>Completed foundation</span>
            <strong>{contractSummary.completedFoundation.length}</strong>
            <p>Completed items exposed by the current contract.</p>
          </article>
        </div>
      </section>
    </>
  );
}