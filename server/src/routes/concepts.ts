import { Router } from "express";
import type Database from "better-sqlite3";
import type { Concept, RuleText } from "../types.js";

interface ListParams {
  type?: string;
  chapter?: string;
  limit?: number;
  offset?: number;
}

export function getConceptsList(
  db: Database.Database,
  params: ListParams,
): Concept[] {
  const conditions: string[] = [];
  const values: any[] = [];

  if (params.type) {
    conditions.push("type = ?");
    values.push(params.type);
  }
  if (params.chapter) {
    conditions.push("chapter = ?");
    values.push(params.chapter);
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";
  const limit = params.limit ?? 100;
  const offset = params.offset ?? 0;

  return db
    .prepare(`SELECT * FROM concepts ${where} LIMIT ? OFFSET ?`)
    .all(...values, limit, offset) as Concept[];
}

export function getConceptById(
  db: Database.Database,
  id: string,
): { concept: Concept; rule_texts: RuleText[]; related: Concept[] } | null {
  const concept = db.prepare("SELECT * FROM concepts WHERE id = ?").get(id) as
    | Concept
    | undefined;
  if (!concept) return null;

  const rule_texts = db
    .prepare("SELECT * FROM rule_texts WHERE parent_concept_id = ?")
    .all(id) as RuleText[];

  const related = db
    .prepare(
      `SELECT DISTINCT c.* FROM concepts c
       JOIN relations r ON (r.target_id = c.id AND r.source_id = ?)
                        OR (r.source_id = c.id AND r.target_id = ?)`,
    )
    .all(id, id) as Concept[];

  return { concept, rule_texts, related };
}

export function getConceptNeighbors(
  db: Database.Database,
  id: string,
  depth: number,
): Concept[] {
  const visited = new Set<string>([id]);
  let frontier = [id];

  for (let d = 0; d < depth; d++) {
    const nextFrontier: string[] = [];
    for (const nodeId of frontier) {
      const neighbors = db
        .prepare(
          `SELECT target_id AS id FROM relations WHERE source_id = ?
           UNION
           SELECT source_id AS id FROM relations WHERE target_id = ?`,
        )
        .all(nodeId, nodeId) as { id: string }[];

      for (const n of neighbors) {
        if (!visited.has(n.id)) {
          visited.add(n.id);
          nextFrontier.push(n.id);
        }
      }
    }
    frontier = nextFrontier;
  }

  visited.delete(id);
  if (visited.size === 0) return [];

  const ids = [...visited];
  const placeholders = ids.map(() => "?").join(",");
  return db
    .prepare(`SELECT * FROM concepts WHERE id IN (${placeholders})`)
    .all(...ids) as Concept[];
}

export function createConceptsRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const params: ListParams = {
      type: req.query.type as string | undefined,
      chapter: req.query.chapter as string | undefined,
      limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
      offset: req.query.offset
        ? parseInt(req.query.offset as string)
        : undefined,
    };
    res.json(getConceptsList(db, params));
  });

  router.get("/:id", (req, res) => {
    const result = getConceptById(db, req.params.id);
    if (!result) {
      res.status(404).json({ error: "Concept not found" });
      return;
    }
    res.json(result);
  });

  router.get("/:id/neighbors", (req, res) => {
    const depth = parseInt(req.query.depth as string) || 1;
    res.json(getConceptNeighbors(db, req.params.id, depth));
  });

  return router;
}
