"""Build the SQLite database from extracted concepts and relations."""

import json
import re
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Range for CJK Unified Ideographs (covers both Simplified and Traditional Chinese
# characters used in the rules). We space-separate these characters at index and
# query time so SQLite's default unicode61 FTS5 tokenizer treats each character as
# its own token. This is necessary because unicode61 otherwise lumps consecutive
# CJK characters into a single token, and the trigram tokenizer cannot match
# 2-character queries like "飞行".
_CJK_RE = re.compile(r"[\u3400-\u9fff]")


def _cjk_tokenize(text: str | None) -> str | None:
    """Insert spaces between consecutive CJK characters so unicode61 can index
    them as individual tokens. Non-CJK text is left untouched."""
    if not text:
        return text
    return _CJK_RE.sub(lambda m: m.group(0) + " ", text).rstrip()


class _FTSConnection(sqlite3.Connection):
    """sqlite3.Connection subclass that transparently CJK-tokenizes parameters
    bound to FTS5 MATCH expressions, so callers can use natural-language CJK
    queries without manual preprocessing."""

    _MATCH_RE = re.compile(r"\bMATCH\b", re.IGNORECASE)

    def _maybe_transform(self, sql: str, params):
        if not params or not isinstance(sql, str) or not self._MATCH_RE.search(sql):
            return params
        if isinstance(params, dict):
            return {
                k: (_cjk_tokenize(v) if isinstance(v, str) else v)
                for k, v in params.items()
            }
        return tuple(_cjk_tokenize(p) if isinstance(p, str) else p for p in params)

    def execute(self, sql, params=()):  # type: ignore[override]
        return super().execute(sql, self._maybe_transform(sql, params))

    def executemany(self, sql, seq_of_params):  # type: ignore[override]
        if isinstance(sql, str) and self._MATCH_RE.search(sql):
            seq_of_params = [self._maybe_transform(sql, p) for p in seq_of_params]
        return super().executemany(sql, seq_of_params)

SCHEMA = """
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    type TEXT NOT NULL,
    rule_ref TEXT,
    definition_en TEXT,
    definition_cn TEXT,
    chapter TEXT,
    complexity INTEGER,
    design_notes TEXT
);

CREATE TABLE IF NOT EXISTS relations (
    source_id TEXT,
    target_id TEXT,
    type TEXT NOT NULL,
    rule_ref TEXT,
    description TEXT,
    PRIMARY KEY (source_id, target_id, type),
    FOREIGN KEY (source_id) REFERENCES concepts(id),
    FOREIGN KEY (target_id) REFERENCES concepts(id)
);

CREATE TABLE IF NOT EXISTS rule_texts (
    rule_ref TEXT PRIMARY KEY,
    text_en TEXT,
    text_cn TEXT,
    parent_concept_id TEXT,
    FOREIGN KEY (parent_concept_id) REFERENCES concepts(id)
);

-- FTS5 indexes use the default unicode61 tokenizer. CJK content is
-- pre-tokenized (one space between characters) by the insert helpers and the
-- _FTSConnection wrapper transforms MATCH parameters the same way at query
-- time, so callers can search using natural multi-character CJK terms.
CREATE VIRTUAL TABLE IF NOT EXISTS rule_texts_fts USING fts5(
    rule_ref,
    text_en,
    text_cn
);

CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    id,
    name_en,
    name_cn,
    definition_en,
    definition_cn
);

CREATE INDEX IF NOT EXISTS idx_concepts_type ON concepts(type);
CREATE INDEX IF NOT EXISTS idx_concepts_chapter ON concepts(chapter);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type);
CREATE INDEX IF NOT EXISTS idx_rule_texts_parent ON rule_texts(parent_concept_id);
"""

def create_db(db_path: Path) -> sqlite3.Connection:
    """Create a new SQLite database with schema."""
    conn = sqlite3.connect(str(db_path), factory=_FTSConnection)
    conn.executescript(SCHEMA)
    return conn


def dedupe_concepts(concepts: list[dict]) -> list[dict]:
    """Remove duplicate concepts by id, keeping the first occurrence."""
    seen = set()
    result = []
    skipped = 0
    required = ("id", "name_en", "name_cn", "type")
    for c in concepts:
        if not all(k in c and c[k] for k in required):
            skipped += 1
            continue
        if c["id"] not in seen:
            seen.add(c["id"])
            # Fill in optional fields
            for opt in ("rule_ref", "definition_en", "definition_cn", "chapter", "complexity", "design_notes"):
                c.setdefault(opt, None)
            # Normalize chapter: strip "_partN" suffix to get raw chapter number
            if c.get("chapter") and isinstance(c["chapter"], str) and "_part" in c["chapter"]:
                c["chapter"] = c["chapter"].split("_part")[0]
            # Also derive from rule_ref if chapter still missing or non-numeric
            if (not c.get("chapter") or not str(c["chapter"]).isdigit()) and c.get("rule_ref"):
                # Rule refs like "702.9" → chapter 7 (first digit of 3-digit rule number)
                m = re.match(r"^(\d)\d{2}\.", str(c["rule_ref"]))
                if m:
                    c["chapter"] = m.group(1)
            result.append(c)
    if skipped:
        print(f"  Skipped {skipped} malformed concepts (missing required fields)")
    return result


def dedupe_relations(relations: list[dict]) -> list[dict]:
    """Remove duplicate relations by (source_id, target_id, type). Skips malformed."""
    seen = set()
    result = []
    skipped = 0
    for r in relations:
        if not all(k in r for k in ("source_id", "target_id", "type")):
            skipped += 1
            continue
        key = (r["source_id"], r["target_id"], r["type"])
        if key not in seen:
            seen.add(key)
            r.setdefault("rule_ref", None)
            r.setdefault("description", None)
            result.append(r)
    if skipped:
        print(f"  Skipped {skipped} malformed relations (missing required fields)")
    return result


def _fts_row(row: dict, fields: list[str]) -> dict:
    """Project a row to the FTS-bound fields, applying CJK tokenization."""
    return {f: _cjk_tokenize(row.get(f)) for f in fields}


def insert_concepts(conn: sqlite3.Connection, concepts: list[dict]):
    conn.executemany(
        """INSERT OR REPLACE INTO concepts
           (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
           VALUES (:id, :name_en, :name_cn, :type, :rule_ref, :definition_en, :definition_cn, :chapter, :complexity, :design_notes)""",
        concepts,
    )
    fts_fields = ["id", "name_en", "name_cn", "definition_en", "definition_cn"]
    conn.executemany(
        """INSERT INTO concepts_fts (id, name_en, name_cn, definition_en, definition_cn)
           VALUES (:id, :name_en, :name_cn, :definition_en, :definition_cn)""",
        [_fts_row(c, fts_fields) for c in concepts],
    )
    conn.commit()


def insert_relations(conn: sqlite3.Connection, relations: list[dict]):
    conn.executemany(
        """INSERT OR REPLACE INTO relations
           (source_id, target_id, type, rule_ref, description)
           VALUES (:source_id, :target_id, :type, :rule_ref, :description)""",
        relations,
    )
    conn.commit()


def insert_rule_texts(conn: sqlite3.Connection, rule_texts: list[dict]):
    conn.executemany(
        """INSERT OR REPLACE INTO rule_texts
           (rule_ref, text_en, text_cn, parent_concept_id)
           VALUES (:rule_ref, :text_en, :text_cn, :parent_concept_id)""",
        rule_texts,
    )
    fts_fields = ["rule_ref", "text_en", "text_cn"]
    conn.executemany(
        """INSERT INTO rule_texts_fts (rule_ref, text_en, text_cn)
           VALUES (:rule_ref, :text_en, :text_cn)""",
        [_fts_row(r, fts_fields) for r in rule_texts],
    )
    conn.commit()


def build(force: bool = False):
    """Build the complete database from processed data."""
    db_path = DATA_DIR / "concepts.db"
    if db_path.exists() and not force:
        print(f"Database already exists at {db_path}. Use force=True to rebuild.")
        return

    if db_path.exists():
        db_path.unlink()

    concepts_path = DATA_DIR / "processed" / "concepts_raw.json"
    relations_path = DATA_DIR / "processed" / "relations_raw.json"
    aligned_path = DATA_DIR / "processed" / "aligned.json"

    concepts = json.loads(concepts_path.read_text(encoding="utf-8"))
    relations = json.loads(relations_path.read_text(encoding="utf-8"))
    aligned = json.loads(aligned_path.read_text(encoding="utf-8"))

    concepts = dedupe_concepts(concepts)
    relations = dedupe_relations(relations)

    concept_ids = {c["id"] for c in concepts}
    relations = [r for r in relations if r["source_id"] in concept_ids and r["target_id"] in concept_ids]

    rule_ref_to_concept: dict[str, str] = {}
    for c in concepts:
        if c.get("rule_ref"):
            rule_ref_to_concept[c["rule_ref"]] = c["id"]

    rule_texts = []
    for chapter_entries in aligned.values():
        for entry in chapter_entries:
            parent = rule_ref_to_concept.get(entry["rule_ref"])
            if not parent:
                base_ref = entry["rule_ref"].rstrip("abcdefghijklmnopqrstuvwxyz")
                parent = rule_ref_to_concept.get(base_ref)

            rule_texts.append({
                "rule_ref": entry["rule_ref"],
                "text_en": entry["text_en"],
                "text_cn": entry["text_cn"],
                "parent_concept_id": parent,
            })

    conn = create_db(db_path)
    insert_concepts(conn, concepts)
    insert_relations(conn, relations)
    insert_rule_texts(conn, rule_texts)
    conn.close()

    print(f"Database built: {len(concepts)} concepts, {len(relations)} relations, {len(rule_texts)} rule texts")
    print(f"Saved to {db_path}")


if __name__ == "__main__":
    build(force=True)
