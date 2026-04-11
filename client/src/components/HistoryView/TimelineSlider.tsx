import { useEffect, useMemo } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { VersionInfo, GraphData } from "../../types/index.js";

interface TimelineSliderProps {
  versions: VersionInfo[];
  selectedVersion: string | null;
  graphData: GraphData | null;
  loading: boolean;
  onVersionChange: (setCode: string) => void;
}

export function TimelineSlider({ versions, selectedVersion, graphData, loading, onVersionChange }: TimelineSliderProps) {
  const currentIdx = versions.findIndex((v) => v.set_code === selectedVersion);
  const safeIdx = currentIdx >= 0 ? currentIdx : versions.length - 1;
  const current = versions[safeIdx];

  const elements = useMemo(() => {
    if (!graphData) return [];
    return [
      ...graphData.nodes.map((n) => ({
        data: {
          id: n.id,
          label: n.name_cn || n.name_en,
          color: NODE_COLORS[n.type] || "#6b7280",
          size: 14 + (n.complexity ?? 2) * 5,
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
    ];
  }, [graphData]);

  useEffect(() => {
    if (current && !graphData && !loading) {
      onVersionChange(current.set_code);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current?.set_code]);

  if (versions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        No historical versions loaded
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="p-4 bg-gray-900 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2 text-sm">
          <span className="text-gray-400">{versions[0]?.set_code} ({versions[0]?.release_date})</span>
          <span className="text-white font-bold">
            {current?.set_name} ({current?.set_code})
            {current?.release_date && <span className="text-gray-400 ml-2">{current.release_date}</span>}
          </span>
          <span className="text-gray-400">
            {versions[versions.length - 1]?.set_code} ({versions[versions.length - 1]?.release_date})
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={versions.length - 1}
          value={safeIdx}
          onChange={(e) => onVersionChange(versions[parseInt(e.target.value)].set_code)}
          className="w-full"
        />
      </div>
      <div className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-950/50 z-10 text-gray-400">
            Loading {current?.set_code}...
          </div>
        )}
        <GraphView elements={elements} onNodeClick={() => { /* no-op for now */ }} />
      </div>
    </div>
  );
}
