import type {
  ApiHealth,
  ExperimentalDesignSummary,
  PlatformReport,
  PlatformRoute,
  PlatformSnapshot,
  PlatformStatus,
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

function readBoolean(record: JsonRecord, key: string, fallback: boolean): boolean {
  const value = record[key];

  if (typeof value === "boolean") {
    return value;
  }

  return fallback;
}

function readOptionalBoolean(record: JsonRecord, keys: string[]): boolean | null {
  for (const key of keys) {
    const value = record[key];

    if (typeof value === "boolean") {
      return value;
    }
  }

  return null;
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

function titleFromId(id: string): string {
  return id
    .split("_")
    .filter((part) => part.length > 0)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function normalizeRoutes(value: unknown): PlatformRoute[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((item) => {
    const record = asRecord(item);

    return {
      method: readString(record, "method", "GET"),
      path: readString(record, "path", "/"),
      description: readString(record, "description", "Read-only route."),
    };
  });
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
    routes: normalizeRoutes(payload.routes),
    contractAvailable: readBoolean(contract, "available", false),
    contractPath: readString(
      contract,
      "path",
      "platform/contracts/fieldops_platform_contract.json",
    ),
  };
}

function normalizeProjectStatus(payload: JsonRecord): PlatformStatus {
  const summaryMetrics = asRecord(
    payload.summary_metrics ?? payload.summaryMetrics,
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
      payload,
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
      payload,
      ["engineering_status", "engineeringStatus"],
      "passed_current_structural_quality_gate",
    ),
  );

  const scientificStatus = readStringFromKeys(
    summaryMetrics,
    ["scientific_status", "scientificStatus"],
    readStringFromKeys(
      payload,
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
      payload,
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
      [
        "artifactPath",
        "artifact_path",
        "path",
        "report_path",
        "json_path",
        "markdown_path",
      ],
      "analysis/reports",
    ),
    qualityPath: readStringFromKeys(
      record,
      [
        "qualityPath",
        "quality_path",
        "qualityCheckPath",
        "quality_check_path",
      ],
      "",
    ),
    available: readBoolean(record, "available", readBoolean(record, "exists", true)),
    loaded: readBoolean(record, "loaded", true),
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

function normalizeExperimentalDesign(
  payload: JsonRecord,
): ExperimentalDesignSummary {
  const summary = asRecord(payload.summary);

  return {
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
    reproducibleFromExplicitFactors: readBoolean(
      summary,
      "reproducible_from_explicit_factors",
      false,
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

  async getExperimentalDesign(): Promise<ExperimentalDesignSummary> {
    const payload = await fetchJson(
      this.baseUrl,
      "/api/v1/experimental-design-matrix",
    );

    return normalizeExperimentalDesign(payload);
  }

  async getSnapshot(): Promise<PlatformSnapshot> {
    const [health, status, reports, experimentalDesign] = await Promise.all([
      this.getHealth(),
      this.getProjectStatus(),
      this.getReports(),
      this.getExperimentalDesign(),
    ]);

    const warnings = [
      status.conservativeNote,
      "Generated artifacts are engineering and diagnostic evidence, not final scientific validation.",
      "Backend execution remains intentionally unavailable from the web interface.",
    ];

    return {
      health,
      status,
      reports,
      experimentalDesign,
      warnings,
      apiBaseUrl: this.baseUrl,
    };
  }
}

export function createReadOnlyPlatformApi(
  baseUrl?: string,
): ReadOnlyPlatformApi {
  return new ReadOnlyPlatformApi(baseUrl);
}