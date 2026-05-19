import type {
  ApiHealth,
  DelayInjectionPlannedEndpoint,
  DelayInjectionRequestContractSnapshot,
  DelayInjectionRequestField,
  DelayInjectionSafetyRequirement,
  ReplanningDecisionMetricSection,
  ReplanningDecisionResponseContractSnapshot,
  ReplanningDecisionResponseEndpoint,
  ReplanningDecisionStatusValue,
  ExperimentalDesignFactor,
  ExperimentalDesignSummary,
  JsonObject,
  PlatformReport,
  PlatformRoute,
  PlatformSnapshot,
  PlatformStatus,
  ReportDetail,
  ReportResource,
  ResearchMethodSnapshot,
  SimulationCandidatePolicy,
  SimulationClock,
  SimulationFutureEndpoint,
  SimulationMapState,
  SimulationModeSummary,
  SimulationPoint,
  SimulationReplanningDecision,
  SimulationRoute,
  SimulationSafetyFlags,
  SimulationStateContractSnapshot,
  SimulationStateSampleSnapshot,
  SimulationTask,
  SimulationTechnician,
  SimulationTimelineEvent,
} from "../domain/platform";

type JsonRecord = Record<string, unknown>;

const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_FIELDOPS_API_BASE_URL ?? "http://127.0.0.1:8080";

function asRecord(value: unknown): JsonRecord {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return value as JsonRecord;
  }

  return {};
}

function readString(record: JsonRecord, key: string, fallback: string): string {
  const value = record[key];

  if (typeof value === "string" && value.trim().length > 0) {
    return value;
  }

  return fallback;
}

function readBoolean(
  record: JsonRecord,
  key: string,
  fallback: boolean,
): boolean {
  const value = record[key];

  if (typeof value === "boolean") {
    return value;
  }

  return fallback;
}

function readOptionalBoolean(
  record: JsonRecord,
  keys: string[],
): boolean | null {
  for (const key of keys) {
    const value = record[key];

    if (typeof value === "boolean") {
      return value;
    }
  }

  return null;
}

function readBooleanFromKeys(
  record: JsonRecord,
  keys: string[],
  fallback: boolean,
): boolean {
  for (const key of keys) {
    const value = record[key];

    if (typeof value === "boolean") {
      return value;
    }
  }

  return fallback;
}

function readNumberFromKeys(
  record: JsonRecord,
  keys: string[],
  fallback: number,
): number {
  for (const key of keys) {
    const value = record[key];

    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }

    if (typeof value === "string") {
      const parsed = Number(value.replace("%", "").trim());

      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }

  return fallback;
}

function readNullableNumberFromKeys(
  record: JsonRecord,
  keys: string[],
): number | null {
  for (const key of keys) {
    const value = record[key];

    if (value === null) {
      return null;
    }

    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
  }

  return null;
}

