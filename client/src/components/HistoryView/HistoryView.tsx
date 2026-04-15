import { useHistory } from "./useHistory.js";
import { ComplexityChart } from "./ComplexityChart.js";
import { TimelineSlider } from "./TimelineSlider.js";
import { DiffCompare } from "./DiffCompare.js";

export function HistoryView() {
  const h = useHistory();

  if (h.loading && h.versions.length === 0) {
    return <div className="flex-1 flex items-center justify-center text-gray-400">Loading history...</div>;
  }
  if (h.error) {
    return <div className="flex-1 flex items-center justify-center text-red-400">{h.error}</div>;
  }
  if (h.versions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-center px-8">
        No historical data found.<br />
        Run <code className="text-indigo-400">python -m parser.history.run_history_pipeline</code> first.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="flex items-center gap-2 p-2 bg-gray-900 border-b border-gray-700">
        <button
          onClick={() => h.setSubView("chart")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "chart" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Complexity Chart
        </button>
        <button
          onClick={() => h.setSubView("slider")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "slider" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Timeline Slider
        </button>
        <button
          onClick={() => h.setSubView("diff")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "diff" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Diff Compare
        </button>
      </div>

      <div className="flex-1 flex min-h-0">
        {h.subView === "chart" && (
          <ComplexityChart
            metrics={h.metrics}
            spikes={h.spikes}
            onSpikeClick={h.compareVersions}
          />
        )}
        {h.subView === "slider" && (
          <TimelineSlider
            versions={h.versions}
            selectedVersion={h.selectedVersion}
            graphData={h.selectedGraph}
            loading={h.loading}
            onVersionChange={h.selectVersion}
          />
        )}
        {h.subView === "diff" && (
          <DiffCompare
            versions={h.versions}
            oldCode={h.compareVersion}
            newCode={h.compareVersion ? h.selectedVersion : null}
            oldGraph={h.compareGraph}
            newGraph={h.selectedGraph}
            diff={h.diff}
            loading={h.loading}
            onCompare={h.compareVersions}
          />
        )}
      </div>
    </div>
  );
}
