import type {
  DashboardSnapshot,
  ExperimentalDesignSummary,
  PlatformHealth,
  ReportArtifact
} from "../domain/platform";

export interface ReadOnlyPlatformApi {
  health(): Promise<PlatformHealth>;
  dashboard(): Promise<DashboardSnapshot>;
  reports(): Promise<ReportArtifact[]>;
  experimentalDesign(): Promise<ExperimentalDesignSummary>;
}

const healthSnapshot: PlatformHealth = {
  service: "fieldops_lab_web",
  status: "ok",
  mode: "read_only_dashboard",
  readOnly: true,
  allowsArbitraryCommandExecution: false
};

const reportsSnapshot: ReportArtifact[] = [
  {
    id: "project_status",
    title: "Project status report",
    category: "engineering",
    path: "analysis/reports/project_status_report.md",
    qualityCheckPath: "analysis/reports/project_status_quality_check.json",
    exists: true,
    passed: true,
    warningCount: 1,
    problemCount: 0
  },
  {
    id: "scientific_validation_plan",
    title: "Scientific validation plan",
    category: "scientific_validation",
    path: "analysis/reports/scientific_validation_plan.md",
    qualityCheckPath: "analysis/reports/scientific_validation_plan_quality_check.json",
    exists: true,
    passed: true,
    warningCount: 0,
    problemCount: 0
  },
  {
    id: "experimental_design_matrix",
    title: "Experimental design matrix",
    category: "experimental_design",
    path: "analysis/reports/experimental_design_matrix.md",
    qualityCheckPath: "analysis/reports/experimental_design_matrix_quality_check.json",
    exists: true,
    passed: true,
    warningCount: 0,
    problemCount: 0
  }
];

const experimentalDesignSnapshot: ExperimentalDesignSummary = {
  experimentCount: 648,
  scenarioCount: 108,
  replicationCount: 3,
  reproducibleFromExplicitFactors: true
};

const dashboardSnapshot: DashboardSnapshot = {
  health: healthSnapshot,
  status: {
    completionPercent: 39,
    engineeringStatus: "passed_current_structural_quality_gate",
    scientificStatus: "diagnostic_only_with_methodological_warnings",
    scientificValidityProven: false,
    conservativeNote:
      "The current platform does not prove scientific validity. It exposes engineering status, diagnostic reports, and a planned experimental design."
  },
  reports: reportsSnapshot,
  experimentalDesign: experimentalDesignSnapshot,
  safetyRules: [
    "The web dashboard is read-only in this stage.",
    "No arbitrary command execution is exposed.",
    "Diagnostic reports must not be presented as scientific proof.",
    "Backend execution will require an explicit allowlist before being exposed."
  ]
};

export function createStaticReadOnlyPlatformApi(): ReadOnlyPlatformApi {
  return {
    async health(): Promise<PlatformHealth> {
      return healthSnapshot;
    },

    async dashboard(): Promise<DashboardSnapshot> {
      return dashboardSnapshot;
    },

    async reports(): Promise<ReportArtifact[]> {
      return reportsSnapshot;
    },

    async experimentalDesign(): Promise<ExperimentalDesignSummary> {
      return experimentalDesignSnapshot;
    }
  };
}