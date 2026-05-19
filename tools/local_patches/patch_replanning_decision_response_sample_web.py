from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE_PATH = ROOT / "apps" / "web" / "src" / "pages" / "SimulationWorkspacePage.tsx"
TEST_PATH = ROOT / "apps" / "web" / "src" / "__tests__" / "SimulationWorkspacePage.test.tsx"


def patch_page() -> None:
    source = PAGE_PATH.read_text(encoding="utf-8")

    if "interface ReplanningDecisionResponseSampleView" not in source:
        marker = "interface WorkspaceDataState {"
        insert = '''interface ReplanningDecisionResponseSampleView {
  sampleId: string;
  decisionStatus: string;
  recommendation: string;
  reason: string;
  injectedDelayMinutes: number;
  baselinePropagatedDelayMinutes: number;
  candidatePropagatedDelayMinutes: number;
  recoveredDelayMinutes: number;
  dominantBenefit: string;
  dominantRisk: string;
  statisticalClaimReady: boolean;
  decisionRuleReady: boolean;
  conservativeNote: string;
  safetyNote: string;
}

function asViewRecord(value: unknown): Record<string, unknown> {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }

  return {};
}

function readViewString(
  record: Record<string, unknown>,
  key: string,
  fallback: string,
): string {
  const value = record[key];

  if (typeof value === "string" && value.trim().length > 0) {
    return value;
  }

  return fallback;
}

function readViewNumber(
  record: Record<string, unknown>,
  key: string,
  fallback: number,
): number {
  const value = record[key];

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  return fallback;
}

function readViewBoolean(
  record: Record<string, unknown>,
  key: string,
  fallback: boolean,
): boolean {
  const value = record[key];

  if (typeof value === "boolean") {
    return value;
  }

  return fallback;
}

async function loadReplanningDecisionResponseSample(): Promise<ReplanningDecisionResponseSampleView> {
  const baseUrl =
    import.meta.env.VITE_FIELDOPS_API_BASE_URL ?? "http://127.0.0.1:8080";

  const response = await fetch(
    `${baseUrl}/api/v1/replanning-decision-response-sample`,
  );

  if (!response.ok) {
    throw new Error(
      `Could not load re-planning decision response sample. HTTP ${response.status}`,
    );
  }

  const endpointPayload = asViewRecord(await response.json());
  const sample = asViewRecord(
    endpointPayload.replanning_decision_response_sample,
  );
  const decisionSummary = asViewRecord(sample.decision_summary);
  const delayPropagation = asViewRecord(sample.delay_propagation);
  const tradeoffSummary = asViewRecord(sample.tradeoff_summary);

  return {
    sampleId: readViewString(
      sample,
      "sample_id",
      readViewString(endpointPayload, "sample_id", "unknown_sample"),
    ),
    decisionStatus: readViewString(
      decisionSummary,
      "decision_status",
      "not_executed_by_this_sample",
    ),
    recommendation: readViewString(
      decisionSummary,
      "recommendation",
      "manual_review_required",
    ),
    reason: readViewString(
      decisionSummary,
      "reason",
      "Sample is read-only and does not execute re-planning.",
    ),
    injectedDelayMinutes: readViewNumber(
      delayPropagation,
      "injected_delay_minutes",
      0,
    ),
    baselinePropagatedDelayMinutes: readViewNumber(
      delayPropagation,
      "propagated_delay_minutes_baseline",
      0,
    ),
    candidatePropagatedDelayMinutes: readViewNumber(
      delayPropagation,
      "propagated_delay_minutes_candidate",
      0,
    ),
    recoveredDelayMinutes: readViewNumber(
      delayPropagation,
      "recovered_delay_minutes",
      0,
    ),
    dominantBenefit: readViewString(
      tradeoffSummary,
      "dominant_benefit",
      "not_available",
    ),
    dominantRisk: readViewString(
      tradeoffSummary,
      "dominant_risk",
      "not_available",
    ),
    statisticalClaimReady: readViewBoolean(
      tradeoffSummary,
      "statistical_claim_ready",
      false,
    ),
    decisionRuleReady: readViewBoolean(
      tradeoffSummary,
      "decision_rule_ready",
      false,
    ),
    conservativeNote: readViewString(
      sample,
      "conservative_note",
      "This sample is read-only and does not execute operational decisions.",
    ),
    safetyNote: readViewString(
      endpointPayload,
      "safety_note",
      "This endpoint is read-only and does not trigger backend jobs.",
    ),
  };
}

'''
        if marker not in source:
            raise SystemExit("Could not find WorkspaceDataState marker.")
        source = source.replace(marker, insert + marker, 1)

    if "replanningDecisionResponseSample:" not in source:
        source = source.replace(
            "  replanningDecisionResponseContract: ReplanningDecisionResponseContractSnapshot | null;\n",
            "  replanningDecisionResponseContract: ReplanningDecisionResponseContractSnapshot | null;\n"
            "  replanningDecisionResponseSample: ReplanningDecisionResponseSampleView | null;\n",
            1,
        )

    source = re.sub(
        r"(\s+replanningDecisionResponseContract: null,\n)(?!\s+replanningDecisionResponseSample:)",
        r"\1      replanningDecisionResponseSample: null,\n",
        source,
    )

    if "api.getReplanningDecisionResponseContract(),\n      loadReplanningDecisionResponseSample()," not in source:
        source = source.replace(
            "      api.getReplanningDecisionResponseContract(),\n",
            "      api.getReplanningDecisionResponseContract(),\n"
            "      loadReplanningDecisionResponseSample(),\n",
            1,
        )

    source = source.replace(
        ".then(([contract, sample, delayInjectionContract, replanningDecisionResponseContract]) => {",
        ".then(([\n"
        "        contract,\n"
        "        sample,\n"
        "        delayInjectionContract,\n"
        "        replanningDecisionResponseContract,\n"
        "        replanningDecisionResponseSample,\n"
        "      ]) => {",
        1,
    )

    source = re.sub(
        r"(\s+replanningDecisionResponseContract,\n)(?!\s+replanningDecisionResponseSample,)",
        r"\1          replanningDecisionResponseSample,\n",
        source,
        count=1,
    )

    if (
        "const replanningDecisionResponseSample = "
        "workspaceState.replanningDecisionResponseSample;"
        not in source
    ):
        source = source.replace(
            "  const replanningDecisionResponseContract = workspaceState.replanningDecisionResponseContract;\n",
            "  const replanningDecisionResponseContract = workspaceState.replanningDecisionResponseContract;\n"
            "  const replanningDecisionResponseSample = workspaceState.replanningDecisionResponseSample;\n",
            1,
        )

    if "function ReplanningDecisionResponseSamplePanel" not in source:
        marker = "export function SimulationWorkspacePage()"
        panel = '''function ReplanningDecisionResponseSamplePanel({
  sample,
}: {
  sample: ReplanningDecisionResponseSampleView;
}) {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Re-planning decision sample</p>
          <h2>Re-planning decision response sample</h2>
        </div>
        <span className="source-pill">read-only sample</span>
      </div>

      <div className="status-grid">
        <article className="metric-card">
          <span>sample id</span>
          <h3>{sample.sampleId}</h3>
          <p>{formatToken(sample.decisionStatus)}</p>
          <strong>{formatToken(sample.recommendation)}</strong>
        </article>

        <article className="metric-card">
          <span>delay propagation</span>
          <h3>{sample.recoveredDelayMinutes} min recovered delay</h3>
          <p>{sample.injectedDelayMinutes} min injected delay</p>
          <strong>
            {sample.baselinePropagatedDelayMinutes} min baseline propagation
          </strong>
        </article>

        <article className="metric-card">
          <span>candidate impact</span>
          <h3>{sample.candidatePropagatedDelayMinutes} min candidate propagation</h3>
          <p>{formatToken(sample.dominantBenefit)}</p>
          <strong>{formatToken(sample.dominantRisk)}</strong>
        </article>
      </div>

      <div className="status-grid">
        <BooleanStatusCard
          label="statistical claim ready"
          value={sample.statisticalClaimReady}
          safeWhenFalse={true}
        />
        <BooleanStatusCard
          label="decision rule ready"
          value={sample.decisionRuleReady}
          safeWhenFalse={true}
        />
      </div>

      <div className="code-preview">
        <strong>Decision reason</strong>
        <p>{sample.reason}</p>
        <strong>Conservative note</strong>
        <p>{sample.conservativeNote}</p>
        <strong>Endpoint safety note</strong>
        <p>{sample.safetyNote}</p>
      </div>
    </section>
  );
}

'''
        if marker not in source:
            raise SystemExit("Could not find SimulationWorkspacePage export marker.")
        source = source.replace(marker, panel + marker, 1)

    if "<ReplanningDecisionResponseSamplePanel" not in source:
        scope_marker = '        <p className="eyebrow">Scope control</p>'
        insertion = '''      {replanningDecisionResponseSample && (
        <ReplanningDecisionResponseSamplePanel
          sample={replanningDecisionResponseSample}
        />
      )}

'''
        if scope_marker not in source:
            raise SystemExit("Could not find Scope control marker.")
        source = source.replace(scope_marker, insertion + scope_marker, 1)

    PAGE_PATH.write_text(source, encoding="utf-8")


