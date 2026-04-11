# MTG History Complexity Analysis — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an incremental extraction pipeline that ingests all historical MTG Comprehensive Rules versions from Academy Ruins API, computes multi-dimensional complexity metrics across versions, automatically detects spikes with LLM culprit analysis, and surfaces results in an interactive React HistoryView integrated into the existing MTGRuler client.

**Architecture:** New `parser/history/` Python subpackage that reuses existing `extract.py`/`build_db.py`/`normalize_relations.py` infrastructure. Per-version SQLite DBs in `parser/data/history/concept_dbs/`. New Express route module `server/src/routes/history.ts`. New React module `client/src/components/HistoryView/` integrated as the 6th view in the existing ViewSwitcher.

**Tech Stack:** Python 3.10+ (httpx, anthropic), SQLite + FTS5, Node.js + Express + TypeScript + better-sqlite3, React 19 + Vite + Cytoscape.js + Recharts (new dep), Tailwind CSS v4

---

### Task 1: Academy Ruins API client + version enumeration

**Files:**
- Create: `parser/history/__init__.py`
- Create: `parser/history/fetch.py`
- Create: `parser/history/walk_versions.py`
- Create: `parser/tests/test_history_fetch.py`
- Create: `parser/tests/test_history_walk.py`

- [ ] **Step 1: Create empty `parser/history/__init__.py`**

```python
"""History pipeline for MTG Comprehensive Rules complexity evolution analysis."""
```

- [ ] **Step 2: Create `parser/history/fetch.py`**

```python
"""Academy Ruins API client and on-disk caching for CR text + diffs."""

import json
from pathlib import Path

import httpx

API_BASE = "https://api.academyruins.com"
DATA_DIR = Path(__file__).parent.parent / "data" / "history"
VERSIONS_DIR = DATA_DIR / "versions"
DIFFS_DIR = DATA_DIR / "diffs"

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=API_BASE,
            timeout=60.0,
            follow_redirects=True,
            headers={"User-Agent": "MTGRuler-history/0.1"},
        )
    return _client


def fetch_cr_text(set_code: str, force: bool = False) -> str:
    """Fetch raw CR text for a set code, with disk caching.

    Returns the text content. Caches as parser/data/history/versions/{set_code}.txt.
    Raises httpx.HTTPStatusError on API errors.
    """
    set_code = set_code.upper()
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = VERSIONS_DIR / f"{set_code}.txt"

    if cache_file.exists() and not force:
        return cache_file.read_text(encoding="utf-8")

    client = _get_client()
    resp = client.get(f"/file/cr/{set_code}", params={"format": "txt"})
    resp.raise_for_status()
    text = resp.text
    cache_file.write_text(text, encoding="utf-8")
    return text


def fetch_diff(old_set: str, new_set: str, force: bool = False) -> dict:
    """Fetch the structured diff between two adjacent CR versions.

    Caches as parser/data/history/diffs/{old}_{new}.json.
    Returns the diff dict, or raises if Academy Ruins has no diff for this pair.
    """
    old_set = old_set.upper()
    new_set = new_set.upper()
    DIFFS_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = DIFFS_DIR / f"{old_set}_{new_set}.json"

    if cache_file.exists() and not force:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    client = _get_client()
    resp = client.get("/diff/cr", params={"old": old_set, "new": new_set, "nav": "true"})
    resp.raise_for_status()
    data = resp.json()
    if "detail" in data and "No diff" in data.get("detail", ""):
        raise ValueError(f"No diff between {old_set} and {new_set}")
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def fetch_latest_diff_with_nav() -> dict:
    """Fetch the latest diff (no params), used as the entry point for walking
    the version chain backward via prevSourceCode."""
    client = _get_client()
    resp = client.get("/diff/cr", params={"nav": "true"})
    resp.raise_for_status()
    return resp.json()
```

- [ ] **Step 3: Create `parser/history/walk_versions.py`**

```python
"""Walk the Academy Ruins CR version chain backward to enumerate all set codes."""

import json
from pathlib import Path

from .fetch import fetch_diff, fetch_latest_diff_with_nav, DATA_DIR

VERSIONS_INDEX = DATA_DIR / "versions_index.json"


def walk_all_versions(max_steps: int = 200) -> list[dict]:
    """Enumerate all CR versions by walking backward through the diff chain.

    Returns a list of version dicts ordered chronologically (oldest first):
        [{"set_code": "ODY", "set_name": "Odyssey", "release_date": "2001-09-24",
          "prev_set_code": null, "next_set_code": "TOR"}, ...]

    Caches the result to parser/data/history/versions_index.json.
    """
    latest = fetch_latest_diff_with_nav()
    chain: list[dict] = []

    current = {
        "set_code": latest["destCode"],
        "set_name": latest["destSet"],
        "release_date": latest.get("creationDay"),
        "prev_set_code": latest["sourceCode"],
        "next_set_code": None,
    }
    chain.append(current)

    # The first hop also tells us about the source set
    chain.append({
        "set_code": latest["sourceCode"],
        "set_name": latest["sourceSet"],
        "release_date": None,  # filled in next iteration
        "prev_set_code": latest.get("nav", {}).get("prevSourceCode"),
        "next_set_code": latest["destCode"],
    })

    # Walk backward
    steps = 0
    while chain[-1]["prev_set_code"] and steps < max_steps:
        prev_code = chain[-1]["prev_set_code"]
        curr_code = chain[-1]["set_code"]
        try:
            diff = fetch_diff(prev_code, curr_code)
        except (ValueError, Exception):
            break

        chain[-1]["release_date"] = diff.get("creationDay")
        chain.append({
            "set_code": diff["sourceCode"],
            "set_name": diff["sourceSet"],
            "release_date": None,
            "prev_set_code": diff.get("nav", {}).get("prevSourceCode"),
            "next_set_code": curr_code,
        })
        steps += 1

    chain.reverse()  # chronological order
    VERSIONS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    VERSIONS_INDEX.write_text(json.dumps(chain, ensure_ascii=False, indent=2), encoding="utf-8")
    return chain


def load_versions_index() -> list[dict]:
    """Load the cached versions index, or enumerate fresh if missing."""
    if VERSIONS_INDEX.exists():
        return json.loads(VERSIONS_INDEX.read_text(encoding="utf-8"))
    return walk_all_versions()
```

- [ ] **Step 4: Create `parser/tests/test_history_fetch.py`** (no network tests, just the API surface)

```python
"""Tests for history.fetch module — focuses on cache logic without hitting network."""

import json
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import pytest
from unittest.mock import patch, MagicMock

from history import fetch as fetch_mod


def test_fetch_cr_text_uses_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "VERSIONS_DIR", tmp_path)
    cache_file = tmp_path / "ODY.txt"
    cache_file.write_text("cached content", encoding="utf-8")

    # Should not call HTTP
    mock_client = MagicMock()
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    result = fetch_mod.fetch_cr_text("ODY")
    assert result == "cached content"
    mock_client.get.assert_not_called()


def test_fetch_cr_text_writes_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "VERSIONS_DIR", tmp_path)
    mock_resp = MagicMock()
    mock_resp.text = "fresh content"
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    result = fetch_mod.fetch_cr_text("XYZ")
    assert result == "fresh content"
    assert (tmp_path / "XYZ.txt").read_text(encoding="utf-8") == "fresh content"


def test_fetch_diff_raises_on_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "DIFFS_DIR", tmp_path)
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"detail": "No diff between these set codes found"}
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    with pytest.raises(ValueError, match="No diff"):
        fetch_mod.fetch_diff("FOO", "BAR")
```

- [ ] **Step 5: Create `parser/tests/test_history_walk.py`**

```python
"""Tests for history.walk_versions module — mock fetch_diff to test chain walking."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from history import walk_versions


def test_walk_returns_chronological_order(monkeypatch, tmp_path):
    monkeypatch.setattr(walk_versions, "VERSIONS_INDEX", tmp_path / "idx.json")

    # Simulate a 3-version chain: A → B → C (latest)
    latest = {
        "sourceCode": "B", "sourceSet": "Beta",
        "destCode": "C", "destSet": "Charlie",
        "creationDay": "2024-01-01",
        "nav": {"prevSourceCode": "A"},
    }
    diff_AB = {
        "sourceCode": "A", "sourceSet": "Alpha",
        "destCode": "B", "destSet": "Beta",
        "creationDay": "2023-01-01",
        "nav": {"prevSourceCode": None},
    }

    monkeypatch.setattr(walk_versions, "fetch_latest_diff_with_nav", lambda: latest)
    monkeypatch.setattr(walk_versions, "fetch_diff",
                        lambda old, new: diff_AB if (old, new) == ("A", "B") else (_ for _ in ()).throw(ValueError()))

    chain = walk_versions.walk_all_versions(max_steps=10)
    codes = [v["set_code"] for v in chain]
    assert codes == ["A", "B", "C"]
    assert chain[0]["next_set_code"] == "B"
    assert chain[-1]["next_set_code"] is None
```

