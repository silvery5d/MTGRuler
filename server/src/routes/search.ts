import { Router } from "express";
import type Database from "better-sqlite3";
import type { Concept } from "../types.js";

/**
 * Rewrite a user search query so CJK Han characters are tokenizable by
 * SQLite FTS5's unicode61 tokenizer. The Phase 1 parser indexes CJK text
 * with a space inserted between consecutive Han characters (e.g. "飞行"
 * is stored as "飞 行"). To match that, we apply the same transformation
 * to the query string before passing it to FTS5 MATCH.
 */
export function rewriteCjkQuery(q: string): string {
  return q.replace(/([\u3400-\u9fff])(?=[\u3400-\u9fff])/g, "$1 ");
}

export function searchConcepts(
  db: Database.Database,
  query: string,
  type?: string,
): Concept[] {
  // Sanitize quotes so we don't break FTS5 syntax, then apply CJK split.
  const sanitized = query.replace(/['"]/g, "");
  const ftsQuery = rewriteCjkQuery(sanitized);

  let sql = `
    SELECT c.* FROM concepts c
    JOIN concepts_fts f ON c.rowid = f.rowid
    WHERE concepts_fts MATCH ?
  `;
  const values: any[] = [ftsQuery];

  if (type) {
    sql += " AND c.type = ?";
    values.push(type);
  }

  sql += " LIMIT 50";

  try {
    return db.prepare(sql).all(...values) as Concept[];
  } catch {
    // If FTS fails (bad query syntax), fall back to LIKE
    let likeSql = `
      SELECT * FROM concepts
      WHERE (name_en LIKE ? OR name_cn LIKE ? OR definition_en LIKE ? OR definition_cn LIKE ?)
    `;
    const likePattern = `%${query}%`;
    const likeValues: any[] = [likePattern, likePattern, likePattern, likePattern];

    if (type) {
      likeSql += " AND type = ?";
      likeValues.push(type);
    }

    likeSql += " LIMIT 50";
    return db.prepare(likeSql).all(...likeValues) as Concept[];
  }
}

export function createSearchRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const q = req.query.q as string;
    if (!q) {
      res.status(400).json({ error: "Query parameter 'q' is required" });
      return;
    }
    const type = req.query.type as string | undefined;
    res.json(searchConcepts(db, q, type));
  });

  return router;
}
