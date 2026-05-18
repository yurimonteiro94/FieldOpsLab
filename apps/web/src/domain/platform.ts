export type ScientificStatus =
  | "diagnostic_only_with_methodological_warnings"
  | "experimental_design"
  | "validated";

export type EngineeringStatus =
  | "passed_current_structural_quality_gate"
  | "needs_attention"
  | "unknown";

export type ReportCategory =
  | "engineering"
  | "diagnostic"
  | "scientific_validation"
  | "experimental_design";

export interface PlatformHealth {
  service: "fieldops_lab_web";
  status: "ok";
  mode: "read_only_dashboard";
  readOnly: true;
  allowsArbitraryCommandExecution: false;
}

export interface PlatformStatus {
  completionPercent: number;
  engineeringStatus: EngineeringStatus;
  scientificStatus: ScientificStatus;
  scientificValidityProven: boolean;
  conservativeNote: string;
}

export interface ReportArtifact {
  id: string;
  title: string;
  category: ReportCategory;
  path: string;
  qualityCheckPath?: string;
  exists: boolean;
  passed?: boolean;
  warningCount?: number;
  problemCount?: number;
}

export interface ExperimentalDesignSummary {
  experimentCount: number;
  scenarioCount: number;
  replicationCount: number;
  reproducibleFromExplicitFactors: boolean;
}

export interface DashboardSnapshot {
  health: PlatformHealth;
  status: PlatformStatus;
  reports: ReportArtifact[];
  experimentalDesign: ExperimentalDesignSummary;
  safetyRules: string[];
}