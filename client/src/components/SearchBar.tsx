import type { Concept } from "../types/index.js";

const NODE_TYPES = [
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
      <div className="relative flex-1 max-w-md">
        <input
          type="text"
          value={query}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search concepts (EN / 中文)..."
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

      <select
        onChange={(e) => onChapterFilter(e.target.value || undefined)}
        className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
      >
        <option value="">All Chapters</option>
        {CHAPTERS.map((ch) => (
          <option key={ch} value={ch}>Chapter {ch}</option>
        ))}
      </select>

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