- [ ] **Step 6: Run tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/test_history_fetch.py tests/test_history_walk.py -v`
Expected: All tests pass.

- [ ] **Step 7: Smoke test against real API (one call only)**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -c "from history.fetch import fetch_cr_text; t = fetch_cr_text('ODY'); print(f'Got {len(t)} chars'); assert len(t) > 50000"`
Expected: `Got 227023 chars` (or similar).

- [ ] **Step 8: Commit**

```bash
git add parser/history/__init__.py parser/history/fetch.py parser/history/walk_versions.py parser/tests/test_history_fetch.py parser/tests/test_history_walk.py
git commit -m "feat(history): Academy Ruins API client + version chain enumeration"
```

---

### Task 2: Per-version parser (reuse existing parsing logic)

**Files:**
- Create: `parser/history/parse_version.py`
- Create: `parser/tests/test_history_parse.py`

- [ ] **Step 1: Create `parser/history/parse_version.py`**

```python
"""Parse a single historical CR version into the same rule_texts shape used by
the existing MTGRuler pipeline. Reuses the parsing logic from fetch_rules.py."""

import json
from pathlib import Path

from fetch_rules import parse_en_chapters
from .fetch import fetch_cr_text, DATA_DIR

PARSED_DIR = DATA_DIR / "parsed"


def parse_version(set_code: str, force: bool = False) -> dict[str, list[dict]]:
    """Parse a CR version into chapters of rule entries.

    Returns dict[chapter_str, list[{"rule_ref", "text"}]] — same shape as
    fetch_rules.parse_en_chapters output. Caches to parser/data/history/parsed/{set_code}.json.
    """
    set_code = set_code.upper()
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = PARSED_DIR / f"{set_code}.json"

    if cache_file.exists() and not force:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    text = fetch_cr_text(set_code)
    chapters = parse_en_chapters(text)
    cache_file.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    return chapters


def to_rule_text_records(chapters: dict[str, list[dict]]) -> list[dict]:
    """Flatten parsed chapters into rule_texts table records (text_en only,
    text_cn = None for historical versions)."""
    records = []
    for chapter, entries in chapters.items():
        for entry in entries:
            records.append({
                "rule_ref": entry["rule_ref"],
                "text_en": entry["text"],
                "text_cn": None,
                "chapter": chapter,
            })
    return records
```

- [ ] **Step 2: Create `parser/tests/test_history_parse.py`**

```python
"""Tests for history.parse_version — uses a tiny synthetic CR text."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from history import parse_version as pv


def test_parse_version_uses_existing_parser(monkeypatch, tmp_path):
    sample_text = """1. Game Concepts

100. General

100.1. These Magic rules apply to any Magic game.
100.2. Some rules apply to specific cases.

Glossary

A bunch of terms here..."""

    monkeypatch.setattr(pv, "PARSED_DIR", tmp_path)
    monkeypatch.setattr(pv, "fetch_cr_text", lambda code, force=False: sample_text)

    chapters = pv.parse_version("TEST")
    assert "1" in chapters
    assert any(r["rule_ref"] == "100.1" for r in chapters["1"])


def test_to_rule_text_records():
    chapters = {
        "1": [{"rule_ref": "100.1", "text": "Hello"}],
        "2": [{"rule_ref": "200.1", "text": "World"}],
    }
    records = pv.to_rule_text_records(chapters)
    assert len(records) == 2
    assert records[0]["text_cn"] is None
    assert records[0]["chapter"] == "1"
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/test_history_parse.py -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add parser/history/parse_version.py parser/tests/test_history_parse.py
git commit -m "feat(history): per-version parser reusing existing CR parsing logic"
```

---

### Task 3: Baseline extraction (full LLM extraction for the earliest version)

**Files:**
- Create: `parser/history/baseline_extract.py`

- [ ] **Step 1: Create `parser/history/baseline_extract.py`**

```python
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

    # Build aligned-style structure (no CN for historical versions)
    aligned_by_chapter = {
        chapter: [
            {"rule_ref": e["rule_ref"], "text_en": e["text"], "text_cn": ""}
            for e in entries
        ]
        for chapter, entries in chapters.items()
    }

    print(f"  Running full LLM extraction (this is expensive)...")
    concepts, relations = extract_all(aligned_by_chapter, force=force)

    # Build the DB using existing build_db helpers
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
```

- [ ] **Step 2: Commit (no test — this is an integration entry point that requires real LLM calls)**

```bash
git add parser/history/baseline_extract.py
git commit -m "feat(history): baseline extraction for the earliest CR version"
```

---

### Task 4: Incremental extraction core algorithm

**Files:**
- Create: `parser/history/incremental_extract.py`
- Create: `parser/tests/test_history_incremental.py`

- [ ] **Step 1: Create `parser/history/incremental_extract.py`**

```python
"""Incrementally extract concepts for a new CR version using the previous
version's DB plus the Academy Ruins diff."""

import json
import shutil
import sqlite3
from pathlib import Path

from extract import extract_chapter
from build_db import dedupe_concepts, dedupe_relations
from normalize_relations import normalize_db as normalize_db_file
from .fetch import fetch_diff, DATA_DIR
from .parse_version import parse_version, to_rule_text_records
from .baseline_extract import CONCEPT_DBS_DIR


def derive_chapter(rule_ref: str) -> str | None:
    """Map a rule_ref like '702.9a' to its chapter ('7')."""
    if not rule_ref:
        return None
    head = rule_ref.split(".")[0]
    if head.isdigit() and len(head) >= 1:
        return head[0]  # first digit of 3-digit rule number
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
) -> None:
    """Merge newly extracted concepts/relations for a chapter into the DB.

    Strategy: replace all concepts whose chapter == this chapter with the new
    set. Relations are merged via INSERT OR REPLACE.
    """
    new_concepts = dedupe_concepts(new_concepts)
    new_relations = dedupe_relations(new_relations)

    # Delete old concepts and rule_texts for this chapter that are not in the
    # new set. Concepts referenced from other chapters' relations stay.
    new_ids = {c["id"] for c in new_concepts}
    old_ids_in_chapter = {
        row[0] for row in db.execute(
            "SELECT id FROM concepts WHERE chapter = ?", (chapter,)
        ).fetchall()
    }
    to_delete = old_ids_in_chapter - new_ids

    for cid in to_delete:
        # Drop relations where this concept is endpoint and no other concept references it
        db.execute("DELETE FROM relations WHERE source_id = ? OR target_id = ?", (cid, cid))
        db.execute("DELETE FROM concepts WHERE id = ?", (cid,))

    # Insert/replace new concepts
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

    # Insert/replace relations (only those whose endpoints exist)
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
        """INSERT INTO rule_texts (rule_ref, text_en, text_cn, parent_concept_id)
           VALUES (:rule_ref, :text_en, :text_cn, :parent_concept_id)""",
        records,
    )
    db.executemany(
        """INSERT INTO rule_texts_fts (rule_ref, text_en, text_cn)
           VALUES (:rule_ref, :text_en, :text_cn)""",
        [{"rule_ref": r["rule_ref"], "text_en": r["text_en"], "text_cn": r["text_cn"]} for r in records],
    )
    db.commit()


def incremental_extract(prev_set: str, curr_set: str, force: bool = False) -> Path:
    """Build curr_set.db from prev_set.db using Academy Ruins diff.

    Steps:
        1. Copy prev_set.db -> curr_set.db
        2. Load Academy Ruins diff
        3. Find affected refs and chapters
        4. Re-run extraction for each affected chapter
        5. Merge new concepts/relations
        6. Replace rule_texts table with new version
        7. Re-normalize relations
    """
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

    print(f"  Fetching diff {prev_set} → {curr_set}")
    diff = fetch_diff(prev_set, curr_set)

    affected_refs = collect_affected_refs(diff)
    chapters_to_redo = affected_chapters(affected_refs)
    print(f"  {len(affected_refs)} affected refs, {len(chapters_to_redo)} chapters to re-extract")

    if not chapters_to_redo:
        print(f"  No structural changes; just updating rule_texts")
    else:
        # Parse the new version's text
        chapters = parse_version(curr_set)
        new_records = to_rule_text_records(chapters)

        # Build aligned-style structure for affected chapters only
        affected_aligned = {
            chapter: [
                {"rule_ref": e["rule_ref"], "text_en": e["text"], "text_cn": ""}
                for e in chapters.get(chapter, [])
            ]
            for chapter in chapters_to_redo
            if chapter in chapters
        }

        # Re-extract each affected chapter
        db = sqlite3.connect(curr_db)
        try:
            for chapter, entries in affected_aligned.items():
                print(f"    Re-extracting chapter {chapter} ({len(entries)} entries)...")
                # Use incremental cache key namespaced by set_code
                concepts, relations = extract_chapter(
                    entries, f"hist_{curr_set}_{chapter}", force=force,
                )
                merge_chapter(db, chapter, concepts, relations)

            replace_rule_texts(db, new_records)
        finally:
            db.close()

    # Re-normalize relations
    print(f"  Normalizing relations in {curr_set}.db")
    # normalize_db_file expects to read from concepts_raw.db; we adapt by
    # copying and using its normalize_type logic directly.
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

        # Dedupe
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
```

