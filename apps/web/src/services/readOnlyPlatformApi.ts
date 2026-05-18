import type {
  DashboardSnapshot,
  PlatformMetric,
  PlatformReport,
  ReadOnlyPlatformApi,
} from "../domain/platform";

interface HealthPayload {
  read_only?: boolean;
  allows_arbitrary_command_execution?: boolean;
}

interface ProjectStatusPayload {
  report?: string;
  source?: {
    exists?: boolean;
    loaded?: boolean;
  };
  summary_metrics?: Record<string, string | number | boolean>;
  conservative_note?: string;
}

interface ReportsPayload {
  reports?: Array<{
    id?: string;
    title?: string;
    category?: string;
    description?: string;
    path?: string;
    quality_path?: string;
    available?: boolean;
  }>;
}

interface ExperimentalDesignPayload {
  summary?: {
    experiment_count?: number;
    scenario_count?: number;
    replication_count?: number;
    reproducible_from_explicit_factors?: boolean;
  };
}

const DEFAULT_CONSERVATIVE_NOTE =
  "This dashboard does not prove scientific validity. It separates structural engineering consistency from diagnostic evidence and pending scientific validation.";

function humanize(value: string): string {
  return value.split("_").join(" ");
}

function metric(label: string, value: string | number | boolean, helperText: string): PlatformMetric {
  return {
    label,
    value: String(value),
    helperText,
  };
}

function fallbackReports(): PlatformReport[] {
  return [
    {
      id: "project_status",
      title: "Project status",
      category: "engineering",
      description: "Current structural engineering and diagnostic status.",
      path: "analysis/reports/project_status_report.json",
      qualityPath: "analysis/reports/project_status_quality_check.json",
      available: true,
    },
    {
      id: "scientific_validation_plan",
      title: "Scientific validation plan",
      category: "scientific_validation",
      description: "Open scientific risks and validation actions.",
      path: "analysis/reports/scientific_validation_plan.json",
      qualityPath: "analysis/reports/scientific_validation_plan_quality_check.json",
      available: true,
    },
    {
      id: "experimental_design_matrix",
      title: "Experimental design matrix",
      category: "experimental_design",
      description: "Planned experiment matrix and reproducibility factors.",
      path: "analysis/reports/experimental_design_matrix.json",
      qualityPath: "analysis/reports/experimental_design_matrix_quality_check.json",
      available: true,
    },
  ];
}

function fallbackSnapshot(): DashboardSnapshot {
  return {
    productCompletenessPercent: 46,
    dataSource: "static_fallback",
    status: {
      engineeringStatus: "passed_current_structural_quality_gate",
      scientificStatus: "diagnostic_only_with_methodological_warnings",
      structuralChecksPassed: true,
      readOnly: true,
      executionSupported: false,
      arbitraryCommandExecutionAllowed: false,
    },
    metrics: [
      metric("Product completeness", "46%", "Complete application estimate, including web, API, hosting, Firebase, execution, and user readiness."),
      metric("Current API mode", "read only", "The current platform layer exposes reports but does not execute backend commands."),
      metric("Scientific maturity", "diagnostic only", "Current results are useful diagnostics, not final scientific proof."),
      metric("Execution safety", "no arbitrary commands", "Execution endpoints are intentionally absent at this stage."),
    ],
    reports: fallbackReports(),
    evidenceWarnings: [
      {
        id: "scientific_validity",
        severity: "warning",
        message: "The current platform does not prove scientific validity.",
      },
      {
        id: "execution_disabled",
        severity: "info",
        message: "Backend execution remains disabled until an explicit allowlist model is implemented.",
      },
    ],
    conservativeNote: DEFAULT_CONSERVATIVE_NOTE,
  };
}

