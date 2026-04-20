import { Router } from "express";
import Database from "better-sqlite3";
import { existsSync, readdirSync, readFileSync } from "fs";
import { resolve, basename } from "path";
import type {
  Concept, GraphData, GraphNode, GraphEdge, RuleText,
  VersionInfo, MetricsRecord, SpikeRecord,
} from "../types.js";
import { computeUnderstandingComplexity } from "../utils/understanding-complexity.js";

const HISTORY_DIR =
  process.env.HISTORY_DIR ||
  resolve(import.meta.dirname, "../../../parser/data/history");

interface VersionEntry {
  db: Database.Database;
  ucCache: Map<string, number>;
  info: VersionInfo;
}

const versions = new Map<string, VersionEntry>();
let metricsCache: MetricsRecord[] = [];
let spikesCache: SpikeRecord[] = [];
let versionsIndex: VersionInfo[] = [];

export function loadHistory(): void {
  if (!existsSync(HISTORY_DIR)) {
    console.warn(`History dir not found: ${HISTORY_DIR}`);
    return;
  }

  const indexPath = resolve(HISTORY_DIR, "versions_index.json");
  if (existsSync(indexPath)) {
    versionsIndex = JSON.parse(readFileSync(indexPath, "utf-8"));
  }

  const metricsPath = resolve(HISTORY_DIR, "metrics.json");
  if (existsSync(metricsPath)) {
    metricsCache = JSON.parse(readFileSync(metricsPath, "utf-8"));
  }

  const spikesPath = resolve(HISTORY_DIR, "spikes.json");
  if (existsSync(spikesPath)) {
    spikesCache = JSON.parse(readFileSync(spikesPath, "utf-8"));
  }

  const conceptDbsDir = resolve(HISTORY_DIR, "concept_dbs");
  if (!existsSync(conceptDbsDir)) return;
  const dbFiles = readdirSync(conceptDbsDir).filter((f) => f.endsWith(".db"));
  for (const file of dbFiles) {
    const setCode = basename(file, ".db");
    const dbPath = resolve(conceptDbsDir, file);
    const db = new Database(dbPath, { readonly: true });
    const ucCache = computeUnderstandingComplexity(db);
    const info = versionsIndex.find((v) => v.set_code === setCode) || {
      set_code: setCode, set_name: setCode, release_date: null,
      prev_set_code: null, next_set_code: null,
    };
    versions.set(setCode, { db, ucCache, info });
  }
  console.log(`  Loaded ${versions.size} historical versions`);
}

function getVersion(setCode: string): VersionEntry | undefined {
  return versions.get(setCode.toUpperCase());
}

function buildGraphData(db: Database.Database, ucCache: Map<string, number>): GraphData {
  const rawNodes = db.prepare(
    `SELECT id, name_en, name_cn, type, complexity FROM concepts`,
  ).all() as GraphNode[];
  const nodes = rawNodes.map((n) => ({
    ...n,
    understanding_complexity: ucCache.get(n.id) ?? null,
  }));
  const edges = db.prepare(
    `SELECT source_id AS source, target_id AS target, type FROM relations`,
  ).all() as GraphEdge[];
  return { nodes, edges };
}