- [ ] **Step 2: Create `parser/tests/test_history_incremental.py`**

```python
"""Tests for history.incremental_extract — focus on pure functions
(derive_chapter, collect_affected_refs, affected_chapters, merge_chapter)."""

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
    assert "keyword.kept" in ids  # other chapter, untouched
    assert "keyword.old" not in ids  # deleted because chapter 1 was replaced
    conn.close()
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/test_history_incremental.py -v`
Expected: All 4 tests pass.

- [ ] **Step 4: Commit**

```bash
git add parser/history/incremental_extract.py parser/tests/test_history_incremental.py
git commit -m "feat(history): incremental extraction algorithm with diff-driven re-extraction"
```

---

### Task 5: Multi-dimensional metrics computation

**Files:**
- Create: `parser/history/metrics.py`
- Create: `parser/tests/test_history_metrics.py`

- [ ] **Step 1: Create `parser/history/metrics.py`**

```python
"""Compute multi-dimensional complexity metrics from a single concept_db."""

import json
import sqlite3
from pathlib import Path
from statistics import mean, median

from .fetch import DATA_DIR
from .baseline_extract import CONCEPT_DBS_DIR

METRICS_FILE = DATA_DIR / "metrics.json"


def compute_understanding_complexity(conn: sqlite3.Connection) -> dict[str, int]:
    """Replicate server/src/utils/understanding-complexity.ts in Python.

    uc(A) = complexity(A) + sum(uc(B) for B where A DEPENDS_ON B)
    """
    rows = conn.execute("SELECT id, complexity FROM concepts").fetchall()
    base = {r[0]: (r[1] or 1) for r in rows}

    deps_rows = conn.execute(
        "SELECT source_id, target_id FROM relations WHERE type = 'DEPENDS_ON'"
    ).fetchall()
    depends_on: dict[str, list[str]] = {}
    for src, tgt in deps_rows:
        depends_on.setdefault(src, []).append(tgt)

    memo: dict[str, int] = {}
    in_progress: set[str] = set()

    def compute(cid: str) -> int:
        if cid in memo:
            return memo[cid]
        if cid in in_progress:
            return 0  # cycle
        in_progress.add(cid)
        total = base.get(cid, 1)
        for dep in depends_on.get(cid, []):
            total += compute(dep)
        in_progress.remove(cid)
        memo[cid] = total
        return total

    for cid in base:
        compute(cid)
    return memo


def compute_metrics(set_code: str, set_name: str, release_date: str | None,
                    prev_set_code: str | None = None) -> dict:
    """Compute the full MetricsRecord for a single version's DB."""
    set_code = set_code.upper()
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        # Scale metrics
        rule_count = conn.execute("SELECT COUNT(*) FROM rule_texts").fetchone()[0]
        rule_text_rows = conn.execute("SELECT text_en FROM rule_texts WHERE text_en IS NOT NULL").fetchall()
        all_text = " ".join(r[0] for r in rule_text_rows)
        words = all_text.split()
        rule_total_words = len(words)
        rule_avg_length = round(rule_total_words / max(rule_count, 1), 1)

        chapter_count = conn.execute("SELECT COUNT(DISTINCT chapter) FROM concepts WHERE chapter IS NOT NULL").fetchone()[0]
        max_rule_depth = _compute_max_rule_depth(conn)

        # Graph metrics
        concept_count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        type_rows = conn.execute("SELECT type, COUNT(*) FROM concepts GROUP BY type").fetchall()
        concept_count_by_type = {t: c for t, c in type_rows}

        relation_count = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        rel_type_rows = conn.execute("SELECT type, COUNT(*) FROM relations GROUP BY type").fetchall()
        relation_count_by_type = {t: c for t, c in rel_type_rows}

        isolated_concepts = conn.execute("""
            SELECT COUNT(*) FROM concepts c
            WHERE c.id NOT IN (SELECT source_id FROM relations)
              AND c.id NOT IN (SELECT target_id FROM relations)
        """).fetchone()[0]

        degree_rows = conn.execute("""
            SELECT id, (
                (SELECT COUNT(*) FROM relations WHERE source_id = c.id) +
                (SELECT COUNT(*) FROM relations WHERE target_id = c.id)
            ) as degree
            FROM concepts c
        """).fetchall()
        highly_connected_count = sum(1 for _, d in degree_rows if d > 10)

        # Cognitive metrics
        uc_map = compute_understanding_complexity(conn)
        uc_values = list(uc_map.values())
        if uc_values:
            uc_total = sum(uc_values)
            uc_max = max(uc_values)
            uc_avg = round(uc_total / len(uc_values), 1)
            sorted_uc = sorted(uc_values)
            uc_p50 = sorted_uc[len(sorted_uc) // 2]
            uc_p90 = sorted_uc[int(len(sorted_uc) * 0.9)]
            uc_p99 = sorted_uc[min(int(len(sorted_uc) * 0.99), len(sorted_uc) - 1)]
        else:
            uc_total = uc_max = uc_avg = uc_p50 = uc_p90 = uc_p99 = 0

        top10 = sorted(uc_map.items(), key=lambda x: -x[1])[:10]
        top10_names = {
            row[0]: row[1] for row in conn.execute(
                f"SELECT id, name_en FROM concepts WHERE id IN ({','.join('?' * len(top10))})",
                [t[0] for t in top10],
            ).fetchall()
        } if top10 else {}
        uc_top10_concepts = [
            {"id": cid, "uc": uc, "name_en": top10_names.get(cid, cid)}
            for cid, uc in top10
        ]

        depends_on_chain_max = _compute_max_chain(conn)

        # Mechanic metrics
        keyword_count = concept_count_by_type.get("Keyword", 0)
        card_type_count = concept_count_by_type.get("CardType", 0)
        evergreen_keyword_count = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE type = 'Keyword' AND complexity = 1"
        ).fetchone()[0]
        high_complexity_keywords = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE type = 'Keyword' AND complexity >= 4"
        ).fetchone()[0]

        keywords_added: list[str] = []
        keywords_removed: list[str] = []
        if prev_set_code:
            prev_db = CONCEPT_DBS_DIR / f"{prev_set_code.upper()}.db"
            if prev_db.exists():
                prev_conn = sqlite3.connect(prev_db)
                try:
                    prev_kw = {r[0] for r in prev_conn.execute(
                        "SELECT id FROM concepts WHERE type = 'Keyword'"
                    ).fetchall()}
                    curr_kw = {r[0] for r in conn.execute(
                        "SELECT id FROM concepts WHERE type = 'Keyword'"
                    ).fetchall()}
                    keywords_added = sorted(curr_kw - prev_kw)
                    keywords_removed = sorted(prev_kw - curr_kw)
                finally:
                    prev_conn.close()

        return {
            "set_code": set_code,
            "set_name": set_name,
            "release_date": release_date,
            "scale": {
                "rule_count": rule_count,
                "rule_total_words": rule_total_words,
                "rule_avg_length": rule_avg_length,
                "chapter_count": chapter_count,
                "max_rule_depth": max_rule_depth,
            },
            "graph": {
                "concept_count": concept_count,
                "concept_count_by_type": concept_count_by_type,
                "relation_count": relation_count,
                "relation_count_by_type": relation_count_by_type,
                "isolated_concepts": isolated_concepts,
                "highly_connected_count": highly_connected_count,
            },
            "cognitive": {
                "uc_total": uc_total,
                "uc_max": uc_max,
                "uc_avg": uc_avg,
                "uc_p50": uc_p50,
                "uc_p90": uc_p90,
                "uc_p99": uc_p99,
                "uc_top10_concepts": uc_top10_concepts,
                "depends_on_chain_max": depends_on_chain_max,
            },
            "mechanic": {
                "keyword_count": keyword_count,
                "keywords_added_since_prev": keywords_added,
                "keywords_removed_since_prev": keywords_removed,
                "card_type_count": card_type_count,
                "evergreen_keyword_count": evergreen_keyword_count,
                "high_complexity_keywords": high_complexity_keywords,
            },
        }
    finally:
        conn.close()


def _compute_max_rule_depth(conn: sqlite3.Connection) -> int:
    """Max sub-rule depth — count digits + letter chars in rule_ref."""
    rows = conn.execute("SELECT rule_ref FROM rule_texts WHERE rule_ref IS NOT NULL").fetchall()
    max_depth = 0
    for (ref,) in rows:
        # 702.9a → depth 4 (3 digits + dot + 1 + letter)
        depth = len([c for c in ref if c.isdigit() or c.isalpha()])
        max_depth = max(max_depth, depth)
    return max_depth


def _compute_max_chain(conn: sqlite3.Connection) -> int:
    """Longest DEPENDS_ON chain length using DFS."""
    deps_rows = conn.execute(
        "SELECT source_id, target_id FROM relations WHERE type = 'DEPENDS_ON'"
    ).fetchall()
    graph: dict[str, list[str]] = {}
    for src, tgt in deps_rows:
        graph.setdefault(src, []).append(tgt)

    memo: dict[str, int] = {}
    in_progress: set[str] = set()

    def longest(cid: str) -> int:
        if cid in memo:
            return memo[cid]
        if cid in in_progress:
            return 0
        in_progress.add(cid)
        best = 0
        for dep in graph.get(cid, []):
            best = max(best, 1 + longest(dep))
        in_progress.remove(cid)
        memo[cid] = best
        return best

    if not graph:
        return 0
    return max(longest(cid) for cid in graph)


def compute_all_metrics(versions: list[dict]) -> list[dict]:
    """Compute metrics for all versions in order. Returns the time series."""
    timeline = []
    for i, version in enumerate(versions):
        prev_code = versions[i - 1]["set_code"] if i > 0 else None
        try:
            record = compute_metrics(
                version["set_code"],
                version["set_name"],
                version.get("release_date"),
                prev_set_code=prev_code,
            )
            timeline.append(record)
        except FileNotFoundError as e:
            print(f"  Skipping {version['set_code']}: {e}")
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
```

