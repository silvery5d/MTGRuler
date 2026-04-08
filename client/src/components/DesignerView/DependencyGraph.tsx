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
                  className="block w-full text-left px-3 py-1 hover:bg-gray-700 text-xs text-white whitespace-nowrap"
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
