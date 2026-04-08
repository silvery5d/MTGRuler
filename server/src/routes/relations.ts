import { Router } from "express";
import type Database from "better-sqlite3";

export function createRelationsRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const conditions: string[] = [];
    const values: any[] = [];

    if (req.query.type) {
      conditions.push("type = ?");
      values.push(req.query.type);
    }
    if (req.query.source) {
      conditions.push("source_id = ?");
      values.push(req.query.source);
    }
    if (req.query.target) {
      conditions.push("target_id = ?");
      values.push(req.query.target);
    }

    const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";
    const limit = parseInt(req.query.limit as string) || 100;
    const offset = parseInt(req.query.offset as string) || 0;

    const results = db
      .prepare(`SELECT * FROM relations ${where} LIMIT ? OFFSET ?`)
      .all(...values, limit, offset);
    res.json(results);
  });

  return router;
}