- [ ] **Step 2: Create `parser/tests/test_history_metrics.py`**

```python
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
    # c: 1 (own only)
    # b: 3 (own) + 1 (c) = 4
    # a: 2 (own) + 4 (b) = 6
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
    # Cycle is broken; both should be finite
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
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/test_history_metrics.py -v`
Expected: All 3 tests pass.

- [ ] **Step 4: Commit**

```bash
git add parser/history/metrics.py parser/tests/test_history_metrics.py
git commit -m "feat(history): multi-dimensional complexity metrics computation"
```

---

### Task 6: Spike detection + LLM culprit analysis

**Files:**
- Create: `parser/history/detect_spikes.py`
- Create: `parser/tests/test_history_spikes.py`

- [ ] **Step 1: Create `parser/history/detect_spikes.py`**

```python
"""Detect complexity spikes between adjacent versions and ask the LLM
to identify the culprit mechanics."""

import json
import os
import re
import sqlite3
from pathlib import Path
from statistics import mean, stdev

import anthropic
from dotenv import load_dotenv

from .fetch import DATA_DIR, fetch_diff
from .baseline_extract import CONCEPT_DBS_DIR

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
SPIKES_FILE = DATA_DIR / "spikes.json"
Z_THRESHOLD = 2.0  # standard deviations above mean

METRIC_PATHS = [
    "scale.rule_count",
    "graph.concept_count",
    "graph.relation_count",
    "cognitive.uc_total",
    "mechanic.keyword_count",
]


def _get_nested(d: dict, path: str) -> float:
    parts = path.split(".")
    val = d
    for p in parts:
        val = val.get(p, 0)
    return float(val or 0)


def find_spikes(metrics: list[dict]) -> list[dict]:
    """Find versions where any metric grew more than Z_THRESHOLD sigmas above mean.

    Returns spikes grouped by version. Each spike entry:
        {
            "set_code": "...",
            "set_name": "...",
            "release_date": "...",
            "prev_set_code": "...",
            "spiked_metrics": ["cognitive.uc_total", ...],
            "deltas": {"cognitive.uc_total": {"pct": 0.18, "abs": 723}, ...}
        }
    """
    if len(metrics) < 3:
        return []

    spikes_by_version: dict[str, dict] = {}

    for metric_path in METRIC_PATHS:
        values = [_get_nested(m, metric_path) for m in metrics]
        deltas = []
        for i in range(1, len(values)):
            prev = values[i - 1]
            if prev > 0:
                deltas.append((values[i] - prev) / prev)
            else:
                deltas.append(0.0)

        if len(deltas) < 2:
            continue
        mu = mean(deltas)
        sigma = stdev(deltas) if len(deltas) > 1 else 0.0
        threshold = mu + Z_THRESHOLD * sigma

        for i, delta in enumerate(deltas):
            if delta > threshold and delta > 0.05:  # also require >5% absolute growth
                version = metrics[i + 1]
                key = version["set_code"]
                if key not in spikes_by_version:
                    spikes_by_version[key] = {
                        "set_code": key,
                        "set_name": version["set_name"],
                        "release_date": version.get("release_date"),
                        "prev_set_code": metrics[i]["set_code"],
                        "spiked_metrics": [],
                        "deltas": {},
                    }
                spikes_by_version[key]["spiked_metrics"].append(metric_path)
                spikes_by_version[key]["deltas"][metric_path] = {
                    "pct": round(delta, 4),
                    "abs": values[i + 1] - values[i],
                }

    return list(spikes_by_version.values())


def _summarize_added_concepts(prev_set: str, curr_set: str, max_items: int = 30) -> list[dict]:
    """Find concepts present in curr but not in prev."""
    prev_db = CONCEPT_DBS_DIR / f"{prev_set}.db"
    curr_db = CONCEPT_DBS_DIR / f"{curr_set}.db"
    if not prev_db.exists() or not curr_db.exists():
        return []

    prev_conn = sqlite3.connect(prev_db)
    curr_conn = sqlite3.connect(curr_db)
    try:
        prev_ids = {r[0] for r in prev_conn.execute("SELECT id FROM concepts").fetchall()}
        added_rows = curr_conn.execute(
            "SELECT id, name_en, type, complexity, definition_en FROM concepts"
        ).fetchall()
        added = [
            {"id": r[0], "name_en": r[1], "type": r[2], "complexity": r[3], "definition_en": r[4]}
            for r in added_rows if r[0] not in prev_ids
        ]
        return added[:max_items]
    finally:
        prev_conn.close()
        curr_conn.close()


def _summarize_rule_diff(prev_set: str, curr_set: str, max_items: int = 30) -> str:
    """Use Academy Ruins diff to summarize rule additions/changes."""
    try:
        diff = fetch_diff(prev_set, curr_set)
    except Exception:
        return "(diff unavailable)"
    lines = []
    for change in diff.get("changes", [])[:max_items]:
        old = change.get("old")
        new = change.get("new")
        if old is None and new:
            lines.append(f"  + {new['ruleNumber']}: {new['ruleText'][:200]}")
        elif new is None and old:
            lines.append(f"  - {old['ruleNumber']}: {old['ruleText'][:200]}")
        elif old and new:
            lines.append(f"  ~ {new['ruleNumber']}: (modified)")
    return "\n".join(lines)


def analyze_spike(spike: dict, model: str | None = None) -> dict:
    """Use LLM to identify the culprit mechanics behind a spike."""
    model = model or DEFAULT_MODEL
    client = anthropic.Anthropic()

    added_concepts = _summarize_added_concepts(spike["prev_set_code"], spike["set_code"])
    rule_diff = _summarize_rule_diff(spike["prev_set_code"], spike["set_code"])

    deltas_str = "\n".join(
        f"- {path}: +{round(d['pct'] * 100, 1)}% (abs change: {d['abs']})"
        for path, d in spike["deltas"].items()
    )

    added_str = "\n".join(
        f"  - {c['id']} ({c['type']}, complexity {c['complexity']}): {c['name_en']}"
        for c in added_concepts
    ) or "  (none)"

    user_prompt = f"""You are analyzing a complexity spike in MTG Comprehensive Rules between
{spike['prev_set_code']} and {spike['set_code']} ({spike.get('set_name', '?')}, released {spike.get('release_date', '?')}).

Metrics that spiked above 2 standard deviations:
{deltas_str}

Concepts and keywords newly added in this version:
{added_str}

Rules added or significantly modified (from Academy Ruins diff, top 30):
{rule_diff}

Question: Which specific mechanic(s), keyword(s), or rule subsystem(s) introduced
in this version are the primary causes of the complexity increase? Focus on
mechanics that introduce new game-state interactions, recursive effects, or
system-wide ripples.

Respond ONLY with valid JSON, no markdown fences:
{{
  "primary_culprits": [
    {{
      "name": "<mechanic/keyword name>",
      "type": "Keyword|Mechanic|RuleSystem",
      "explanation": "<why this caused complexity to jump>",
      "affected_concepts": [<concept ids>],
      "estimated_contribution_pct": <0-100>
    }}
  ],
  "secondary_factors": [],
  "summary": "<one sentence>"
}}"""

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = next((b.text for b in message.content if getattr(b, "type", None) == "text"), "")
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"primary_culprits": [], "secondary_factors": [], "summary": "(analysis failed to parse)"}


def detect_and_analyze(metrics: list[dict], force: bool = False) -> list[dict]:
    """Run the full spike detection + LLM analysis pipeline."""
    if SPIKES_FILE.exists() and not force:
        return json.loads(SPIKES_FILE.read_text(encoding="utf-8"))

    spikes = find_spikes(metrics)
    print(f"  Found {len(spikes)} version-level spikes")

    for spike in spikes:
        print(f"  Analyzing {spike['set_code']}: {', '.join(spike['spiked_metrics'])}")
        spike["analysis"] = analyze_spike(spike)
        spike["delta_summary"] = ", ".join(
            f"+{round(d['pct'] * 100)}% {p.split('.')[-1]}"
            for p, d in spike["deltas"].items()
        )

    SPIKES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SPIKES_FILE.write_text(json.dumps(spikes, ensure_ascii=False, indent=2), encoding="utf-8")
    return spikes
```

