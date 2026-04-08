import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import { searchConcepts, rewriteCjkQuery } from "../src/routes/search.js";

let db: Database.Database;

beforeAll(() => {
  db = createTestDb();
});
afterAll(() => {
  db.close();
});

describe("rewriteCjkQuery", () => {
  it("inserts spaces between consecutive Han characters", () => {
    expect(rewriteCjkQuery("飞行")).toBe("飞 行");
    expect(rewriteCjkQuery("战斗阶段")).toBe("战 斗 阶 段");
  });

  it("leaves ASCII alone", () => {
    expect(rewriteCjkQuery("Flying")).toBe("Flying");
  });

  it("handles mixed content", () => {
    expect(rewriteCjkQuery("Flying 飞行")).toBe("Flying 飞 行");
  });
});

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
    expect(results.every((r: any) => r.type === "Concept")).toBe(true);
  });

  it("returns empty for no match", () => {
    const results = searchConcepts(db, "xyznonexistent");
    expect(results.length).toBe(0);
  });
});
