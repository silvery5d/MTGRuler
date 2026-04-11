"""Tests for history.incremental_extract — focus on pure functions."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
from history.incremental_extract import (
    derive_chapter, collect_affected_refs, affected_chapters, merge_chapter,
)
from build_db import create_db


def test_derive_chapter():
    assert derive_chapter("100.1") == "1"
    assert derive_chapter("702.9a") == "7"
    assert derive_chapter("999.99z") == "9"
    assert derive_chapter("") is None
    assert derive_chapter(None) is None


def test_collect_affected_refs():
    diff = {
        "changes": [
            {"old": None, "new": {"ruleNumber": "100.1", "ruleText": "X"}},
            {"old": {"ruleNumber": "200.2", "ruleText": "Y"}, "new": None},
            {"old": {"ruleNumber": "300.3", "ruleText": "A"},
             "new": {"ruleNumber": "300.3", "ruleText": "B"}},
        ],
        "moves": [{"fromRule": "400.1", "toRule": "401.1"}],
    }
    refs = collect_affected_refs(diff)
    assert refs == {"100.1", "200.2", "300.3", "400.1", "401.1"}


def test_affected_chapters():
    refs = {"100.1", "702.9a", "405.2"}
    assert affected_chapters(refs) == {"1", "7", "4"}


def test_merge_chapter_replaces_concepts(tmp_path):
    db_path = tmp_path / "t.db"
    conn = create_db(db_path)
    conn.executemany(
        """INSERT INTO concepts (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ("keyword.old", "Old", "旧", "Keyword", "100.1", None, None, "1", 1, None),
            ("keyword.kept", "Kept", "保留", "Keyword", "200.1", None, None, "2", 1, None),
        ],
    )
    conn.commit()

    new_concepts = [
        {"id": "keyword.new", "name_en": "New", "name_cn": "新", "type": "Keyword",
         "rule_ref": "100.1", "definition_en": "...", "chapter": "1", "complexity": 2},
    ]
    merge_chapter(conn, "1", new_concepts, [])

    rows = conn.execute("SELECT id FROM concepts ORDER BY id").fetchall()
    ids = [r[0] for r in rows]
    assert "keyword.new" in ids
    assert "keyword.kept" in ids
    assert "keyword.old" not in ids
    conn.close()