- [ ] **Step 2: Create `parser/tests/test_history_spikes.py`**

```python
"""Tests for history.detect_spikes — focuses on find_spikes pure function."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from history.detect_spikes import find_spikes, _get_nested


def test_get_nested():
    assert _get_nested({"a": {"b": {"c": 5}}}, "a.b.c") == 5.0
    assert _get_nested({"a": {"b": 0}}, "a.b") == 0.0
    assert _get_nested({}, "x.y") == 0.0


def make_metric(set_code, uc):
    return {
        "set_code": set_code,
        "set_name": set_code,
        "release_date": "2020-01-01",
        "scale": {"rule_count": 100},
        "graph": {"concept_count": 100, "relation_count": 100},
        "cognitive": {"uc_total": uc},
        "mechanic": {"keyword_count": 50},
    }


def test_find_spikes_detects_outlier():
    metrics = [
        make_metric("V1", 1000),
        make_metric("V2", 1010),  # +1%
        make_metric("V3", 1020),  # +1%
        make_metric("V4", 1030),  # +1%
        make_metric("V5", 1500),  # +46% — clear spike
        make_metric("V6", 1510),  # +0.7%
    ]
    spikes = find_spikes(metrics)
    spiked_codes = [s["set_code"] for s in spikes]
    assert "V5" in spiked_codes


def test_find_spikes_handles_short_series():
    assert find_spikes([]) == []
    assert find_spikes([make_metric("V1", 100)]) == []
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/test_history_spikes.py -v`
Expected: All 3 tests pass.

- [ ] **Step 4: Commit**

```bash
git add parser/history/detect_spikes.py parser/tests/test_history_spikes.py
git commit -m "feat(history): spike detection with LLM culprit analysis"
```

---

### Task 7: Pipeline orchestrator CLI

**Files:**
- Create: `parser/history/run_history_pipeline.py`

- [ ] **Step 1: Create `parser/history/run_history_pipeline.py`**

```python
"""Run the full history pipeline: walk versions, baseline extract, incremental
extract chain, compute metrics, detect spikes."""

import argparse
import sys
from pathlib import Path

from .walk_versions import walk_all_versions, load_versions_index
from .fetch import fetch_cr_text
from .parse_version import parse_version
from .baseline_extract import baseline_extract, CONCEPT_DBS_DIR
from .incremental_extract import incremental_extract
from .metrics import compute_all_metrics, METRICS_FILE
from .detect_spikes import detect_and_analyze, SPIKES_FILE


def run(
    baseline_set: str | None = None,
    max_versions: int | None = None,
    skip_extract: bool = False,
    skip_metrics: bool = False,
    skip_spikes: bool = False,
    force: bool = False,
):
    print("=" * 60)
    print("MTG History Pipeline")
    print("=" * 60)

    print("\n[1/6] Walking version chain...")
    if force:
        versions = walk_all_versions()
    else:
        versions = load_versions_index()
    print(f"  Found {len(versions)} versions: {versions[0]['set_code']} ... {versions[-1]['set_code']}")

    if max_versions:
        versions = versions[:max_versions]
        print(f"  Limited to first {max_versions} versions")

    print("\n[2/6] Pre-fetching CR text + diffs...")
    for i, v in enumerate(versions):
        print(f"  [{i+1}/{len(versions)}] {v['set_code']}", end="\r")
        try:
            fetch_cr_text(v["set_code"])
            parse_version(v["set_code"])
        except Exception as e:
            print(f"\n  WARN: failed to fetch {v['set_code']}: {e}")
    print()

    if not skip_extract:
        baseline_code = baseline_set or versions[0]["set_code"]
        print(f"\n[3/6] Baseline extraction: {baseline_code}")
        baseline_extract(baseline_code, force=force)

        print(f"\n[4/6] Incremental extraction across {len(versions) - 1} versions...")
        baseline_idx = next((i for i, v in enumerate(versions) if v["set_code"] == baseline_code), 0)
        for i in range(baseline_idx + 1, len(versions)):
            prev = versions[i - 1]["set_code"]
            curr = versions[i]["set_code"]
            print(f"  [{i}/{len(versions) - 1}] {prev} → {curr}")
            try:
                incremental_extract(prev, curr, force=force)
            except Exception as e:
                print(f"    ERROR: {e}")
                print(f"    Skipping {curr} and continuing")

    if not skip_metrics:
        print(f"\n[5/6] Computing metrics for all versions...")
        timeline = compute_all_metrics(versions)
        print(f"  Wrote {len(timeline)} metric records to {METRICS_FILE}")
    else:
        import json
        timeline = json.loads(METRICS_FILE.read_text(encoding="utf-8")) if METRICS_FILE.exists() else []

    if not skip_spikes:
        print(f"\n[6/6] Detecting spikes + LLM analysis...")
        spikes = detect_and_analyze(timeline, force=force)
        print(f"  Found {len(spikes)} spikes; analysis saved to {SPIKES_FILE}")

    print("\n" + "=" * 60)
    print("History pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="MTG History Pipeline")
    ap.add_argument("--baseline-set", type=str, help="Set code to use as baseline (default: earliest)")
    ap.add_argument("--max-versions", type=int, help="Limit to first N versions for testing")
    ap.add_argument("--skip-extract", action="store_true")
    ap.add_argument("--skip-metrics", action="store_true")
    ap.add_argument("--skip-spikes", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    run(
        baseline_set=args.baseline_set,
        max_versions=args.max_versions,
        skip_extract=args.skip_extract,
        skip_metrics=args.skip_metrics,
        skip_spikes=args.skip_spikes,
        force=args.force,
    )
```

- [ ] **Step 2: Commit**

```bash
git add parser/history/run_history_pipeline.py
git commit -m "feat(history): pipeline orchestrator CLI"
```

---

### Task 8: Server route module for history API

**Files:**
- Create: `server/src/routes/history.ts`
- Modify: `server/src/index.ts`
- Modify: `server/src/types.ts`
- Create: `server/tests/history.test.ts`

- [ ] **Step 1: Add types to `server/src/types.ts`**

Append at the end of the existing file:

