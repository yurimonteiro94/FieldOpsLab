import { useEffect, useMemo, useState } from "react";
import { formatPercent, formatToken } from "../domain/platform";
import type {
  DelayInjectionRequestContractSnapshot,
  SimulationStateContractSnapshot,
  SimulationStateSampleSnapshot,
  SimulationTask,
} from "../domain/platform";
import { createReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";
import { useDashboardViewModel } from "../viewModels/useDashboardViewModel";

interface WorkspaceDataState {
  loading: boolean;
  error: string | null;
  contract: SimulationStateContractSnapshot | null;
  sample: SimulationStateSampleSnapshot | null;
  delayInjectionContract: DelayInjectionRequestContractSnapshot | null;
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
    <section className="hero-card compact">
      <div>
        <p className="eyebrow">Simulation workspace</p>
        <h2>Simulation workspace unavailable</h2>
        <p className="hero-copy">{message}</p>
        <button className="nav-item active" type="button" onClick={onRetry}>
          Retry
        </button>
      </div>
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
    <article className="metric-card">
      <span>{label}</span>
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

function taskById(tasks: SimulationTask[], id: string): SimulationTask | undefined {
  return tasks.find((task) => task.id === id);
}

function OperationMap({ sample }: { sample: SimulationStateSampleSnapshot }) {
  const routeLines = sample.map.routes
    .map((route) => {
      const points = route.taskSequence
        .map((taskId) => taskById(sample.map.tasks, taskId))
        .filter((task): task is SimulationTask => task !== undefined)
        .map((task) => `${task.x},${task.y}`)
        .join(" ");

      return {
        id: route.id,
        points,
      };
    })
    .filter((route) => route.points.length > 0);

  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Read-only visual sample</p>
          <h2>Normalized operation map</h2>
          <p>{sample.map.coordinateSystem}</p>
        </div>
        <span className="source-pill">static sample</span>
      </div>

      <svg
        aria-label="Read-only normalized operation map"
        viewBox="0 0 100 100"
        role="img"
        className="code-preview"
      >
        {routeLines.map((route) => (
          <polyline
            key={route.id}
            points={route.points}
            fill="none"
            stroke="currentColor"
            strokeWidth="0.6"
          />
        ))}

        {sample.map.depots.map((depot) => (
          <g key={depot.id}>
            <rect x={depot.x - 2} y={depot.y - 2} width="4" height="4" />
            <text x={depot.x + 3} y={depot.y} fontSize="3">
              {depot.label}
            </text>
          </g>
        ))}

        {sample.map.tasks.map((task) => (
          <g key={task.id}>
            <circle cx={task.x} cy={task.y} r="1.8" />
            <text x={task.x + 3} y={task.y} fontSize="3">
              {task.label}
            </text>
          </g>
        ))}

        {sample.map.technicians.map((technician) => (
          <g key={technician.id}>
            <circle cx={technician.x} cy={technician.y} r="2.4" />
            <text x={technician.x + 3} y={technician.y + 1} fontSize="3">
              {technician.label}
            </text>
          </g>
        ))}
      </svg>
    </section>
  );
}

function ClockPanel({ sample }: { sample: SimulationStateSampleSnapshot }) {
  const progress =
    sample.clock.endTime > sample.clock.startTime
      ? ((sample.clock.currentTime - sample.clock.startTime) /
          (sample.clock.endTime - sample.clock.startTime)) *
        100
      : 0;

  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Simulation clock</p>
          <h2>{sample.clock.simulationId}</h2>
        </div>
        <span className="source-pill">{sample.clock.status}</span>
      </div>

      <div className="status-grid">
        <WorkspaceCard
          title={`${sample.clock.currentTime} ${sample.clock.timeUnit}`}
          label="Current time"
          description={`Window from ${sample.clock.startTime} to ${sample.clock.endTime}.`}
          status={`${Math.round(progress)}% elapsed`}
        />
        <BooleanStatusCard
          label="User time control"
          value={sample.clock.canUserAdvanceTime}
          safeWhenFalse
        />
        <BooleanStatusCard
          label="User delay injection"
          value={sample.clock.canUserInjectDelay}
          safeWhenFalse
        />
      </div>
    </section>
  );
}

