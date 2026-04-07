# MTGRuler Phase 2: Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Node.js/Express REST API that reads `concepts.db` (from Phase 1) and serves concepts, relations, search, path queries, and Cytoscape-compatible graph data.

**Architecture:** Express + better-sqlite3 with typed route handlers. FTS5 for search. BFS for path queries. All endpoints return JSON. CORS enabled for frontend dev.

**Tech Stack:** Node.js, TypeScript, Express, better-sqlite3, cors

**Spec:** `docs/superpowers/specs/2026-04-07-mtgruler-knowledge-graph-design.md`
**Depends on:** Phase 1 output (`parser/data/concepts.db`)

---

## File Structure

```
server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # Express entry, middleware, mount routes
│   ├── db.ts                 # SQLite connection singleton
│   ├── types.ts              # Shared TypeScript types
│   ├── routes/
│   │   ├── concepts.ts       # GET /concepts, /concepts/:id, /concepts/:id/neighbors
│   │   ├── relations.ts      # GET /relations
│   │   ├── search.ts         # GET /search (FTS5)
│   │   ├── path.ts           # GET /path (BFS shortest path)
│   │   ├── graph.ts          # GET /graph (Cytoscape format)
│   │   └── stats.ts          # GET /stats
│   └── utils/
│       └── pathfinder.ts     # BFS shortest path on relation graph
└── tests/
    ├── setup.ts              # Test DB setup helper
    ├── concepts.test.ts
    ├── search.test.ts
    ├── path.test.ts
    └── graph.test.ts
```

---

### Task 1: Server Project Setup

**Files:**
- Create: `server/package.json`
- Create: `server/tsconfig.json`
- Create: `server/src/types.ts`

- [ ] **Step 1: Initialize project**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler
mkdir -p server/src/{routes,utils} server/tests
cd server
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "mtgruler-server",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "better-sqlite3": "^11.0.0",
    "cors": "^2.8.5",
    "express": "^4.21.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.0",
    "@types/cors": "^2.8.0",
    "@types/express": "^4.17.0",
    "tsx": "^4.0.0",
    "typescript": "^5.5.0",
    "vitest": "^2.0.0"
  }
}
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

- [ ] **Step 4: Create shared types**

```typescript
// server/src/types.ts

export interface Concept {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  rule_ref: string | null;
  definition_en: string | null;
  definition_cn: string | null;
  chapter: string | null;
  complexity: number | null;
  design_notes: string | null;
}

export interface Relation {
  source_id: string;
  target_id: string;
  type: string;
  rule_ref: string | null;
  description: string | null;
}

export interface RuleText {
  rule_ref: string;
  text_en: string | null;
  text_cn: string | null;
  parent_concept_id: string | null;
}

export interface GraphNode {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  complexity: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
```

- [ ] **Step 5: Install dependencies**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/server
npm install
```

- [ ] **Step 6: Commit**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler
git add server/package.json server/tsconfig.json server/src/types.ts
echo "server/node_modules/" >> .gitignore
echo "server/dist/" >> .gitignore
git add .gitignore
git commit -m "feat(server): initialize server project with types"
```

---

### Task 2: Database Connection

**Files:**
- Create: `server/src/db.ts`

- [ ] **Step 1: Implement db.ts**

```typescript
// server/src/db.ts
import Database from "better-sqlite3";
import { existsSync } from "fs";
import { resolve } from "path";

const DB_PATH = process.env.DB_PATH || resolve(import.meta.dirname, "../../parser/data/concepts.db");

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    if (!existsSync(DB_PATH)) {
      throw new Error(`Database not found at ${DB_PATH}. Run the parser pipeline first.`);
    }
    db = new Database(DB_PATH, { readonly: true });
    db.pragma("journal_mode = WAL");
  }
  return db;
}

export function closeDb(): void {
  if (db) {
    db.close();
    db = null;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add server/src/db.ts
git commit -m "feat(server): add SQLite database connection"
```

---

### Task 3: Concepts Route

**Files:**
- Create: `server/src/routes/concepts.ts`
- Create: `server/tests/concepts.test.ts`
- Create: `server/tests/setup.ts`

- [ ] **Step 1: Create test setup helper**

