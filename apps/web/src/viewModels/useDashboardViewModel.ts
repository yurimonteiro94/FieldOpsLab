import { useEffect, useMemo, useState } from "react";
import type { DashboardSnapshot, ReadOnlyPlatformApi } from "../domain/platform";
import { createReadOnlyPlatformApi } from "../services/readOnlyPlatformApi";

export interface DashboardViewModel {
  loading: boolean;
  errorMessage: string | null;
  snapshot: DashboardSnapshot | null;
  reload: () => void;
}

export function useDashboardViewModel(api?: ReadOnlyPlatformApi): DashboardViewModel {
  const defaultApi = useMemo(() => api ?? createReadOnlyPlatformApi(), [api]);
  const [reloadToken, setReloadToken] = useState(0);
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadSnapshot(): Promise<void> {
      setLoading(true);
      setErrorMessage(null);

      try {
        const nextSnapshot = await defaultApi.getDashboardSnapshot();

        if (!cancelled) {
          setSnapshot(nextSnapshot);
        }
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Unknown dashboard loading error.";
          setErrorMessage(message);
          setSnapshot(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadSnapshot();

    return () => {
      cancelled = true;
    };
  }, [defaultApi, reloadToken]);

  return {
    loading,
    errorMessage,
    snapshot,
    reload: () => setReloadToken((current) => current + 1),
  };
}