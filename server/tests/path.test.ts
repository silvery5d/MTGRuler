import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { findShortestPath } from "../src/utils/pathfinder.js";

let db: Database.Database;

beforeAll(() => {
  db = createTestDb();
});
afterAll(() => {
  db.close();
});

describe("findShortestPath", () => {
  it("finds direct path between connected nodes", () => {
    const path = findShortestPath(db, "keyword.flying", "keyword.reach");
    expect(path).not.toBeNull();
    expect(path!.nodes.length).toBe(2);
    expect(path!.nodes[0].id).toBe("keyword.flying");
    expect(path!.nodes[1].id).toBe("keyword.reach");
    expect(path!.edges.length).toBe(1);
  });

  it("finds direct path stack -> priority", () => {
    const path = findShortestPath(db, "concept.stack", "concept.priority");
    expect(path).not.toBeNull();
    expect(path!.nodes.length).toBe(2);
  });

  it("returns null for disconnected nodes", () => {
    const path = findShortestPath(db, "concept.priority", "keyword.reach");
    expect(path).toBeNull();
  });
});