function normalizeReports(payload: ReportsPayload): PlatformReport[] {
  const reports = payload.reports ?? [];

  if (reports.length === 0) {
    return fallbackReports();
  }

  return reports.map((report) => ({
    id: report.id ?? "unknown_report",
    title: report.title ?? humanize(report.id ?? "unknown report"),
    category: normalizeReportCategory(report.category),
    description: report.description ?? "Generated FieldOps Lab artifact.",
    path: report.path ?? "",
    qualityPath: report.quality_path,
    available: Boolean(report.available ?? true),
  }));
}

function normalizeReportCategory(category: string | undefined): PlatformReport["category"] {
  switch (category) {
    case "engineering":
    case "scientific_validation":
    case "experimental_design":
    case "diagnostic":
    case "quality":
      return category;
    default:
      return "diagnostic";
  }
}

async function getJson<TPayload>(baseUrl: string, path: string): Promise<TPayload> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed for ${path}: ${response.status}`);
  }

  return response.json() as Promise<TPayload>;
}

export class StaticReadOnlyPlatformApi implements ReadOnlyPlatformApi {
  async getDashboardSnapshot(): Promise<DashboardSnapshot> {
    return fallbackSnapshot();
  }
}

export class HttpReadOnlyPlatformApi implements ReadOnlyPlatformApi {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
  }

  async getDashboardSnapshot(): Promise<DashboardSnapshot> {
    const [health, projectStatus, reports, experimentalDesign] = await Promise.all([
      getJson<HealthPayload>(this.baseUrl, "/api/v1/health"),
      getJson<ProjectStatusPayload>(this.baseUrl, "/api/v1/project-status"),
      getJson<ReportsPayload>(this.baseUrl, "/api/v1/reports"),
      getJson<ExperimentalDesignPayload>(this.baseUrl, "/api/v1/experimental-design-matrix"),
    ]);

    const summaryMetrics = projectStatus.summary_metrics ?? {};
    const experimentalSummary = experimentalDesign.summary ?? {};

    return {
      productCompletenessPercent: 46,
      dataSource: "local_http_api",
      apiBaseUrl: this.baseUrl,
      status: {
        engineeringStatus: "passed_current_structural_quality_gate",
        scientificStatus: "diagnostic_only_with_methodological_warnings",
        structuralChecksPassed: Boolean(summaryMetrics.structural_all_required_checks_passed ?? true),
        readOnly: Boolean(health.read_only ?? true),
        executionSupported: false,
        arbitraryCommandExecutionAllowed: Boolean(health.allows_arbitrary_command_execution ?? false),
      },
      metrics: [
        metric("Product completeness", "46%", "Complete application estimate, including web, API, hosting, Firebase, execution, and user readiness."),
        metric("API source", this.baseUrl, "Dashboard data came from the local read-only HTTP API."),
        metric("Planned experiments", experimentalSummary.experiment_count ?? "unknown", "Experiment count exposed by the experimental design endpoint."),
        metric("Planned scenarios", experimentalSummary.scenario_count ?? "unknown", "Scenario count exposed by the experimental design endpoint."),
        metric("Replications", experimentalSummary.replication_count ?? "unknown", "Replication count exposed by the experimental design endpoint."),
        metric("Engineering status", humanize(String(summaryMetrics.engineering_status ?? "unknown")), "Status reported by the generated project status artifact."),
      ],
      reports: normalizeReports(reports),
      evidenceWarnings: [
        {
          id: "scientific_validity",
          severity: "warning",
          message: "The current platform does not prove scientific validity.",
        },
        {
          id: "read_only_api",
          severity: "info",
          message: "The dashboard is connected to the local read-only API and still does not expose execution endpoints.",
        },
      ],
      conservativeNote: projectStatus.conservative_note ?? DEFAULT_CONSERVATIVE_NOTE,
    };
  }
}

export function createReadOnlyPlatformApi(): ReadOnlyPlatformApi {
  const configuredBaseUrl = import.meta.env.VITE_FIELDOPS_API_BASE_URL;

  if (configuredBaseUrl !== undefined && configuredBaseUrl.trim().length > 0) {
    return new HttpReadOnlyPlatformApi(configuredBaseUrl);
  }

  return new StaticReadOnlyPlatformApi();
}