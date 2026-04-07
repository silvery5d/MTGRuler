import sqlite3
import tempfile
from pathlib import Path


def test_create_db_and_insert():
    """Test DB creation, insertion, and querying."""
    from build_db import create_db, insert_concepts, insert_relations, insert_rule_texts

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = create_db(db_path)

        concepts = [
            {
                "id": "keyword.flying",
                "name_en": "Flying",
                "name_cn": "飞行",
                "type": "Keyword",
                "rule_ref": "702.9",
                "definition_en": "Can't be blocked except by flying/reach",
                "definition_cn": "不能被不具飞行或延势的生物阻挡",
                "chapter": "7",
                "complexity": 2,
                "design_notes": "Core evasion",
            },
            {
                "id": "keyword.reach",
                "name_en": "Reach",
                "name_cn": "延势",
                "type": "Keyword",
                "rule_ref": "702.17",
                "definition_en": "Can block creatures with flying",
                "definition_cn": "可以阻挡具有飞行的生物",
                "chapter": "7",
                "complexity": 1,
                "design_notes": "Flying counter",
            },
        ]

        relations = [
            {
                "source_id": "keyword.flying",
                "target_id": "keyword.reach",
                "type": "INTERACTS_WITH",
                "rule_ref": "702.9a",
                "description": "Reach can block flying",
            }
        ]

        rule_texts = [
            {
                "rule_ref": "702.9",
                "text_en": "Flying is a keyword ability.",
                "text_cn": "飞行是关键字异能。",
                "parent_concept_id": "keyword.flying",
            },
            {
                "rule_ref": "702.9a",
                "text_en": "A creature with flying can't be blocked except...",
                "text_cn": "具有飞行异能的生物不能被阻挡除非...",
                "parent_concept_id": "keyword.flying",
            },
        ]

        insert_concepts(conn, concepts)
        insert_relations(conn, relations)
        insert_rule_texts(conn, rule_texts)

        cur = conn.execute("SELECT COUNT(*) FROM concepts")
        assert cur.fetchone()[0] == 2

        cur = conn.execute("SELECT COUNT(*) FROM relations")
        assert cur.fetchone()[0] == 1

        cur = conn.execute("SELECT COUNT(*) FROM rule_texts")
        assert cur.fetchone()[0] == 2

        # FTS search
        cur = conn.execute(
            "SELECT rule_ref FROM rule_texts_fts WHERE rule_texts_fts MATCH ?",
            ("飞行",),
        )
        results = [r[0] for r in cur.fetchall()]
        assert "702.9" in results

        conn.close()


def test_dedupe_concepts():
    """Test that duplicate concept IDs are handled."""
    from build_db import dedupe_concepts

    concepts = [
        {"id": "keyword.flying", "name_en": "Flying", "complexity": 2},
        {"id": "keyword.flying", "name_en": "Flying", "complexity": 3},
        {"id": "keyword.reach", "name_en": "Reach", "complexity": 1},
    ]
    deduped = dedupe_concepts(concepts)
    assert len(deduped) == 2
    ids = [c["id"] for c in deduped]
    assert ids.count("keyword.flying") == 1
