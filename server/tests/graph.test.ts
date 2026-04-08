import { describe, it, expect, beforeAll, afterAll } from "vitest";
import type Database from "better-sqlite3";
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
    expect(result.nodes.every((n) => n.type === "Keyword")).toBe(true);
    expect(result.edges.length).toBeGreaterThan(0);
  });

  it("returns ego-centric subgraph", () => {
    const result = getGraphData(db, { center: "keyword.flying", depth: 1 });
    expect(result.nodes.some((n) => n.id === "keyword.flying")).toBe(true);
    expect(result.nodes.some((n) => n.id === "keyword.reach")).toBe(true);
  });
});
