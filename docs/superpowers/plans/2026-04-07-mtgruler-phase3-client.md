# MTGRuler Phase 3: Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a React + Cytoscape.js interactive frontend that visualizes the MTG rules knowledge graph with search, filtering, path queries, detail panels, and designer views.

**Architecture:** Vite + React + TypeScript SPA. Cytoscape.js for graph rendering. API calls to the Express backend. Component-driven with hooks for data fetching and state management.

**Tech Stack:** React 18, TypeScript, Vite, Cytoscape.js, react-cytoscapejs, Tailwind CSS

**Spec:** `docs/superpowers/specs/2026-04-07-mtgruler-knowledge-graph-design.md`
**Depends on:** Phase 2 (server running on localhost:3001)

---

## File Structure

```
client/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── index.html
├── src/
│   ├── main.tsx               # App entry
│   ├── App.tsx                # Layout shell
│   ├── types/
│   │   └── index.ts           # Shared types (mirror server types)
│   ├── services/
│   │   └── api.ts             # API client
│   ├── hooks/
│   │   ├── useGraph.ts        # Graph data fetching & state
│   │   └── useSearch.ts       # Search logic
│   ├── components/
│   │   ├── GraphView.tsx      # Cytoscape graph canvas
│   │   ├── SearchBar.tsx      # Search input + filter dropdowns
│   │   ├── DetailPanel.tsx    # Right sidebar concept detail
│   │   ├── PathQuery.tsx      # Path query mode UI
│   │   ├── StatusBar.tsx      # Bottom status bar
│   │   ├── ViewSwitcher.tsx   # View mode dropdown
│   │   └── DesignerView/
│   │       ├── DependencyGraph.tsx
│   │       ├── HeatMap.tsx
│   │       ├── ChapterOverview.tsx
│   │       └── InteractionMatrix.tsx
│   └── styles/
│       └── cytoscape.ts       # Cytoscape style definitions
└── tests/
    └── api.test.ts
```

---

### Task 1: Client Project Setup

**Files:**
- Create: `client/package.json`, `client/vite.config.ts`, `client/tsconfig.json`, `client/tailwind.config.js`, `client/index.html`, `client/src/main.tsx`

- [ ] **Step 1: Scaffold with Vite**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler
npm create vite@latest client -- --template react-ts
cd client
```

- [ ] **Step 2: Install dependencies**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/client
npm install cytoscape react-cytoscapejs
npm install -D @types/cytoscape tailwindcss @tailwindcss/vite
```

- [ ] **Step 3: Configure Tailwind in vite.config.ts**

```typescript
// client/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:3001",
    },
  },
});
```

- [ ] **Step 4: Add Tailwind import to CSS**

Replace `client/src/index.css` with:

```css
@import "tailwindcss";
```

- [ ] **Step 5: Create shared types**

```typescript
// client/src/types/index.ts

export interface Concept {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  rule_ref: string | null;
  definition_en: string | null;
  definition_cn: string | null;
  chapter: string | null;
  complexity: number | null;
  design_notes: string | null;
}

export interface Relation {
  source_id: string;
  target_id: string;
  type: string;
  rule_ref: string | null;
  description: string | null;
}

export interface RuleText {
  rule_ref: string;
  text_en: string | null;
  text_cn: string | null;
  parent_concept_id: string | null;
}

export interface GraphNode {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  complexity: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ConceptDetail {
  concept: Concept;
  rule_texts: RuleText[];
  related: Concept[];
}

export interface PathResult {
  nodes: Concept[];
  edges: { source: string; target: string; type: string }[];
}

export interface Stats {
  totals: { concepts: number; relations: number; rule_texts: number };
  concepts_by_type: { type: string; count: number }[];
  concepts_by_chapter: { chapter: string; count: number }[];
  concepts_by_complexity: { complexity: number; count: number }[];
  relations_by_type: { type: string; count: number }[];
}

export type ViewMode = "graph" | "dependency" | "heatmap" | "chapter-overview" | "interaction-matrix";

export type NodeType = "Chapter" | "Concept" | "Zone" | "CardType" | "Phase" | "Step" | "Keyword" | "Action" | "MechanicPattern";
```

- [ ] **Step 6: Verify it builds**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/client
npm run build
```
Expected: Build succeeds

- [ ] **Step 7: Commit**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler
echo "client/node_modules/" >> .gitignore
echo "client/dist/" >> .gitignore
git add client/ .gitignore
git commit -m "feat(client): scaffold React + Vite + Tailwind + Cytoscape project"
```

---

### Task 2: API Service

**Files:**
- Create: `client/src/services/api.ts`

- [ ] **Step 1: Implement API client**

```typescript
// client/src/services/api.ts
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
```

- [ ] **Step 2: Commit**

```bash
git add client/src/services/api.ts client/src/types/index.ts
git commit -m "feat(client): add API service layer"
```

