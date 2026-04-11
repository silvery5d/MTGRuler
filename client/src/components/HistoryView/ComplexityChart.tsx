import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from "recharts";
import { useMemo, useState } from "react";
import type { MetricsRecord, SpikeRecord } from "../../types/index.js";

interface ComplexityChartProps {
  metrics: MetricsRecord[];
  spikes: SpikeRecord[];
  onSpikeClick: (oldCode: string, newCode: string) => void;
}

interface ChartPoint {
  set_code: string;
  set_name: string;
  release_date: string | null;
  rule_count: number;
  concept_count: number;
  uc_total: number;
  keyword_count: number;
}

const METRIC_LINES = [
  { key: "rule_count", color: "#6366f1", label: "Rule Count" },
  { key: "concept_count", color: "#10b981", label: "Concept Count" },
  { key: "uc_total", color: "#f59e0b", label: "Understanding Complexity (Total)" },
  { key: "keyword_count", color: "#ef4444", label: "Keyword Count" },
];

export function ComplexityChart({ metrics, spikes, onSpikeClick }: ComplexityChartProps) {
  const [enabled, setEnabled] = useState<Set<string>>(new Set(METRIC_LINES.map((m) => m.key)));

  const data: ChartPoint[] = useMemo(
    () =>
      metrics.map((m) => ({
        set_code: m.set_code,
        set_name: m.set_name,
        release_date: m.release_date,
        rule_count: m.scale.rule_count,
        concept_count: m.graph.concept_count,
        uc_total: m.cognitive.uc_total,
        keyword_count: m.mechanic.keyword_count,
      })),
    [metrics],
  );

  const toggleMetric = (key: string) => {
    setEnabled((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const formatTick = (setCode: string) => {
    const point = data.find((d) => d.set_code === setCode);
    return point?.release_date?.slice(0, 4) || setCode;
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-950 p-4 overflow-hidden">
      <div className="flex items-center gap-4 mb-3">
        <h2 className="text-white font-bold">Complexity Over Time</h2>
        <div className="flex gap-3">
          {METRIC_LINES.map((m) => (
            <label key={m.key} className="flex items-center gap-1 text-sm text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={enabled.has(m.key)}
                onChange={() => toggleMetric(m.key)}
              />
              <span style={{ color: m.color }}>{m.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="set_code" tick={{ fill: "#9ca3af", fontSize: 11 }} tickFormatter={formatTick} />
            <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              labelStyle={{ color: "#f3f4f6" }}
              labelFormatter={(setCode: string) => {
                const point = data.find((d) => d.set_code === setCode);
                return point ? `${point.set_name} (${point.release_date || setCode})` : setCode;
              }}
            />
            <Legend wrapperStyle={{ color: "#d1d5db" }} />
            {METRIC_LINES.filter((m) => enabled.has(m.key)).map((m) => (
              <Line
                key={m.key}
                type="monotone"
                dataKey={m.key}
                stroke={m.color}
                strokeWidth={2}
                dot={false}
                name={m.label}
              />
            ))}
            {spikes.map((s) => {
              const point = data.find((d) => d.set_code === s.set_code);
              if (!point) return null;
              return (
                <ReferenceDot
                  key={s.set_code}
                  x={s.set_code}
                  y={point.uc_total}
                  r={6}
                  fill="#fbbf24"
                  stroke="#fff"
                  strokeWidth={1}
                  onClick={() => onSpikeClick(s.prev_set_code, s.set_code)}
                  style={{ cursor: "pointer" }}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {spikes.length > 0 && (
        <div className="mt-4 max-h-40 overflow-y-auto bg-gray-900 rounded-lg p-3">
          <h3 className="text-sm font-bold text-amber-400 mb-2">⚠️ Detected Spikes</h3>
          <div className="space-y-2">
            {spikes.map((s) => (
              <button
                key={s.set_code}
                onClick={() => onSpikeClick(s.prev_set_code, s.set_code)}
                className="w-full text-left p-2 bg-gray-800 hover:bg-gray-700 rounded text-xs"
              >
                <div className="flex justify-between text-white">
                  <span>{s.set_name} ({s.set_code})</span>
                  <span className="text-amber-400">{s.delta_summary}</span>
                </div>
                <div className="text-gray-400 mt-1">{s.analysis.summary}</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
