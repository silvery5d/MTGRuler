"""Tests for history.metrics — uses synthetic in-memory DBs."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
from build_db import create_db
from history.metrics import compute_understanding_complexity, _compute_max_chain


def test_uc_simple_chain(tmp_path):
    db_path = tmp_path / "t.db"
    conn = create_db(db_path)
    conn.executemany(
        """INSERT INTO concepts (id, name_en, name_cn, type, complexity)
           VALUES (?, ?, ?, ?, ?)""",
        [
            ("a", "A", "甲", "Concept", 2),
            ("b", "B", "乙", "Concept", 3),
            ("c", "C", "丙", "Concept", 1),
        ],
    )
    conn.executemany(
        """INSERT INTO relations (source_id, target_id, type) VALUES (?, ?, ?)""",
        [("a", "b", "DEPENDS_ON"), ("b", "c", "DEPENDS_ON")],
    )
    conn.commit()

    uc = compute_understanding_complexity(conn)
    assert uc["c"] == 1
    assert uc["b"] == 4
    assert uc["a"] == 6
    conn.close()


def test_uc_handles_cycle(tmp_path):
    db_path = tmp_path / "t.db"
    conn = create_db(db_path)
    conn.executemany(
        """INSERT INTO concepts (id, name_en, name_cn, type, complexity) VALUES (?, ?, ?, ?, ?)""",
        [("a", "A", "甲", "Concept", 1), ("b", "B", "乙", "Concept", 1)],
    )
    conn.executemany(
        """INSERT INTO relations (source_id, target_id, type) VALUES (?, ?, ?)""",
        [("a", "b", "DEPENDS_ON"), ("b", "a", "DEPENDS_ON")],
    )
    conn.commit()
    uc = compute_understanding_complexity(conn)
    assert uc["a"] >= 1
    assert uc["b"] >= 1
    conn.close()


def test_max_chain(tmp_path):
    db_path = tmp_path / "t.db"
    conn = create_db(db_path)
    conn.executemany(
        """INSERT INTO concepts (id, name_en, name_cn, type) VALUES (?, ?, ?, ?)""",
        [("a", "A", "甲", "Concept"), ("b", "B", "乙", "Concept"),
         ("c", "C", "丙", "Concept"), ("d", "D", "丁", "Concept")],
    )
    conn.executemany(
        """INSERT INTO relations (source_id, target_id, type) VALUES (?, ?, ?)""",
        [("a", "b", "DEPENDS_ON"), ("b", "c", "DEPENDS_ON"), ("c", "d", "DEPENDS_ON")],
    )
    conn.commit()
    assert _compute_max_chain(conn) == 3
    conn.close()
