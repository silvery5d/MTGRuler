import type { Concept, ConceptDetail, GraphData, PathResult, Stats } from "../types/index.js";

const BASE = "/api/v1";

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") url.searchParams.set(k, v);
    });
  }
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getConcepts(params?: { type?: string; chapter?: string; limit?: string; offset?: string }) {
    return get<Concept[]>(`${BASE}/concepts`, params);
  },

  getConcept(id: string) {
    return get<ConceptDetail>(`${BASE}/concepts/${encodeURIComponent(id)}`);
  },

  getNeighbors(id: string, depth = 1) {
    return get<Concept[]>(`${BASE}/concepts/${encodeURIComponent(id)}/neighbors`, { depth: String(depth) });
  },

  search(q: string, type?: string) {
    return get<Concept[]>(`${BASE}/search`, { q, ...(type ? { type } : {}) });
  },

  getGraph(params?: { chapter?: string; center?: string; depth?: string }) {
    return get<GraphData>(`${BASE}/graph`, params);
  },

  getPath(from: string, to: string) {
    return get<PathResult>(`${BASE}/path`, { from, to });
  },

  getStats() {
    return get<Stats>(`${BASE}/stats`);
  },
};
