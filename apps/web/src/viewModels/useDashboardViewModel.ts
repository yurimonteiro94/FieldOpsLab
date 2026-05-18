import { useEffect, useMemo, useState } from "react";
import type { DashboardSnapshot } from "../domain/platform";
import {
  createStaticReadOnlyPlatformApi,
  type ReadOnlyPlatformApi
} from "../services/readOnlyPlatformApi";

export type DashboardViewState =
  | {
      kind: "loading";
    }
  | {
      kind: "ready";
      snapshot: DashboardSnapshot;
      reportCount: number;
      passedReportCount: number;
      hasScientificProof: boolean;
    }
  | {
      kind: "error";
      message: string;
    };

export function useDashboardViewModel(
  api: ReadOnlyPlatformApi = createStaticReadOnlyPlatformApi()
): DashboardViewState {
  const stableApi = useMemo(() => api, [api]);
  const [state, setState] = useState<DashboardViewState>({ kind: "loading" });

  useEffect(() => {
    let active = true;

    stableApi
      .dashboard()
      .then((snapshot) => {
        if (!active) {
          return;
        }

        setState({
          kind: "ready",
          snapshot,
          reportCount: snapshot.reports.length,
          passedReportCount: snapshot.reports.filter((report) => report.passed).length,
          hasScientificProof: snapshot.status.scientificValidityProven
        });
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }

        const message =
          error instanceof Error
            ? error.message
            : "Unknown dashboard loading error.";

        setState({
          kind: "error",
          message
        });
      });

    return () => {
      active = false;
    };
  }, [stableApi]);

  return state;
}