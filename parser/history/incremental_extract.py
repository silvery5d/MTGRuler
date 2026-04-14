"""Incrementally extract concepts for a new CR version using the previous
version's DB plus a diff (from Academy Ruins or computed locally)."""

import json
import shutil
import sqlite3
from pathlib import Path

from extract import extract_chapter
from build_db import dedupe_concepts, dedupe_relations
from .fetch import fetch_diff, DATA_DIR
from .parse_version import parse_version, to_rule_text_records
from .baseline_extract import CONCEPT_DBS_DIR


def derive_chapter(rule_ref: str) -> str | None:
    """Map a rule_ref like '702.9a' to its chapter ('7')."""
    if not rule_ref:
        return None
    head = rule_ref.split(".")[0]
    if head.isdigit() and len(head) >= 1:
        return head[0]
    return None


def collect_affected_refs(diff: dict) -> set[str]:
    """Extract all rule references mentioned in a diff (added, removed, modified, moved)."""
    refs: set[str] = set()
    for change in diff.get("changes", []):
        if change.get("old"):
            refs.add(change["old"]["ruleNumber"])
        if change.get("new"):
            refs.add(change["new"]["ruleNumber"])
    for move in diff.get("moves", []):
        if "fromRule" in move:
            refs.add(move["fromRule"])
        if "toRule" in move:
            refs.add(move["toRule"])
    return refs


def affected_chapters(refs: set[str]) -> set[str]:
    """Determine which chapters need re-extraction given a set of affected refs."""
    chapters: set[str] = set()
    for ref in refs:
        ch = derive_chapter(ref)
        if ch:
            chapters.add(ch)
    return chapters


def merge_chapter(
    db: sqlite3.Connection,
    chapter: str,
    new_concepts: list[dict],
    new_relations: list[dict],
    removed_refs: set[str] | None = None,
) -> None:
    """Merge newly extracted concepts/relations for a chapter into the DB.

    Strategy:
      - Only delete concepts whose rule_ref is in `removed_refs` (the rules
        that were explicitly deleted between versions).
      - Existing concepts NOT touched by the diff are preserved, even if the
        LLM re-extraction didn't re-emit them (avoids silent concept loss
        from LLM output variability).
      - New concepts (INSERT OR REPLACE) overwrite matching ids.
    """
    new_concepts = dedupe_concepts(new_concepts)
    new_relations = dedupe_relations(new_relations)

    # Only delete concepts tied to rules that were explicitly removed.
    if removed_refs:
        placeholders = ",".join(["?"] * len(removed_refs))
        rows = db.execute(
            f"SELECT id FROM concepts WHERE chapter = ? AND rule_ref IN ({placeholders})",
            [chapter, *removed_refs],
        ).fetchall()
        for (cid,) in rows:
            db.execute("DELETE FROM relations WHERE source_id = ? OR target_id = ?", (cid, cid))
            db.execute("DELETE FROM concepts WHERE id = ?", (cid,))

    for c in new_concepts:
        for opt in ("rule_ref", "definition_en", "definition_cn", "chapter", "complexity", "design_notes"):
            c.setdefault(opt, None)
        c.setdefault("chapter", chapter)
    db.executemany(
        """INSERT OR REPLACE INTO concepts
           (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
           VALUES (:id, :name_en, :name_cn, :type, :rule_ref, :definition_en, :definition_cn, :chapter, :complexity, :design_notes)""",
        new_concepts,
    )

    concept_ids_now = {row[0] for row in db.execute("SELECT id FROM concepts").fetchall()}
    valid_relations = [
        r for r in new_relations
        if r["source_id"] in concept_ids_now and r["target_id"] in concept_ids_now
    ]
    for r in valid_relations:
        r.setdefault("rule_ref", None)
        r.setdefault("description", None)
    db.executemany(
        """INSERT OR REPLACE INTO relations
           (source_id, target_id, type, rule_ref, description)
           VALUES (:source_id, :target_id, :type, :rule_ref, :description)""",
        valid_relations,
    )
    db.commit()


def collect_removed_refs(diff: dict) -> set[str]:
    """Rule refs that were deleted in this version (present in old, absent in new)."""
    refs: set[str] = set()
    for change in diff.get("changes", []):
        if change.get("old") and not change.get("new"):
            refs.add(change["old"]["ruleNumber"])
    return refs


def replace_rule_texts(db: sqlite3.Connection, records: list[dict]) -> None:
    """Replace the rule_texts table with the new version's records."""
    db.execute("DELETE FROM rule_texts")
    db.execute("DELETE FROM rule_texts_fts")
    rule_ref_to_concept = {
        row[0]: row[1]
        for row in db.execute("SELECT rule_ref, id FROM concepts WHERE rule_ref IS NOT NULL").fetchall()
    }
    for r in records:
        parent = rule_ref_to_concept.get(r["rule_ref"])
        if not parent:
            base_ref = r["rule_ref"].rstrip("abcdefghijklmnopqrstuvwxyz")
            parent = rule_ref_to_concept.get(base_ref)
        r["parent_concept_id"] = parent
    db.executemany(
        """INSERT OR REPLACE INTO rule_texts (rule_ref, text_en, text_cn, parent_concept_id)
           VALUES (:rule_ref, :text_en, :text_cn, :parent_concept_id)""",
        records,
    )
    db.executemany(
        """INSERT OR REPLACE INTO rule_texts_fts (rule_ref, text_en, text_cn)
           VALUES (:rule_ref, :text_en, :text_cn)""",
        [{"rule_ref": r["rule_ref"], "text_en": r["text_en"], "text_cn": r["text_cn"]} for r in records],
    )
    db.commit()


