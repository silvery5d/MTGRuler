import { describe, it, expect } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";

describe("history routes (smoke)", () => {
  it("test DB has concepts table", () => {
    const db: Database.Database = createTestDb();
    const count = (db.prepare("SELECT COUNT(*) as c FROM concepts").get() as any).c;
    expect(count).toBeGreaterThan(0);
    db.close();
  });
});
