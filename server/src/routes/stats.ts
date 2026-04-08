import { Router } from "express";
import type Database from "better-sqlite3";

export function createStatsRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (_req, res) => {
    const byType = db.prepare("SELECT type, COUNT(*) as count FROM concepts GROUP BY type ORDER BY count DESC").all();
    const byChapter = db.prepare("SELECT chapter, COUNT(*) as count FROM concepts GROUP BY chapter ORDER BY chapter").all();
    const byComplexity = db.prepare("SELECT complexity, COUNT(*) as count FROM concepts GROUP BY complexity ORDER BY complexity").all();
    const relationsByType = db.prepare("SELECT type, COUNT(*) as count FROM relations GROUP BY type ORDER BY count DESC").all();
    const totalConcepts = db.prepare("SELECT COUNT(*) as count FROM concepts").get() as { count: number };
    const totalRelations = db.prepare("SELECT COUNT(*) as count FROM relations").get() as { count: number };
    const totalRuleTexts = db.prepare("SELECT COUNT(*) as count FROM rule_texts").get() as { count: number };

    res.json({
      totals: {
        concepts: totalConcepts.count,
        relations: totalRelations.count,
        rule_texts: totalRuleTexts.count,
      },
      concepts_by_type: byType,
      concepts_by_chapter: byChapter,
      concepts_by_complexity: byComplexity,
      relations_by_type: relationsByType,
    });
  });

  return router;
}
