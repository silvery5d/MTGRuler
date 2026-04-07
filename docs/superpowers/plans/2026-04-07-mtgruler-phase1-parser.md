# MTGRuler Phase 1: Parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python data pipeline that fetches MTG Comprehensive Rules (EN + CN), extracts concepts and relationships via LLM, and writes them to a SQLite database.

**Architecture:** Three-stage pipeline — (1) fetch & preprocess raw rule text into structured entries, (2) use Claude API to extract concepts and relationships from each chapter, (3) validate and write to SQLite. Results cached at each stage to avoid redundant API calls.

**Tech Stack:** Python 3.11+, httpx, beautifulsoup4, anthropic SDK, sqlite3 (stdlib)

**Spec:** `docs/superpowers/specs/2026-04-07-mtgruler-knowledge-graph-design.md`

---

## File Structure

```
parser/
├── requirements.txt          # Dependencies
├── fetch_rules.py            # Fetch EN rules file + scrape CN wiki pages
├── preprocess.py             # Split by chapter/entry, align EN/CN
├── extract.py                # LLM concept extraction via Claude API
├── build_db.py               # Validate, dedupe, write SQLite
├── run_pipeline.py           # Orchestrate all stages
├── cache/                    # LLM response cache (JSON files per chapter)
├── data/
│   ├── raw/                  # Downloaded rule texts
│   │   ├── comp_rules_en.txt
│   │   └── comp_rules_cn.json
│   ├── processed/            # Structured intermediates
│   │   ├── entries_en.json
│   │   ├── entries_cn.json
│   │   └── aligned.json
│   └── concepts.db           # Final SQLite database
└── tests/
    ├── test_preprocess.py
    ├── test_extract.py
    └── test_build_db.py
```

---

### Task 1: Project Setup

**Files:**
- Create: `parser/requirements.txt`
- Create: `parser/data/raw/.gitkeep`
- Create: `parser/data/processed/.gitkeep`
- Create: `parser/cache/.gitkeep`

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler
mkdir -p parser/{data/{raw,processed},cache,tests}
touch parser/data/raw/.gitkeep parser/data/processed/.gitkeep parser/cache/.gitkeep
touch parser/__init__.py parser/tests/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

```
httpx>=0.27
beautifulsoup4>=4.12
lxml>=5.0
anthropic>=0.40
```

- [ ] **Step 3: Set up virtual environment and install**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/parser
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest
```

- [ ] **Step 4: Commit**

```bash
git add parser/
git commit -m "feat(parser): initialize parser project structure and dependencies"
```

---

### Task 2: Fetch English Rules

**Files:**
- Create: `parser/fetch_rules.py`
- Create: `parser/tests/test_fetch.py`

- [ ] **Step 1: Write the test**

```python
# parser/tests/test_fetch.py
import json
from pathlib import Path

def test_parse_en_rules_structure():
    """Test that EN rules text can be parsed into chapter dict."""
    # Simulate a small snippet of real Comprehensive Rules format
    sample = """Magic: The Gathering Comprehensive Rules

These rules are effective as of...

Contents
1. Game Concepts
100. General
101. The Magic Golden Rules

1. Game Concepts

100. General

100.1. These Magic rules apply to any Magic game with two or more players...

100.2. To play, each player needs their own deck...

101. The Magic Golden Rules

101.1. Whenever a card's text directly contradicts these rules, the card takes precedence...

101.2. When a rule or effect allows or directs something to happen...

2. Parts of a Card

200. General

200.1. The parts of a card are name, mana cost...

Glossary

Abandon — ...
"""
    from fetch_rules import parse_en_chapters
    chapters = parse_en_chapters(sample)

    assert "1" in chapters, "Chapter 1 should exist"
    assert "2" in chapters, "Chapter 2 should exist"
    # Chapter 1 should contain rules 100.x and 101.x
    assert any("100.1" in entry["rule_ref"] for entry in chapters["1"])
    assert any("101.1" in entry["rule_ref"] for entry in chapters["1"])
    # Each entry has rule_ref and text
    for entry in chapters["1"]:
        assert "rule_ref" in entry
        assert "text" in entry
        assert len(entry["text"]) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/parser
source .venv/bin/activate
python -m pytest tests/test_fetch.py::test_parse_en_rules_structure -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'fetch_rules'`

- [ ] **Step 3: Implement fetch_rules.py**

```python
# parser/fetch_rules.py
"""Fetch and parse MTG Comprehensive Rules (EN + CN)."""

import re
import json
import httpx
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"

# --- English Rules ---