export function createHistoryRouter(): Router {
  const router = Router();

  router.get("/versions", (_req, res) => {
    res.json(versionsIndex);
  });

  router.get("/metrics", (_req, res) => {
    res.json(metricsCache);
  });

  router.get("/spikes", (_req, res) => {
    res.json(spikesCache);
  });

  router.get("/diff", (req, res) => {
    const oldCode = (req.query.old as string)?.toUpperCase();
    const newCode = (req.query.new as string)?.toUpperCase();
    if (!oldCode || !newCode) {
      res.status(400).json({ error: "old and new query params required" });
      return;
    }
    const oldVer = getVersion(oldCode);
    const newVer = getVersion(newCode);
    if (!oldVer || !newVer) {
      res.status(404).json({ error: "version not found" });
      return;
    }

    const oldIds = new Set(
      (oldVer.db.prepare("SELECT id FROM concepts").all() as { id: string }[]).map((r) => r.id),
    );
    const newRows = newVer.db.prepare(
      "SELECT id, name_en, name_cn, type, complexity, definition_en FROM concepts",
    ).all() as Concept[];
    const oldRows = oldVer.db.prepare(
      "SELECT id, name_en, name_cn, type, complexity, definition_en FROM concepts",
    ).all() as Concept[];
    const newIds = new Set(newRows.map((c) => c.id));

    const addedRaw = newRows.filter((c) => !oldIds.has(c.id));
    const removedRaw = oldRows.filter((c) => !newIds.has(c.id));

    // Known historical MTG concept renames (name changed officially)
    const KNOWN_RENAMES: Record<string, string> = {
      "zone.removed_from_game": "zone.exile",
      "concept.removed_from_the_game": "zone.exile",
      "concept.converted_mana_cost": "concept.mana_value",
      "concept.local_enchantment": "concept.aura",
      "concept.global_enchantment": "concept.enchantment",
      "concept.bury": "action.destroy",
      "concept.in_play": "zone.battlefield",
      "zone.in_play": "zone.battlefield",
    };

    // Detect likely renames: match removed→added by name_en similarity
    const renamed: { old_id: string; new_id: string; old_name: string; new_name: string; confidence: "high" | "medium" }[] = [];
    const matchedOldIds = new Set<string>();
    const matchedNewIds = new Set<string>();

    // Pass 0: known historical renames
    for (const old of removedRaw) {
      const knownNew = KNOWN_RENAMES[old.id];
      if (knownNew) {
        const match = addedRaw.find((n) => !matchedNewIds.has(n.id) && n.id === knownNew);
        if (match) {
          renamed.push({ old_id: old.id, new_id: match.id, old_name: old.name_en, new_name: match.name_en, confidence: "high" });
          matchedOldIds.add(old.id);
          matchedNewIds.add(match.id);
        }
      }
    }

    for (const old of removedRaw) {
      if (matchedOldIds.has(old.id)) continue;
      const oldName = (old.name_en || "").toLowerCase().trim();
      if (oldName.length < 2) continue;

      // High confidence: exact name match (different ID, same name)
      let best = addedRaw.find(
        (n) => !matchedNewIds.has(n.id) && (n.name_en || "").toLowerCase().trim() === oldName,
      );
      let confidence: "high" | "medium" = "high";

      // Medium confidence: same slug AND names share a significant word
      if (!best) {
        const oldSlug = old.id.split(".").pop() || "";
        if (oldSlug.length > 5) {
          const oldWords = new Set(oldName.split(/\s+/).filter((w) => w.length > 3));
          best = addedRaw.find((n) => {
            if (matchedNewIds.has(n.id)) return false;
            if (n.id.split(".").pop() !== oldSlug) return false;
            // Names must share >50% of significant words (avoids generic matches like "spell")
            const newWords = (n.name_en || "").toLowerCase().split(/\s+/).filter((w) => w.length > 3);
            const shared = newWords.filter((w) => oldWords.has(w)).length;
            const shorter = Math.min(oldWords.size, newWords.length);
            return shorter > 0 && shared / shorter > 0.5;
          });
          confidence = "medium";
        }
      }

      if (best) {
        renamed.push({ old_id: old.id, new_id: best.id, old_name: old.name_en, new_name: best.name_en, confidence });
        matchedOldIds.add(old.id);
        matchedNewIds.add(best.id);
      }
    }

    const added = addedRaw.filter((c) => !matchedNewIds.has(c.id));
    const removed = removedRaw.filter((c) => !matchedOldIds.has(c.id));

    res.json({ added, removed, renamed, old_set: oldCode, new_set: newCode });
  });

  router.get("/concept-trace/:id", (req, res) => {
    const conceptId = req.params.id;
    const trace: any[] = [];
    for (const version of versionsIndex) {
      const entry = versions.get(version.set_code);
      if (!entry) continue;
      const row = entry.db.prepare(
        "SELECT id, name_en, complexity, definition_en FROM concepts WHERE id = ?",
      ).get(conceptId) as Concept | undefined;
      if (row) {
        trace.push({
          set_code: version.set_code,
          release_date: version.release_date,
          complexity: row.complexity,
          understanding_complexity: entry.ucCache.get(conceptId) ?? null,
          definition_en: row.definition_en,
        });
      }
    }
    res.json(trace);
  });

  router.get("/:set_code/concepts", (req, res) => {
    const ver = getVersion(req.params.set_code);
    if (!ver) { res.status(404).json({ error: "version not found" }); return; }
    const concepts = ver.db.prepare("SELECT * FROM concepts").all() as Concept[];
    res.json(concepts.map((c) => ({ ...c, understanding_complexity: ver.ucCache.get(c.id) ?? null })));
  });

  router.get("/:set_code/concepts/:id", (req, res) => {
    const ver = getVersion(req.params.set_code);
    if (!ver) { res.status(404).json({ error: "version not found" }); return; }
    const concept = ver.db.prepare("SELECT * FROM concepts WHERE id = ?").get(req.params.id) as Concept | undefined;
    if (!concept) { res.status(404).json({ error: "concept not found" }); return; }
    const rule_texts = ver.db.prepare(
      "SELECT * FROM rule_texts WHERE parent_concept_id = ?",
    ).all(req.params.id) as RuleText[];
    const related = ver.db.prepare(
      `SELECT DISTINCT c.* FROM concepts c
       JOIN relations r ON (r.target_id = c.id AND r.source_id = ?)
                        OR (r.source_id = c.id AND r.target_id = ?)`,
    ).all(req.params.id, req.params.id) as Concept[];
    res.json({
      concept: { ...concept, understanding_complexity: ver.ucCache.get(concept.id) ?? null },
      rule_texts,
      related: related.map((c) => ({ ...c, understanding_complexity: ver.ucCache.get(c.id) ?? null })),
    });
  });

  router.get("/:set_code/graph", (req, res) => {
    const ver = getVersion(req.params.set_code);
    if (!ver) { res.status(404).json({ error: "version not found" }); return; }
    res.json(buildGraphData(ver.db, ver.ucCache));
  });

  return router;
}

export function closeHistory(): void {
  for (const v of versions.values()) v.db.close();
  versions.clear();
}
