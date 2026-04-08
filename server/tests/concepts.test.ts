import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
import {
  getConceptsList,
  getConceptById,
  getConceptNeighbors,
} from "../src/routes/concepts.js";

let db: Database.Database;

beforeAll(() => {
  db = createTestDb();
});
afterAll(() => {
  db.close();
});

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