# The official rules URL (Wizards publishes a .txt file)
EN_RULES_URL = "https://media.wizards.com/2024/downloads/MagicCompRules_20250404.txt"


def fetch_en_rules(force: bool = False) -> str:
    """Download the official EN Comprehensive Rules text file."""
    out = RAW_DIR / "comp_rules_en.txt"
    if out.exists() and not force:
        return out.read_text(encoding="utf-8")

    resp = httpx.get(EN_RULES_URL, follow_redirects=True, timeout=60)
    resp.raise_for_status()
    # The file is UTF-8 with BOM sometimes
    text = resp.content.decode("utf-8-sig")
    out.write_text(text, encoding="utf-8")
    return text


def parse_en_chapters(text: str) -> dict[str, list[dict]]:
    """
    Parse EN rules text into a dict keyed by chapter number.
    Each value is a list of {"rule_ref": "100.1a", "text": "..."}.

    The rules text has this structure:
      - Header / TOC
      - Chapter sections like "1. Game Concepts"
      - Rule entries like "100.1. Some rule text..."
      - Glossary at the end
    """
    chapters: dict[str, list[dict]] = {}

    # Find where the actual rules start (after TOC) and end (before Glossary)
    # Rules start with a line like "1. Game Concepts"
    lines = text.split("\n")

    in_rules = False
    current_chapter = None

    # Pattern for chapter headers: "N. Title" at start of line
    chapter_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    # Pattern for rule entries: "NNN.Na. text" or "NNN.N. text"
    rule_pattern = re.compile(r"^(\d{3}\.\d+[a-z]?)\.\s+(.+)")

    # Track multi-line rule text
    current_rule_ref = None
    current_rule_lines: list[str] = []

    def flush_rule():
        nonlocal current_rule_ref, current_rule_lines
        if current_rule_ref and current_chapter is not None:
            chapters.setdefault(current_chapter, []).append({
                "rule_ref": current_rule_ref,
                "text": " ".join(current_rule_lines).strip(),
            })
        current_rule_ref = None
        current_rule_lines = []

    for line in lines:
        stripped = line.strip()

        # Stop at Glossary
        if stripped.lower() == "glossary":
            flush_rule()
            break

        # Detect chapter header
        ch_match = chapter_pattern.match(stripped)
        if ch_match and not rule_pattern.match(stripped):
            flush_rule()
            current_chapter = ch_match.group(1)
            in_rules = True
            continue

        if not in_rules:
            continue

        # Detect rule entry
        rule_match = rule_pattern.match(stripped)
        if rule_match:
            flush_rule()
            current_rule_ref = rule_match.group(1)
            current_rule_lines = [rule_match.group(2)]
        elif current_rule_ref and stripped:
            # Continuation of current rule
            current_rule_lines.append(stripped)

    flush_rule()
    return chapters


