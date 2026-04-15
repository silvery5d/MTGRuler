"""Post-processing pass over history DBs to fix two quality issues.

1. Concept interpolation: if concept X exists in version A and version B
   (chronologically), ensure all versions between A and B also have X.
   LLM output variability caused concepts to "flicker" in/out across versions
   even when they obviously still existed in the game.

2. Multi-edge collapsing: between any (source, target) node pair, keep at
   most one canonical relation type. When multiple exist (e.g. cost→mana
   had 8 different types), pick the most informative by priority.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .walk_versions import load_versions_index
from .baseline_extract import CONCEPT_DBS_DIR


# Priority: higher priority relation types win when multiple exist
# between the same pair. Roughly ordered from most to least informative.
RELATION_PRIORITY = [
    "DEPENDS_ON",
    "CREATES",
    "MODIFIES",
    "CONTAINS",
    "OCCURS_IN",
    "MOVES_TO",
    "PATTERN_OF",
    "INTERACTS_WITH",
    "REFERENCES",
]


def interpolate_concepts(versions: list[dict]) -> dict:
    """For each concept, fill gaps between first and last occurrence.

    Returns a stats dict.
    """
    existing = [v for v in versions if (CONCEPT_DBS_DIR / f"{v['set_code']}.db").exists()]
    if len(existing) < 3:
        return {"interpolated": 0, "concepts_touched": 0}

    # Step 1: build presence matrix {concept_id: set(set_codes)} + store concept data from each version
    print(f"  Scanning {len(existing)} versions for concept presence...")
    presence: dict[str, set[str]] = {}
    # For each concept_id, remember the most recent version's data (we'll copy from there)
    source_data: dict[str, dict] = {}

    for v in existing:
        db_path = CONCEPT_DBS_DIR / f"{v['set_code']}.db"
        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute(
                "SELECT id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes FROM concepts"
            ).fetchall()
            for r in rows:
                cid = r[0]
                presence.setdefault(cid, set()).add(v["set_code"])
                # Always overwrite: source_data ends up with data from the LAST version that has this concept
                source_data[cid] = {
                    "id": r[0], "name_en": r[1], "name_cn": r[2], "type": r[3],
                    "rule_ref": r[4], "definition_en": r[5], "definition_cn": r[6],
                    "chapter": r[7], "complexity": r[8], "design_notes": r[9],
                }
        finally:
            conn.close()

    # Step 2: for each concept, find first and last version that has it
    # then check which versions between are missing, and insert there
    total_inserts = 0
    concepts_interpolated = 0
    version_order = {v["set_code"]: i for i, v in enumerate(existing)}

    for cid, versions_with in presence.items():
        if len(versions_with) < 2:
            continue
        indices = sorted(version_order[c] for c in versions_with)
        first_idx, last_idx = indices[0], indices[-1]
        # Gap count
        gap_indices = [i for i in range(first_idx, last_idx + 1) if existing[i]["set_code"] not in versions_with]
        if not gap_indices:
            continue

        # Collect data from any version that has this concept — use source_data
        c_data = source_data[cid]
        for idx in gap_indices:
            code = existing[idx]["set_code"]
            db_path = CONCEPT_DBS_DIR / f"{code}.db"
            conn = sqlite3.connect(db_path)
            try:
                # Safety: skip if somehow already present
                existing_row = conn.execute("SELECT 1 FROM concepts WHERE id = ?", (cid,)).fetchone()
                if existing_row:
                    continue
                conn.execute(
                    """INSERT INTO concepts (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
                       VALUES (:id, :name_en, :name_cn, :type, :rule_ref, :definition_en, :definition_cn, :chapter, :complexity, :design_notes)""",
                    c_data,
                )
                conn.commit()
                total_inserts += 1
            finally:
                conn.close()
        concepts_interpolated += 1

    return {"interpolated": total_inserts, "concepts_touched": concepts_interpolated}


def collapse_multi_edges(versions: list[dict]) -> dict:
    """Between each (source, target) pair, keep only the highest-priority relation type."""
    priority_rank = {t: i for i, t in enumerate(RELATION_PRIORITY)}
    existing = [v for v in versions if (CONCEPT_DBS_DIR / f"{v['set_code']}.db").exists()]

    total_removed = 0
    pairs_collapsed = 0
    for v in existing:
        db_path = CONCEPT_DBS_DIR / f"{v['set_code']}.db"
        conn = sqlite3.connect(db_path)
        try:
            # Find all (src, tgt) pairs with multiple relations
            pairs = conn.execute("""
                SELECT source_id, target_id
                FROM relations
                GROUP BY source_id, target_id
                HAVING COUNT(*) > 1
            """).fetchall()

            for src, tgt in pairs:
                rows = conn.execute(
                    "SELECT type, rule_ref, description FROM relations WHERE source_id = ? AND target_id = ?",
                    (src, tgt),
                ).fetchall()
                # Pick the best by priority (lower rank wins). Unknown types fall to the end.
                best = min(rows, key=lambda r: priority_rank.get(r[0], 999))
                # Delete all, reinsert best
                conn.execute("DELETE FROM relations WHERE source_id = ? AND target_id = ?", (src, tgt))
                conn.execute(
                    "INSERT INTO relations (source_id, target_id, type, rule_ref, description) VALUES (?, ?, ?, ?, ?)",
                    (src, tgt, best[0], best[1], best[2]),
                )
                total_removed += len(rows) - 1
                pairs_collapsed += 1
            conn.commit()
        finally:
            conn.close()

    return {"pairs_collapsed": pairs_collapsed, "edges_removed": total_removed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interpolate", action="store_true", help="Fill concept gaps across versions")
    ap.add_argument("--collapse-edges", action="store_true", help="Keep only one relation type per node pair")
    ap.add_argument("--all", action="store_true", help="Run everything")
    args = ap.parse_args()

    if args.all:
        args.interpolate = True
        args.collapse_edges = True

    if not (args.interpolate or args.collapse_edges):
        print("Nothing to do. Pass --interpolate, --collapse-edges, or --all")
        return 1

    versions = load_versions_index()
    print(f"Loaded {len(versions)} versions from index")

    if args.interpolate:
        print("\n[1] Interpolating missing concepts across versions...")
        stats = interpolate_concepts(versions)
        print(f"  Inserted {stats['interpolated']} concept rows across {stats['concepts_touched']} concept ids")

    if args.collapse_edges:
        print("\n[2] Collapsing multi-edges between node pairs...")
        stats = collapse_multi_edges(versions)
        print(f"  Collapsed {stats['pairs_collapsed']} pairs, removed {stats['edges_removed']} redundant edges")

    print("\nDone. Re-run metrics/spikes to reflect changes:")
    print("  python -m history.run_history_pipeline --skip-extract --force")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
