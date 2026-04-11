"""Run a full LLM extraction on a single historical CR version (the baseline).

Used once at the start of the history pipeline to bootstrap the chain.
After this, incremental_extract.py handles all subsequent versions.
"""

import json
import sqlite3
from pathlib import Path

from extract import extract_all
from build_db import (
    create_db, dedupe_concepts, dedupe_relations,
    insert_concepts, insert_relations, insert_rule_texts,
)
from .fetch import DATA_DIR
from .parse_version import parse_version, to_rule_text_records

CONCEPT_DBS_DIR = DATA_DIR / "concept_dbs"


def baseline_extract(set_code: str, force: bool = False) -> Path:
    """Run full LLM extraction on a single version, producing concept_dbs/{set_code}.db.

    This is expensive (~9 LLM calls × N batches per chapter). Only call once
    per pipeline run on the earliest version. Returns the path to the DB.
    """
    set_code = set_code.upper()
    CONCEPT_DBS_DIR.mkdir(parents=True, exist_ok=True)
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"

    if db_path.exists() and not force:
        print(f"  Baseline DB already exists at {db_path}")
        return db_path

    print(f"  Parsing {set_code} CR text...")
    chapters = parse_version(set_code)
    total_entries = sum(len(v) for v in chapters.values())
    print(f"  {len(chapters)} chapters, {total_entries} rule entries")

    aligned_by_chapter = {
        chapter: [
            {"rule_ref": e["rule_ref"], "text_en": e["text"], "text_cn": ""}
            for e in entries
        ]
        for chapter, entries in chapters.items()
    }

    print(f"  Running full LLM extraction (this is expensive)...")
    concepts, relations = extract_all(aligned_by_chapter, force=force)

    if db_path.exists():
        db_path.unlink()

    concepts = dedupe_concepts(concepts)
    relations = dedupe_relations(relations)

    concept_ids = {c["id"] for c in concepts}
    relations = [
        r for r in relations
        if r["source_id"] in concept_ids and r["target_id"] in concept_ids
    ]

    rule_ref_to_concept = {c["rule_ref"]: c["id"] for c in concepts if c.get("rule_ref")}
    rule_text_records = to_rule_text_records(chapters)
    for r in rule_text_records:
        parent = rule_ref_to_concept.get(r["rule_ref"])
        if not parent:
            base_ref = r["rule_ref"].rstrip("abcdefghijklmnopqrstuvwxyz")
            parent = rule_ref_to_concept.get(base_ref)
        r["parent_concept_id"] = parent

    conn = create_db(db_path)
    insert_concepts(conn, concepts)
    insert_relations(conn, relations)
    insert_rule_texts(conn, rule_text_records)
    conn.close()

    print(f"  Baseline DB built: {len(concepts)} concepts, {len(relations)} relations")
    print(f"  Saved to {db_path}")
    return db_path