def patch_test() -> None:
    source = TEST_PATH.read_text(encoding="utf-8")

    if "const replanningDecisionResponseSamplePayload" not in source:
        marker = "function jsonResponse(payload: unknown): Response {"
        sample_payload = '''const replanningDecisionResponseSamplePayload = {
  schema: "fieldops_lab.replanning_decision_response_sample_endpoint",
  version: "0.1.0",
  read_only: true,
  execution_enabled: false,
  write_operations_supported: false,
  browser_triggered_execution_enabled: false,
  artifact_path: "platform/contracts/replanning_decision_response_sample.json",
  safety_note:
    "This endpoint exposes a static read-only sample of a future re-planning decision response. It does not execute re-planning, run solvers, start optimization, start simulations, mutate schedules, write files, or trigger backend jobs.",
  replanning_decision_response_sample: {
    schema: "fieldops_lab.replanning_decision_response_sample",
    version: "0.1.0",
    sample_id: "demo_replanning_decision_response_001",
    sample_status: "planned_not_executed",
    read_only: true,
    execution_enabled: false,
    decision_summary: {
      decision_status: "not_executed_by_this_sample",
      decision_enabled: false,
      execution_status: "disabled",
      recommendation: "manual_review_required",
      reason:
        "The sample shows how a future response could compare a baseline and a threshold-delay re-planning candidate without executing a solver.",
    },
    delay_propagation: {
      injected_delay_minutes: 18,
      propagated_delay_minutes_baseline: 42,
      propagated_delay_minutes_candidate: 16,
      recovered_delay_minutes: 26,
    },
    tradeoff_summary: {
      dominant_benefit: "lower_delay_propagation",
      dominant_risk: "schedule_instability",
      policy_comparison_ready: true,
      statistical_claim_ready: false,
      decision_rule_ready: false,
    },
    conservative_note:
      "Sample only. No operational decision is executed, no solver is called, and no schedule is mutated.",
  },
};

'''
        if marker not in source:
            raise SystemExit("Could not find jsonResponse marker.")
        source = source.replace(marker, sample_payload + marker, 1)

    if "/api/v1/replanning-decision-response-sample" not in source:
        marker = '''    if (url.endsWith("/api/v1/replanning-decision-response-contract")) {
      return Promise.resolve(jsonResponse(replanningDecisionResponseContractPayload));
    }
'''
        insert = marker + '''    if (url.endsWith("/api/v1/replanning-decision-response-sample")) {
      return Promise.resolve(jsonResponse(replanningDecisionResponseSamplePayload));
    }
'''
        if marker not in source:
            raise SystemExit("Could not find re-planning decision response contract fetch marker.")
        source = source.replace(marker, insert, 1)

    source = source.replace(
        "loads the simulation state sample, delay injection contract, and decision response contract without enabling browser execution",
        "loads the simulation state sample, delay injection contract, decision response contract, and decision response sample without enabling browser execution",
        1,
    )

    if 'screen.getByText("Re-planning decision response sample")' not in source:
        marker = '''    expect(screen.getByText("Re-planning decision response contract")).not.toBeNull();
'''
        insert = marker + '''    expect(screen.getByText("Re-planning decision response sample")).not.toBeNull();
    expect(screen.getByRole("heading", { name: "demo_replanning_decision_response_001" })).not.toBeNull();
    expect(screen.getByText("manual review required")).not.toBeNull();
    expect(screen.getByText("26 min recovered delay")).not.toBeNull();
    expect(screen.getByText("18 min injected delay")).not.toBeNull();
    expect(screen.getByText("42 min baseline propagation")).not.toBeNull();
    expect(screen.getByText("16 min candidate propagation")).not.toBeNull();
    expect(screen.getByText("lower delay propagation")).not.toBeNull();
    expect(screen.getByText("schedule instability")).not.toBeNull();
    expect(screen.getAllByText("Current state is conservative.").length).toBeGreaterThan(0);
'''
        if marker not in source:
            raise SystemExit("Could not find decision response contract assertion marker.")
        source = source.replace(marker, insert, 1)

    if '"http://127.0.0.1:8080/api/v1/replanning-decision-response-sample"' not in source:
        marker = '''    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/replanning-decision-response-contract",
    );
'''
        insert = marker + '''    expect(requestedUrls).toContain(
      "http://127.0.0.1:8080/api/v1/replanning-decision-response-sample",
    );
'''
        if marker not in source:
            raise SystemExit("Could not find requested URL assertion marker.")
        source = source.replace(marker, insert, 1)

    TEST_PATH.write_text(source, encoding="utf-8")


patch_page()
patch_test()
print("Re-planning decision response sample web patch applied.")