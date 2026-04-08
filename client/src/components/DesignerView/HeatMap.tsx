import { GraphView } from "../GraphView.js";
import { COMPLEXITY_COLORS } from "../../styles/cytoscape.js";
import type { GraphData } from "../../types/index.js";

interface HeatMapProps {
  graphData: GraphData | null;
  onNodeClick: (id: string) => void;
}

export function HeatMap({ graphData, onNodeClick }: HeatMapProps) {
  if (!graphData) return null;

  const elements = [
    ...graphData.nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.name_cn || n.name_en,
        color: COMPLEXITY_COLORS[Math.max(0, Math.min(4, (n.complexity ?? 1) - 1))],
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