function TechnicianCards({ sample }: { sample: SimulationStateSampleSnapshot }) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Operational entities</p>
          <h2>Technicians and active tasks</h2>
        </div>
        <span className="source-pill">{sample.map.technicians.length} technicians</span>
      </div>

      <div className="status-grid">
        {sample.map.technicians.map((technician) => (
          <article className="metric-card" key={technician.id}>
            <span>{formatToken(technician.status)}</span>
            <h3>{technician.label}</h3>
            <p>Current task: {technician.currentTaskId}</p>
            <p>Route: {technician.routeId}</p>
            <strong>{technician.delayMinutes} delay minutes</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function TaskCards({ sample }: { sample: SimulationStateSampleSnapshot }) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Task state</p>
          <h2>Customers in the visual sample</h2>
        </div>
        <span className="source-pill">{sample.map.tasks.length} tasks</span>
      </div>

      <div className="status-grid">
        {sample.map.tasks.map((task) => (
          <article className="metric-card" key={task.id}>
            <span>{formatToken(task.status)}</span>
            <h3>{task.label}</h3>
            <p>
              Planned: {task.plannedStart} to {task.plannedEnd}
            </p>
            <p>Priority: {formatToken(task.priority)}</p>
            <strong>{task.actualEnd === null ? "not finished" : "finished"}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function TimelinePanel({ sample }: { sample: SimulationStateSampleSnapshot }) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Timeline</p>
          <h2>Delay propagation events</h2>
        </div>
        <span className="source-pill">{sample.timeline.length} events</span>
      </div>

      <div className="report-grid">
        {sample.timeline.map((event) => (
          <article className="report-card" key={`${event.time}-${event.type}`}>
            <span className="report-category">{formatToken(event.type)}</span>
            <h3>{event.label}</h3>
            <p>Time: {event.time}</p>
            <p>Affected: {event.affectedEntityId}</p>
            <strong>{event.delayMinutes} delay minutes</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function ReplanningPanel({ sample }: { sample: SimulationStateSampleSnapshot }) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Re-planning decision</p>
          <h2>{formatToken(sample.replanningDecision.status)}</h2>
        </div>
        <span className="source-pill">
          {formatToken(sample.replanningDecision.primaryDelayType)}
        </span>
      </div>

      <div className="report-grid">
        {sample.replanningDecision.candidatePolicies.map((policy) => (
          <article className="report-card" key={policy.id}>
            <span className="report-category">
              {policy.executionEnabled ? "enabled" : "disabled"}
            </span>
            <h3>{policy.label}</h3>
            <p>{policy.id}</p>
            <strong>
              {policy.executionEnabled ? "execution requires review" : "read-only candidate"}
            </strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function DelayInjectionContractPanel({
  contract,
}: {
  contract: DelayInjectionRequestContractSnapshot;
}) {
  const visibleFields = contract.requestFields.slice(0, 6);

  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Delay injection planning</p>
          <h2>Delay injection request contract</h2>
          <p>{contract.primaryPurpose}</p>
        </div>
        <span className="source-pill">{formatToken(contract.status)}</span>
      </div>

      <div className="status-grid">
        <WorkspaceCard
          title={contract.plannedEndpoint.path}
          label={`${contract.plannedEndpoint.method} endpoint`}
          description={contract.plannedEndpoint.currentBehavior}
          status={
            contract.plannedEndpoint.executionEnabled
              ? "execution requires review"
              : "execution disabled"
          }
        />
        <BooleanStatusCard
          label="Browser delay injection"
          value={contract.browserExecutionEnabled}
          safeWhenFalse
        />
        <BooleanStatusCard
          label="Write operations"
          value={contract.writeOperationsSupported}
          safeWhenFalse
        />
      </div>

      <div className="section-heading">
        <div>
          <p className="eyebrow">Future request shape</p>
          <h2>Fields that a future delay event must carry</h2>
        </div>
        <span className="source-pill">{visibleFields.length} fields shown</span>
      </div>

      <div className="report-grid">
        {visibleFields.map((field) => (
          <article className="report-card" key={field.id}>
            <span className="report-category">
              {field.required ? "required" : "optional"}
            </span>
            <h3>{field.id}</h3>
            <p>{field.description}</p>
            <p>Type: {field.type}</p>
            {field.allowedValues.length > 0 && (
              <strong>{field.allowedValues.map(formatToken).join(", ")}</strong>
            )}
            {field.minimum !== null && <strong>minimum {field.minimum}</strong>}
          </article>
        ))}
      </div>

      <div className="section-heading">
        <div>
          <p className="eyebrow">Validation and safety</p>
          <h2>Visible contract, no runtime mutation</h2>
        </div>
        <span className="source-pill">planned only</span>
      </div>

      <div className="status-grid">
        <WorkspaceCard
          title={contract.plannedEndpoint.status}
          label="Endpoint status"
          description="The endpoint shape is documented so the UI can be designed before execution is enabled."
          status={
            contract.plannedEndpoint.executionEnabled
              ? "execution enabled"
              : "execution disabled"
          }
        />
        <WorkspaceCard
          title={contract.replanningDecisionCurrentStatus}
          label="Re-planning output"
          description="The contract names future decision fields but does not compute a decision here."
          status="not executed"
        />
        <WorkspaceCard
          title={contract.artifactPath}
          label="Contract artifact"
          description={contract.scopePolicy}
          status="read-only"
        />
      </div>

      <div className="notice-card">
        <p className="eyebrow">Conservative note</p>
        <p>{contract.conservativeNote}</p>
      </div>

      {contract.validationRules.length > 0 && (
        <pre className="code-preview">
          {contract.validationRules.slice(0, 5).join("\n")}
        </pre>
      )}
    </section>
  );
}

export function SimulationWorkspacePage() {
  const viewModel = useDashboardViewModel();
  const [workspaceState, setWorkspaceState] = useState<WorkspaceDataState>({
    loading: true,
    error: null,
    contract: null,
    sample: null,
    delayInjectionContract: null,
  });

  useEffect(() => {
    let cancelled = false;
    const api = createReadOnlyPlatformApi();

    setWorkspaceState({
      loading: true,
      error: null,
      contract: null,
      sample: null,
      delayInjectionContract: null,
    });

    void Promise.all([
      api.getSimulationStateContract(),
      api.getSimulationStateSample(),
      api.getDelayInjectionRequestContract(),
    ])
      .then(([contract, sample, delayInjectionContract]) => {
        if (!cancelled) {
          setWorkspaceState({
            loading: false,
            error: null,
            contract,
            sample,
            delayInjectionContract,
          });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setWorkspaceState({
            loading: false,
            error:
              error instanceof Error
                ? error.message
                : "Unknown simulation workspace loading error.",
            contract: null,
            sample: null,
            delayInjectionContract: null,
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const contract = workspaceState.contract;
  const sample = workspaceState.sample;
  const delayInjectionContract = workspaceState.delayInjectionContract;

  const activeSafetyNotes = useMemo(() => sample?.safetyNotes ?? [], [sample]);

  if (viewModel.loading) {
    return <LoadingState />;
  }

  if (viewModel.error || !viewModel.snapshot) {
    return (
      <ErrorState
        message={viewModel.error ?? "Dashboard snapshot is unavailable."}
        onRetry={viewModel.reload}
      />
    );
  }

  const { snapshot } = viewModel;

  return (
    <>
      <section className="hero-card compact">
        <div>
          <p className="eyebrow">Simulation workspace</p>
          <h2>Visual operation simulation foundation</h2>
          <p className="hero-copy">
            Read-only workspace for the future real-time map, operational timeline,
            technician movement, task execution, delay propagation, delay injection,
            and re-planning visualization.
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
          {(contract?.modes ?? []).map((mode) => (
            <WorkspaceCard
              key={mode.id}
              title={mode.label}
              label={mode.id}
              description={mode.purpose}
              status={mode.executionEnabled ? "enabled" : "disabled"}
            />
          ))}
        </div>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Simulation state contract</p>
            <h2>Read-only contract-backed workspace</h2>
          </div>
          <span className="source-pill">
            {workspaceState.loading
              ? "loading"
              : contract?.available && sample?.available
                ? "available"
                : "unavailable"}
          </span>
        </div>

        {workspaceState.loading && <p>Loading simulation state sample...</p>}

        {workspaceState.error && (
          <p>Simulation workspace data could not be loaded: {workspaceState.error}</p>
        )}

        {contract && sample && (
          <div className="status-grid">
            <WorkspaceCard
              title={sample.clock.simulationId}
              label="Sample simulation"
              description={sample.purpose}
              status={sample.executionEnabled ? "execution enabled" : "execution disabled"}
            />
            <WorkspaceCard
              title={contract.contractPath}
              label="Contract path"
              description="The web workspace is driven by the explicit simulation state contract."
              status={contract.readOnly ? "read-only" : "requires review"}
            />
            <WorkspaceCard
              title={sample.artifactPath}
              label="Sample path"
              description="Static state used to validate map, timeline, delay, and re-planning visualization."
              status={sample.readOnly ? "read-only" : "requires review"}
            />
          </div>
        )}
      </section>

      {sample && (
        <>
          <ClockPanel sample={sample} />
          <OperationMap sample={sample} />
          <TechnicianCards sample={sample} />
          <TaskCards sample={sample} />
          <TimelinePanel sample={sample} />
          <ReplanningPanel sample={sample} />
        </>
      )}

      {delayInjectionContract && (
        <DelayInjectionContractPanel contract={delayInjectionContract} />
      )}

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
            <span>primary focus</span>
            <h3>Dissertation focus</h3>
            <TokenList
              items={contract?.primaryDissertationScope ?? []}
              fallback="Delay propagation, travel delay, and service delay remain the primary focus."
            />
          </article>
          <article className="metric-card">
            <span>secondary focus</span>
            <h3>Future platform extensions</h3>
            <TokenList
              items={contract?.futurePlatformPerturbations ?? []}
              fallback="Future perturbation types are not loaded yet."
            />
          </article>
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
              <article className="report-card" key={`${endpoint.method}-${endpoint.path}`}>
                <span className="report-category">{endpoint.method}</span>
                <h3>{endpoint.path}</h3>
                <p>{formatToken(endpoint.status)}</p>
                <strong>
                  {endpoint.executionEnabled ? "enabled" : "execution disabled"}
                </strong>
              </article>
            ))}
          </div>
        </section>
      )}

      {activeSafetyNotes.length > 0 && (
        <section className="notice-card">
          <p className="eyebrow">Safety notes</p>
          <p>{activeSafetyNotes.join(" ")}</p>
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