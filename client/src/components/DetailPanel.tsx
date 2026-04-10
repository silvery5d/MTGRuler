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
    <div className="w-80 flex-shrink-0 bg-gray-900 border-l border-gray-700 overflow-y-auto flex flex-col">
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

      <div className="p-4 border-b border-gray-700">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Definition</h4>
        {concept.definition_cn && (
          <p className="text-sm text-gray-200 mb-2">{concept.definition_cn}</p>
        )}
        {concept.definition_en && (
          <p className="text-sm text-gray-400 italic">{concept.definition_en}</p>
        )}
      </div>

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
