import Database from "better-sqlite3";
import { existsSync } from "fs";
import { resolve } from "path";

// concepts.db is the final curated DB (normalized relations + concept fixes).
// The raw LLM output lives in concepts_raw.db for rebuild/audit purposes.
const DB_PATH =
  process.env.DB_PATH ||
  resolve(import.meta.dirname, "../../parser/data/concepts.db");

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    if (!existsSync(DB_PATH)) {
      throw new Error(
        `Database not found at ${DB_PATH}. Run the parser pipeline first.`,
      );
    }
    db = new Database(DB_PATH, { readonly: true });
  }
  return db;
}

export function closeDb(): void {
  if (db) {
    db.close();
    db = null;
  }
}