```typescript
// server/tests/setup.ts
import Database from "better-sqlite3";
import { resolve } from "path";

const SCHEMA = `
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    type TEXT NOT NULL,
    rule_ref TEXT,
    definition_en TEXT,
    definition_cn TEXT,
    chapter TEXT,
    complexity INTEGER,
    design_notes TEXT
);
CREATE TABLE IF NOT EXISTS relations (
    source_id TEXT,
    target_id TEXT,
    type TEXT NOT NULL,
    rule_ref TEXT,
    description TEXT,
    PRIMARY KEY (source_id, target_id, type)
);
CREATE TABLE IF NOT EXISTS rule_texts (
    rule_ref TEXT PRIMARY KEY,
    text_en TEXT,
    text_cn TEXT,
    parent_concept_id TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    id, name_en, name_cn, definition_en, definition_cn,
    content='concepts', content_rowid='rowid'
);
CREATE VIRTUAL TABLE IF NOT EXISTS rule_texts_fts USING fts5(
    rule_ref, text_en, text_cn,
    content='rule_texts', content_rowid='rowid'
);
`;

const SEED = `
INSERT INTO concepts VALUES ('keyword.flying','Flying','飞行','Keyword','702.9','Can''t be blocked except by flying/reach','不能被不具飞行或延势的生物阻挡','7',2,'Core evasion');
INSERT INTO concepts VALUES ('keyword.reach','Reach','延势','Keyword','702.17','Can block flying','可以阻挡飞行','7',1,'Flying counter');
INSERT INTO concepts VALUES ('concept.stack','Stack','堆叠','Concept','405','LIFO zone for spells/abilities','后进先出的区域','4',4,'Core resolution mechanic');
INSERT INTO concepts VALUES ('concept.priority','Priority','优先权','Concept','117','Permission to act','允许行动的权利','1',4,'Turn structure core');
INSERT INTO concepts VALUES ('phase.combat','Combat Phase','战斗阶段','Phase','506','Phase for attacking/blocking','攻击和阻挡的阶段','5',3,'Core gameplay');

INSERT INTO relations VALUES ('keyword.flying','keyword.reach','INTERACTS_WITH','702.9a','Reach can block flying');
INSERT INTO relations VALUES ('concept.stack','concept.priority','DEPENDS_ON','405.1','Stack uses priority');
INSERT INTO relations VALUES ('keyword.flying','phase.combat','OCCURS_IN','702.9','Flying matters in combat');

INSERT INTO rule_texts VALUES ('702.9','Flying is a keyword ability.','飞行是关键字异能。','keyword.flying');
INSERT INTO rule_texts VALUES ('702.9a','A creature with flying...','具有飞行异能的生物...','keyword.flying');

INSERT INTO concepts_fts(rowid, id, name_en, name_cn, definition_en, definition_cn)
  SELECT rowid, id, name_en, name_cn, definition_en, definition_cn FROM concepts;
INSERT INTO rule_texts_fts(rowid, rule_ref, text_en, text_cn)
  SELECT rowid, rule_ref, text_en, text_cn FROM rule_texts;
`;

export function createTestDb(): Database.Database {
  const db = new Database(":memory:");
  db.exec(SCHEMA);
  db.exec(SEED);
  return db;
}
```

- [ ] **Step 2: Write the test**

```typescript
// server/tests/concepts.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { getConceptsList, getConceptById, getConceptNeighbors } from "../src/routes/concepts.js";

let db: Database.Database;

beforeAll(() => { db = createTestDb(); });
afterAll(() => { db.close(); });

describe("getConceptsList", () => {
  it("returns all concepts", () => {
    const result = getConceptsList(db, {});
    expect(result.length).toBe(5);
  });

  it("filters by type", () => {
    const result = getConceptsList(db, { type: "Keyword" });
    expect(result.length).toBe(2);
    expect(result.every((c: any) => c.type === "Keyword")).toBe(true);
  });

  it("filters by chapter", () => {
    const result = getConceptsList(db, { chapter: "7" });
    expect(result.length).toBe(2);
  });

  it("paginates", () => {
    const result = getConceptsList(db, { limit: 2, offset: 0 });
    expect(result.length).toBe(2);
  });
});

describe("getConceptById", () => {
  it("returns concept with rule texts and relations", () => {
    const result = getConceptById(db, "keyword.flying");
    expect(result).not.toBeNull();
    expect(result!.concept.name_en).toBe("Flying");
    expect(result!.rule_texts.length).toBeGreaterThan(0);
    expect(result!.related.length).toBeGreaterThan(0);
  });

  it("returns null for unknown id", () => {
    const result = getConceptById(db, "nonexistent");
    expect(result).toBeNull();
  });
});

describe("getConceptNeighbors", () => {
  it("returns direct neighbors", () => {
    const result = getConceptNeighbors(db, "keyword.flying", 1);
    const ids = result.map((c: any) => c.id);
    expect(ids).toContain("keyword.reach");
    expect(ids).toContain("phase.combat");
  });
});
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/server
npx vitest run tests/concepts.test.ts
```
Expected: FAIL — module not found