---

### Task 3: Cytoscape Style Definitions

**Files:**
- Create: `client/src/styles/cytoscape.ts`

- [ ] **Step 1: Define node and edge styles**

```typescript
// client/src/styles/cytoscape.ts
import type { Stylesheet } from "cytoscape";

// Color mapping for node types
export const NODE_COLORS: Record<string, string> = {
  Chapter: "#6366f1",        // indigo
  Concept: "#8b5cf6",        // violet
  Zone: "#06b6d4",           // cyan
  CardType: "#f59e0b",       // amber
  Phase: "#10b981",          // emerald
  Step: "#34d399",           // emerald light
  Keyword: "#ef4444",        // red
  Action: "#f97316",         // orange
  MechanicPattern: "#ec4899", // pink
};

// Complexity-based colors for heatmap view
export const COMPLEXITY_COLORS = [
  "#22c55e", // 1 - green
  "#84cc16", // 2 - lime
  "#eab308", // 3 - yellow
  "#f97316", // 4 - orange
  "#ef4444", // 5 - red
];

export const EDGE_COLORS: Record<string, string> = {
  CONTAINS: "#94a3b8",
  DEPENDS_ON: "#f59e0b",
  REFERENCES: "#8b5cf6",
  OCCURS_IN: "#10b981",
  MODIFIES: "#ef4444",
  INTERACTS_WITH: "#06b6d4",
  MOVES_TO: "#f97316",
  PATTERN_OF: "#ec4899",
};

export const defaultStylesheet: Stylesheet[] = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "text-valign": "center",
      "text-halign": "center",
      "background-color": "data(color)",
      color: "#fff",
      "text-outline-color": "data(color)",
      "text-outline-width": 2,
      "font-size": 12,
      width: "data(size)",
      height: "data(size)",
    },
  },
  {
    selector: "node:selected",
    style: {
      "border-width": 3,
      "border-color": "#fff",
    },
  },
  {
    selector: "node.highlighted",
    style: {
      "border-width": 3,
      "border-color": "#fbbf24",
    },
  },
  {
    selector: "node.dimmed",
    style: {
      opacity: 0.3,
    },
  },
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": "data(color)",
      "target-arrow-color": "data(color)",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      "font-size": 10,
      "text-rotation": "autorotate",
      opacity: 0.7,
    },
  },
  {
    selector: "edge.highlighted",
    style: {
      width: 4,
      opacity: 1,
    },
  },
  {
    selector: "edge.dimmed",
    style: {
      opacity: 0.15,
    },
  },
];
```

- [ ] **Step 2: Commit**

```bash
git add client/src/styles/cytoscape.ts
git commit -m "feat(client): add Cytoscape style definitions with color mappings"
```

---

### Task 4: useGraph Hook

**Files:**
- Create: `client/src/hooks/useGraph.ts`

- [ ] **Step 1: Implement the hook**

```typescript
// client/src/hooks/useGraph.ts
import { useState, useCallback } from "react";
import type { GraphData, ConceptDetail, PathResult, ViewMode } from "../types/index.js";
import { NODE_COLORS } from "../styles/cytoscape.js";
import { api } from "../services/api.js";

export interface GraphState {
  graphData: GraphData | null;
  selectedConcept: ConceptDetail | null;
  pathResult: PathResult | null;
  loading: boolean;
  error: string | null;
  viewMode: ViewMode;
  filters: { chapter?: string; type?: string };
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

  // Convert GraphData to Cytoscape elements
  const cytoscapeElements = state.graphData
    ? [
        ...state.graphData.nodes.map((n) => ({
          data: {
            id: n.id,
            label: n.name_cn || n.name_en,
            color: NODE_COLORS[n.type] || "#6b7280",
            size: 20 + (n.complexity ?? 2) * 8,
            nodeType: n.type,
          },
        })),
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
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/hooks/useGraph.ts
git commit -m "feat(client): add useGraph hook for graph state management"
```

---

### Task 5: useSearch Hook

**Files:**
- Create: `client/src/hooks/useSearch.ts`

- [ ] **Step 1: Implement the hook**

```typescript
// client/src/hooks/useSearch.ts
import { useState, useCallback, useRef } from "react";
import type { Concept } from "../types/index.js";
import { api } from "../services/api.js";

export function useSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Concept[]>([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  const search = useCallback(async (q: string, type?: string) => {
    setQuery(q);

    if (!q.trim()) {
      setResults([]);
      return;
    }

    // Debounce: wait 300ms after last keystroke
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await api.search(q, type);
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, []);

  const clear = useCallback(() => {
    setQuery("");
    setResults([]);
  }, []);

  return { query, results, loading, search, clear };
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/hooks/useSearch.ts
git commit -m "feat(client): add useSearch hook with debounce"
```

