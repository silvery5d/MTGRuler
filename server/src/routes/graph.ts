import { Router } from "express";
import type Database from "better-sqlite3";
import type { GraphData, GraphNode, GraphEdge } from "../types.js";

type UcCache = Map<string, number>;

interface GraphParams {
  chapter?: string;
  center?: string;
  depth?: number;
}

export function getGraphData(db: Database.Database, params: GraphParams, ucCache?: UcCache): GraphData {
  let nodeIds: Set<string>;

  if (params.center) {
    // Ego-centric subgraph: BFS from center node
    const depth = params.depth ?? 2;
    nodeIds = new Set([params.center]);
    let frontier = [params.center];

    for (let d = 0; d < depth; d++) {
      const next: string[] = [];
      for (const id of frontier) {
        const neighbors = db.prepare(`
          SELECT target_id AS id FROM relations WHERE source_id = ?
          UNION
          SELECT source_id AS id FROM relations WHERE target_id = ?
        `).all(id, id) as { id: string }[];

        for (const n of neighbors) {
          if (!nodeIds.has(n.id)) {
            nodeIds.add(n.id);
            next.push(n.id);
          }
        }
      }
      frontier = next;
    }
  } else if (params.chapter) {
    const concepts = db.prepare("SELECT id FROM concepts WHERE chapter = ?").all(params.chapter) as { id: string }[];
    nodeIds = new Set(concepts.map((c) => c.id));
  } else {
    const concepts = db.prepare("SELECT id FROM concepts").all() as { id: string }[];
    nodeIds = new Set(concepts.map((c) => c.id));
  }

  if (nodeIds.size === 0) return { nodes: [], edges: [] };

  const idList = [...nodeIds];
  const placeholders = idList.map(() => "?").join(",");
  const rawNodes = db.prepare(
    `SELECT id, name_en, name_cn, type, complexity FROM concepts WHERE id IN (${placeholders})`,
  ).all(...idList) as GraphNode[];

  const nodes = rawNodes.map((n) => ({
    ...n,
    understanding_complexity: ucCache?.get(n.id) ?? null,
  }));

  const edges = db.prepare(
    `SELECT source_id AS source, target_id AS target, type FROM relations
     WHERE source_id IN (${placeholders}) AND target_id IN (${placeholders})`,
  ).all(...idList, ...idList) as GraphEdge[];

  return { nodes, edges };
}

export function createGraphRouter(db: Database.Database, ucCache: UcCache): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const params: GraphParams = {
      chapter: req.query.chapter as string | undefined,
      center: req.query.center as string | undefined,
      depth: req.query.depth ? parseInt(req.query.depth as string) : undefined,
    };
    res.json(getGraphData(db, params, ucCache));
  });

  return router;
}