```typescript
export interface VersionInfo {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string | null;
  next_set_code: string | null;
}

export interface MetricsRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  scale: {
    rule_count: number;
    rule_total_words: number;
    rule_avg_length: number;
    chapter_count: number;
    max_rule_depth: number;
  };
  graph: {
    concept_count: number;
    concept_count_by_type: Record<string, number>;
    relation_count: number;
    relation_count_by_type: Record<string, number>;
    isolated_concepts: number;
    highly_connected_count: number;
  };
  cognitive: {
    uc_total: number;
    uc_max: number;
    uc_avg: number;
    uc_p50: number;
    uc_p90: number;
    uc_p99: number;
    uc_top10_concepts: { id: string; uc: number; name_en: string }[];
    depends_on_chain_max: number;
  };
  mechanic: {
    keyword_count: number;
    keywords_added_since_prev: string[];
    keywords_removed_since_prev: string[];
    card_type_count: number;
    evergreen_keyword_count: number;
    high_complexity_keywords: number;
  };
}

export interface SpikeAnalysis {
  primary_culprits: {
    name: string;
    type: string;
    explanation: string;
    affected_concepts: string[];
    estimated_contribution_pct: number;
  }[];
  secondary_factors: any[];
  summary: string;
}

export interface SpikeRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string;
  spiked_metrics: string[];
  deltas: Record<string, { pct: number; abs: number }>;
  delta_summary: string;
  analysis: SpikeAnalysis;
}
```

- [ ] **Step 2: Create `server/src/routes/history.ts`**

```typescript
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

  // Load versions index
  const indexPath = resolve(HISTORY_DIR, "versions_index.json");
  if (existsSync(indexPath)) {
    versionsIndex = JSON.parse(readFileSync(indexPath, "utf-8"));
  }

  // Load metrics
  const metricsPath = resolve(HISTORY_DIR, "metrics.json");
  if (existsSync(metricsPath)) {
    metricsCache = JSON.parse(readFileSync(metricsPath, "utf-8"));
  }

  // Load spikes
  const spikesPath = resolve(HISTORY_DIR, "spikes.json");
  if (existsSync(spikesPath)) {
    spikesCache = JSON.parse(readFileSync(spikesPath, "utf-8"));
  }

  // Open per-version DBs
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

    const added = newRows.filter((c) => !oldIds.has(c.id));
    const removed = oldRows.filter((c) => !newIds.has(c.id));

    res.json({ added, removed, old_set: oldCode, new_set: newCode });
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
```

- [ ] **Step 3: Modify `server/src/index.ts` to mount the history router**

Find the existing `import` block and add:

```typescript
import { createHistoryRouter, loadHistory, closeHistory } from "./routes/history.js";
```

After the existing `db = getDb()` and ucCache setup (around line 17-19), add:

```typescript
loadHistory();
```

Add the route mount after the existing routes:

```typescript
app.use("/api/v1/history", createHistoryRouter());
```

In the SIGINT handler, add `closeHistory();` before `closeDb();`.

- [ ] **Step 4: Create `server/tests/history.test.ts`**

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import Database from "better-sqlite3";
import { createTestDb } from "./setup.js";
// History router uses module-level state and FS, so we test buildGraphData
// indirectly via the existing graph logic patterns. For unit testing, we
// import the raw helper if exposed, or test endpoint behavior via supertest.
// Here we just verify the test DB has the expected shape — full integration
// requires real history data.

describe("history routes (smoke)", () => {
  it("test DB has concepts table", () => {
    const db: Database.Database = createTestDb();
    const count = (db.prepare("SELECT COUNT(*) as c FROM concepts").get() as any).c;
    expect(count).toBeGreaterThan(0);
    db.close();
  });
});
```

- [ ] **Step 5: Run server tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/server && npx vitest run`
Expected: All tests pass (including the new smoke test).

- [ ] **Step 6: Commit**

```bash
git add server/src/routes/history.ts server/src/types.ts server/src/index.ts server/tests/history.test.ts
git commit -m "feat(server): history routes for versions, metrics, spikes, per-version queries"
```

---

### Task 9: Client — install Recharts dependency

**Files:**
- Modify: `client/package.json`

- [ ] **Step 1: Install Recharts**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npm install recharts@^2.12.0`
Expected: Recharts added to dependencies, package-lock.json updated.

- [ ] **Step 2: Verify TypeScript still passes**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add client/package.json client/package-lock.json
git commit -m "chore(client): add recharts dependency for history complexity charts"
```

---

### Task 10: Client — types and API client for history

**Files:**
- Modify: `client/src/types/index.ts`
- Modify: `client/src/services/api.ts`

- [ ] **Step 1: Add types to `client/src/types/index.ts`**

Append at the end:

```typescript
export interface VersionInfo {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string | null;
  next_set_code: string | null;
}

export interface MetricsRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  scale: {
    rule_count: number;
    rule_total_words: number;
    rule_avg_length: number;
    chapter_count: number;
    max_rule_depth: number;
  };
  graph: {
    concept_count: number;
    concept_count_by_type: Record<string, number>;
    relation_count: number;
    relation_count_by_type: Record<string, number>;
    isolated_concepts: number;
    highly_connected_count: number;
  };
  cognitive: {
    uc_total: number;
    uc_max: number;
    uc_avg: number;
    uc_p50: number;
    uc_p90: number;
    uc_p99: number;
    uc_top10_concepts: { id: string; uc: number; name_en: string }[];
    depends_on_chain_max: number;
  };
  mechanic: {
    keyword_count: number;
    keywords_added_since_prev: string[];
    keywords_removed_since_prev: string[];
    card_type_count: number;
    evergreen_keyword_count: number;
    high_complexity_keywords: number;
  };
}

export interface SpikeRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string;
  spiked_metrics: string[];
  deltas: Record<string, { pct: number; abs: number }>;
  delta_summary: string;
  analysis: {
    primary_culprits: {
      name: string;
      type: string;
      explanation: string;
      affected_concepts: string[];
      estimated_contribution_pct: number;
    }[];
    secondary_factors: any[];
    summary: string;
  };
}

export interface HistoryDiff {
  added: Concept[];
  removed: Concept[];
  old_set: string;
  new_set: string;
}
```

Update the existing `ViewMode` type:

```typescript
export type ViewMode = "graph" | "dependency" | "heatmap" | "chapter-overview" | "interaction-matrix" | "history";
```

- [ ] **Step 2: Add history methods to `client/src/services/api.ts`**

Append the following methods to the `api` object (before the closing `};`):

```typescript
  // History endpoints
  getHistoryVersions() {
    return get<VersionInfo[]>(`${BASE}/history/versions`);
  },
  getHistoryMetrics() {
    return get<MetricsRecord[]>(`${BASE}/history/metrics`);
  },
  getHistorySpikes() {
    return get<SpikeRecord[]>(`${BASE}/history/spikes`);
  },
  getHistoryVersionGraph(setCode: string) {
    return get<GraphData>(`${BASE}/history/${encodeURIComponent(setCode)}/graph`);
  },
  getHistoryVersionConcept(setCode: string, conceptId: string) {
    return get<ConceptDetail>(`${BASE}/history/${encodeURIComponent(setCode)}/concepts/${encodeURIComponent(conceptId)}`);
  },
  getHistoryDiff(oldCode: string, newCode: string) {
    return get<HistoryDiff>(`${BASE}/history/diff`, { old: oldCode, new: newCode });
  },
  getConceptTrace(conceptId: string) {
    return get<any[]>(`${BASE}/history/concept-trace/${encodeURIComponent(conceptId)}`);
  },
```

Add the type imports at the top of the file:

```typescript
import type { VersionInfo, MetricsRecord, SpikeRecord, HistoryDiff } from "../types/index.js";
```

- [ ] **Step 3: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add client/src/types/index.ts client/src/services/api.ts
git commit -m "feat(client): history types and API client methods"
```

---

### Task 11: Client — useHistory hook

**Files:**
- Create: `client/src/components/HistoryView/useHistory.ts`

- [ ] **Step 1: Create directory and hook**

Create `client/src/components/HistoryView/useHistory.ts`:

```typescript
import { useState, useCallback, useEffect } from "react";
import type { VersionInfo, MetricsRecord, SpikeRecord, GraphData, HistoryDiff } from "../../types/index.js";
import { api } from "../../services/api.js";

export type HistorySubView = "chart" | "slider" | "diff";

export interface HistoryState {
  versions: VersionInfo[];
  metrics: MetricsRecord[];
  spikes: SpikeRecord[];
  loading: boolean;
  error: string | null;
  selectedVersion: string | null;
  compareVersion: string | null;
  selectedGraph: GraphData | null;
  compareGraph: GraphData | null;
  diff: HistoryDiff | null;
  subView: HistorySubView;
}

