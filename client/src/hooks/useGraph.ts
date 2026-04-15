import { useState, useCallback } from "react";
import type { GraphData, ConceptDetail, PathResult, ViewMode } from "../types/index.js";
import { NODE_COLORS, COMPLEXITY_COLORS } from "../styles/cytoscape.js";
import { api } from "../services/api.js";

export type ColorMode = "type" | "complexity";

export interface GraphState {
  graphData: GraphData | null;
  selectedConcept: ConceptDetail | null;
  pathResult: PathResult | null;
  loading: boolean;
  error: string | null;
  viewMode: ViewMode;
  filters: { chapter?: string; type?: string };
  colorMode: ColorMode;
}

export function useGraph() {
  const [state, setState] = useState<GraphState>({
    graphData: null,
    selectedConcept: null,
    pathResult: null,
    loading: false,
    error: null,
    viewMode: "graph",
    filters: {},
    colorMode: "type",
  });

  const setLoading = (loading: boolean) => setState((s) => ({ ...s, loading }));
  const setError = (error: string | null) => setState((s) => ({ ...s, error, loading: false }));

  const loadGraph = useCallback(async (params?: { chapter?: string; center?: string; depth?: string }) => {
    setLoading(true);
    try {
      const graphData = await api.getGraph(params);
      setState((s) => ({ ...s, graphData, loading: false, error: null }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load graph");
    }
  }, []);

  const selectConcept = useCallback(async (id: string) => {
    try {
      const detail = await api.getConcept(id);
      setState((s) => ({ ...s, selectedConcept: detail }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load concept");
    }
  }, []);

  const clearSelection = useCallback(() => {
    setState((s) => ({ ...s, selectedConcept: null }));
  }, []);

  const findPath = useCallback(async (from: string, to: string) => {
    setLoading(true);
    try {
      const pathResult = await api.getPath(from, to);
      setState((s) => ({ ...s, pathResult, loading: false }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "No path found");
    }
  }, []);

  const clearPath = useCallback(() => {
    setState((s) => ({ ...s, pathResult: null }));
  }, []);

  const setViewMode = useCallback((viewMode: ViewMode) => {
    setState((s) => ({ ...s, viewMode }));
  }, []);

  const setFilters = useCallback((filters: { chapter?: string; type?: string }) => {
    setState((s) => ({ ...s, filters }));
  }, []);

  const setColorMode = useCallback((colorMode: ColorMode) => {
    setState((s) => ({ ...s, colorMode }));
  }, []);

  // Convert GraphData to Cytoscape elements
  const cytoscapeElements = state.graphData
    ? [
        ...state.graphData.nodes.map((n) => {
          const color =
            state.colorMode === "complexity"
              ? COMPLEXITY_COLORS[Math.max(0, Math.min(4, (n.complexity ?? 1) - 1))]
              : NODE_COLORS[n.type] || "#6b7280";
          const size =
            state.colorMode === "complexity"
              ? 12 + (n.complexity ?? 2) * 5
              : 8 + (n.complexity ?? 2) * 3;
          return {
            data: {
              id: n.id,
              label: n.name_cn || n.name_en,
              color,
              size,
              nodeType: n.type,
            },
          };
        }),
        ...state.graphData.edges.map((e) => ({
          data: {
            id: `${e.source}-${e.target}-${e.type}`,
            source: e.source,
            target: e.target,
            label: e.type,
            color: "#64748b",
          },
        })),
      ]
    : [];

  return {
    ...state,
    cytoscapeElements,
    loadGraph,
    selectConcept,
    clearSelection,
    findPath,
    clearPath,
    setViewMode,
    setFilters,
    setColorMode,
  };
}
