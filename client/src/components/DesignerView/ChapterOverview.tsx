import { useState, useEffect } from "react";
import type { Stats } from "../../types/index.js";
import { api } from "../../services/api.js";

interface ChapterOverviewProps {
  onChapterClick: (chapter: string) => void;
}

const CHAPTER_NAMES: Record<string, string> = {
  "1": "Game Concepts / 游戏概念",
  "2": "Parts of a Card / 牌的组成",
  "3": "Card Types / 牌的类别",
  "4": "Zones / 区域",
  "5": "Turn Structure / 回合结构",
  "6": "Spells, Abilities, and Effects / 咒语、异能和效应",
  "7": "Additional Rules / 额外规则",
  "8": "Multiplayer Rules / 多人规则",
  "9": "Casual Variants / 休闲玩法",
};

export function ChapterOverview({ onChapterClick }: ChapterOverviewProps) {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.getStats().then(setStats);
  }, []);

  if (!stats) return <div className="flex-1 flex items-center justify-center text-gray-400">Loading stats...</div>;

  const maxCount = Math.max(...stats.concepts_by_chapter.map((c) => c.count));

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <h2 className="text-lg font-bold text-white mb-4">Chapter Overview</h2>
      <div className="space-y-3">
        {stats.concepts_by_chapter.map(({ chapter, count }) => (
          <button
            key={chapter}
            onClick={() => onChapterClick(chapter)}
            className="w-full text-left p-3 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            <div className="flex justify-between items-center mb-1">
              <span className="text-white font-medium">
                Ch.{chapter}: {CHAPTER_NAMES[chapter] || `Chapter ${chapter}`}
              </span>
              <span className="text-gray-400 text-sm">{count} concepts</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full"
                style={{ width: `${(count / maxCount) * 100}%` }}
              />
            </div>
          </button>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-indigo-400">{stats.totals.concepts}</p>
          <p className="text-gray-400 text-sm">Concepts</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-green-400">{stats.totals.relations}</p>
          <p className="text-gray-400 text-sm">Relations</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-lg text-center">
          <p className="text-2xl font-bold text-amber-400">{stats.totals.rule_texts}</p>
          <p className="text-gray-400 text-sm">Rule Texts</p>
        </div>
      </div>
    </div>
  );
}