function readStringFromKeys(
  record: JsonRecord,
  keys: string[],
  fallback: string,
): string {
  for (const key of keys) {
    const value = record[key];

    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  return fallback;
}

function readStringArray(
  record: JsonRecord,
  key: string,
  fallback: string[] = [],
): string[] {
  const value = record[key];

  if (!Array.isArray(value)) {
    return fallback;
  }

  return value.filter((item): item is string => typeof item === "string");
}

function readStringArrayFromKeys(
  record: JsonRecord,
  keys: string[],
  fallback: string[] = [],
): string[] {
  for (const key of keys) {
    const value = record[key];

    if (Array.isArray(value)) {
      const strings = value.filter(
        (item): item is string => typeof item === "string",
      );

      if (strings.length > 0) {
        return strings;
      }
    }
  }

  return fallback;
}

function readRecordArrayFromKeys(
  record: JsonRecord,
  keys: string[],
): JsonRecord[] {
  for (const key of keys) {
    const value = record[key];

    if (Array.isArray(value)) {
      return value.map(asRecord).filter((item) => Object.keys(item).length > 0);
    }
  }

  return [];
}

function titleFromId(id: string): string {
  return id
    .split("_")
    .filter((part) => part.length > 0)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function normalizeRoutes(payload: JsonRecord): PlatformRoute[] {
  const routes = payload.routes;

  if (Array.isArray(routes)) {
    return routes.map((item) => {
      const record = asRecord(item);

      return {
        method: readString(record, "method", "GET"),
        path: readString(record, "path", "/"),
        description: readString(record, "description", "Read-only route."),
      };
    });
  }

  const endpoints = payload.endpoints;

  if (Array.isArray(endpoints)) {
    return endpoints
      .filter((endpoint): endpoint is string => typeof endpoint === "string")
      .map((path) => ({
        method: "GET",
        path,
        description: "Read-only route.",
      }));
  }

  return [];
}

function normalizeHealth(payload: JsonRecord): ApiHealth {
  const contract = asRecord(payload.contract);

  return {
    service: readString(payload, "service", "fieldops_lab_api"),
    status: readString(payload, "status", "unknown"),
    mode: readString(payload, "mode", "read_only"),
    readOnly: readBoolean(payload, "read_only", true),
    allowsArbitraryCommandExecution: readBoolean(
      payload,
      "allows_arbitrary_command_execution",
      false,
    ),
    routes: normalizeRoutes(payload),
    contractAvailable: readBoolean(contract, "available", false),
    contractPath: readString(
      contract,
      "path",
      "platform/contracts/fieldops_platform_contract.json",
    ),
  };
}

function normalizeProjectStatus(payload: JsonRecord): PlatformStatus {
  const source = asRecord(payload.project_status);
  const effectivePayload = Object.keys(source).length > 0 ? source : payload;
  const summaryMetrics = asRecord(
    effectivePayload.summary_metrics ?? effectivePayload.summaryMetrics,
  );

  const productCompleteness = readNumberFromKeys(
    summaryMetrics,
    [
      "product_completeness",
      "productCompleteness",
      "current_estimated_product_completeness",
      "currentEstimatedProductCompleteness",
    ],
    readNumberFromKeys(
      effectivePayload,
      [
        "product_completeness",
        "productCompleteness",
        "current_estimated_product_completeness",
        "currentEstimatedProductCompleteness",
      ],
      48,
    ),
  );

  const engineeringStatus = readStringFromKeys(
    summaryMetrics,
    ["engineering_status", "engineeringStatus"],
    readStringFromKeys(
      effectivePayload,
      ["engineering_status", "engineeringStatus"],
      "passed_current_structural_quality_gate",
    ),
  );

  const scientificStatus = readStringFromKeys(
    summaryMetrics,
    ["scientific_status", "scientificStatus"],
    readStringFromKeys(
      effectivePayload,
      ["scientific_status", "scientificStatus"],
      "diagnostic_only_with_methodological_warnings",
    ),
  );

  return {
    productCompleteness,
    engineeringStatus,
    scientificStatus,
    dataSource: "local http api",
    executionStatus: "disabled",
    conservativeNote: readStringFromKeys(
      effectivePayload,
      ["conservative_note", "conservativeNote"],
      "This dashboard does not prove scientific validity.",
    ),
  };
}

function normalizeReport(item: unknown): PlatformReport {
  const record = asRecord(item);
  const id = readString(record, "id", "unknown_report");

  return {
    id,
    title: readString(record, "title", titleFromId(id)),
    category: readString(record, "category", "report"),
    description: readString(
      record,
      "description",
      "Generated FieldOps Lab artifact.",
    ),
    artifactPath: readStringFromKeys(
      record,
      ["artifactPath", "artifact_path", "path", "report_path", "json_path"],
      "analysis/reports",
    ),
    markdownPath: readStringFromKeys(
      record,
      ["markdownPath", "markdown_path"],
      "",
    ),
    qualityPath: readStringFromKeys(
      record,
      ["qualityPath", "quality_path", "qualityCheckPath", "quality_check_path"],
      "",
    ),
    available: readBoolean(record, "available", readBoolean(record, "exists", true)),
    loaded: readBoolean(record, "loaded", true),
    markdownAvailable: readBoolean(record, "markdown_available", false),
    qualityAvailable: readBoolean(record, "quality_available", false),
    qualityPassed: readOptionalBoolean(record, [
      "qualityPassed",
      "quality_passed",
      "passed",
    ]),
  };
}

function normalizeReports(payload: JsonRecord): PlatformReport[] {
  const reports = Array.isArray(payload.reports) ? payload.reports : [];
  return reports.map(normalizeReport);
}

function normalizeJsonResource(value: unknown): ReportResource<JsonObject> {
  const record = asRecord(value);
  const data = asRecord(record.data ?? record.content);

  return {
    path: readString(record, "path", ""),
    exists: readBoolean(record, "exists", readBoolean(record, "available", false)),
    loaded: readBoolean(record, "loaded", Object.keys(data).length > 0),
    data: Object.keys(data).length > 0 ? data : null,
    text: "",
    error: readString(record, "error", ""),
  };
}

function normalizeTextResource(value: unknown): ReportResource {
  const record = asRecord(value);

  return {
    path: readString(record, "path", ""),
    exists: readBoolean(record, "exists", readBoolean(record, "available", false)),
    loaded: readBoolean(record, "loaded", false),
    data: null,
    text: readStringFromKeys(record, ["text", "preview"], ""),
    error: readString(record, "error", ""),
  };
}

function normalizeReportDetail(payload: JsonRecord): ReportDetail {
  const metadata = asRecord(payload.metadata);

  return {
    report: readString(payload, "report", "report_detail"),
    id: readString(payload, "id", "unknown_report"),
    title: readString(payload, "title", "Unknown report"),
    category: readString(payload, "category", "report"),
    description: readString(payload, "description", "Report detail."),
    readOnly: readBoolean(payload, "read_only", true),
    executionSupported: readBoolean(payload, "execution_supported", false),
    writeOperationsSupported: readBoolean(
      payload,
      "write_operations_supported",
      false,
    ),
    available: readBoolean(payload, "available", true),
    metadata: {
      artifactPath: readStringFromKeys(
        metadata,
        ["artifact_path", "artifactPath"],
        readString(payload, "artifact_path", ""),
      ),
      markdownPath: readStringFromKeys(
        metadata,
        ["markdown_path", "markdownPath"],
        readString(payload, "markdown_path", ""),
      ),
      qualityPath: readStringFromKeys(
        metadata,
        ["quality_path", "qualityPath"],
        readString(payload, "quality_check_path", ""),
      ),
      qualityPassed: readOptionalBoolean(metadata, [
        "quality_passed",
        "qualityPassed",
      ]),
    },
    artifact: normalizeJsonResource(payload.artifact),
    markdown: normalizeTextResource(payload.markdown),
    qualityCheck: normalizeJsonResource(payload.quality_check),
    conservativeNote: readStringFromKeys(
      payload,
      ["conservative_note", "safety_note"],
      "Report detail is available for inspection only.",
    ),
  };
}

function normalizeDesignFactor(
  item: JsonRecord,
  index: number,
): ExperimentalDesignFactor {
  const id = readStringFromKeys(
    item,
    ["id", "name", "factor", "key"],
    `factor_${index + 1}`,
  );

  return {
    id,
    label: readStringFromKeys(item, ["label", "title", "name"], titleFromId(id)),
    description: readStringFromKeys(
      item,
      ["description", "rationale", "note"],
      "Experimental factor exposed by the current design matrix.",
    ),
    levels: readStringArrayFromKeys(
      item,
      ["levels", "values", "allowed_values", "classes"],
      [],
    ),
  };
}

function normalizeExperimentalDesign(
  payload: JsonRecord,
): ExperimentalDesignSummary {
  const wrapped = asRecord(payload.experimental_design_matrix);
  const source = Object.keys(wrapped).length > 0 ? wrapped : payload;
  const summary = asRecord(source.summary);

  const payloadFactors = readRecordArrayFromKeys(source, [
    "factors",
    "experimental_factors",
    "factor_matrix",
    "design_factors",
  ]);
  const summaryFactors = readRecordArrayFromKeys(summary, [
    "factors",
    "experimental_factors",
    "factor_matrix",
    "design_factors",
  ]);

  const factors = (payloadFactors.length > 0 ? payloadFactors : summaryFactors).map(
    normalizeDesignFactor,
  );

  return {
    report: readString(source, "report", "experimental_design_matrix"),
    available: readBoolean(source, "available", true),
    readOnly: readBoolean(source, "read_only", true),
    experimentCount: readNumberFromKeys(
      summary,
      ["experiment_count", "experimentCount"],
      0,
    ),
    scenarioCount: readNumberFromKeys(
      summary,
      ["scenario_count", "scenarioCount"],
      0,
    ),
    replicationCount: readNumberFromKeys(
      summary,
      ["replication_count", "replicationCount"],
      0,
    ),
    factorCount: readNumberFromKeys(
      summary,
      ["factor_count", "factorCount"],
      factors.length,
    ),
    reproducibleFromExplicitFactors: readBoolean(
      summary,
      "reproducible_from_explicit_factors",
      false,
    ),
    factors,
    limitations: readStringArrayFromKeys(
      source,
      ["limitations", "methodological_limitations", "warnings", "conservative_warnings"],
      readStringArrayFromKeys(summary, ["limitations", "warnings"], []),
    ),
    qualityNotes: readStringArrayFromKeys(
      source,
      ["quality_notes", "qualityNotes", "validation_notes"],
      readStringArrayFromKeys(summary, ["quality_notes", "qualityNotes"], []),
    ),
  };
}

function normalizeResearchMethod(payload: JsonRecord): ResearchMethodSnapshot {
  const contract = asRecord(payload.contract);
  const methodSummary = asRecord(payload.method_summary);
  const projectQuestion = asRecord(contract.project_question);
  const researchGap = asRecord(contract.research_gap);
  const contributionClaims = asRecord(contract.contribution_claims);
  const fuzzyLogicPosition = asRecord(contract.fuzzy_logic_position);
  const conservative = asRecord(payload.conservative_interpretation);

  return {
    readOnly: readBoolean(payload, "read_only", true),
    available: readBoolean(payload, "available", Object.keys(contract).length > 0),
    contractPath: readString(
      payload,
      "contract_path",
      "platform/contracts/research_method_contract.json",
    ),
    framingPath: readString(
      payload,
      "framing_path",
      "platform/research_framing.md",
    ),
    framingMarkdown: readString(payload, "framing_markdown", ""),
    interpretation: {
      doesNotClaimFinalScientificValidity: readBoolean(
        conservative,
        "does_not_claim_final_scientific_validity",
        true,
      ),
      fuzzyLogicIsOptional: readBoolean(
        conservative,
        "fuzzy_logic_is_optional",
        true,
      ),
      practicalEquivalenceMustBeHandled: readBoolean(
        conservative,
        "practical_equivalence_must_be_handled",
        true,
      ),
      realCompanyDataRequiresValidationBeforeDecisionSupport: readBoolean(
        conservative,
        "real_company_data_requires_validation_before_decision_support",
        true,
      ),
    },
    contractSummary: {
      status: readString(contract, "status", "draft"),
      scientificMaturity: readString(
        contract,
        "scientific_maturity",
        "diagnostic_foundation",
      ),
      projectQuestion: readString(
        projectQuestion,
        "summary",
        readString(
          methodSummary,
          "platform_goal",
          "How can a field service operation choose an appropriate replanning policy when operational disruptions occur during execution?",
        ),
      ),
      researchGap: readString(
        researchGap,
        "specific_gap",
        "A replicable experimental and decision framework for comparing replanning policies under controlled dynamic disruptions.",
      ),
      primaryDynamicFocus: readStringArray(researchGap, "primary_dynamic_focus", [
        "delay_propagation",
      ]),
      secondaryDynamicFocus: readStringArray(
        researchGap,
        "secondary_dynamic_focus",
        [],
      ),
      completedFoundation: readStringArray(
        contract,
        "current_completed_foundation",
        [],
      ),
      missingMajorWork: readStringArray(contract, "missing_major_work", []),
      preferredBaselineAlternatives: readStringArray(
        fuzzyLogicPosition,
        "preferred_baseline_alternatives",
        [],
      ),
      claimsPolicyDecisionFramework: readBoolean(
        contributionClaims,
        "claims_policy_decision_framework",
        false,
      ),
      claimsReproducibleExperimentalPlatform: readBoolean(
        contributionClaims,
        "claims_reproducible_experimental_platform",
        false,
      ),
    },
  };
}

function normalizeSimulationModes(contract: JsonRecord): SimulationModeSummary[] {
  const modeRecords = readRecordArrayFromKeys(contract, [
    "modes",
    "operating_modes",
    "target_operating_modes",
    "execution_modes",
  ]);

  if (modeRecords.length === 0) {
    return [
      {
        id: "optimization_mode",
        label: "Optimization mode",
        purpose:
          "Batch experiments, policy comparison, metrics, ranking, and statistical analysis.",
        executionEnabled: false,
      },
      {
        id: "simulation_mode",
        label: "Simulation mode",
        purpose:
          "Visual map and operational timeline for inspecting technicians, tasks, delays, and re-planning decisions.",
        executionEnabled: false,
      },
    ];
  }

  return modeRecords.map((mode, index) => {
    const id = readStringFromKeys(
      mode,
      ["id", "name", "mode", "key"],
      `mode_${index + 1}`,
    );

    return {
      id,
      label: readStringFromKeys(mode, ["label", "title", "name"], titleFromId(id)),
      purpose: readStringFromKeys(
        mode,
        ["purpose", "description", "scope"],
        "Mode defined by the simulation state contract.",
      ),
      executionEnabled: readBooleanFromKeys(
        mode,
        ["execution_enabled", "currently_enabled", "enabled"],
        false,
      ),
    };
  });
}

function normalizeFutureEndpoints(contract: JsonRecord): SimulationFutureEndpoint[] {
  const endpointRecords = readRecordArrayFromKeys(contract, [
    "future_api_endpoints",
    "planned_api_endpoints",
    "planned_endpoints",
    "future_endpoints",
  ]);

  return endpointRecords.map((endpoint) => ({
    method: readString(endpoint, "method", "GET"),
    path: readString(endpoint, "path", "/api/v1/future-simulation-endpoint"),
    status: readStringFromKeys(
      endpoint,
      ["status", "state", "availability"],
      "planned_not_enabled",
    ),
    executionEnabled: readBooleanFromKeys(
      endpoint,
      ["execution_enabled", "currently_enabled", "enabled"],
      false,
    ),
  }));
}

function normalizeSimulationSafetyFlags(
  payload: JsonRecord,
  contract: JsonRecord,
): SimulationSafetyFlags {
  const safety = asRecord(
    payload.safety_flags ??
      payload.safety_interpretation ??
      contract.safety_flags ??
      contract.safety_requirements,
  );

  return {
    browserExecutionEnabled: readBooleanFromKeys(
      safety,
      ["browser_execution_enabled", "browserExecutionEnabled"],
      false,
    ),
    arbitraryCommandExecutionAllowed: readBooleanFromKeys(
      safety,
      [
        "arbitrary_command_execution_allowed",
        "allows_arbitrary_command_execution",
        "arbitraryCommandExecutionAllowed",
      ],
      false,
    ),
    writeOperationsSupported: readBooleanFromKeys(
      safety,
      ["write_operations_supported", "writeOperationsSupported"],
      false,
    ),
    futureJobApiCurrentlyEnabled: readBooleanFromKeys(
      safety,
      [
        "future_job_api_currently_enabled",
        "futureJobApiCurrentlyEnabled",
        "job_api_enabled",
      ],
      false,
    ),
  };
}

function normalizeSimulationStateContract(
  payload: JsonRecord,
): SimulationStateContractSnapshot {
  const wrappedContract = asRecord(payload.simulation_state_contract);
  const contract =
    Object.keys(wrappedContract).length > 0 ? wrappedContract : asRecord(payload.contract);

  const scope = asRecord(contract.scope ?? contract.research_scope);
  const stateSchema = asRecord(
    contract.state_schema ??
      contract.simulation_state_schema ??
      contract.simulation_state ??
      contract.visual_state,
  );
  const timeline = asRecord(stateSchema.timeline ?? contract.timeline);
  const replanning = asRecord(
    contract.replanning_decision ??
      contract.replanning_decision_contract ??
      contract.decision_contract,
  );

  const primaryDissertationScope = readStringArrayFromKeys(
    scope,
    ["primary_dissertation_scope", "primary_dynamic_focus", "primary_scope"],
    readStringArrayFromKeys(contract, ["primary_dissertation_scope"], [
      "delay_propagation",
      "travel_delay",
      "service_delay",
    ]),
  );

  const futurePlatformPerturbations = readStringArrayFromKeys(
    scope,
    [
      "future_platform_perturbations",
      "secondary_dynamic_focus",
      "extension_perturbations",
    ],
    readStringArrayFromKeys(contract, ["future_platform_perturbations"], [
      "new_requests",
      "cancellations",
      "priority_changes",
    ]),
  );

  return {
    readOnly: readBoolean(payload, "read_only", true),
    available: readBoolean(payload, "available", Object.keys(contract).length > 0),
    contractPath: readString(
      payload,
      "contract_path",
      readString(payload, "artifact_path", "platform/contracts/simulation_state_contract.json"),
    ),
    primaryDissertationScope,
    futurePlatformPerturbations,
    modes: normalizeSimulationModes(contract),
    mapEntities: readStringArrayFromKeys(
      stateSchema,
      ["map_entities", "entities", "mapEntityTypes"],
      ["technicians", "tasks", "depots", "routes", "operational_events"],
    ),
    timelineEvents: readStringArrayFromKeys(
      timeline,
      ["events", "event_types", "timeline_events"],
      ["planned_start", "arrival", "service_start", "delay", "replanning_decision"],
    ),
    replanningDecisionFields: readStringArrayFromKeys(
      replanning,
      ["fields", "decision_fields", "tracked_fields"],
      [
        "policy_id",
        "trigger_reason",
        "computational_cost",
        "route_stability",
        "practical_equivalence_status",
      ],
    ),
    futureEndpoints: normalizeFutureEndpoints(contract),
    safetyFlags: normalizeSimulationSafetyFlags(payload, contract),
    conservativeNote: readStringFromKeys(
      payload,
      ["conservative_note", "note"],
      "Simulation state contract is read-only and does not enable browser-triggered execution.",
    ),
  };
}

function normalizePoint(record: JsonRecord): SimulationPoint {
  return {
    id: readString(record, "id", "point"),
    label: readString(record, "label", readString(record, "id", "Point")),
    x: readNumberFromKeys(record, ["x"], 0),
    y: readNumberFromKeys(record, ["y"], 0),
  };
}

function normalizeTechnician(record: JsonRecord): SimulationTechnician {
  const point = normalizePoint(record);

  return {
    ...point,
    status: readString(record, "status", "unknown"),
    currentTaskId: readString(record, "current_task_id", ""),
    routeId: readString(record, "route_id", ""),
    delayMinutes: readNumberFromKeys(record, ["delay_minutes", "delayMinutes"], 0),
  };
}

function normalizeTask(record: JsonRecord): SimulationTask {
  const point = normalizePoint(record);

  return {
    ...point,
    status: readString(record, "status", "pending"),
    plannedStart: readNumberFromKeys(record, ["planned_start", "plannedStart"], 0),
    plannedEnd: readNumberFromKeys(record, ["planned_end", "plannedEnd"], 0),
    actualStart: readNullableNumberFromKeys(record, ["actual_start", "actualStart"]),
    actualEnd: readNullableNumberFromKeys(record, ["actual_end", "actualEnd"]),
    priority: readString(record, "priority", "normal"),
  };
}

function normalizeRoute(record: JsonRecord): SimulationRoute {
  return {
    id: readString(record, "id", "route"),
    technicianId: readString(record, "technician_id", ""),
    taskSequence: readStringArray(record, "task_sequence", []),
    status: readString(record, "status", "unknown"),
    totalDelayMinutes: readNumberFromKeys(
      record,
      ["total_delay_minutes", "totalDelayMinutes"],
      0,
    ),
  };
}

function normalizeClock(record: JsonRecord): SimulationClock {
  return {
    simulationId: readString(record, "simulation_id", "demo_simulation"),
    status: readString(record, "status", "paused"),
    timeUnit: readString(record, "time_unit", "minutes"),
    startTime: readNumberFromKeys(record, ["start_time", "startTime"], 0),
    currentTime: readNumberFromKeys(record, ["current_time", "currentTime"], 0),
    endTime: readNumberFromKeys(record, ["end_time", "endTime"], 0),
    speedMultiplier: readNumberFromKeys(
      record,
      ["speed_multiplier", "speedMultiplier"],
      1,
    ),
    canUserAdvanceTime: readBooleanFromKeys(
      record,
      ["can_user_advance_time", "canUserAdvanceTime"],
      false,
    ),
    canUserInjectDelay: readBooleanFromKeys(
      record,
      ["can_user_inject_delay", "canUserInjectDelay"],
      false,
    ),
  };
}

function normalizeMapState(record: JsonRecord): SimulationMapState {
  return {
    coordinateSystem: readString(
      record,
      "coordinate_system",
      "normalized_demo_coordinates",
    ),
    depots: readRecordArrayFromKeys(record, ["depots"]).map(normalizePoint),
    technicians: readRecordArrayFromKeys(record, ["technicians"]).map(
      normalizeTechnician,
    ),
    tasks: readRecordArrayFromKeys(record, ["tasks"]).map(normalizeTask),
    routes: readRecordArrayFromKeys(record, ["routes"]).map(normalizeRoute),
  };
}

function normalizeTimelineEvent(record: JsonRecord): SimulationTimelineEvent {
  return {
    time: readNumberFromKeys(record, ["time"], 0),
    type: readString(record, "type", "event"),
    label: readString(record, "label", "Simulation event"),
    affectedEntityId: readString(record, "affected_entity_id", ""),
    delayMinutes: readNumberFromKeys(record, ["delay_minutes", "delayMinutes"], 0),
  };
}

function normalizeCandidatePolicy(record: JsonRecord): SimulationCandidatePolicy {
  return {
    id: readString(record, "id", "policy"),
    label: readString(record, "label", readString(record, "id", "Policy")),
    executionEnabled: readBooleanFromKeys(
      record,
      ["execution_enabled", "currently_enabled", "enabled"],
      false,
    ),
  };
}

function normalizeReplanningDecision(
  record: JsonRecord,
): SimulationReplanningDecision {
  return {
    status: readString(record, "status", "not_required"),
    trigger: readString(record, "trigger", "none"),
    triggerTime: readNumberFromKeys(record, ["trigger_time", "triggerTime"], 0),
    affectedRouteId: readString(record, "affected_route_id", ""),
    affectedTechnicianId: readString(record, "affected_technician_id", ""),
    primaryDelayType: readString(record, "primary_delay_type", "delay"),
    delayPropagationDetected: readBoolean(
      record,
      "delay_propagation_detected",
      false,
    ),
    candidatePolicies: readRecordArrayFromKeys(record, ["candidate_policies"]).map(
      normalizeCandidatePolicy,
    ),
    decisionFields: readStringArray(record, "decision_fields", []),
  };
}

function normalizeSimulationStateSample(
  payload: JsonRecord,
): SimulationStateSampleSnapshot {
  const sample = asRecord(payload.simulation_state_sample ?? payload.sample ?? payload);
  const researchScope = asRecord(sample.research_scope);

  return {
    readOnly: readBoolean(payload, "read_only", readBoolean(sample, "read_only", true)),
    available: readBoolean(payload, "available", Object.keys(sample).length > 0),
    artifactPath: readString(
      payload,
      "artifact_path",
      "platform/contracts/simulation_state_sample.json",
    ),
    executionEnabled: readBoolean(
      payload,
      "execution_enabled",
      readBoolean(sample, "execution_enabled", false),
    ),
    writeOperationsSupported: readBoolean(
      payload,
      "write_operations_supported",
      readBoolean(sample, "write_operations_supported", false),
    ),
    browserTriggeredExecutionEnabled: readBoolean(
      payload,
      "browser_triggered_execution_enabled",
      readBoolean(sample, "browser_triggered_execution_enabled", false),
    ),
    arbitraryCommandExecutionAllowed: readBoolean(
      payload,
      "arbitrary_command_execution_allowed",
      readBoolean(sample, "arbitrary_command_execution_allowed", false),
    ),
    schema: readString(sample, "schema", "fieldops_lab.simulation_state_sample"),
    version: readString(sample, "version", "0.1.0"),
    purpose: readString(
      sample,
      "purpose",
      "Provide a conservative sample simulation state for future read-only map and timeline rendering.",
    ),
    clock: normalizeClock(asRecord(sample.clock)),
    map: normalizeMapState(asRecord(sample.map)),
    timeline: readRecordArrayFromKeys(sample, ["timeline"]).map(
      normalizeTimelineEvent,
    ),
    replanningDecision: normalizeReplanningDecision(
      asRecord(sample.replanning_decision),
    ),
    primaryDissertationScope: readStringArray(
      researchScope,
      "primary_dissertation_scope",
      ["delay_propagation", "travel_delay", "service_delay"],
    ),
    futurePlatformPerturbations: readStringArray(
      researchScope,
      "future_platform_perturbations",
      ["new_requests", "cancellations", "priority_changes"],
    ),
    safetyNotes: readStringArray(sample, "safety_notes", [
      "This sample is static and read-only.",
    ]),
  };
}

function normalizePlannedEndpoint(record: JsonRecord): DelayInjectionPlannedEndpoint {
  return {
    method: readString(record, "method", "POST"),
    path: readString(
      record,
      "path",
      "/api/v1/simulation-runs/{simulation_run_id}/delay-events",
    ),
    status: readString(record, "status", "planned_not_enabled"),
    currentBehavior: readString(
      record,
      "current_behavior",
      "No write endpoint is currently exposed by the read-only API.",
    ),
    executionEnabled: readBoolean(record, "execution_enabled", false),
    requiresFutureAuthentication: readBoolean(
      record,
      "requires_future_authentication",
      true,
    ),
    requiresFutureServerSideValidation: readBoolean(
      record,
      "requires_future_server_side_validation",
      true,
    ),
    requiresFutureAuditLog: readBoolean(record, "requires_future_audit_log", true),
  };
}

function normalizeRequestField(
  id: string,
  record: JsonRecord,
): DelayInjectionRequestField {
  return {
    id,
    type: readString(record, "type", "string"),
    required: readBoolean(record, "required", false),
    description: readString(record, "description", "Delay injection request field."),
    allowedValues: readStringArray(record, "allowed_values", []),
    minimum: readNullableNumberFromKeys(record, ["minimum"]),
  };
}

function normalizeRequestFields(record: JsonRecord): DelayInjectionRequestField[] {
  return Object.entries(record)
    .map(([id, value]) => normalizeRequestField(id, asRecord(value)))
    .filter((field) => field.id.length > 0);
}

function normalizeSafetyRequirements(
  record: JsonRecord,
): DelayInjectionSafetyRequirement[] {
  return Object.entries(record).map(([id, value]) => ({
    id,
    enabled: typeof value === "boolean" ? value : false,
  }));
}

function normalizeDelayInjectionRequestContract(
  payload: JsonRecord,
): DelayInjectionRequestContractSnapshot {
  const wrapped = asRecord(payload.delay_injection_request_contract);
  const contract = Object.keys(wrapped).length > 0 ? wrapped : payload;
  const researchAlignment = asRecord(contract.research_alignment);
  const requestShape = asRecord(contract.request_shape);
  const replanningDecisionOutput = asRecord(contract.replanning_decision_output);
  const safetyRequirements = asRecord(contract.safety_requirements);

  return {
    readOnly: readBoolean(payload, "read_only", readBoolean(contract, "read_only", true)),
    available: readBoolean(payload, "available", Object.keys(contract).length > 0),
    artifactPath: readString(
      payload,
      "artifact_path",
      "platform/contracts/delay_injection_request_contract.json",
    ),
    contract: readString(contract, "contract", "delay_injection_request_contract"),
    version: readString(contract, "version", "0.1.0"),
    status: readString(contract, "status", "planned_disabled"),
    executionEnabled: readBoolean(
      payload,
      "execution_enabled",
      readBoolean(contract, "execution_enabled", false),
    ),
    writeOperationsSupported: readBoolean(
      payload,
      "write_operations_supported",
      readBoolean(contract, "write_operations_supported", false),
    ),
    browserExecutionEnabled: readBoolean(
      payload,
      "browser_triggered_execution_enabled",
      readBoolean(contract, "browser_execution_enabled", false),
    ),
    primaryPurpose: readString(
      contract,
      "primary_purpose",
      "Define the future request shape for injecting delays during visual simulation without enabling execution yet.",
    ),
    primaryDissertationScope: readStringArray(researchAlignment, "primary_dissertation_scope", [
      "delay_propagation",
      "travel_delay",
      "service_delay",
    ]),
    futurePlatformExtensions: readStringArray(
      researchAlignment,
      "future_platform_extensions",
      ["new_requests", "cancellations", "priority_changes"],
    ),
    scopePolicy: readString(
      researchAlignment,
      "scope_policy",
      "The dissertation should stay focused on delays and delay propagation.",
    ),
    plannedEndpoint: normalizePlannedEndpoint(
      asRecord(payload.planned_endpoint ?? contract.planned_endpoint),
    ),
    requestFields: normalizeRequestFields(requestShape),
    validationRules: readStringArray(contract, "validation_rules", []),
    expectedFutureEffects: readStringArray(contract, "expected_future_effects", []),
    replanningDecisionRequiredFutureFields: readStringArray(
      replanningDecisionOutput,
      "required_future_fields",
      [],
    ),
    replanningDecisionCurrentStatus: readString(
      replanningDecisionOutput,
      "current_status",
      "not_executed_by_this_contract",
    ),
    safetyRequirements: normalizeSafetyRequirements(safetyRequirements),
    qualityRequirements: readStringArray(contract, "quality_requirements", []),
    conservativeNote: readString(
      contract,
      "conservative_note",
      readString(
        payload,
        "safety_note",
        "This file is only a read-only planning contract.",
      ),
    ),
  };
}


function normalizeReplanningDecisionEndpoint(
  record: JsonRecord,
): ReplanningDecisionResponseEndpoint {
  return {
    method: readString(record, "method", "POST"),
    path: readString(record, "path", "/api/v1/replanning-decisions"),
    status: readStringFromKeys(
      record,
      ["status", "state", "availability"],
      "planned_not_enabled",
    ),
    executionEnabled: readBooleanFromKeys(
      record,
      ["execution_enabled", "currently_enabled", "enabled"],
      false,
    ),
  };
}

function normalizeReplanningDecisionMetricSection(
  id: string,
  value: unknown,
): ReplanningDecisionMetricSection {
  const record = asRecord(value);

  return {
    id,
    label: readStringFromKeys(record, ["label", "title", "name"], titleFromId(id)),
    fields: readStringArrayFromKeys(
      record,
      ["fields", "required_fields", "tracked_fields"],
      [],
    ),
  };
}

function normalizeReplanningDecisionStatusValue(
  value: unknown,
): ReplanningDecisionStatusValue {
  const record = asRecord(value);
  const statusValue = readStringFromKeys(
    record,
    ["value", "id", "status", "name"],
    "not_executed",
  );

  return {
    value: statusValue,
    description: readStringFromKeys(
      record,
      ["description", "meaning", "note"],
      "Status value exposed by the future re-planning decision response contract.",
    ),
  };
}

function normalizeReplanningDecisionResponseContract(
  payload: JsonRecord,
): ReplanningDecisionResponseContractSnapshot {
  const wrappedContract = asRecord(payload.replanning_decision_response_contract);
  const contract =
    Object.keys(wrappedContract).length > 0 ? wrappedContract : asRecord(payload.contract);
  const futureEndpoint = asRecord(
    payload.future_endpoint ??
      payload.planned_endpoint ??
      contract.future_endpoint ??
      contract.planned_endpoint,
  );
  const responseShape = asRecord(contract.response_shape);
  const inputReferenceRecord = asRecord(contract.input_references);
  const safetyRequirementRecord = asRecord(contract.safety_requirements);

  const responseSections = Object.entries(responseShape).map(([id, value]) =>
    normalizeReplanningDecisionMetricSection(id, value),
  );

  return {
    readOnly: readBoolean(payload, "read_only", readBoolean(contract, "read_only", true)),
    available: readBoolean(payload, "available", Object.keys(contract).length > 0),
    artifactPath: readString(
      payload,
      "artifact_path",
      "platform/contracts/replanning_decision_response_contract.json",
    ),
    contractName: readStringFromKeys(
      contract,
      ["contract_name", "contract", "name"],
      "replanning_decision_response_contract",
    ),
    version: readString(contract, "version", "0.1.0"),
    status: readString(contract, "status", "planned_read_only_contract"),
    enabled: readBoolean(contract, "enabled", false),
    executionEnabled: readBoolean(
      payload,
      "execution_enabled",
      readBoolean(contract, "execution_enabled", false),
    ),
    currentEndpointEnabled: readBooleanFromKeys(
      contract,
      ["current_endpoint_enabled", "endpoint_enabled"],
      false,
    ),
    futureEndpoint: normalizeReplanningDecisionEndpoint(futureEndpoint),
    inputReferences: readStringArrayFromKeys(
      contract,
      ["input_references", "required_input_references"],
      Object.keys(inputReferenceRecord),
    ),
    responseSections,
    statusValues: readRecordArrayFromKeys(
      contract,
      ["status_values", "allowed_status_values"],
    ).map(normalizeReplanningDecisionStatusValue),
    relatedContracts: readStringArrayFromKeys(
      contract,
      ["related_contracts", "contract_dependencies"],
      [],
    ),
    safetyRequirements: readStringArrayFromKeys(
      contract,
      ["safety_requirements", "safety_rules"],
      Object.keys(safetyRequirementRecord),
    ),
    qualityRequirements: readStringArrayFromKeys(
      contract,
      ["quality_requirements", "quality_rules"],
      [],
    ),
    conservativeNote: readStringFromKeys(
      contract,
      ["conservative_note", "safety_note", "note"],
      readStringFromKeys(
        payload,
        ["safety_note", "conservative_note"],
        "This contract is read-only and does not execute re-planning.",
      ),
    ),
  };
}

async function fetchJson(baseUrl: string, path: string): Promise<JsonRecord> {
  const url = new URL(path, baseUrl).toString();

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`);
  }

  return asRecord(await response.json());
}

export class ReadOnlyPlatformApi {
  private readonly baseUrl: string;

  constructor(baseUrl: string = DEFAULT_API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getHealth(): Promise<ApiHealth> {
    const payload = await fetchJson(this.baseUrl, "/api/v1/health");
    return normalizeHealth(payload);
  }

  async getProjectStatus(): Promise<PlatformStatus> {
    const payload = await fetchJson(this.baseUrl, "/api/v1/project-status");
    return normalizeProjectStatus(payload);
  }

  async getReports(): Promise<PlatformReport[]> {
    const payload = await fetchJson(this.baseUrl, "/api/v1/reports");
    return normalizeReports(payload);
  }

  async getReportDetail(reportId: string): Promise<ReportDetail> {
    const safeReportId = encodeURIComponent(reportId);
    const payload = await fetchJson(this.baseUrl, `/api/v1/reports/${safeReportId}`);
    return normalizeReportDetail(payload);
  }

  async getExperimentalDesign(): Promise<ExperimentalDesignSummary> {
    const payload = await fetchJson(
      this.baseUrl,
      "/api/v1/experimental-design-matrix",
    );

    return normalizeExperimentalDesign(payload);
  }

  async getResearchMethod(): Promise<ResearchMethodSnapshot> {
    const payload = await fetchJson(this.baseUrl, "/api/v1/research-method");
    return normalizeResearchMethod(payload);
  }

  async getSimulationStateContract(): Promise<SimulationStateContractSnapshot> {
    const payload = await fetchJson(
      this.baseUrl,
      "/api/v1/simulation-state-contract",
    );

    return normalizeSimulationStateContract(payload);
  }

  async getSimulationStateSample(): Promise<SimulationStateSampleSnapshot> {
    const payload = await fetchJson(this.baseUrl, "/api/v1/simulation-state-sample");

    return normalizeSimulationStateSample(payload);
  }

  async getDelayInjectionRequestContract(): Promise<DelayInjectionRequestContractSnapshot> {
    const payload = await fetchJson(
      this.baseUrl,
      "/api/v1/delay-injection-request-contract",
    );

    return normalizeDelayInjectionRequestContract(payload);
  }


  async getReplanningDecisionResponseContract(): Promise<ReplanningDecisionResponseContractSnapshot> {
    const payload = await fetchJson(
      this.baseUrl,
      "/api/v1/replanning-decision-response-contract",
    );

    return normalizeReplanningDecisionResponseContract(payload);
  }

  async getSnapshot(): Promise<PlatformSnapshot> {
    const [health, status, reports, experimentalDesign, researchMethod] =
      await Promise.all([
        this.getHealth(),
        this.getProjectStatus(),
        this.getReports(),
        this.getExperimentalDesign(),
        this.getResearchMethod(),
      ]);

    const warnings = [
      status.conservativeNote,
      "Generated artifacts are engineering and diagnostic evidence, not final scientific validation.",
      "Backend execution remains intentionally unavailable from the web interface.",
      researchMethod.interpretation.practicalEquivalenceMustBeHandled
        ? "Policy comparisons must handle practical equivalence before recommending a winner."
        : "Practical equivalence handling is not confirmed by the current research method contract.",
    ];

    return {
      health,
      status,
      reports,
      experimentalDesign,
      researchMethod,
      warnings,
      apiBaseUrl: this.baseUrl,
    };
  }
}

export function createReadOnlyPlatformApi(baseUrl?: string): ReadOnlyPlatformApi {
  return new ReadOnlyPlatformApi(baseUrl);
}