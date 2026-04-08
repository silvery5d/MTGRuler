import type cytoscape from "cytoscape";

type Stylesheet = cytoscape.StylesheetStyle | cytoscape.StylesheetCSS;

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
