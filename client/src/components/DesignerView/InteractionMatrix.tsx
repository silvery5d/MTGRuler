import { useState, useEffect } from "react";
import type { Concept, Relation } from "../../types/index.js";
import { api } from "../../services/api.js";

interface InteractionMatrixProps {
  onConceptClick: (id: string) => void;
}

export function InteractionMatrix({ onConceptClick }: InteractionMatrixProps) {
  const [keywords, setKeywords] = useState<Concept[]>([]);
  const [interactions, setInteractions] = useState<Relation[]>([]);
  const [selected, setSelected] = useState<{ row: number; col: number } | null>(null);

  useEffect(() => {
    Promise.all([
      api.getConcepts({ type: "Keyword", limit: "100" }),
      api.getConcepts({ type: "Keyword", limit: "100", offset: "100" }),
    ]).then(([a, b]) => {
      setKeywords([...a, ...b]);
    });
    fetch("/api/v1/relations?type=INTERACTS_WITH&limit=500")
      .then((r) => r.json())
      .then(setInteractions);
  }, []);

  const interactionMap = new Map<string, Set<string>>();
  for (const r of interactions) {
    if (!interactionMap.has(r.source_id)) interactionMap.set(r.source_id, new Set());
    if (!interactionMap.has(r.target_id)) interactionMap.set(r.target_id, new Set());
    interactionMap.get(r.source_id)!.add(r.target_id);
    interactionMap.get(r.target_id)!.add(r.source_id);
  }

  const activeKeywords = keywords.filter(
    (k) => interactionMap.has(k.id) && interactionMap.get(k.id)!.size > 0,
  );

  if (activeKeywords.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        Loading interaction data... (or no INTERACTS_WITH relations in current data)
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-4">
      <h2 className="text-lg font-bold text-white mb-4">Keyword Interaction Matrix</h2>
      <div className="overflow-auto">
        <table className="border-collapse text-xs">
          <thead>
            <tr style={{ height: 120 }}>
              <th className="p-1 align-bottom" />
              {activeKeywords.map((k, colIdx) => {
                const isSelectedHeader = selected && selected.col === colIdx;
                return (
                  <th
                    key={k.id}
                    className={`p-0 font-normal cursor-pointer align-bottom ${
                      isSelectedHeader
                        ? "text-yellow-300 font-bold"
                        : "text-gray-300 hover:text-white"
                    }`}
                    onClick={() => onConceptClick(k.id)}
                  >
                    <div
                      className="whitespace-nowrap origin-bottom-left"
                      style={{
                        transform: "translateX(50%) rotate(-60deg)",
                        transformOrigin: "bottom left",
                        width: 24,
                        height: 120,
                        display: "flex",
                        alignItems: "flex-end",
                      }}
                    >
                      {k.name_cn}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {activeKeywords.map((row, rowIdx) => {
              const isRowSelected = selected && selected.row === rowIdx;
              return (
                <tr key={row.id}>
                  <td
                    className={`p-1 whitespace-nowrap cursor-pointer ${
                      isRowSelected
                        ? "text-yellow-300 font-bold"
                        : "text-gray-300 hover:text-white"
                    }`}
                    onClick={() => onConceptClick(row.id)}
                  >
                    {row.name_cn}
                  </td>
                  {activeKeywords.map((col, colIdx) => {
                    const hasInteraction = interactionMap.get(row.id)?.has(col.id);
                    // A cell is "in the L-shape path" if it's in the same row
                    // AND at or to the left of the selected column, OR in the
                    // same column AND at or above the selected row.
                    const onPath =
                      selected &&
                      ((rowIdx === selected.row && colIdx <= selected.col) ||
                        (colIdx === selected.col && rowIdx <= selected.row));
                    const isTarget =
                      selected &&
                      rowIdx === selected.row &&
                      colIdx === selected.col;

                    let bg = "bg-gray-900";
                    if (row.id === col.id) bg = "bg-gray-800";
                    else if (hasInteraction) bg = "bg-cyan-600 hover:bg-cyan-500";

                    if (isTarget) bg = "bg-yellow-400";
                    else if (onPath) {
                      bg = hasInteraction
                        ? "bg-yellow-600"
                        : "bg-yellow-900/60";
                    }

                    return (
                      <td
                        key={col.id}
                        className={`w-6 h-6 border border-gray-700 cursor-pointer ${bg}`}
                        onClick={() => setSelected({ row: rowIdx, col: colIdx })}
                      />
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
