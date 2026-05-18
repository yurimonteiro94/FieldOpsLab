export type EngineeringStatus = "passed_current_structural_quality_gate";
export type ScientificStatus = "diagnostic_only_with_methodological_warnings";
export type PlatformDataSource = "static_fallback" | "local_http_api";

export type ReportCategory =
  | "engineering"
  | "scientific_validation"
  | "experimental_design"
  | "diagnostic"
  | "quality";

export interface PlatformStatus {
  engineeringStatus: EngineeringStatus;
  scientificStatus: ScientificStatus;
  structuralChecksPassed: boolean;
  readOnly: boolean;
  executionSupported: boolean;
  arbitraryCommandExecutionAllowed: boolean;
}

export interface PlatformMetric {
  label: string;
  value: string;
  helperText: string;
}

export interface PlatformReport {
  id: string;
  title: string;
  category: ReportCategory;
  description: string;
  path: string;
  available: boolean;

  /*
   * Compatibility fields.
   *
   * Some UI components still use qualityCheckPath/passed, while newer service
   * adapters may use qualityPath. Keeping both names avoids fragile refactors
   * while the dashboard contract is still evolving.
   */
  qualityPath?: string;
  qualityCheckPath?: string;
  passed?: boolean;
}

export type ReportArtifact = PlatformReport;

export interface PlatformEvidenceWarning {
  id: string;
  severity: "info" | "warning";
  message: string;
}

export interface DashboardSnapshot {
  productCompletenessPercent: number;
  dataSource: PlatformDataSource;
  apiBaseUrl?: string;
  status: PlatformStatus;
  metrics: PlatformMetric[];
  reports: PlatformReport[];
  evidenceWarnings: PlatformEvidenceWarning[];
  conservativeNote: string;
}

export interface ReadOnlyPlatformApi {
  getDashboardSnapshot: () => Promise<DashboardSnapshot>;
}