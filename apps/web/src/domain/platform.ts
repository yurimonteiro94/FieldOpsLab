export type PageId = "dashboard" | "reports" | "scientific-validation";

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
  qualityPath: string;
  available: boolean;
  loaded: boolean;
  qualityPassed: boolean | null;
}

export interface ExperimentalDesignSummary {
  experimentCount: number;
  scenarioCount: number;
  replicationCount: number;
  reproducibleFromExplicitFactors: boolean;
}

export interface PlatformSnapshot {
  health: ApiHealth;
  status: PlatformStatus;
  reports: PlatformReport[];
  experimentalDesign: ExperimentalDesignSummary;
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