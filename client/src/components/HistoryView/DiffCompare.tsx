import { useMemo } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { GraphData, HistoryDiff } from "../../types/index.js";

interface DiffCompareProps {
  oldCode: string | null;
  newCode: string | null;
  oldGraph: GraphData | null;
  newGraph: GraphData | null;
  diff: HistoryDiff | null;
}

export function DiffCompare({ oldCode, newCode, oldGraph, newGraph, diff }: DiffCompareProps) {
  const addedIds = useMemo(() => new Set(diff?.added.map((c) => c.id) ?? []), [diff]);
  const removedIds = useMemo(() => new Set(diff?.removed.map((c) => c.id) ?? []), [diff]);

  if (!oldCode || !newCode) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        Click a spike marker on the chart to compare two versions
      </div>
    );
  }

  const buildElements = (graph: GraphData | null, side: "old" | "new") => {
    if (!graph) return [];
    return [
      ...graph.nodes.map((n) => {
        let color = NODE_COLORS[n.type] || "#6b7280";
        if (side === "new" && addedIds.has(n.id)) color = "#10b981";
        if (side === "old" && removedIds.has(n.id)) color = "#ef4444";
        return {
          data: {
            id: n.id,
            label: n.name_cn || n.name_en,
            color,
            size: 14 + (n.complexity ?? 2) * 5,
            nodeType: n.type,
          },
        };
      }),
      ...graph.edges.map((e) => ({
        data: {
          id: `${e.source}-${e.target}-${e.type}`,
          source: e.source,
          target: e.target,
          label: e.type,
          color: "#64748b",
        },
      })),
    ];
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 flex flex-col border-r border-gray-700">
          <div className="p-2 bg-gray-900 border-b border-gray-700 text-center text-sm text-white font-bold">
            {oldCode}
          </div>
          <GraphView elements={buildElements(oldGraph, "old")} onNodeClick={() => {}} />
        </div>
        <div className="flex-1 flex flex-col">
          <div className="p-2 bg-gray-900 border-b border-gray-700 text-center text-sm text-white font-bold">
            {newCode}
          </div>
          <GraphView elements={buildElements(newGraph, "new")} onNodeClick={() => {}} />
        </div>
      </div>

      {diff && (
        <div className="max-h-40 overflow-y-auto bg-gray-900 border-t border-gray-700 p-3 grid grid-cols-2 gap-3">
          <div>
            <h4 className="text-sm font-bold text-green-400 mb-1">+ Added ({diff.added.length})</h4>
            <div className="space-y-1 text-xs">
              {diff.added.slice(0, 20).map((c) => (
                <div key={c.id} className="text-gray-200">
                  <span className="text-green-400">+</span> {c.id} ({c.type})
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-bold text-red-400 mb-1">− Removed ({diff.removed.length})</h4>
            <div className="space-y-1 text-xs">
              {diff.removed.slice(0, 20).map((c) => (
                <div key={c.id} className="text-gray-200">
                  <span className="text-red-400">−</span> {c.id} ({c.type})
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
