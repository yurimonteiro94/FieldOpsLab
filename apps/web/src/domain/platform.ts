export type PageId =
  | "dashboard"
  | "reports"
  | "experimental-design"
  | "api-safety"
  | "scientific-validation"
  | "research-method"
  | "campaign-diagnostics"
  | "simulation-workspace";

export type JsonObject = Record<string, unknown>;

export interface PlatformRoute {
  method: string;
  path: string;
  description: string;
}

export interface ApiHealth {
  service: string;
  status: string;
  mode: string;
  readOnly: boolean;
  allowsArbitraryCommandExecution: boolean;
  routes: PlatformRoute[];
  contractAvailable: boolean;
  contractPath: string;
}

export interface PlatformStatus {
  productCompleteness: number;
  engineeringStatus: string;
  scientificStatus: string;
  dataSource: string;
  executionStatus: string;
  conservativeNote: string;
}

export interface PlatformReport {
  id: string;
  title: string;
  category: string;
  description: string;
  artifactPath: string;
  markdownPath: string;
  qualityPath: string;
  available: boolean;
  loaded: boolean;
  markdownAvailable: boolean;
  qualityAvailable: boolean;
  qualityPassed: boolean | null;
}

export interface ReportResource<T = JsonObject> {
  path: string;
  exists: boolean;
  loaded: boolean;
  data: T | null;
  text: string;
  error: string | null;
}

export interface ReportDetailMetadata {
  artifactPath: string;
  markdownPath: string;
  qualityPath: string;
  qualityPassed: boolean | null;
}

export interface ReportDetail {
  report: string;
  id: string;
  title: string;
  category: string;
  description: string;
  readOnly: boolean;
  executionSupported: boolean;
  writeOperationsSupported: boolean;
  available: boolean;
  metadata: ReportDetailMetadata;
  artifact: ReportResource;
  markdown: ReportResource;
  qualityCheck: ReportResource;
  conservativeNote: string;
}

export interface ExperimentalDesignFactor {
  id: string;
  label: string;
  description: string;
  levels: string[];
}

export interface ExperimentalDesignSummary {
  report: string;
  available: boolean;
  readOnly: boolean;
  experimentCount: number;
  scenarioCount: number;
  replicationCount: number;
  factorCount: number;
  reproducibleFromExplicitFactors: boolean;
  factors: ExperimentalDesignFactor[];
  limitations: string[];
  qualityNotes: string[];
}

export interface ResearchMethodInterpretation {
  doesNotClaimFinalScientificValidity: boolean;
  fuzzyLogicIsOptional: boolean;
  practicalEquivalenceMustBeHandled: boolean;
  realCompanyDataRequiresValidationBeforeDecisionSupport: boolean;
}

export interface ResearchMethodContractSummary {
  status: string;
  scientificMaturity: string;
  projectQuestion: string;
  researchGap: string;
  primaryDynamicFocus: string[];
  secondaryDynamicFocus: string[];
  completedFoundation: string[];
  missingMajorWork: string[];
  preferredBaselineAlternatives: string[];
  claimsPolicyDecisionFramework: boolean;
  claimsReproducibleExperimentalPlatform: boolean;
}

export interface ResearchMethodSnapshot {
  readOnly: boolean;
  available: boolean;
  contractPath: string;
  framingPath: string;
  framingMarkdown: string;
  interpretation: ResearchMethodInterpretation;
  contractSummary: ResearchMethodContractSummary;
}

export interface SimulationModeSummary {
  id: string;
  label: string;
  purpose: string;
  executionEnabled: boolean;
}

export interface SimulationFutureEndpoint {
  method: string;
  path: string;
  status: string;
  executionEnabled: boolean;
}

export interface SimulationSafetyFlags {
  browserExecutionEnabled: boolean;
  arbitraryCommandExecutionAllowed: boolean;
  writeOperationsSupported: boolean;
  futureJobApiCurrentlyEnabled: boolean;
}

export interface SimulationStateContractSnapshot {
  readOnly: boolean;
  available: boolean;
  contractPath: string;
  primaryDissertationScope: string[];
  futurePlatformPerturbations: string[];
  modes: SimulationModeSummary[];
  mapEntities: string[];
  timelineEvents: string[];
  replanningDecisionFields: string[];
  futureEndpoints: SimulationFutureEndpoint[];
  safetyFlags: SimulationSafetyFlags;
  conservativeNote: string;
}

export interface SimulationClock {
  simulationId: string;
  status: string;
  timeUnit: string;
  startTime: number;
  currentTime: number;
  endTime: number;
  speedMultiplier: number;
  canUserAdvanceTime: boolean;
  canUserInjectDelay: boolean;
}

export interface SimulationPoint {
  id: string;
  label: string;
  x: number;
  y: number;
}

export interface SimulationTechnician extends SimulationPoint {
  status: string;
  currentTaskId: string;
  routeId: string;
  delayMinutes: number;
}

export interface SimulationTask extends SimulationPoint {
  status: string;
  plannedStart: number;
  plannedEnd: number;
  actualStart: number | null;
  actualEnd: number | null;
  priority: string;
}

export interface SimulationRoute {
  id: string;
  technicianId: string;
  taskSequence: string[];
  status: string;
  totalDelayMinutes: number;
}

export interface SimulationMapState {
  coordinateSystem: string;
  depots: SimulationPoint[];
  technicians: SimulationTechnician[];
  tasks: SimulationTask[];
  routes: SimulationRoute[];
}

export interface SimulationTimelineEvent {
  time: number;
  type: string;
  label: string;
  affectedEntityId: string;
  delayMinutes: number;
}

export interface SimulationCandidatePolicy {
  id: string;
  label: string;
  executionEnabled: boolean;
}

export interface SimulationReplanningDecision {
  status: string;
  trigger: string;
  triggerTime: number;
  affectedRouteId: string;
  affectedTechnicianId: string;
  primaryDelayType: string;
  delayPropagationDetected: boolean;
  candidatePolicies: SimulationCandidatePolicy[];
  decisionFields: string[];
}

export interface SimulationStateSampleSnapshot {
  readOnly: boolean;
  available: boolean;
  artifactPath: string;
  executionEnabled: boolean;
  writeOperationsSupported: boolean;
  browserTriggeredExecutionEnabled: boolean;
  arbitraryCommandExecutionAllowed: boolean;
  schema: string;
  version: string;
  purpose: string;
  clock: SimulationClock;
  map: SimulationMapState;
  timeline: SimulationTimelineEvent[];
  replanningDecision: SimulationReplanningDecision;
  primaryDissertationScope: string[];
  futurePlatformPerturbations: string[];
  safetyNotes: string[];
}

export interface PlatformSnapshot {
  health: ApiHealth;
  status: PlatformStatus;
  reports: PlatformReport[];
  experimentalDesign: ExperimentalDesignSummary;
  researchMethod: ResearchMethodSnapshot;
  warnings: string[];
  apiBaseUrl: string;
}

export interface DashboardViewState {
  loading: boolean;
  error: string | null;
  snapshot: PlatformSnapshot | null;
  reload: () => void;
}

export function formatToken(value: string): string {
  return value.replace(/_/g, " ");
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}