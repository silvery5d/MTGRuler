import { useState, useCallback, useEffect } from "react";
import type { VersionInfo, MetricsRecord, SpikeRecord, GraphData, HistoryDiff } from "../../types/index.js";
import { api } from "../../services/api.js";

export type HistorySubView = "chart" | "slider" | "diff";

export interface HistoryState {
  versions: VersionInfo[];
  metrics: MetricsRecord[];
  spikes: SpikeRecord[];
  loading: boolean;
  error: string | null;
  selectedVersion: string | null;
  compareVersion: string | null;
  selectedGraph: GraphData | null;
  compareGraph: GraphData | null;
  diff: HistoryDiff | null;
  subView: HistorySubView;
}

export function useHistory() {
  const [state, setState] = useState<HistoryState>({
    versions: [],
    metrics: [],
    spikes: [],
    loading: false,
    error: null,
    selectedVersion: null,
    compareVersion: null,
    selectedGraph: null,
    compareGraph: null,
    diff: null,
    subView: "chart",
  });

  useEffect(() => {
    setState((s) => ({ ...s, loading: true }));
    Promise.all([
      api.getHistoryVersions(),
      api.getHistoryMetrics(),
      api.getHistorySpikes(),
    ])
      .then(([versions, metrics, spikes]) => {
        // Only versions that exist in metrics have DBs server-side
        const metricsSet = new Set(metrics.map((m) => m.set_code));
        const loadable = versions.filter((v) => metricsSet.has(v.set_code));
        const defaultVersion = loadable.length > 0
          ? loadable[loadable.length - 1].set_code
          : null;
        setState((s) => ({
          ...s,
          versions: loadable.length > 0 ? loadable : versions,
          metrics,
          spikes,
          loading: false,
          selectedVersion: defaultVersion,
        }));
      })
      .catch((e) => {
        setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to load history" }));
      });
  }, []);

  const selectVersion = useCallback(async (setCode: string) => {
    setState((s) => ({ ...s, selectedVersion: setCode, loading: true }));
    try {
      const graph = await api.getHistoryVersionGraph(setCode);
      setState((s) => ({ ...s, selectedGraph: graph, loading: false }));
    } catch (e) {
      setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to load version graph" }));
    }
  }, []);

  const compareVersions = useCallback(async (oldCode: string, newCode: string) => {
    setState((s) => ({ ...s, loading: true }));
    try {
      const [oldGraph, newGraph, diff] = await Promise.all([
        api.getHistoryVersionGraph(oldCode),
        api.getHistoryVersionGraph(newCode),
        api.getHistoryDiff(oldCode, newCode),
      ]);
      setState((s) => ({
        ...s,
        selectedVersion: newCode,
        compareVersion: oldCode,
        selectedGraph: newGraph,
        compareGraph: oldGraph,
        diff,
        loading: false,
        subView: "diff",
      }));
    } catch (e) {
      setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to compare versions" }));
    }
  }, []);

  const setSubView = useCallback((subView: HistorySubView) => {
    setState((s) => ({ ...s, subView }));
  }, []);

  return { ...state, selectVersion, compareVersions, setSubView };
}
