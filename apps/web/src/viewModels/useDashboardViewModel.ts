import { useCallback, useEffect, useMemo, useState } from "react";
import type { DashboardViewState, PlatformSnapshot } from "../domain/platform";
import {
  ReadOnlyPlatformApi,
  createReadOnlyPlatformApi,
} from "../services/readOnlyPlatformApi";

interface InternalState {
  loading: boolean;
  error: string | null;
  snapshot: PlatformSnapshot | null;
}

export function useDashboardViewModel(api?: ReadOnlyPlatformApi): DashboardViewState {
  const client = useMemo(() => api ?? createReadOnlyPlatformApi(), [api]);

  const [state, setState] = useState<InternalState>({
    loading: true,
    error: null,
    snapshot: null,
  });

  const load = useCallback(() => {
    setState((current) => ({
      ...current,
      loading: true,
      error: null,
    }));

    void client
      .getSnapshot()
      .then((snapshot) => {
        setState({
          loading: false,
          error: null,
          snapshot,
        });
      })
      .catch((error: unknown) => {
        const message =
          error instanceof Error
            ? error.message
            : "Unknown API communication error.";

        setState({
          loading: false,
          error: message,
          snapshot: null,
        });
      });
  }, [client]);

  useEffect(() => {
    load();
  }, [load]);

  return {
    loading: state.loading,
    error: state.error,
    snapshot: state.snapshot,
    reload: load,
  };
}