---

### Task 6: GraphView Component

**Files:**
- Create: `client/src/components/GraphView.tsx`

- [ ] **Step 1: Implement GraphView**

```tsx
// client/src/components/GraphView.tsx
import { useRef, useCallback } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import { defaultStylesheet } from "../styles/cytoscape.js";

interface GraphViewProps {
  elements: cytoscape.ElementDefinition[];
  onNodeClick: (nodeId: string) => void;
  highlightedNodes?: Set<string>;
  highlightedEdges?: Set<string>;
}

export function GraphView({ elements, onNodeClick, highlightedNodes, highlightedEdges }: GraphViewProps) {
  const cyRef = useRef<cytoscape.Core | null>(null);

  const handleCy = useCallback(
    (cy: cytoscape.Core) => {
      cyRef.current = cy;

      // Remove old listeners
      cy.removeAllListeners();

      // Click handler
      cy.on("tap", "node", (evt) => {
        const nodeId = evt.target.id();
        onNodeClick(nodeId);
      });

      // Double-click to center and zoom
      cy.on("dbltap", "node", (evt) => {
        const node = evt.target;
        cy.animate({
          center: { eles: node },
          zoom: cy.zoom() * 1.5,
        });
      });

      // Apply highlight classes
      if (highlightedNodes || highlightedEdges) {
        cy.elements().addClass("dimmed");
        if (highlightedNodes) {
          highlightedNodes.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
        }
        if (highlightedEdges) {
          highlightedEdges.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
        }
      } else {
        cy.elements().removeClass("dimmed highlighted");
      }

      // Layout
      cy.layout({
        name: "cose",
        animate: true,
        animationDuration: 500,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 100,
        padding: 50,
      }).run();
    },
    [onNodeClick, highlightedNodes, highlightedEdges],
  );

  return (
    <div className="flex-1 relative">
      {elements.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          Loading graph...
        </div>
      ) : (
        <CytoscapeComponent
          elements={elements}
          stylesheet={defaultStylesheet}
          cy={handleCy}
          className="w-full h-full"
          style={{ width: "100%", height: "100%" }}
        />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/components/GraphView.tsx
git commit -m "feat(client): add Cytoscape GraphView component"
```

---

### Task 7: SearchBar Component

**Files:**
- Create: `client/src/components/SearchBar.tsx`

- [ ] **Step 1: Implement SearchBar**

```tsx
// client/src/components/SearchBar.tsx
import type { Concept, NodeType } from "../types/index.js";

const NODE_TYPES: NodeType[] = [
  "Chapter", "Concept", "Zone", "CardType", "Phase", "Step", "Keyword", "Action", "MechanicPattern",
];

const CHAPTERS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];

interface SearchBarProps {
  query: string;
  results: Concept[];
  loading: boolean;
  onSearch: (q: string, type?: string) => void;
  onClear: () => void;
  onResultClick: (conceptId: string) => void;
  onChapterFilter: (chapter?: string) => void;
  onTypeFilter: (type?: string) => void;
}

export function SearchBar({
  query,
  results,
  loading,
  onSearch,
  onClear,
  onResultClick,
  onChapterFilter,
  onTypeFilter,
}: SearchBarProps) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-900 border-b border-gray-700">
      {/* Search input */}
      <div className="relative flex-1 max-w-md">
        <input
          type="text"
          value={query}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search concepts (EN/中文)..."
          className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
        />
        {query && (
          <button
            onClick={onClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            ×
          </button>
        )}
        {/* Dropdown results */}
        {results.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto z-50">
            {results.map((c) => (
              <button
                key={c.id}
                onClick={() => {
                  onResultClick(c.id);
                  onClear();
                }}
                className="w-full text-left px-3 py-2 hover:bg-gray-700 text-sm"
              >
                <span className="text-white">{c.name_cn}</span>
                <span className="text-gray-400 ml-2">{c.name_en}</span>
                <span className="text-gray-500 ml-2 text-xs">[{c.type}]</span>
              </button>
            ))}
          </div>
        )}
        {loading && (
          <div className="absolute right-8 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
            ...
          </div>
        )}
      </div>

      {/* Chapter filter */}
      <select
        onChange={(e) => onChapterFilter(e.target.value || undefined)}
        className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
      >
        <option value="">All Chapters</option>
        {CHAPTERS.map((ch) => (
          <option key={ch} value={ch}>Chapter {ch}</option>
        ))}
      </select>

      {/* Type filter */}
      <select
        onChange={(e) => onTypeFilter(e.target.value || undefined)}
        className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
      >
        <option value="">All Types</option>
        {NODE_TYPES.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/components/SearchBar.tsx
git commit -m "feat(client): add SearchBar with filters and dropdown results"
```

---

### Task 8: DetailPanel Component