if __name__ == "__main__":
    print("Fetching EN rules...")
    text = fetch_en_rules()
    chapters = parse_en_chapters(text)
    # Save structured output
    out = DATA_DIR / "processed" / "entries_en.json"
    out.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(v) for v in chapters.values())
    print(f"Parsed {len(chapters)} chapters, {total} rule entries.")
    print(f"Saved to {out}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/parser
source .venv/bin/activate
PYTHONPATH=. python -m pytest tests/test_fetch.py -v
```
Expected: PASS

- [ ] **Step 5: Run the fetcher on real data**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/parser
source .venv/bin/activate
python fetch_rules.py
```
Expected: Downloads rules, prints chapter/entry counts. If the URL is outdated, update `EN_RULES_URL` in `fetch_rules.py` to the latest Wizards download link (search for "Magic Comprehensive Rules" on their site).

- [ ] **Step 6: Commit**

```bash
git add parser/fetch_rules.py parser/tests/test_fetch.py
git commit -m "feat(parser): fetch and parse EN comprehensive rules"
```

---

### Task 3: Scrape Chinese Translation

**Files:**
- Modify: `parser/fetch_rules.py` (add CN fetching functions)
- Create: `parser/tests/test_fetch_cn.py`

- [ ] **Step 1: Investigate the CN wiki structure**

Open https://wiki.mtgjudge.cn/cr in a browser. Note:
- How chapters are organized (separate pages per chapter? single page?)
- The HTML structure of rule entries
- URL patterns (e.g., `/cr/1`, `/cr/2`, etc.)

Use WebFetch to inspect:
```bash
# Fetch the main CR index page to understand structure
```

- [ ] **Step 2: Write the test**

```python
# parser/tests/test_fetch_cn.py

def test_parse_cn_page():
    """Test parsing a CN wiki HTML page into rule entries."""
    # Simulated HTML based on observed wiki structure
    sample_html = """
    <div class="rule-content">
        <p><b>100.1.</b> 这些万智牌规则适用于任何两人或多人的万智牌游戏...</p>
        <p><b>100.2.</b> 进行游戏时，每位牌手需要拥有自己的套牌...</p>
    </div>
    """
    from fetch_rules import parse_cn_page
    entries = parse_cn_page(sample_html)

    assert len(entries) >= 2
    assert entries[0]["rule_ref"] == "100.1"
    assert "万智牌" in entries[0]["text"]
```

- [ ] **Step 3: Run test to verify it fails**

```bash
PYTHONPATH=. python -m pytest tests/test_fetch_cn.py -v
```
Expected: FAIL — `ImportError: cannot import name 'parse_cn_page'`

- [ ] **Step 4: Implement CN fetching**

Add to `parser/fetch_rules.py`:

```python
# --- Chinese Translation ---

CN_WIKI_BASE = "https://wiki.mtgjudge.cn/cr"


def fetch_cn_rules(force: bool = False) -> dict[str, list[dict]]:
    """Scrape CN translation from wiki.mtgjudge.cn/cr."""
    out = RAW_DIR / "comp_rules_cn.json"
    if out.exists() and not force:
        return json.loads(out.read_text(encoding="utf-8"))

    from bs4 import BeautifulSoup

    # First fetch the index page to discover chapter URLs
    resp = httpx.get(CN_WIKI_BASE, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Find chapter links — adapt selectors after inspecting actual page
    chapter_links = []
    for a in soup.select("a[href]"):
        href = a["href"]
        # Look for links like /cr/1, /cr/2, etc.
        if re.match(r".*/cr/\d+$", href):
            chapter_num = href.rstrip("/").split("/")[-1]
            full_url = href if href.startswith("http") else f"https://wiki.mtgjudge.cn{href}"
            chapter_links.append((chapter_num, full_url))

    chapters: dict[str, list[dict]] = {}
    for ch_num, url in chapter_links:
        print(f"  Fetching CN chapter {ch_num}...")
        resp = httpx.get(url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        entries = parse_cn_page(resp.text)
        if entries:
            chapters[ch_num] = entries

    out.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    return chapters


def parse_cn_page(html: str) -> list[dict]:
    """Parse a single CN wiki page into rule entries."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    entries = []

    # Strategy: find all text nodes matching rule_ref pattern "NNN.N."
    # The exact selector depends on the wiki's HTML structure.
    # Common patterns: <p><b>100.1.</b> text</p> or <div class="rule">...
    rule_pattern = re.compile(r"^(\d{3}\.\d+[a-z]?)\.\s*(.+)", re.DOTALL)

    # Try extracting from <p> tags containing bold rule refs
    for p in soup.find_all(["p", "div", "li"]):
        text = p.get_text(strip=True)
        m = rule_pattern.match(text)
        if m:
            entries.append({
                "rule_ref": m.group(1),
                "text": m.group(2).strip(),
            })

    return entries
```

- [ ] **Step 5: Run test to verify it passes**

```bash
PYTHONPATH=. python -m pytest tests/test_fetch_cn.py -v
```
Expected: PASS

- [ ] **Step 6: Test on real wiki (manual verification)**

```bash
python -c "
from fetch_rules import fetch_cn_rules
chapters = fetch_cn_rules()
for ch, entries in sorted(chapters.items()):
    print(f'Chapter {ch}: {len(entries)} entries')
"
```

If selectors don't match the actual wiki HTML, adjust `parse_cn_page()` and `fetch_cn_rules()` after inspecting the real page structure. This is expected — scraping requires adapting to the actual DOM.

- [ ] **Step 7: Commit**

```bash
git add parser/fetch_rules.py parser/tests/test_fetch_cn.py
git commit -m "feat(parser): scrape Chinese translation from wiki.mtgjudge.cn"
```

---

### Task 4: Preprocess & Align EN/CN

**Files:**
- Create: `parser/preprocess.py`
- Create: `parser/tests/test_preprocess.py`

- [ ] **Step 1: Write the test**

```python
# parser/tests/test_preprocess.py
import json

def test_align_entries():
    """Test EN/CN alignment by rule_ref."""
    from preprocess import align_entries

    en_chapters = {
        "1": [
            {"rule_ref": "100.1", "text": "These Magic rules apply..."},
            {"rule_ref": "100.2", "text": "To play, each player needs..."},
            {"rule_ref": "101.1", "text": "Whenever a card's text..."},
        ]
    }
    cn_chapters = {
        "1": [
            {"rule_ref": "100.1", "text": "这些万智牌规则适用于..."},
            {"rule_ref": "100.2", "text": "进行游戏时..."},
            # 101.1 missing in CN — should still appear with empty cn
        ]
    }
    aligned = align_entries(en_chapters, cn_chapters)

    assert len(aligned) == 3
    assert aligned[0]["rule_ref"] == "100.1"
    assert aligned[0]["text_en"] == "These Magic rules apply..."
    assert aligned[0]["text_cn"] == "这些万智牌规则适用于..."
    assert aligned[0]["chapter"] == "1"
    # Missing CN entry should have empty string
    assert aligned[2]["rule_ref"] == "101.1"
    assert aligned[2]["text_cn"] == ""


def test_group_by_chapter():
    """Test grouping aligned entries back by chapter."""
    from preprocess import align_entries, group_by_chapter

    en = {"1": [{"rule_ref": "100.1", "text": "A"}],
          "2": [{"rule_ref": "200.1", "text": "B"}]}
    cn = {"1": [{"rule_ref": "100.1", "text": "甲"}],
          "2": [{"rule_ref": "200.1", "text": "乙"}]}

    aligned = align_entries(en, cn)
    grouped = group_by_chapter(aligned)

    assert "1" in grouped
    assert "2" in grouped
    assert grouped["1"][0]["text_en"] == "A"
    assert grouped["2"][0]["text_cn"] == "乙"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
PYTHONPATH=. python -m pytest tests/test_preprocess.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement preprocess.py**

```python
# parser/preprocess.py
"""Align EN and CN rule entries by rule_ref."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def align_entries(
    en_chapters: dict[str, list[dict]],
    cn_chapters: dict[str, list[dict]],
) -> list[dict]:
    """
    Align EN and CN entries by rule_ref.
    Returns flat list of {"rule_ref", "text_en", "text_cn", "chapter"}.
    EN is the authority — every EN entry appears; CN fills in where available.
    """
    # Build CN lookup: rule_ref -> text
    cn_lookup: dict[str, str] = {}
    for entries in cn_chapters.values():
        for entry in entries:
            cn_lookup[entry["rule_ref"]] = entry["text"]

    aligned = []
    for chapter, entries in sorted(en_chapters.items()):
        for entry in entries:
            aligned.append({
                "rule_ref": entry["rule_ref"],
                "text_en": entry["text"],
                "text_cn": cn_lookup.get(entry["rule_ref"], ""),
                "chapter": chapter,
            })
    return aligned


def group_by_chapter(aligned: list[dict]) -> dict[str, list[dict]]:
    """Group aligned entries by chapter number."""
    grouped: dict[str, list[dict]] = {}
    for entry in aligned:
        grouped.setdefault(entry["chapter"], []).append(entry)
    return grouped


if __name__ == "__main__":
    en_path = DATA_DIR / "processed" / "entries_en.json"
    cn_path = DATA_DIR / "raw" / "comp_rules_cn.json"

    en_chapters = json.loads(en_path.read_text(encoding="utf-8"))
    cn_chapters = json.loads(cn_path.read_text(encoding="utf-8"))

    aligned = align_entries(en_chapters, cn_chapters)
    grouped = group_by_chapter(aligned)

    out = DATA_DIR / "processed" / "aligned.json"
    out.write_text(json.dumps(grouped, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(aligned)
    matched = sum(1 for a in aligned if a["text_cn"])
    print(f"Aligned {total} entries, {matched} have CN translation ({matched*100//total}%).")
    print(f"Saved to {out}")
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=. python -m pytest tests/test_preprocess.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add parser/preprocess.py parser/tests/test_preprocess.py
git commit -m "feat(parser): align EN/CN rule entries by rule_ref"
```

---

### Task 5: LLM Concept Extraction

**Files:**
- Create: `parser/extract.py`
- Create: `parser/tests/test_extract.py`

- [ ] **Step 1: Write the test**

```python
# parser/tests/test_extract.py
import json

def test_build_extraction_prompt():
    """Test that the extraction prompt includes rule entries."""
    from extract import build_extraction_prompt

    entries = [
        {"rule_ref": "702.9", "text_en": "Flying", "text_cn": "飞行", "chapter": "7"},
        {"rule_ref": "702.9a", "text_en": "A creature with flying...", "text_cn": "具有飞行异能的生物...", "chapter": "7"},
    ]
    prompt = build_extraction_prompt(entries, chapter="7")
    assert "702.9" in prompt
    assert "Flying" in prompt
    assert "飞行" in prompt


def test_parse_llm_response():
    """Test parsing a simulated LLM JSON response."""
    from extract import parse_llm_response

    raw = json.dumps({
        "concepts": [
            {
                "id": "keyword.flying",
                "name_en": "Flying",
                "name_cn": "飞行",
                "type": "Keyword",
                "rule_ref": "702.9",
                "definition_en": "A creature with flying can't be blocked except by creatures with flying or reach.",
                "definition_cn": "具有飞行异能的生物不能被不具有飞行或延势的生物阻挡。",
                "complexity": 2,
                "design_notes": "Core evasion mechanic"
            }
        ],
        "relations": [
            {
                "source_id": "keyword.flying",
                "target_id": "keyword.reach",
                "type": "INTERACTS_WITH",
                "rule_ref": "702.9a",
                "description": "Reach allows blocking creatures with flying"
            }
        ]
    })

    concepts, relations = parse_llm_response(raw)
    assert len(concepts) == 1
    assert concepts[0]["id"] == "keyword.flying"
    assert concepts[0]["type"] == "Keyword"
    assert len(relations) == 1
    assert relations[0]["type"] == "INTERACTS_WITH"


def test_parse_llm_response_handles_markdown_fence():
    """LLM sometimes wraps JSON in ```json ... ``` — parser should handle it."""
    from extract import parse_llm_response

    raw = '```json\n{"concepts": [], "relations": []}\n```'
    concepts, relations = parse_llm_response(raw)
    assert concepts == []
    assert relations == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
PYTHONPATH=. python -m pytest tests/test_extract.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement extract.py**

```python
# parser/extract.py
"""Extract concepts and relations from rule entries using Claude API."""

import json
import re
import hashlib
from pathlib import Path

import anthropic

CACHE_DIR = Path(__file__).parent / "cache"

SYSTEM_PROMPT = """\
You are an expert on Magic: The Gathering rules. Your task is to extract structured knowledge from MTG Comprehensive Rules entries.

Given a set of rule entries from one chapter, extract:

1. **Concepts** — the core game concepts defined or referenced in these rules.
2. **Relations** — how these concepts relate to each other.

For each concept, provide:
- id: a unique identifier in the format "type.snake_case_name" (e.g., "keyword.flying", "zone.battlefield", "phase.combat")
- name_en: English name
- name_cn: Chinese name
- type: one of Chapter, Concept, Zone, CardType, Phase, Step, Keyword, Action, MechanicPattern
- rule_ref: the primary rule reference (e.g., "702.9")
- definition_en: concise English definition
- definition_cn: concise Chinese definition
- complexity: 1-5 (1=simple/intuitive, 5=very complex/many edge cases)
- design_notes: brief note on the mechanic's design purpose or pattern

For each relation, provide:
- source_id: concept id
- target_id: concept id
- type: one of CONTAINS, DEPENDS_ON, REFERENCES, OCCURS_IN, MODIFIES, INTERACTS_WITH, MOVES_TO, PATTERN_OF
- rule_ref: the rule that establishes this relationship
- description: brief explanation

Output valid JSON with keys "concepts" and "relations". No markdown fences.\
"""

USER_PROMPT_TEMPLATE = """\
Extract concepts and relations from Chapter {chapter} of the MTG Comprehensive Rules.

Rule entries:

{entries_text}

Return JSON with "concepts" and "relations" arrays.\
"""


def build_extraction_prompt(entries: list[dict], chapter: str) -> str:
    """Build the user prompt with rule entries."""
    lines = []
    for e in entries:
        cn_part = f" | CN: {e['text_cn']}" if e.get("text_cn") else ""
        lines.append(f"{e['rule_ref']}. {e['text_en']}{cn_part}")
    entries_text = "\n".join(lines)
    return USER_PROMPT_TEMPLATE.format(chapter=chapter, entries_text=entries_text)


def parse_llm_response(raw: str) -> tuple[list[dict], list[dict]]:
    """Parse LLM response into (concepts, relations)."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    data = json.loads(cleaned)
    return data.get("concepts", []), data.get("relations", [])


def extract_chapter(
    entries: list[dict],
    chapter: str,
    model: str = "claude-sonnet-4-20250514",
    force: bool = False,
) -> tuple[list[dict], list[dict]]:
    """
    Extract concepts and relations for one chapter.
    Results are cached to avoid redundant API calls.
    """
    # Cache key based on chapter + content hash
    content_hash = hashlib.md5(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:8]
    cache_file = CACHE_DIR / f"chapter_{chapter}_{content_hash}.json"

    if cache_file.exists() and not force:
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        return cached["concepts"], cached["relations"]

    # Build prompt
    user_prompt = build_extraction_prompt(entries, chapter)

    # Call Claude API
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_response = message.content[0].text
    concepts, relations = parse_llm_response(raw_response)

    # Ensure chapter field is set on all concepts
    for c in concepts:
        c.setdefault("chapter", chapter)

    # Cache result
    cache_data = {"concepts": concepts, "relations": relations}
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return concepts, relations


def extract_all(
    aligned_by_chapter: dict[str, list[dict]],
    model: str = "claude-sonnet-4-20250514",
    force: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Extract concepts and relations from all chapters."""
    all_concepts = []
    all_relations = []

    for chapter in sorted(aligned_by_chapter.keys(), key=lambda x: int(x)):
        entries = aligned_by_chapter[chapter]
        print(f"  Extracting chapter {chapter} ({len(entries)} entries)...")

        # Split large chapters into batches of ~100 entries to stay within context
        batch_size = 100
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            batch_id = f"{chapter}" if len(entries) <= batch_size else f"{chapter}_part{i // batch_size}"
            concepts, relations = extract_chapter(batch, batch_id, model=model, force=force)
            all_concepts.extend(concepts)
            all_relations.extend(relations)

    print(f"  Total: {len(all_concepts)} concepts, {len(all_relations)} relations")
    return all_concepts, all_relations


if __name__ == "__main__":
    from pathlib import Path
    DATA_DIR = Path(__file__).parent / "data"

    aligned_path = DATA_DIR / "processed" / "aligned.json"
    aligned = json.loads(aligned_path.read_text(encoding="utf-8"))

    concepts, relations = extract_all(aligned)

    out_c = DATA_DIR / "processed" / "concepts_raw.json"
    out_r = DATA_DIR / "processed" / "relations_raw.json"
    out_c.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    out_r.write_text(json.dumps(relations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {out_c} and {out_r}")
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=. python -m pytest tests/test_extract.py -v
```
Expected: PASS (tests only cover prompt building and response parsing, no API calls)

- [ ] **Step 5: Commit**

```bash
git add parser/extract.py parser/tests/test_extract.py
git commit -m "feat(parser): LLM concept extraction with caching"
```

---

### Task 6: Build SQLite Database

**Files:**
- Create: `parser/build_db.py`
- Create: `parser/tests/test_build_db.py`

- [ ] **Step 1: Write the test**

```python
# parser/tests/test_build_db.py
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

        # Query back
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
        {"id": "keyword.flying", "name_en": "Flying", "complexity": 3},  # dupe
        {"id": "keyword.reach", "name_en": "Reach", "complexity": 1},
    ]
    deduped = dedupe_concepts(concepts)
    assert len(deduped) == 2
    ids = [c["id"] for c in deduped]
    assert ids.count("keyword.flying") == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
PYTHONPATH=. python -m pytest tests/test_build_db.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement build_db.py**

```python
# parser/build_db.py
"""Build the SQLite database from extracted concepts and relations."""

import json
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

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

-- Full-text search on rule texts (bilingual)
CREATE VIRTUAL TABLE IF NOT EXISTS rule_texts_fts USING fts5(
    rule_ref,
    text_en,
    text_cn,
    content='rule_texts',
    content_rowid='rowid'
);

-- FTS on concept names and definitions
CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    id,
    name_en,
    name_cn,
    definition_en,
    definition_cn,
    content='concepts',
    content_rowid='rowid'
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_concepts_type ON concepts(type);
CREATE INDEX IF NOT EXISTS idx_concepts_chapter ON concepts(chapter);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type);
CREATE INDEX IF NOT EXISTS idx_rule_texts_parent ON rule_texts(parent_concept_id);
"""

FTS_TRIGGERS = """
-- Keep FTS in sync with content tables
CREATE TRIGGER IF NOT EXISTS rule_texts_ai AFTER INSERT ON rule_texts BEGIN
    INSERT INTO rule_texts_fts(rowid, rule_ref, text_en, text_cn)
    VALUES (new.rowid, new.rule_ref, new.text_en, new.text_cn);
END;

CREATE TRIGGER IF NOT EXISTS concepts_ai AFTER INSERT ON concepts BEGIN
    INSERT INTO concepts_fts(rowid, id, name_en, name_cn, definition_en, definition_cn)
    VALUES (new.rowid, new.id, new.name_en, new.name_cn, new.definition_en, new.definition_cn);
END;
"""


def create_db(db_path: Path) -> sqlite3.Connection:
    """Create a new SQLite database with schema."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.executescript(FTS_TRIGGERS)
    return conn


def dedupe_concepts(concepts: list[dict]) -> list[dict]:
    """Remove duplicate concepts by id, keeping the first occurrence."""
    seen = set()
    result = []
    for c in concepts:
        if c["id"] not in seen:
            seen.add(c["id"])
            result.append(c)
    return result


def dedupe_relations(relations: list[dict]) -> list[dict]:
    """Remove duplicate relations by (source_id, target_id, type)."""
    seen = set()
    result = []
    for r in relations:
        key = (r["source_id"], r["target_id"], r["type"])
        if key not in seen:
            seen.add(key)
            result.append(r)
    return result


def insert_concepts(conn: sqlite3.Connection, concepts: list[dict]):
    """Insert concepts into the database."""
    conn.executemany(
        """INSERT OR REPLACE INTO concepts
           (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
           VALUES (:id, :name_en, :name_cn, :type, :rule_ref, :definition_en, :definition_cn, :chapter, :complexity, :design_notes)""",
        concepts,
    )
    conn.commit()


def insert_relations(conn: sqlite3.Connection, relations: list[dict]):
    """Insert relations into the database."""
    conn.executemany(
        """INSERT OR REPLACE INTO relations
           (source_id, target_id, type, rule_ref, description)
           VALUES (:source_id, :target_id, :type, :rule_ref, :description)""",
        relations,
    )
    conn.commit()


def insert_rule_texts(conn: sqlite3.Connection, rule_texts: list[dict]):
    """Insert rule texts into the database."""
    conn.executemany(
        """INSERT OR REPLACE INTO rule_texts
           (rule_ref, text_en, text_cn, parent_concept_id)
           VALUES (:rule_ref, :text_en, :text_cn, :parent_concept_id)""",
        rule_texts,
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

    # Load extracted data
    concepts_path = DATA_DIR / "processed" / "concepts_raw.json"
    relations_path = DATA_DIR / "processed" / "relations_raw.json"
    aligned_path = DATA_DIR / "processed" / "aligned.json"

    concepts = json.loads(concepts_path.read_text(encoding="utf-8"))
    relations = json.loads(relations_path.read_text(encoding="utf-8"))
    aligned = json.loads(aligned_path.read_text(encoding="utf-8"))

    # Dedupe
    concepts = dedupe_concepts(concepts)
    relations = dedupe_relations(relations)

    # Filter relations to only include known concept IDs
    concept_ids = {c["id"] for c in concepts}
    relations = [r for r in relations if r["source_id"] in concept_ids and r["target_id"] in concept_ids]

    # Build rule_texts from aligned entries
    # Map rule_ref to closest concept
    rule_ref_to_concept: dict[str, str] = {}
    for c in concepts:
        if c.get("rule_ref"):
            rule_ref_to_concept[c["rule_ref"]] = c["id"]

    rule_texts = []
    for chapter_entries in aligned.values():
        for entry in chapter_entries:
            # Find parent concept: exact match or prefix match
            parent = rule_ref_to_concept.get(entry["rule_ref"])
            if not parent:
                # Try matching by prefix (e.g., 702.9a -> 702.9)
                base_ref = entry["rule_ref"].rstrip("abcdefghijklmnopqrstuvwxyz")
                parent = rule_ref_to_concept.get(base_ref)

            rule_texts.append({
                "rule_ref": entry["rule_ref"],
                "text_en": entry["text_en"],
                "text_cn": entry["text_cn"],
                "parent_concept_id": parent,
            })

    # Create DB and insert
    conn = create_db(db_path)
    insert_concepts(conn, concepts)
    insert_relations(conn, relations)
    insert_rule_texts(conn, rule_texts)
    conn.close()

    print(f"Database built: {len(concepts)} concepts, {len(relations)} relations, {len(rule_texts)} rule texts")
    print(f"Saved to {db_path}")


if __name__ == "__main__":
    build(force=True)
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=. python -m pytest tests/test_build_db.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add parser/build_db.py parser/tests/test_build_db.py
git commit -m "feat(parser): build SQLite database with FTS5 search"
```

---

### Task 7: Pipeline Orchestrator

**Files:**
- Create: `parser/run_pipeline.py`

- [ ] **Step 1: Implement the orchestrator**

```python
# parser/run_pipeline.py
"""Run the full parser pipeline: fetch → preprocess → extract → build DB."""

import argparse
import json
from pathlib import Path

from fetch_rules import fetch_en_rules, parse_en_chapters, fetch_cn_rules
from preprocess import align_entries, group_by_chapter
from extract import extract_all
from build_db import build

DATA_DIR = Path(__file__).parent / "data"


def run(force: bool = False):
    """Execute the complete pipeline."""
    print("=" * 60)
    print("MTGRuler Parser Pipeline")
    print("=" * 60)

    # Stage 1: Fetch
    print("\n[1/4] Fetching rules...")
    en_text = fetch_en_rules(force=force)
    en_chapters = parse_en_chapters(en_text)
    # Save EN parsed output
    en_out = DATA_DIR / "processed" / "entries_en.json"
    en_out.write_text(json.dumps(en_chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    total_en = sum(len(v) for v in en_chapters.values())
    print(f"  EN: {len(en_chapters)} chapters, {total_en} entries")

    cn_chapters = fetch_cn_rules(force=force)
    total_cn = sum(len(v) for v in cn_chapters.values())
    print(f"  CN: {len(cn_chapters)} chapters, {total_cn} entries")

    # Stage 2: Preprocess
    print("\n[2/4] Aligning EN/CN entries...")
    aligned = align_entries(en_chapters, cn_chapters)
    grouped = group_by_chapter(aligned)
    aligned_out = DATA_DIR / "processed" / "aligned.json"
    aligned_out.write_text(json.dumps(grouped, ensure_ascii=False, indent=2), encoding="utf-8")
    matched = sum(1 for a in aligned if a["text_cn"])
    print(f"  {len(aligned)} entries aligned, {matched} with CN ({matched * 100 // max(len(aligned), 1)}%)")

    # Stage 3: Extract
    print("\n[3/4] Extracting concepts via LLM...")
    concepts, relations = extract_all(grouped, force=force)
    concepts_out = DATA_DIR / "processed" / "concepts_raw.json"
    relations_out = DATA_DIR / "processed" / "relations_raw.json"
    concepts_out.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    relations_out.write_text(json.dumps(relations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {len(concepts)} concepts, {len(relations)} relations extracted")

    # Stage 4: Build DB
    print("\n[4/4] Building SQLite database...")
    build(force=True)

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MTGRuler Parser Pipeline")
    parser.add_argument("--force", action="store_true", help="Force re-fetch and re-extract")
    args = parser.parse_args()
    run(force=args.force)
```

- [ ] **Step 2: Test the pipeline end-to-end**

```bash
cd /Users/deosigner/Documents/claude/MTGRuler/parser
source .venv/bin/activate
PYTHONPATH=. python run_pipeline.py
```

Expected: Pipeline runs through all 4 stages and creates `data/concepts.db`. The LLM extraction stage (3/4) will take several minutes and requires `ANTHROPIC_API_KEY` to be set.

- [ ] **Step 3: Verify the database**

```bash
sqlite3 parser/data/concepts.db "
SELECT type, COUNT(*) FROM concepts GROUP BY type ORDER BY COUNT(*) DESC;
SELECT type, COUNT(*) FROM relations GROUP BY type ORDER BY COUNT(*) DESC;
SELECT COUNT(*) FROM rule_texts;
"
```

- [ ] **Step 4: Commit**

```bash
git add parser/run_pipeline.py
echo "parser/data/raw/" >> .gitignore
echo "parser/data/processed/*.json" >> .gitignore
echo "parser/cache/" >> .gitignore
echo "parser/.venv/" >> .gitignore
git add .gitignore
git commit -m "feat(parser): add pipeline orchestrator and gitignore"
```

---

### Task 8: Add concepts.db to Repository

The SQLite database is a build artifact that downstream consumers (server) need. Include it in the repo so contributors can clone and run without running the parser.

- [ ] **Step 1: Verify DB exists and has data**

```bash
ls -lh parser/data/concepts.db
sqlite3 parser/data/concepts.db "SELECT COUNT(*) FROM concepts; SELECT COUNT(*) FROM relations; SELECT COUNT(*) FROM rule_texts;"
```

- [ ] **Step 2: Commit the database**

```bash
git add parser/data/concepts.db
git commit -m "data: add generated concepts.db for downstream consumers"
```

---

## Completion

After all tasks are done, the parser pipeline is complete. The output is `parser/data/concepts.db` containing:
- `concepts` table with all extracted concepts (bilingual)
- `relations` table with inter-concept relationships
- `rule_texts` table with full bilingual rule text
- FTS5 indexes for bilingual full-text search

**Next:** Proceed to Phase 2 (Server) plan.