- [ ] **Step 4: Implement concepts route**

```typescript
// server/src/routes/concepts.ts
import { Router } from "express";
import type Database from "better-sqlite3";
import type { Concept, RuleText, Relation } from "../types.js";

interface ListParams {
  type?: string;
  chapter?: string;
  limit?: number;
  offset?: number;
}

export function getConceptsList(db: Database.Database, params: ListParams): Concept[] {
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

  return db.prepare(`SELECT * FROM concepts ${where} LIMIT ? OFFSET ?`).all(...values, limit, offset) as Concept[];
}

export function getConceptById(
  db: Database.Database,
  id: string,
): { concept: Concept; rule_texts: RuleText[]; related: Concept[] } | null {
  const concept = db.prepare("SELECT * FROM concepts WHERE id = ?").get(id) as Concept | undefined;
  if (!concept) return null;

  const rule_texts = db.prepare("SELECT * FROM rule_texts WHERE parent_concept_id = ?").all(id) as RuleText[];

  // Get related concepts via relations (both directions)
  const related = db.prepare(`
    SELECT DISTINCT c.* FROM concepts c
    JOIN relations r ON (r.target_id = c.id AND r.source_id = ?) OR (r.source_id = c.id AND r.target_id = ?)
  `).all(id, id) as Concept[];

  return { concept, rule_texts, related };
}

export function getConceptNeighbors(db: Database.Database, id: string, depth: number): Concept[] {
  // BFS to find neighbors up to given depth
  const visited = new Set<string>([id]);
  let frontier = [id];

  for (let d = 0; d < depth; d++) {
    const nextFrontier: string[] = [];
    for (const nodeId of frontier) {
      const neighbors = db.prepare(`
        SELECT target_id AS id FROM relations WHERE source_id = ?
        UNION
        SELECT source_id AS id FROM relations WHERE target_id = ?
      `).all(nodeId, nodeId) as { id: string }[];

      for (const n of neighbors) {
        if (!visited.has(n.id)) {
          visited.add(n.id);
          nextFrontier.push(n.id);
        }
      }
    }
    frontier = nextFrontier;
  }

  visited.delete(id); // Remove the starting node
  if (visited.size === 0) return [];

  const placeholders = [...visited].map(() => "?").join(",");
  return db.prepare(`SELECT * FROM concepts WHERE id IN (${placeholders})`).all(...visited) as Concept[];
}

export function createConceptsRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const params: ListParams = {
      type: req.query.type as string | undefined,
      chapter: req.query.chapter as string | undefined,
      limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
      offset: req.query.offset ? parseInt(req.query.offset as string) : undefined,
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
```

- [ ] **Step 5: Run tests**

```bash
npx vitest run tests/concepts.test.ts
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add server/src/routes/concepts.ts server/tests/setup.ts server/tests/concepts.test.ts
git commit -m "feat(server): add concepts API routes with tests"
```

---

### Task 4: Relations Route

**Files:**
- Create: `server/src/routes/relations.ts`

- [ ] **Step 1: Implement relations route**

```typescript
// server/src/routes/relations.ts
import { Router } from "express";
import type Database from "better-sqlite3";
import type { Relation } from "../types.js";

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

    const results = db.prepare(`SELECT * FROM relations ${where} LIMIT ? OFFSET ?`).all(...values, limit, offset);
    res.json(results);
  });

  return router;
}
```

- [ ] **Step 2: Commit**

```bash
git add server/src/routes/relations.ts
git commit -m "feat(server): add relations API route"
```

---

### Task 5: Search Route

**Files:**
- Create: `server/src/routes/search.ts`
- Create: `server/tests/search.test.ts`