**Files:**
- Create: `client/src/components/DetailPanel.tsx`

- [ ] **Step 1: Implement DetailPanel**

```tsx
// client/src/components/DetailPanel.tsx
import type { ConceptDetail } from "../types/index.js";
import { NODE_COLORS } from "../styles/cytoscape.js";

interface DetailPanelProps {
  detail: ConceptDetail | null;
  onClose: () => void;
  onConceptClick: (id: string) => void;
}

export function DetailPanel({ detail, onClose, onConceptClick }: DetailPanelProps) {
  if (!detail) return null;

  const { concept, rule_texts, related } = detail;
  const color = NODE_COLORS[concept.type] || "#6b7280";

  return (
    <div className="w-80 bg-gray-900 border-l border-gray-700 overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <span
            className="px-2 py-1 rounded text-xs font-medium text-white"
            style={{ backgroundColor: color }}
          >
            {concept.type}
          </span>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-lg">×</button>
        </div>
        <h2 className="text-xl font-bold text-white">{concept.name_cn}</h2>
        <h3 className="text-sm text-gray-400">{concept.name_en}</h3>
        {concept.rule_ref && (
          <p className="text-xs text-gray-500 mt-1">Rule {concept.rule_ref}</p>
        )}
      </div>

      {/* Definition */}
      <div className="p-4 border-b border-gray-700">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Definition</h4>
        {concept.definition_cn && (
          <p className="text-sm text-gray-200 mb-2">{concept.definition_cn}</p>
        )}
        {concept.definition_en && (
          <p className="text-sm text-gray-400 italic">{concept.definition_en}</p>
        )}
      </div>

      {/* Complexity & Design Notes */}
      {(concept.complexity || concept.design_notes) && (
        <div className="p-4 border-b border-gray-700">
          {concept.complexity && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm text-gray-400">Complexity:</span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor: i <= concept.complexity! ? color : "#374151",
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          {concept.design_notes && (
            <p className="text-sm text-gray-300">{concept.design_notes}</p>
          )}
        </div>
      )}

      {/* Rule Texts */}
      {rule_texts.length > 0 && (
        <div className="p-4 border-b border-gray-700">
          <h4 className="text-sm font-medium text-gray-300 mb-2">
            Rule Texts ({rule_texts.length})
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {rule_texts.map((rt) => (
              <div key={rt.rule_ref} className="text-xs">
                <p className="text-indigo-400 font-mono">{rt.rule_ref}</p>
                {rt.text_cn && <p className="text-gray-200 mt-1">{rt.text_cn}</p>}
                {rt.text_en && <p className="text-gray-500 mt-1 italic">{rt.text_en}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Concepts */}
      {related.length > 0 && (
        <div className="p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-2">
            Related ({related.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {related.map((r) => (
              <button
                key={r.id}
                onClick={() => onConceptClick(r.id)}
                className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-white border border-gray-600"
              >
                {r.name_cn}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/components/DetailPanel.tsx
git commit -m "feat(client): add bilingual DetailPanel sidebar"
```

---

### Task 9: PathQuery Component

**Files:**
- Create: `client/src/components/PathQuery.tsx`

- [ ] **Step 1: Implement PathQuery**

```tsx
// client/src/components/PathQuery.tsx
import { useState } from "react";
import type { PathResult, Concept } from "../types/index.js";

interface PathQueryProps {
  active: boolean;
  pathResult: PathResult | null;
  onToggle: () => void;
  onFindPath: (from: string, to: string) => void;
  onClear: () => void;
  searchFn: (q: string) => Promise<Concept[]>;
}

export function PathQuery({ active, pathResult, onToggle, onFindPath, onClear, searchFn }: PathQueryProps) {
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [fromResults, setFromResults] = useState<Concept[]>([]);
  const [toResults, setToResults] = useState<Concept[]>([]);

  const handleFromSearch = async (q: string) => {
    setFrom(q);
    if (q.length >= 2) {
      const results = await searchFn(q);
      setFromResults(results.slice(0, 5));
    } else {
      setFromResults([]);
    }
  };

  const handleToSearch = async (q: string) => {
    setTo(q);
    if (q.length >= 2) {
      const results = await searchFn(q);
      setToResults(results.slice(0, 5));
    } else {
      setToResults([]);
    }
  };

  if (!active) {
    return (
      <button
        onClick={onToggle}
        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white"
      >
        Path Query
      </button>
    );
  }

  return (
    <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg">
      <span className="text-yellow-400 text-sm font-medium">Path:</span>

      {/* From input */}
      <div className="relative">
        <input
          value={from}
          onChange={(e) => handleFromSearch(e.target.value)}
          placeholder="From..."
          className="w-32 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
        />
        {fromResults.length > 0 && (
          <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-50">
            {fromResults.map((c) => (
              <button
                key={c.id}
                onClick={() => { setFromId(c.id); setFrom(c.name_cn); setFromResults([]); }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-700 text-xs text-white"
              >
                {c.name_cn}
              </button>
            ))}
          </div>
        )}
      </div>

      <span className="text-gray-400">→</span>

      {/* To input */}
      <div className="relative">
        <input
          value={to}
          onChange={(e) => handleToSearch(e.target.value)}
          placeholder="To..."
          className="w-32 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
        />
        {toResults.length > 0 && (
          <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-50">
            {toResults.map((c) => (
              <button
                key={c.id}
                onClick={() => { setToId(c.id); setTo(c.name_cn); setToResults([]); }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-700 text-xs text-white"
              >
                {c.name_cn}
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={() => { if (fromId && toId) onFindPath(fromId, toId); }}
        disabled={!fromId || !toId}
        className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-600 rounded text-sm text-white"
      >
        Find
      </button>

      {pathResult && (
        <span className="text-green-400 text-xs">
          {pathResult.nodes.length} nodes, {pathResult.edges.length} edges
        </span>
      )}

      <button
        onClick={() => { onClear(); onToggle(); setFrom(""); setTo(""); setFromId(""); setToId(""); }}
        className="text-gray-400 hover:text-white text-sm"
      >
        ×
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add client/src/components/PathQuery.tsx
git commit -m "feat(client): add PathQuery component with autocomplete"
```

