import { useMemo, useState } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { GraphData, HistoryDiff, VersionInfo } from "../../types/index.js";

interface DiffCompareProps {
  versions: VersionInfo[];
  oldCode: string | null;
  newCode: string | null;
  oldGraph: GraphData | null;
  newGraph: GraphData | null;
  diff: HistoryDiff | null;
  loading: boolean;
  onCompare: (oldCode: string, newCode: string) => void;
}

export function DiffCompare({ versions, oldCode, newCode, oldGraph, newGraph, diff, loading, onCompare }: DiffCompareProps) {
  const addedIds = useMemo(() => new Set(diff?.added.map((c) => c.id) ?? []), [diff]);
  const removedIds = useMemo(() => new Set(diff?.removed.map((c) => c.id) ?? []), [diff]);

  const [draftOld, setDraftOld] = useState(oldCode || (versions[0]?.set_code ?? ""));
  const [draftNew, setDraftNew] = useState(newCode || (versions[versions.length - 1]?.set_code ?? ""));

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
      <div className="flex items-center gap-3 p-3 bg-gray-900 border-b border-gray-700 text-sm">
        <span className="text-gray-400">Old:</span>
        <select
          value={draftOld}
          onChange={(e) => setDraftOld(e.target.value)}
          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white"
        >
          {versions.map((v) => (
            <option key={v.set_code} value={v.set_code}>
              {v.set_code} — {v.set_name} ({v.release_date || "?"})
            </option>
          ))}
        </select>
        <span className="text-gray-400">→</span>
        <span className="text-gray-400">New:</span>
        <select
          value={draftNew}
          onChange={(e) => setDraftNew(e.target.value)}
          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white"
        >
          {versions.map((v) => (
            <option key={v.set_code} value={v.set_code}>
              {v.set_code} — {v.set_name} ({v.release_date || "?"})
            </option>
          ))}
        </select>
        <button
          onClick={() => onCompare(draftOld, draftNew)}
          disabled={!draftOld || !draftNew || draftOld === draftNew || loading}
          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 rounded text-white"
        >
          {loading ? "Loading..." : "Compare"}
        </button>
      </div>

      {!oldCode || !newCode ? (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          Select two versions above and click Compare
        </div>
      ) : (
        <>
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
            <div className="max-h-48 overflow-y-auto bg-gray-900 border-t border-gray-700 p-3 grid grid-cols-3 gap-3">
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
              {diff.renamed && diff.renamed.length > 0 && (
                <div>
                  <h4 className="text-sm font-bold text-amber-400 mb-1">~ Renamed ({diff.renamed.length})</h4>
                  <div className="space-y-1 text-xs">
                    {diff.renamed.slice(0, 20).map((r) => (
                      <div key={r.old_id} className="text-gray-200">
                        <span className="text-amber-400">~</span> {r.old_name} → {r.new_name}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
