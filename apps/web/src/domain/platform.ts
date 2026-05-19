export type PageId =
  | "dashboard"
  | "simulation-workspace"
  | "reports"
  | "campaign-diagnostics"
  | "experimental-design"
  | "api-safety"
  | "scientific-validation"
  | "research-method";

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

export interface ReportResource<TData = Record<string, unknown>> {
  path: string;
  exists: boolean;
  loaded: boolean;
  data: TData | null;
  text: string;
  error: string;
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
  metadata: {
    artifactPath: string;
    markdownPath: string;
    qualityPath: string;
    qualityPassed: boolean | null;
  };
  artifact: ReportResource<Record<string, unknown>>;
  markdown: ReportResource;
  qualityCheck: ReportResource<Record<string, unknown>>;
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