---

### Task 10: StatusBar & ViewSwitcher

**Files:**
- Create: `client/src/components/StatusBar.tsx`
- Create: `client/src/components/ViewSwitcher.tsx`

- [ ] **Step 1: Implement StatusBar**

```tsx
// client/src/components/StatusBar.tsx

interface StatusBarProps {
  nodeCount: number;
  totalCount: number | null;
  loading: boolean;
  error: string | null;
  children?: React.ReactNode;
}

export function StatusBar({ nodeCount, totalCount, loading, error, children }: StatusBarProps) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-t border-gray-700 text-sm">
      <div className="flex items-center gap-4">
        {loading && <span className="text-yellow-400">Loading...</span>}
        {error && <span className="text-red-400">{error}</span>}
        {!loading && !error && (
          <span className="text-gray-400">
            Showing {nodeCount} concepts
            {totalCount !== null && ` / ${totalCount} total`}
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        {children}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Implement ViewSwitcher**

```tsx
// client/src/components/ViewSwitcher.tsx
import type { ViewMode } from "../types/index.js";

const VIEW_OPTIONS: { value: ViewMode; label: string }[] = [
  { value: "graph", label: "Graph View" },
  { value: "dependency", label: "Dependency Graph" },
  { value: "heatmap", label: "Complexity Heatmap" },
  { value: "chapter-overview", label: "Chapter Overview" },
  { value: "interaction-matrix", label: "Interaction Matrix" },
];

interface ViewSwitcherProps {
  current: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function ViewSwitcher({ current, onChange }: ViewSwitcherProps) {
  return (
    <select
      value={current}
      onChange={(e) => onChange(e.target.value as ViewMode)}
      className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
    >
      {VIEW_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add client/src/components/StatusBar.tsx client/src/components/ViewSwitcher.tsx
git commit -m "feat(client): add StatusBar and ViewSwitcher components"
```

---

### Task 11: Designer Views

**Files:**
- Create: `client/src/components/DesignerView/HeatMap.tsx`
- Create: `client/src/components/DesignerView/ChapterOverview.tsx`
- Create: `client/src/components/DesignerView/InteractionMatrix.tsx`
- Create: `client/src/components/DesignerView/DependencyGraph.tsx`

- [ ] **Step 1: Implement HeatMap**

The heatmap reuses GraphView but overrides node colors based on complexity.

```tsx
// client/src/components/DesignerView/HeatMap.tsx
import { GraphView } from "../GraphView.js";
import { COMPLEXITY_COLORS } from "../../styles/cytoscape.js";
import type { GraphData } from "../../types/index.js";

interface HeatMapProps {
  graphData: GraphData | null;
  onNodeClick: (id: string) => void;
}

export function HeatMap({ graphData, onNodeClick }: HeatMapProps) {
  if (!graphData) return null;

  // Override colors with complexity-based heatmap
  const elements = [
    ...graphData.nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.name_cn || n.name_en,
        color: COMPLEXITY_COLORS[(n.complexity ?? 1) - 1] || COMPLEXITY_COLORS[0],
        size: 20 + (n.complexity ?? 2) * 10,
        nodeType: n.type,
      },
    })),
    ...graphData.edges.map((e) => ({
      data: {
        id: `${e.source}-${e.target}-${e.type}`,
        source: e.source,
        target: e.target,
        label: e.type,
        color: "#475569",
      },
    })),
  ];