- [ ] **Step 1: Write the test**

```typescript
// server/tests/search.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { searchConcepts } from "../src/routes/search.js";

let db: Database.Database;

beforeAll(() => { db = createTestDb(); });
afterAll(() => { db.close(); });

describe("searchConcepts", () => {
  it("finds concepts by English name", () => {
    const results = searchConcepts(db, "Flying");
    expect(results.some((r: any) => r.id === "keyword.flying")).toBe(true);
  });

  it("finds concepts by Chinese name", () => {
    const results = searchConcepts(db, "飞行");
    expect(results.some((r: any) => r.id === "keyword.flying")).toBe(true);
  });

  it("filters by type", () => {
    const results = searchConcepts(db, "飞行", "Concept");
    // Flying is a Keyword, not a Concept — should not appear
    expect(results.every((r: any) => r.type === "Concept")).toBe(true);
  });

  it("returns empty for no match", () => {
    const results = searchConcepts(db, "xyznonexistent");
    expect(results.length).toBe(0);
  });
});
```

- [ ] **Step 2: Implement search route**

```typescript
// server/src/routes/search.ts
import { Router } from "express";
import type Database from "better-sqlite3";
import type { Concept } from "../types.js";

export function searchConcepts(db: Database.Database, query: string, type?: string): Concept[] {
  // FTS5 search on concepts
  const ftsQuery = query.replace(/['"]/g, ""); // Sanitize
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
      WHERE name_en LIKE ? OR name_cn LIKE ? OR definition_en LIKE ? OR definition_cn LIKE ?
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
```

- [ ] **Step 3: Run tests**

```bash
npx vitest run tests/search.test.ts
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add server/src/routes/search.ts server/tests/search.test.ts
git commit -m "feat(server): add FTS5 search route with LIKE fallback"
```

---

### Task 6: Path Query Route

**Files:**
- Create: `server/src/utils/pathfinder.ts`
- Create: `server/src/routes/path.ts`
- Create: `server/tests/path.test.ts`

- [ ] **Step 1: Write the test**

```typescript
// server/tests/path.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { findShortestPath } from "../src/utils/pathfinder.js";

let db: Database.Database;

beforeAll(() => { db = createTestDb(); });
afterAll(() => { db.close(); });

describe("findShortestPath", () => {
  it("finds direct path between connected nodes", () => {
    const path = findShortestPath(db, "keyword.flying", "keyword.reach");
    expect(path).not.toBeNull();
    expect(path!.nodes.length).toBe(2);
    expect(path!.nodes[0].id).toBe("keyword.flying");
    expect(path!.nodes[1].id).toBe("keyword.reach");
    expect(path!.edges.length).toBe(1);
  });

  it("finds multi-hop path", () => {
    // flying -> combat -> (no direct to stack, but stack -> priority exists)
    // We need a path: flying -> combat? or stack -> priority
    const path = findShortestPath(db, "concept.stack", "concept.priority");
    expect(path).not.toBeNull();
    expect(path!.nodes.length).toBe(2);
  });

  it("returns null for disconnected nodes", () => {
    // priority and reach have no path in test data
    const path = findShortestPath(db, "concept.priority", "keyword.reach");
    expect(path).toBeNull();
  });
});
```

- [ ] **Step 2: Implement pathfinder**