export function useHistory() {
  const [state, setState] = useState<HistoryState>({
    versions: [],
    metrics: [],
    spikes: [],
    loading: false,
    error: null,
    selectedVersion: null,
    compareVersion: null,
    selectedGraph: null,
    compareGraph: null,
    diff: null,
    subView: "chart",
  });

  // Initial load
  useEffect(() => {
    setState((s) => ({ ...s, loading: true }));
    Promise.all([
      api.getHistoryVersions(),
      api.getHistoryMetrics(),
      api.getHistorySpikes(),
    ])
      .then(([versions, metrics, spikes]) => {
        setState((s) => ({
          ...s,
          versions,
          metrics,
          spikes,
          loading: false,
          selectedVersion: versions.length > 0 ? versions[versions.length - 1].set_code : null,
        }));
      })
      .catch((e) => {
        setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to load history" }));
      });
  }, []);

  const selectVersion = useCallback(async (setCode: string) => {
    setState((s) => ({ ...s, selectedVersion: setCode, loading: true }));
    try {
      const graph = await api.getHistoryVersionGraph(setCode);
      setState((s) => ({ ...s, selectedGraph: graph, loading: false }));
    } catch (e) {
      setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to load version graph" }));
    }
  }, []);

  const compareVersions = useCallback(async (oldCode: string, newCode: string) => {
    setState((s) => ({ ...s, loading: true }));
    try {
      const [oldGraph, newGraph, diff] = await Promise.all([
        api.getHistoryVersionGraph(oldCode),
        api.getHistoryVersionGraph(newCode),
        api.getHistoryDiff(oldCode, newCode),
      ]);
      setState((s) => ({
        ...s,
        selectedVersion: newCode,
        compareVersion: oldCode,
        selectedGraph: newGraph,
        compareGraph: oldGraph,
        diff,
        loading: false,
        subView: "diff",
      }));
    } catch (e) {
      setState((s) => ({ ...s, loading: false, error: e instanceof Error ? e.message : "Failed to compare versions" }));
    }
  }, []);

  const setSubView = useCallback((subView: HistorySubView) => {
    setState((s) => ({ ...s, subView }));
  }, []);

  return { ...state, selectVersion, compareVersions, setSubView };
}
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/HistoryView/useHistory.ts
git commit -m "feat(client): useHistory hook for version timeline state"
```

---

### Task 12: Client — ComplexityChart sub-view

**Files:**
- Create: `client/src/components/HistoryView/ComplexityChart.tsx`

- [ ] **Step 1: Create the chart component**

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from "recharts";
import { useMemo, useState } from "react";
import type { MetricsRecord, SpikeRecord } from "../../types/index.js";

interface ComplexityChartProps {
  metrics: MetricsRecord[];
  spikes: SpikeRecord[];
  onSpikeClick: (oldCode: string, newCode: string) => void;
}

interface ChartPoint {
  set_code: string;
  set_name: string;
  release_date: string | null;
  rule_count: number;
  concept_count: number;
  uc_total: number;
  keyword_count: number;
}

const METRIC_LINES = [
  { key: "rule_count", color: "#6366f1", label: "Rule Count" },
  { key: "concept_count", color: "#10b981", label: "Concept Count" },
  { key: "uc_total", color: "#f59e0b", label: "Understanding Complexity (Total)" },
  { key: "keyword_count", color: "#ef4444", label: "Keyword Count" },
];

export function ComplexityChart({ metrics, spikes, onSpikeClick }: ComplexityChartProps) {
  const [enabled, setEnabled] = useState<Set<string>>(new Set(METRIC_LINES.map((m) => m.key)));

  const data: ChartPoint[] = useMemo(
    () =>
      metrics.map((m) => ({
        set_code: m.set_code,
        set_name: m.set_name,
        release_date: m.release_date,
        rule_count: m.scale.rule_count,
        concept_count: m.graph.concept_count,
        uc_total: m.cognitive.uc_total,
        keyword_count: m.mechanic.keyword_count,
      })),
    [metrics],
  );

  const spikeMap = useMemo(() => {
    const m = new Map<string, SpikeRecord>();
    for (const s of spikes) m.set(s.set_code, s);
    return m;
  }, [spikes]);

  const toggleMetric = (key: string) => {
    setEnabled((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const formatTick = (setCode: string) => {
    const point = data.find((d) => d.set_code === setCode);
    return point?.release_date?.slice(0, 4) || setCode;
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-950 p-4 overflow-hidden">
      <div className="flex items-center gap-4 mb-3">
        <h2 className="text-white font-bold">Complexity Over Time</h2>
        <div className="flex gap-3">
          {METRIC_LINES.map((m) => (
            <label key={m.key} className="flex items-center gap-1 text-sm text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={enabled.has(m.key)}
                onChange={() => toggleMetric(m.key)}
              />
              <span style={{ color: m.color }}>{m.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="set_code" tick={{ fill: "#9ca3af", fontSize: 11 }} tickFormatter={formatTick} />
            <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #4b5563" }}
              labelStyle={{ color: "#f3f4f6" }}
              labelFormatter={(setCode: string) => {
                const point = data.find((d) => d.set_code === setCode);
                return point ? `${point.set_name} (${point.release_date || setCode})` : setCode;
              }}
            />
            <Legend wrapperStyle={{ color: "#d1d5db" }} />
            {METRIC_LINES.filter((m) => enabled.has(m.key)).map((m) => (
              <Line
                key={m.key}
                type="monotone"
                dataKey={m.key}
                stroke={m.color}
                strokeWidth={2}
                dot={false}
                name={m.label}
              />
            ))}
            {spikes.map((s) => {
              const point = data.find((d) => d.set_code === s.set_code);
              if (!point) return null;
              return (
                <ReferenceDot
                  key={s.set_code}
                  x={s.set_code}
                  y={point.uc_total}
                  r={6}
                  fill="#fbbf24"
                  stroke="#fff"
                  strokeWidth={1}
                  onClick={() => onSpikeClick(s.prev_set_code, s.set_code)}
                  style={{ cursor: "pointer" }}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {spikes.length > 0 && (
        <div className="mt-4 max-h-40 overflow-y-auto bg-gray-900 rounded-lg p-3">
          <h3 className="text-sm font-bold text-amber-400 mb-2">⚠️ Detected Spikes</h3>
          <div className="space-y-2">
            {spikes.map((s) => (
              <button
                key={s.set_code}
                onClick={() => onSpikeClick(s.prev_set_code, s.set_code)}
                className="w-full text-left p-2 bg-gray-800 hover:bg-gray-700 rounded text-xs"
              >
                <div className="flex justify-between text-white">
                  <span>{s.set_name} ({s.set_code})</span>
                  <span className="text-amber-400">{s.delta_summary}</span>
                </div>
                <div className="text-gray-400 mt-1">{s.analysis.summary}</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/HistoryView/ComplexityChart.tsx
git commit -m "feat(client): ComplexityChart sub-view with Recharts and spike markers"
```

---

### Task 13: Client — TimelineSlider sub-view

**Files:**
- Create: `client/src/components/HistoryView/TimelineSlider.tsx`

- [ ] **Step 1: Create the slider component**

```tsx
import { useEffect, useMemo } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { VersionInfo, GraphData } from "../../types/index.js";

interface TimelineSliderProps {
  versions: VersionInfo[];
  selectedVersion: string | null;
  graphData: GraphData | null;
  loading: boolean;
  onVersionChange: (setCode: string) => void;
}

export function TimelineSlider({ versions, selectedVersion, graphData, loading, onVersionChange }: TimelineSliderProps) {
  const currentIdx = versions.findIndex((v) => v.set_code === selectedVersion);
  const safeIdx = currentIdx >= 0 ? currentIdx : versions.length - 1;
  const current = versions[safeIdx];

  const elements = useMemo(() => {
    if (!graphData) return [];
    return [
      ...graphData.nodes.map((n) => ({
        data: {
          id: n.id,
          label: n.name_cn || n.name_en,
          color: NODE_COLORS[n.type] || "#6b7280",
          size: 14 + (n.complexity ?? 2) * 5,
          nodeType: n.type,
        },
      })),
      ...graphData.edges.map((e) => ({
        data: {
          id: `${e.source}-${e.target}-${e.type}`,
          source: e.source,
          target: e.target,
          label: e.type,
          color: "#64748b",
        },
      })),
    ];
  }, [graphData]);

  // Trigger initial graph load
  useEffect(() => {
    if (current && !graphData && !loading) {
      onVersionChange(current.set_code);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current?.set_code]);

  if (versions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        No historical versions loaded
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="p-4 bg-gray-900 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2 text-sm">
          <span className="text-gray-400">{versions[0]?.set_code} ({versions[0]?.release_date})</span>
          <span className="text-white font-bold">
            {current?.set_name} ({current?.set_code})
            {current?.release_date && <span className="text-gray-400 ml-2">{current.release_date}</span>}
          </span>
          <span className="text-gray-400">
            {versions[versions.length - 1]?.set_code} ({versions[versions.length - 1]?.release_date})
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={versions.length - 1}
          value={safeIdx}
          onChange={(e) => onVersionChange(versions[parseInt(e.target.value)].set_code)}
          className="w-full"
        />
      </div>
      <div className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-950/50 z-10 text-gray-400">
            Loading {current?.set_code}...
          </div>
        )}
        <GraphView elements={elements} onNodeClick={() => { /* no-op for now */ }} />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/HistoryView/TimelineSlider.tsx
git commit -m "feat(client): TimelineSlider sub-view with version slider and graph"
```