  return (
    <div className="flex-1 flex flex-col">
      {/* Legend */}
      <div className="flex items-center gap-4 p-2 bg-gray-800 border-b border-gray-700">
        <span className="text-gray-400 text-sm">Complexity:</span>
        {COMPLEXITY_COLORS.map((color, i) => (
          <div key={i} className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-300 text-xs">{i + 1}</span>
          </div>
        ))}
      </div>
      <GraphView elements={elements} onNodeClick={onNodeClick} />
    </div>
  );
}
```

- [ ] **Step 2: Implement ChapterOverview**

```tsx
// client/src/components/DesignerView/ChapterOverview.tsx
import { useState, useEffect } from "react";
import type { Stats } from "../../types/index.js";
import { api } from "../../services/api.js";

interface ChapterOverviewProps {
  onChapterClick: (chapter: string) => void;
}

const CHAPTER_NAMES: Record<string, string> = {
  "1": "Game Concepts / 游戏概念",
  "2": "Parts of a Card / 牌的组成",
  "3": "Card Types / 牌的类别",
  "4": "Zones / 区域",
  "5": "Turn Structure / 回合结构",
  "6": "Spells, Abilities, and Effects / 咒语、异能和效应",
  "7": "Additional Rules / 额外规则",
  "8": "Multiplayer Rules / 多人规则",
  "9": "Casual Variants / 休闲玩法",
};