```typescript
// server/src/utils/pathfinder.ts
import type Database from "better-sqlite3";
import type { Concept, GraphEdge } from "../types.js";

interface PathResult {
  nodes: Concept[];
  edges: { source: string; target: string; type: string }[];
}

export function findShortestPath(
  db: Database.Database,
  fromId: string,
  toId: string,
): PathResult | null {
  // BFS shortest path
  const parent = new Map<string, { from: string; edgeType: string }>();
  const visited = new Set<string>([fromId]);
  let queue = [fromId];

  while (queue.length > 0) {
    const nextQueue: string[] = [];

    for (const current of queue) {
      if (current === toId) {
        // Reconstruct path
        return reconstructPath(db, fromId, toId, parent);
      }

      // Get all neighbors (both directions)
      const neighbors = db.prepare(`
        SELECT target_id AS neighbor, type FROM relations WHERE source_id = ?
        UNION ALL
        SELECT source_id AS neighbor, type FROM relations WHERE target_id = ?
      `).all(current, current) as { neighbor: string; type: string }[];

      for (const { neighbor, type } of neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          parent.set(neighbor, { from: current, edgeType: type });
          nextQueue.push(neighbor);
        }
      }
    }

    queue = nextQueue;
  }

  return null; // No path found
}

function reconstructPath(
  db: Database.Database,
  fromId: string,
  toId: string,
  parent: Map<string, { from: string; edgeType: string }>,
): PathResult {
  // Trace back from toId to fromId
  const nodeIds: string[] = [toId];
  const edges: { source: string; target: string; type: string }[] = [];

  let current = toId;
  while (current !== fromId) {
    const p = parent.get(current)!;
    edges.unshift({ source: p.from, target: current, type: p.edgeType });
    nodeIds.unshift(p.from);
    current = p.from;
  }

  // Fetch full concept data for all nodes in path
  const placeholders = nodeIds.map(() => "?").join(",");
  const concepts = db.prepare(`SELECT * FROM concepts WHERE id IN (${placeholders})`).all(...nodeIds) as Concept[];

  // Sort concepts in path order
  const conceptMap = new Map(concepts.map((c) => [c.id, c]));
  const orderedConcepts = nodeIds.map((id) => conceptMap.get(id)!).filter(Boolean);

  return { nodes: orderedConcepts, edges };
}
```

- [ ] **Step 3: Implement path route**

```typescript
// server/src/routes/path.ts
import { Router } from "express";
import type Database from "better-sqlite3";
import { findShortestPath } from "../utils/pathfinder.js";

export function createPathRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const from = req.query.from as string;
    const to = req.query.to as string;

    if (!from || !to) {
      res.status(400).json({ error: "Both 'from' and 'to' parameters are required" });
      return;
    }

    const result = findShortestPath(db, from, to);
    if (!result) {
      res.status(404).json({ error: "No path found between the specified concepts" });
      return;
    }

    res.json(result);
  });

  return router;
}
```

- [ ] **Step 4: Run tests**

```bash
npx vitest run tests/path.test.ts
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add server/src/utils/pathfinder.ts server/src/routes/path.ts server/tests/path.test.ts
git commit -m "feat(server): add BFS shortest path query"
```

---

### Task 7: Graph Route

**Files:**
- Create: `server/src/routes/graph.ts`
- Create: `server/tests/graph.test.ts`

- [ ] **Step 1: Write the test**

```typescript
// server/tests/graph.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { getGraphData } from "../src/routes/graph.js";

let db: Database.Database;

beforeAll(() => { db = createTestDb(); });
afterAll(() => { db.close(); });

describe("getGraphData", () => {
  it("returns all nodes and edges without filters", () => {
    const result = getGraphData(db, {});
    expect(result.nodes.length).toBe(5);
    expect(result.edges.length).toBe(3);
  });

  it("filters by chapter", () => {
    const result = getGraphData(db, { chapter: "7" });
    expect(result.nodes.every((n: any) => n.type === "Keyword")).toBe(true);
    // Should include edges between the filtered nodes
    expect(result.edges.length).toBeGreaterThan(0);
  });

  it("returns ego-centric subgraph", () => {
    const result = getGraphData(db, { center: "keyword.flying", depth: 1 });
    expect(result.nodes.some((n: any) => n.id === "keyword.flying")).toBe(true);
    expect(result.nodes.some((n: any) => n.id === "keyword.reach")).toBe(true);
  });
});
```

- [ ] **Step 2: Implement graph route**

```typescript
// server/src/routes/graph.ts
import { Router } from "express";
import type Database from "better-sqlite3";
import type { GraphData, GraphNode, GraphEdge } from "../types.js";

interface GraphParams {
  chapter?: string;
  center?: string;
  depth?: number;
}

export function getGraphData(db: Database.Database, params: GraphParams): GraphData {
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
    // Chapter subgraph
    const concepts = db.prepare("SELECT id FROM concepts WHERE chapter = ?").all(params.chapter) as { id: string }[];
    nodeIds = new Set(concepts.map((c) => c.id));
  } else {
    // All nodes
    const concepts = db.prepare("SELECT id FROM concepts").all() as { id: string }[];
    nodeIds = new Set(concepts.map((c) => c.id));
  }

  // Fetch full node data
  if (nodeIds.size === 0) return { nodes: [], edges: [] };

  const idList = [...nodeIds];
  const placeholders = idList.map(() => "?").join(",");
  const nodes = db.prepare(
    `SELECT id, name_en, name_cn, type, complexity FROM concepts WHERE id IN (${placeholders})`
  ).all(...idList) as GraphNode[];

  // Fetch edges where both endpoints are in the node set
  const edges = db.prepare(
    `SELECT source_id AS source, target_id AS target, type FROM relations
     WHERE source_id IN (${placeholders}) AND target_id IN (${placeholders})`
  ).all(...idList, ...idList) as GraphEdge[];

  return { nodes, edges };
}

export function createGraphRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const params: GraphParams = {
      chapter: req.query.chapter as string | undefined,
      center: req.query.center as string | undefined,
      depth: req.query.depth ? parseInt(req.query.depth as string) : undefined,
    };
    res.json(getGraphData(db, params));
  });

  return router;
}
```

