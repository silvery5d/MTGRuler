import type { ViewMode } from "../types/index.js";

const VIEW_OPTIONS: { value: ViewMode; label: string }[] = [
  { value: "graph", label: "Graph View" },
  { value: "dependency", label: "Dependency Graph" },
  { value: "heatmap", label: "Complexity Heatmap" },
  { value: "chapter-overview", label: "Chapter Overview" },
  { value: "interaction-matrix", label: "Interaction Matrix" },
  { value: "history", label: "History (Complexity Evolution)" },
];

interface ViewSwitcherProps {
  current: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function ViewSwitcher({ current, onChange }: ViewSwitcherProps) {
  return (
    <select
      value={current}
      onChange={(e) => onChange(e.target.value as ViewMode)}
      className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm"
    >
      {VIEW_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}