---

### Task 14: Client — DiffCompare sub-view

**Files:**
- Create: `client/src/components/HistoryView/DiffCompare.tsx`

- [ ] **Step 1: Create the diff compare component**

```tsx
import { useMemo } from "react";
import { GraphView } from "../GraphView.js";
import { NODE_COLORS } from "../../styles/cytoscape.js";
import type { GraphData, HistoryDiff } from "../../types/index.js";

interface DiffCompareProps {
  oldCode: string | null;
  newCode: string | null;
  oldGraph: GraphData | null;
  newGraph: GraphData | null;
  diff: HistoryDiff | null;
}

export function DiffCompare({ oldCode, newCode, oldGraph, newGraph, diff }: DiffCompareProps) {
  if (!oldCode || !newCode) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        Click a spike marker on the chart to compare two versions
      </div>
    );
  }

  const addedIds = useMemo(() => new Set(diff?.added.map((c) => c.id) ?? []), [diff]);
  const removedIds = useMemo(() => new Set(diff?.removed.map((c) => c.id) ?? []), [diff]);

  const buildElements = (graph: GraphData | null, side: "old" | "new") => {
    if (!graph) return [];
    return [
      ...graph.nodes.map((n) => {
        let color = "#6b7280"; // common = gray
        if (side === "new" && addedIds.has(n.id)) color = "#10b981"; // green
        if (side === "old" && removedIds.has(n.id)) color = "#ef4444"; // red
        if (!addedIds.has(n.id) && !removedIds.has(n.id)) color = NODE_COLORS[n.type] || "#6b7280";
        return {
          data: {
            id: n.id,
            label: n.name_cn || n.name_en,
            color,
            size: 14 + (n.complexity ?? 2) * 5,
            nodeType: n.type,
          },
        };
      }),
      ...graph.edges.map((e) => ({
        data: {
          id: `${e.source}-${e.target}-${e.type}`,
          source: e.source,
          target: e.target,
          label: e.type,
          color: "#64748b",
        },
      })),
    ];
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="flex flex-1 min-h-0">
        <div className="flex-1 flex flex-col border-r border-gray-700">
          <div className="p-2 bg-gray-900 border-b border-gray-700 text-center text-sm text-white font-bold">
            {oldCode}
          </div>
          <GraphView elements={buildElements(oldGraph, "old")} onNodeClick={() => {}} />
        </div>
        <div className="flex-1 flex flex-col">
          <div className="p-2 bg-gray-900 border-b border-gray-700 text-center text-sm text-white font-bold">
            {newCode}
          </div>
          <GraphView elements={buildElements(newGraph, "new")} onNodeClick={() => {}} />
        </div>
      </div>

      {diff && (
        <div className="max-h-40 overflow-y-auto bg-gray-900 border-t border-gray-700 p-3 grid grid-cols-2 gap-3">
          <div>
            <h4 className="text-sm font-bold text-green-400 mb-1">+ Added ({diff.added.length})</h4>
            <div className="space-y-1 text-xs">
              {diff.added.slice(0, 20).map((c) => (
                <div key={c.id} className="text-gray-200">
                  <span className="text-green-400">+</span> {c.id} ({c.type})
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-bold text-red-400 mb-1">− Removed ({diff.removed.length})</h4>
            <div className="space-y-1 text-xs">
              {diff.removed.slice(0, 20).map((c) => (
                <div key={c.id} className="text-gray-200">
                  <span className="text-red-400">−</span> {c.id} ({c.type})
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/HistoryView/DiffCompare.tsx
git commit -m "feat(client): DiffCompare sub-view with side-by-side graph comparison"
```

---

### Task 15: Client — HistoryView container + integration into App

**Files:**
- Create: `client/src/components/HistoryView/HistoryView.tsx`
- Modify: `client/src/components/ViewSwitcher.tsx`
- Modify: `client/src/App.tsx`

- [ ] **Step 1: Create `client/src/components/HistoryView/HistoryView.tsx`**

```tsx
import { useHistory } from "./useHistory.js";
import { ComplexityChart } from "./ComplexityChart.js";
import { TimelineSlider } from "./TimelineSlider.js";
import { DiffCompare } from "./DiffCompare.js";

export function HistoryView() {
  const h = useHistory();

  if (h.loading && h.versions.length === 0) {
    return <div className="flex-1 flex items-center justify-center text-gray-400">Loading history...</div>;
  }
  if (h.error) {
    return <div className="flex-1 flex items-center justify-center text-red-400">{h.error}</div>;
  }
  if (h.versions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-center px-8">
        No historical data found.<br />
        Run <code className="text-indigo-400">python -m parser.history.run_history_pipeline</code> first.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      <div className="flex items-center gap-2 p-2 bg-gray-900 border-b border-gray-700">
        <button
          onClick={() => h.setSubView("chart")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "chart" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Complexity Chart
        </button>
        <button
          onClick={() => h.setSubView("slider")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "slider" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Timeline Slider
        </button>
        <button
          onClick={() => h.setSubView("diff")}
          className={`px-3 py-1 rounded text-sm ${h.subView === "diff" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
        >
          Diff Compare
        </button>
      </div>

      <div className="flex-1 flex min-h-0">
        {h.subView === "chart" && (
          <ComplexityChart
            metrics={h.metrics}
            spikes={h.spikes}
            onSpikeClick={h.compareVersions}
          />
        )}
        {h.subView === "slider" && (
          <TimelineSlider
            versions={h.versions}
            selectedVersion={h.selectedVersion}
            graphData={h.selectedGraph}
            loading={h.loading}
            onVersionChange={h.selectVersion}
          />
        )}
        {h.subView === "diff" && (
          <DiffCompare
            oldCode={h.compareVersion}
            newCode={h.selectedVersion}
            oldGraph={h.compareGraph}
            newGraph={h.selectedGraph}
            diff={h.diff}
          />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Modify `client/src/components/ViewSwitcher.tsx`**

Find the existing `VIEW_OPTIONS` array and add the history option:

```typescript
const VIEW_OPTIONS: { value: ViewMode; label: string }[] = [
  { value: "graph", label: "Graph View" },
  { value: "dependency", label: "Dependency Graph" },
  { value: "heatmap", label: "Complexity Heatmap" },
  { value: "chapter-overview", label: "Chapter Overview" },
  { value: "interaction-matrix", label: "Interaction Matrix" },
  { value: "history", label: "History (Complexity Evolution)" },
];
```

- [ ] **Step 3: Modify `client/src/App.tsx`**

Add the import:

```typescript
import { HistoryView } from "./components/HistoryView/HistoryView.js";
```

In the `renderView()` switch statement, add a new case:

```typescript
case "history":
  return <HistoryView />;
```

- [ ] **Step 4: Verify TypeScript**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add client/src/components/HistoryView/HistoryView.tsx client/src/components/ViewSwitcher.tsx client/src/App.tsx
git commit -m "feat(client): HistoryView container integrated as 6th ViewSwitcher option"
```

---

### Task 16: Final verification and end-to-end test

- [ ] **Step 1: Run all parser tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -m pytest tests/ -v`
Expected: All existing tests + new history tests pass (~15+ new tests added).

- [ ] **Step 2: Run all server tests**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/server && npx vitest run`
Expected: All tests pass.

- [ ] **Step 3: Verify client builds**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/client && npx tsc --noEmit && npx vite build`
Expected: Build succeeds with no errors.

- [ ] **Step 4: Smoke test the version walker (real network call)**

Run: `cd /Users/deosigner/Documents/claude/MTGRuler/parser && python -c "from history.walk_versions import walk_all_versions; v = walk_all_versions(); print(f'Enumerated {len(v)} versions: {v[0][\"set_code\"]} ... {v[-1][\"set_code\"]}')"`
Expected: Output like `Enumerated 80+ versions: ODY ... TMT`. May take 30-60 seconds.

- [ ] **Step 5: Commit any cleanup if needed and report done**

```bash
git status
# If clean: ready to start running the actual pipeline
```

Final smoke check that the wiring is complete. Actually running the full pipeline (Tasks 7's `run_history_pipeline.py --max-versions 5`) is left as a separate operational step, since it consumes LLM credits.