- [ ] **Step 3: Run tests**

```bash
npx vitest run tests/graph.test.ts
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add server/src/routes/graph.ts server/tests/graph.test.ts
git commit -m "feat(server): add Cytoscape-compatible graph endpoint"
```

---

### Task 8: Stats Route

**Files:**
- Create: `server/src/routes/stats.ts`

- [ ] **Step 1: Implement stats route**

```typescript
// server/src/routes/stats.ts
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
```

- [ ] **Step 2: Commit**

```bash
git add server/src/routes/stats.ts
git commit -m "feat(server): add stats endpoint"
```

---

### Task 9: Express App Entry Point

**Files:**
- Create: `server/src/index.ts`

- [ ] **Step 1: Implement Express app**

```typescript
// server/src/index.ts
import express from "express";
import cors from "cors";
import { getDb, closeDb } from "./db.js";
import { createConceptsRouter } from "./routes/concepts.js";
import { createRelationsRouter } from "./routes/relations.js";
import { createSearchRouter } from "./routes/search.js";
import { createPathRouter } from "./routes/path.js";
import { createGraphRouter } from "./routes/graph.js";
import { createStatsRouter } from "./routes/stats.js";

const app = express();
const PORT = parseInt(process.env.PORT || "3001");

app.use(cors());
app.use(express.json());

// Initialize DB and mount routes
const db = getDb();

app.use("/api/v1/concepts", createConceptsRouter(db));
app.use("/api/v1/relations", createRelationsRouter(db));
app.use("/api/v1/search", createSearchRouter(db));
app.use("/api/v1/path", createPathRouter(db));
app.use("/api/v1/graph", createGraphRouter(db));
app.use("/api/v1/stats", createStatsRouter(db));

// Health check
app.get("/api/v1/health", (_req, res) => {
  res.json({ status: "ok" });
});

const server = app.listen(PORT, () => {
  console.log(`MTGRuler API server running on http://localhost:${PORT}`);
  console.log(`  Endpoints: /api/v1/{concepts,relations,search,path,graph,stats}`);
});

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\nShutting down...");
  closeDb();
  server.close();
  process.exit(0);
});
```

- [ ] **Step 2: Start the server and test manually**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/server
npx tsx src/index.ts &
sleep 2

# Test endpoints
curl -s http://localhost:3001/api/v1/health | jq
curl -s http://localhost:3001/api/v1/stats | jq
curl -s "http://localhost:3001/api/v1/concepts?type=Keyword&limit=5" | jq
curl -s "http://localhost:3001/api/v1/search?q=飞行" | jq
curl -s "http://localhost:3001/api/v1/graph?chapter=7" | jq

kill %1
```

- [ ] **Step 3: Commit**

```bash
git add server/src/index.ts
git commit -m "feat(server): add Express entry point with all routes mounted"
```

---

## Completion

After all tasks, the server provides:
- `GET /api/v1/concepts` — list/filter/paginate concepts
- `GET /api/v1/concepts/:id` — concept detail with rule texts and related concepts
- `GET /api/v1/concepts/:id/neighbors` — BFS neighbors
- `GET /api/v1/relations` — list/filter relations
- `GET /api/v1/search?q=` — bilingual FTS5 search
- `GET /api/v1/path?from=&to=` — shortest path query
- `GET /api/v1/graph` — Cytoscape-compatible graph data
- `GET /api/v1/stats` — statistics

**Next:** Proceed to Phase 3 (Client) plan.
