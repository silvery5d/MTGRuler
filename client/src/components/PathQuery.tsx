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

      <div className="relative">
        <input
          value={from}
          onChange={(e) => handleFromSearch(e.target.value)}
          placeholder="From..."
          className="w-32 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
        />
        {fromResults.length > 0 && (
          <div className="absolute bottom-full left-0 mb-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-50">
            {fromResults.map((c) => (
              <button
                key={c.id}
                onClick={() => { setFromId(c.id); setFrom(c.name_cn); setFromResults([]); }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-700 text-xs text-white whitespace-nowrap"
              >
                {c.name_cn}
              </button>
            ))}
          </div>
        )}
      </div>

      <span className="text-gray-400">→</span>

      <div className="relative">
        <input
          value={to}
          onChange={(e) => handleToSearch(e.target.value)}
          placeholder="To..."
          className="w-32 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
        />
        {toResults.length > 0 && (
          <div className="absolute bottom-full left-0 mb-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-50">
            {toResults.map((c) => (
              <button
                key={c.id}
                onClick={() => { setToId(c.id); setTo(c.name_cn); setToResults([]); }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-700 text-xs text-white whitespace-nowrap"
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
