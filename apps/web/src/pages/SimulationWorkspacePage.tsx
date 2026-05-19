import { useEffect, useState } from "react";
import { formatPercent, formatToken } from "../domain/platform";
import type { SimulationStateContractSnapshot } from "../domain/platform";
import { createReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

interface ContractState {
  loading: boolean;
  error: string | null;
  contract: SimulationStateContractSnapshot | null;
}

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
    <section className="notice-card">
      <p className="eyebrow">Simulation workspace</p>
      <h2>Simulation workspace unavailable</h2>
      <p>{message}</p>
      <button className="nav-item" type="button" onClick={onRetry}>
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

function BooleanStatusCard({
  label,
  value,
  safeWhenFalse,
}: {
  label: string;
  value: boolean;
  safeWhenFalse: boolean;
}) {
  const safe = safeWhenFalse ? !value : value;

  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value ? "enabled" : "disabled"}</strong>
      <p>{safe ? "Current state is conservative." : "Requires review before use."}</p>
    </article>
  );
}

function TokenList({
  items,
  fallback,
}: {
  items: string[];
  fallback: string;
}) {
  if (items.length === 0) {
    return <p>{fallback}</p>;
  }

  return <p>{items.map(formatToken).join(", ")}</p>;
}

export function SimulationWorkspacePage() {
  const viewModel = useDashboardViewModel();
  const [contractState, setContractState] = useState<ContractState>({
    loading: true,
    error: null,
    contract: null,
  });

  useEffect(() => {
    let cancelled = false;
    const api = createReadOnlyPlatformApi();

    setContractState({
      loading: true,
      error: null,
      contract: null,
    });

    void api
      .getSimulationStateContract()
      .then((contract) => {
        if (!cancelled) {
          setContractState({
            loading: false,
            error: null,
            contract,
          });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setContractState({
            loading: false,
            error:
              error instanceof Error
                ? error.message
                : "Unknown simulation contract loading error.",
            contract: null,
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (viewModel.loading) {
    return <LoadingState />;
  }

  if (viewModel.error || !viewModel.snapshot) {
    return (
      <ErrorState
        message={viewModel.error ?? "The platform snapshot is unavailable."}
        onRetry={viewModel.reload}
      />
    );
  }

  const { snapshot } = viewModel;
  const contract = contractState.contract;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Simulation workspace</p>
          <h2>Visual operation simulation foundation</h2>
          <p className="hero-copy">
            Planning page for the future real-time map, operational timeline,
            technician movement, task execution, delay injection, and
            re-planning visualization. This page now reads the simulation state
            contract, but it still does not execute solvers or simulations from
            the browser.
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
        <div className="report-grid">
          {contract?.modes.map((mode) => (
            <WorkspaceCard
              key={mode.id}
              title={mode.label}
              label={formatToken(mode.id)}
              description={mode.purpose}
              status={mode.executionEnabled ? "enabled" : "planned only"}
            />
          ))}
          {!contract && (
            <>
              <WorkspaceCard
                title="Optimization mode batch experiments"
                label="optimization mode"
                description="Data in, many runs out. This mode supports exhaustive experiments, policy comparison, metrics, ranking, and statistical analysis."
                status="planned only"
              />
              <WorkspaceCard
                title="Simulation mode visual operation"
                label="simulation mode"
                description="A user-facing map and timeline where technicians, tasks, delays, and operational events can be inspected over simulated time."
                status="planned only"
              />
            </>
          )}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Simulation state contract</p>
            <h2>Read-only contract-backed workspace</h2>
          </div>
          <span className="source-pill">
            {contractState.loading
              ? "loading"
              : contract?.available
                ? "available"
                : "unavailable"}
          </span>
        </div>

        {contractState.loading && <p>Loading simulation state contract...</p>}

        {contractState.error && (
          <p>
            Simulation state contract could not be loaded: {contractState.error}
          </p>
        )}

        {contract && (
          <div className="status-grid">
            <article className="metric-card">
              <span>Contract path</span>
              <strong>{contract.available ? "available" : "missing"}</strong>
              <p>{contract.contractPath}</p>
            </article>
            <article className="metric-card">
              <span>Read-only</span>
              <strong>{contract.readOnly ? "yes" : "no"}</strong>
              <p>Contract inspection does not trigger execution.</p>
            </article>
            <article className="metric-card">
              <span>Future endpoints</span>
              <strong>{contract.futureEndpoints.length}</strong>
              <p>Planned endpoints remain disabled until explicitly gated.</p>
            </article>
          </div>
        )}
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
          {(contract?.mapEntities ?? [
            "technicians",
            "tasks",
            "depots",
            "routes",
            "operational_events",
          ]).map((entity) => (
            <WorkspaceCard
              key={entity}
              title={formatToken(entity)}
              label="map entity"
              description="Entity planned for future visual simulation state rendering."
              status="not implemented yet"
            />
          ))}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Operational timeline</p>
            <h2>Timeline events and delay propagation</h2>
          </div>
          <span className="source-pill">simulation state</span>
        </div>
        <div className="report-grid">
          {(contract?.timelineEvents ?? [
            "planned_start",
            "arrival",
            "service_start",
            "delay",
            "replanning_decision",
          ]).map((event) => (
            <WorkspaceCard
              key={event}
              title={formatToken(event)}
              label="timeline event"
              description="Event type planned for visual inspection during simulated operation."
              status="contract-backed"
            />
          ))}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Scope control</p>
            <h2>Delays first, platform extensible later</h2>
          </div>
          <span className="source-pill">research-aligned</span>
        </div>
        <div className="status-grid">
          <article className="metric-card">
            <span>Dissertation focus</span>
            <strong>primary</strong>
            <TokenList
              items={
                contract?.primaryDissertationScope ??
                snapshot.researchMethod.contractSummary.primaryDynamicFocus
              }
              fallback="delay propagation"
            />
          </article>
          <article className="metric-card">
            <span>Future platform extensions</span>
            <strong>secondary</strong>
            <TokenList
              items={
                contract?.futurePlatformPerturbations ??
                snapshot.researchMethod.contractSummary.secondaryDynamicFocus
              }
              fallback="new requests, cancellations, priority changes"
            />
          </article>
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Re-planning decision</p>
            <h2>Decision fields to preserve cost and stability evidence</h2>
          </div>
          <span className="source-pill">future analysis</span>
        </div>
        <div className="report-grid">
          {(contract?.replanningDecisionFields ?? [
            "policy_id",
            "trigger_reason",
            "computational_cost",
            "route_stability",
            "practical_equivalence_status",
          ]).map((field) => (
            <WorkspaceCard
              key={field}
              title={formatToken(field)}
              label="decision field"
              description="Tracked field for future comparison between re-planning alternatives."
              status="planned"
            />
          ))}
        </div>
      </section>

      {contract && (
        <section className="section-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Execution safety</p>
              <h2>Browser-triggered execution remains disabled</h2>
            </div>
            <span className="source-pill">read-only</span>
          </div>
          <div className="status-grid">
            <BooleanStatusCard
              label="Browser execution"
              value={contract.safetyFlags.browserExecutionEnabled}
              safeWhenFalse
            />
            <BooleanStatusCard
              label="Arbitrary command execution"
              value={contract.safetyFlags.arbitraryCommandExecutionAllowed}
              safeWhenFalse
            />
            <BooleanStatusCard
              label="Write operations"
              value={contract.safetyFlags.writeOperationsSupported}
              safeWhenFalse
            />
            <BooleanStatusCard
              label="Future job API"
              value={contract.safetyFlags.futureJobApiCurrentlyEnabled}
              safeWhenFalse
            />
          </div>
        </section>
      )}

      {contract && contract.futureEndpoints.length > 0 && (
        <section className="section-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Future API gates</p>
              <h2>Planned endpoints are visible but not enabled</h2>
            </div>
            <span className="source-pill">planned only</span>
          </div>
          <div className="report-grid">
            {contract.futureEndpoints.map((endpoint) => (
              <WorkspaceCard
                key={`${endpoint.method}-${endpoint.path}`}
                title={endpoint.path}
                label={endpoint.method}
                description={`Current status: ${formatToken(endpoint.status)}.`}
                status={endpoint.executionEnabled ? "enabled" : "disabled"}
              />
            ))}
          </div>
        </section>
      )}

      <section className="notice-card">
        <p className="eyebrow">Conservative note</p>
        <p>
          {contract?.conservativeNote ??
            "The current web dashboard remains read-only. No browser-triggered optimization or simulation execution is exposed yet."}
        </p>
      </section>
    </>
  );
}