def compute_local_diff(prev_set: str, curr_set: str) -> dict:
    """Compute a diff locally by parsing both versions and comparing rule_refs."""
    prev_chapters = parse_version(prev_set)
    curr_chapters = parse_version(curr_set)

    prev_rules: dict[str, str] = {}
    for entries in prev_chapters.values():
        for e in entries:
            prev_rules[e["rule_ref"]] = e["text"]

    curr_rules: dict[str, str] = {}
    for entries in curr_chapters.values():
        for e in entries:
            curr_rules[e["rule_ref"]] = e["text"]

    changes = []
    for ref in sorted(set(prev_rules) | set(curr_rules)):
        old_text = prev_rules.get(ref)
        new_text = curr_rules.get(ref)
        if old_text and not new_text:
            changes.append({"old": {"ruleNumber": ref, "ruleText": old_text}, "new": None})
        elif new_text and not old_text:
            changes.append({"old": None, "new": {"ruleNumber": ref, "ruleText": new_text}})
        elif old_text != new_text:
            changes.append({
                "old": {"ruleNumber": ref, "ruleText": old_text},
                "new": {"ruleNumber": ref, "ruleText": new_text},
            })

    return {"sourceCode": prev_set, "destCode": curr_set, "changes": changes, "moves": []}


def get_diff(prev_set: str, curr_set: str) -> dict:
    """Get diff: try Academy Ruins first, fall back to local computation."""
    try:
        return fetch_diff(prev_set, curr_set)
    except (ValueError, Exception):
        print(f"    No Academy Ruins diff for {prev_set}→{curr_set}, computing locally...")
        return compute_local_diff(prev_set, curr_set)


def incremental_extract(prev_set: str, curr_set: str, force: bool = False) -> Path:
    """Build curr_set.db from prev_set.db using diff (Academy Ruins or local)."""
    prev_set = prev_set.upper()
    curr_set = curr_set.upper()
    prev_db = CONCEPT_DBS_DIR / f"{prev_set}.db"
    curr_db = CONCEPT_DBS_DIR / f"{curr_set}.db"

    if curr_db.exists() and not force:
        print(f"  {curr_set}.db already exists, skipping")
        return curr_db

    if not prev_db.exists():
        raise FileNotFoundError(f"Previous DB {prev_db} not found — run baseline_extract first")

    print(f"  Copying {prev_set}.db → {curr_set}.db")
    shutil.copy(prev_db, curr_db)

    print(f"  Getting diff {prev_set} → {curr_set}")
    diff = get_diff(prev_set, curr_set)

    affected_refs = collect_affected_refs(diff)
    removed_refs = collect_removed_refs(diff)
    chapters_to_redo = affected_chapters(affected_refs)
    print(f"  {len(affected_refs)} affected refs ({len(removed_refs)} removed), {len(chapters_to_redo)} chapters to re-extract")

    if not chapters_to_redo:
        print(f"  No structural changes; just updating rule_texts")
    else:
        chapters = parse_version(curr_set)
        new_records = to_rule_text_records(chapters)

        affected_aligned = {
            chapter: [
                {"rule_ref": e["rule_ref"], "text_en": e["text"], "text_cn": ""}
                for e in chapters.get(chapter, [])
            ]
            for chapter in chapters_to_redo
            if chapter in chapters
        }

        db = sqlite3.connect(curr_db)
        try:
            for chapter, entries in affected_aligned.items():
                print(f"    Re-extracting chapter {chapter} ({len(entries)} entries)...")
                concepts, relations = extract_chapter(
                    entries, f"hist_{curr_set}_{chapter}", force=force,
                )
                # Filter removed_refs to this chapter
                chapter_removed = {r for r in removed_refs if derive_chapter(r) == chapter}
                merge_chapter(db, chapter, concepts, relations, chapter_removed)

            replace_rule_texts(db, new_records)
        finally:
            db.close()

    print(f"  Normalizing relations in {curr_set}.db")
    _normalize_in_place(curr_db)

    print(f"  Done: {curr_db}")
    return curr_db


def _normalize_in_place(db_path: Path) -> None:
    """Apply relation normalization to a single DB in place."""
    from normalize_relations import normalize_type
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT source_id, target_id, type, rule_ref, description FROM relations"
        ).fetchall()
        kept = []
        for src, tgt, t, rule_ref, desc in rows:
            new_type, _, swapped = normalize_type(t, src, tgt)
            if new_type is None:
                continue
            if swapped is not None:
                src, tgt = swapped
            kept.append((src, tgt, new_type, rule_ref, desc))

        deduped: dict[tuple, tuple] = {}
        for row in kept:
            key = (row[0], row[1], row[2])
            deduped.setdefault(key, row)

        conn.execute("DELETE FROM relations")
        conn.executemany(
            "INSERT INTO relations (source_id, target_id, type, rule_ref, description) VALUES (?, ?, ?, ?, ?)",
            list(deduped.values()),
        )
        conn.commit()
    finally:
        conn.close()
