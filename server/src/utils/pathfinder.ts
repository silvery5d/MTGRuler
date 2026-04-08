import type Database from "better-sqlite3";
import type { Concept } from "../types.js";

interface PathResult {
  nodes: Concept[];
  edges: { source: string; target: string; type: string }[];
}

export function findShortestPath(
  db: Database.Database,
  fromId: string,
  toId: string,
): PathResult | null {
  if (fromId === toId) {
    const c = db.prepare("SELECT * FROM concepts WHERE id = ?").get(fromId) as
      | Concept
      | undefined;
    if (!c) return null;
    return { nodes: [c], edges: [] };
  }

  const parent = new Map<string, { from: string; edgeType: string }>();
  const visited = new Set<string>([fromId]);
  let queue = [fromId];

  while (queue.length > 0) {
    const nextQueue: string[] = [];

    for (const current of queue) {
      if (current === toId) {
        return reconstructPath(db, fromId, toId, parent);
      }

      const neighbors = db
        .prepare(
          `SELECT target_id AS neighbor, type FROM relations WHERE source_id = ?
           UNION ALL
           SELECT source_id AS neighbor, type FROM relations WHERE target_id = ?`,
        )
        .all(current, current) as { neighbor: string; type: string }[];

      for (const { neighbor, type } of neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          parent.set(neighbor, { from: current, edgeType: type });
          nextQueue.push(neighbor);
          if (neighbor === toId) {
            return reconstructPath(db, fromId, toId, parent);
          }
        }
      }
    }

    queue = nextQueue;
  }

  return null;
}

function reconstructPath(
  db: Database.Database,
  fromId: string,
  toId: string,
  parent: Map<string, { from: string; edgeType: string }>,
): PathResult {
  const nodeIds: string[] = [toId];
  const edges: { source: string; target: string; type: string }[] = [];

  let current = toId;
  while (current !== fromId) {
    const p = parent.get(current)!;
    edges.unshift({ source: p.from, target: current, type: p.edgeType });
    nodeIds.unshift(p.from);
    current = p.from;
  }

  const placeholders = nodeIds.map(() => "?").join(",");
  const concepts = db
    .prepare(`SELECT * FROM concepts WHERE id IN (${placeholders})`)
    .all(...nodeIds) as Concept[];

  const conceptMap = new Map(concepts.map((c) => [c.id, c]));
  const orderedConcepts = nodeIds
    .map((id) => conceptMap.get(id)!)
    .filter(Boolean);

  return { nodes: orderedConcepts, edges };
}