export function ChapterOverview({ onChapterClick }: ChapterOverviewProps) {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.getStats().then(setStats);
  }, []);

  if (!stats) return <div className="flex-1 flex items-center justify-center text-gray-400">Loading stats...</div>;

  const maxCount = Math.max(...stats.concepts_by_chapter.map((c) => c.count));

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <h2 className="text-lg font-bold text-white mb-4">Chapter Overview</h2>
      <div className="space-y-3">
        {stats.concepts_by_chapter.map(({ chapter, count }) => (
          <button
            key={chapter}
            onClick={() => onChapterClick(chapter)}
            className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            <div className="flex justify-between items-center mb-1">
              <span className="text-white font-medium">
                Ch.{chapter}: {CHAPTER_NAMES[chapter] || `Chapter ${chapter}`}
              </span>
              <span className="text-gray-400 text-sm">{count} concepts</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full"
                style={{ width: `${(count / maxCount) * 100}%` }}
              />
            </div>
          </button>
        ))}
      </div>

      {/* Summary stats */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-indigo-400">{stats.totals.concepts}</p>
          <p className="text-gray-400 text-sm">Concepts</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-green-400">{stats.totals.relations}</p>
          <p className="text-gray-400 text-sm">Relations</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-amber-400">{stats.totals.rule_texts}</p>
          <p className="text-gray-400 text-sm">Rule Texts</p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Implement InteractionMatrix**

```tsx
// client/src/components/DesignerView/InteractionMatrix.tsx
import { useState, useEffect } from "react";
import type { Concept, Relation } from "../../types/index.js";
import { api } from "../../services/api.js";

interface InteractionMatrixProps {
  onConceptClick: (id: string) => void;
}

export function InteractionMatrix({ onConceptClick }: InteractionMatrixProps) {
  const [keywords, setKeywords] = useState<Concept[]>([]);
  const [interactions, setInteractions] = useState<Relation[]>([]);

  useEffect(() => {
    Promise.all([
      api.getConcepts({ type: "Keyword", limit: "50" }),
      api.getConcepts({ type: "Keyword", limit: "50", offset: "50" }),
    ]).then(([a, b]) => {
      setKeywords([...a, ...b]);
    });
    // Fetch INTERACTS_WITH relations
    fetch("/api/v1/relations?type=INTERACTS_WITH&limit=500")
      .then((r) => r.json())
      .then(setInteractions);
  }, []);

  // Build interaction map
  const interactionMap = new Map<string, Set<string>>();
  for (const r of interactions) {
    if (!interactionMap.has(r.source_id)) interactionMap.set(r.source_id, new Set());
    if (!interactionMap.has(r.target_id)) interactionMap.set(r.target_id, new Set());
    interactionMap.get(r.source_id)!.add(r.target_id);
    interactionMap.get(r.target_id)!.add(r.source_id);
  }

  // Only show keywords that have interactions
  const activeKeywords = keywords.filter(
    (k) => interactionMap.has(k.id) && interactionMap.get(k.id)!.size > 0,
  );

  if (activeKeywords.length === 0) {
    return <div className="flex-1 flex items-center justify-center text-gray-400">Loading interaction data...</div>;
  }

  return (
    <div className="flex-1 overflow-auto p-4">
      <h2 className="text-lg font-bold text-white mb-4">Keyword Interaction Matrix</h2>
      <div className="overflow-auto">
        <table className="border-collapse text-xs">
          <thead>
            <tr>
              <th className="p-1" />
              {activeKeywords.map((k) => (
                <th
                  key={k.id}
                  className="p-1 text-gray-300 font-normal -rotate-45 origin-left whitespace-nowrap cursor-pointer hover:text-white"
                  onClick={() => onConceptClick(k.id)}
                >
                  {k.name_cn}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {activeKeywords.map((row) => (
              <tr key={row.id}>
                <td
                  className="p-1 text-gray-300 whitespace-nowrap cursor-pointer hover:text-white"
                  onClick={() => onConceptClick(row.id)}
                >
                  {row.name_cn}
                </td>
                {activeKeywords.map((col) => {
                  const hasInteraction = interactionMap.get(row.id)?.has(col.id);
                  return (
                    <td
                      key={col.id}
                      className={`w-6 h-6 border border-gray-700 ${
                        row.id === col.id
                          ? "bg-gray-800"
                          : hasInteraction
                            ? "bg-cyan-600 cursor-pointer hover:bg-cyan-500"
                            : "bg-gray-900"
                      }`}
                    />
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Implement DependencyGraph**

```tsx
// client/src/components/DesignerView/DependencyGraph.tsx
import { useState } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { GraphData, Concept } from "../../types/index.js";
import { api } from "../../services/api.js";

interface DependencyGraphProps {
  onNodeClick: (id: string) => void;
}

export function DependencyGraph({ onNodeClick }: DependencyGraphProps) {
  const [centerQuery, setCenterQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Concept[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);

  const handleSearch = async (q: string) => {
    setCenterQuery(q);
    if (q.length >= 2) {
      const results = await api.search(q);
      setSuggestions(results.slice(0, 5));
    } else {
      setSuggestions([]);
    }
  };

  const handleSelect = async (concept: Concept) => {
    setCenterQuery(concept.name_cn);
    setSuggestions([]);
    const data = await api.getGraph({ center: concept.id, depth: "2" });
    setGraphData(data);
  };

  const elements = graphData
    ? [
        ...graphData.nodes.map((n) => ({
          data: {
            id: n.id,
            label: n.name_cn || n.name_en,
            color: NODE_COLORS[n.type] || "#6b7280",
            size: 20 + (n.complexity ?? 2) * 8,
            nodeType: n.type,
          },
        })),
        ...graphData.edges.map((e) => ({
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

  return (
    <div className="flex-1 flex flex-col">
      {/* Center concept selector */}
      <div className="p-3 bg-gray-800 border-b border-gray-700 flex items-center gap-2">
        <span className="text-gray-400 text-sm">Center:</span>
        <div className="relative">
          <input
            value={centerQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search for a concept..."
            className="w-64 px-3 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-50">
              {suggestions.map((c) => (
                <button
                  key={c.id}
                  onClick={() => handleSelect(c)}
                  className="block w-full text-left px-3 py-1 hover:bg-gray-700 text-xs text-white"
                >
                  {c.name_cn} <span className="text-gray-400">{c.name_en}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {elements.length > 0 ? (
        <GraphView elements={elements} onNodeClick={onNodeClick} />
      ) : (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          Select a concept to view its dependency graph
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add client/src/components/DesignerView/
git commit -m "feat(client): add designer views (heatmap, chapter overview, interaction matrix, dependency graph)"
```

---

### Task 12: App Shell & Integration

**Files:**
- Modify: `client/src/App.tsx`
- Modify: `client/src/main.tsx`

- [ ] **Step 1: Implement App.tsx**

```tsx
// client/src/App.tsx
import { useEffect, useMemo, useState, useCallback } from "react";
import { GraphView } from "./components/GraphView.js";
import { SearchBar } from "./components/SearchBar.js";
import { DetailPanel } from "./components/DetailPanel.js";
import { PathQuery } from "./components/PathQuery.js";
import { StatusBar } from "./components/StatusBar.js";
import { ViewSwitcher } from "./components/ViewSwitcher.js";
import { HeatMap } from "./components/DesignerView/HeatMap.js";
import { ChapterOverview } from "./components/DesignerView/ChapterOverview.js";
import { InteractionMatrix } from "./components/DesignerView/InteractionMatrix.js";
import { DependencyGraph } from "./components/DesignerView/DependencyGraph.js";
import { useGraph } from "./hooks/useGraph.js";
import { useSearch } from "./hooks/useSearch.js";
import { api } from "./services/api.js";
import type { Stats } from "./types/index.js";

export default function App() {
  const graph = useGraph();
  const search = useSearch();
  const [pathMode, setPathMode] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);

  // Load initial graph
  useEffect(() => {
    graph.loadGraph();
    api.getStats().then(setStats);
  }, []);

  // Reload graph when filters change
  useEffect(() => {
    const params: Record<string, string> = {};
    if (graph.filters.chapter) params.chapter = graph.filters.chapter;
    graph.loadGraph(params);
  }, [graph.filters.chapter]);

  // Handle node click: select concept and load details
  const handleNodeClick = useCallback((nodeId: string) => {
    graph.selectConcept(nodeId);
  }, [graph.selectConcept]);

  // Handle search result click: select and center on concept
  const handleSearchResultClick = useCallback((conceptId: string) => {
    graph.selectConcept(conceptId);
    graph.loadGraph({ center: conceptId, depth: "2" });
  }, [graph.selectConcept, graph.loadGraph]);

  // Handle chapter filter from chapter overview
  const handleChapterClick = useCallback((chapter: string) => {
    graph.setFilters({ ...graph.filters, chapter });
    graph.setViewMode("graph");
  }, [graph.setFilters, graph.setViewMode, graph.filters]);

  // Path search helper
  const searchForPath = useCallback(async (q: string) => {
    return api.search(q);
  }, []);

  // Compute path highlights
  const pathHighlightedNodes = useMemo(() => {
    if (!graph.pathResult) return undefined;
    return new Set(graph.pathResult.nodes.map((n) => n.id));
  }, [graph.pathResult]);

  const pathHighlightedEdges = useMemo(() => {
    if (!graph.pathResult) return undefined;
    return new Set(
      graph.pathResult.edges.map((e) => `${e.source}-${e.target}-${e.type}`),
    );
  }, [graph.pathResult]);

  // Render the active view
  const renderView = () => {
    switch (graph.viewMode) {
      case "heatmap":
        return <HeatMap graphData={graph.graphData} onNodeClick={handleNodeClick} />;
      case "chapter-overview":
        return <ChapterOverview onChapterClick={handleChapterClick} />;
      case "interaction-matrix":
        return <InteractionMatrix onConceptClick={handleNodeClick} />;
      case "dependency":
        return <DependencyGraph onNodeClick={handleNodeClick} />;
      default:
        return (
          <GraphView
            elements={graph.cytoscapeElements}
            onNodeClick={handleNodeClick}
            highlightedNodes={pathHighlightedNodes}
            highlightedEdges={pathHighlightedEdges}
          />
        );
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white">
      {/* Top bar: search + filters + view switcher */}
      <div className="flex items-center gap-2">
        <SearchBar
          query={search.query}
          results={search.results}
          loading={search.loading}
          onSearch={search.search}
          onClear={search.clear}
          onResultClick={handleSearchResultClick}
          onChapterFilter={(ch) => graph.setFilters({ ...graph.filters, chapter: ch })}
          onTypeFilter={(t) => graph.setFilters({ ...graph.filters, type: t })}
        />
        <div className="pr-3">
          <ViewSwitcher current={graph.viewMode} onChange={graph.setViewMode} />
        </div>
      </div>

      {/* Main content: graph + detail panel */}
      <div className="flex-1 flex overflow-hidden">
        {renderView()}
        <DetailPanel
          detail={graph.selectedConcept}
          onClose={graph.clearSelection}
          onConceptClick={handleNodeClick}
        />
      </div>

      {/* Bottom bar: status + path query */}
      <StatusBar
        nodeCount={graph.graphData?.nodes.length ?? 0}
        totalCount={stats?.totals.concepts ?? null}
        loading={graph.loading}
        error={graph.error}
      >
        <PathQuery
          active={pathMode}
          pathResult={graph.pathResult}
          onToggle={() => { setPathMode(!pathMode); graph.clearPath(); }}
          onFindPath={graph.findPath}
          onClear={graph.clearPath}
          searchFn={searchForPath}
        />
      </StatusBar>
    </div>
  );
}
```

- [ ] **Step 2: Update main.tsx**

```tsx
// client/src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.js";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 3: Verify it builds**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/client
npm run build
```
Expected: Build succeeds

- [ ] **Step 4: Test end-to-end**

Start both server and client:
```bash
# Terminal 1: start server
cd /Users/deosigner/Documents/claude/MTGRuler/server
npx tsx src/index.ts

# Terminal 2: start client
cd /Users/deosigner/Documents/claude/MTGRuler/client
npm run dev
```

Open http://localhost:5173 and verify:
- Graph renders with concept nodes
- Clicking a node opens the detail panel
- Search returns results
- Chapter/type filters reload the graph
- Designer views switch correctly

- [ ] **Step 5: Commit**

```bash
git add client/src/App.tsx client/src/main.tsx
git commit -m "feat(client): integrate all components into App shell"
```

---

## Completion

After all tasks, the client provides:
- Interactive Cytoscape.js graph visualization
- Bilingual search with fuzzy matching
- Chapter and type filtering
- Concept detail sidebar with rule texts
- Path query between concepts
- Designer views: dependency graph, complexity heatmap, chapter overview, interaction matrix

**The full MTGRuler application is now complete across all three phases.**
