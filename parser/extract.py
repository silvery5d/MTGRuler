"""Extract concepts and relations from rule entries using Claude API."""

import json
import os
import re
import hashlib
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# Load .env from project root so ANTHROPIC_BASE_URL / ANTHROPIC_API_KEY /
# ANTHROPIC_MODEL are available to the SDK and to this module.
load_dotenv(Path(__file__).parent.parent / ".env")

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

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
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    data = json.loads(cleaned)
    return data.get("concepts", []), data.get("relations", [])


def _call_llm(entries: list[dict], chapter: str, model: str) -> tuple[list[dict], list[dict]] | None:
    """Single API call attempt. Returns (concepts, relations) on success, None on any failure."""
    import time
    user_prompt = build_extraction_prompt(entries, chapter)
    client = anthropic.Anthropic(timeout=120.0)

    # Network-level retries with 120s timeout per attempt
    message = None
    for attempt in range(4):
        try:
            with client.messages.stream(
                model=model,
                max_tokens=32768,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                message = stream.get_final_message()
            break
        except Exception as e:
            wait = 2 ** attempt
            print(f"  WARN: chapter {chapter} network attempt {attempt + 1}/4 failed ({type(e).__name__}), retrying in {wait}s...", flush=True)
            time.sleep(wait)
    if message is None:
        return None

    raw_response = next(
        (block.text for block in message.content if getattr(block, "type", None) == "text"),
        None,
    )
    if raw_response is None:
        print(f"  WARN: chapter {chapter} no text block in response", flush=True)
        return None

    if message.stop_reason == "max_tokens":
        print(f"  WARN: chapter {chapter} output truncated at max_tokens", flush=True)
        return None

    try:
        return parse_llm_response(raw_response)
    except json.JSONDecodeError as e:
        print(f"  WARN: chapter {chapter} JSON parse error at char {e.pos}", flush=True)
        return None


def extract_chapter(
    entries: list[dict],
    chapter: str,
    model: str = None,
    force: bool = False,
    min_split_size: int = 5,
) -> tuple[list[dict], list[dict]]:
    """
    Extract concepts and relations for one chapter.
    Results are cached to avoid redundant API calls.

    On failure, recursively splits the batch in half until min_split_size or success.
    """
    model = model or DEFAULT_MODEL
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    content_hash = hashlib.md5(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:8]
    cache_file = CACHE_DIR / f"chapter_{chapter}_{content_hash}.json"

    if cache_file.exists() and not force:
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        return cached["concepts"], cached["relations"]

    result = _call_llm(entries, chapter, model)

    if result is None:
        # Try splitting the batch in half
        if len(entries) >= min_split_size * 2:
            mid = len(entries) // 2
            print(f"  -> splitting chapter {chapter} ({len(entries)} entries) into {mid} + {len(entries) - mid}", flush=True)
            left_concepts, left_relations = extract_chapter(
                entries[:mid], f"{chapter}_a", model=model, force=force, min_split_size=min_split_size,
            )
            right_concepts, right_relations = extract_chapter(
                entries[mid:], f"{chapter}_b", model=model, force=force, min_split_size=min_split_size,
            )
            concepts = left_concepts + right_concepts
            relations = left_relations + right_relations
        else:
            print(f"  ERROR: chapter {chapter} below min split size, giving up", flush=True)
            return [], []
    else:
        concepts, relations = result

    for c in concepts:
        c.setdefault("chapter", chapter)

    cache_data = {"concepts": concepts, "relations": relations}
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return concepts, relations


def extract_all(
    aligned_by_chapter: dict[str, list[dict]],
    model: str = None,
    force: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Extract concepts and relations from all chapters."""
    model = model or DEFAULT_MODEL
    all_concepts = []
    all_relations = []

    for chapter in sorted(aligned_by_chapter.keys(), key=lambda x: int(x)):
        entries = aligned_by_chapter[chapter]
        print(f"  Extracting chapter {chapter} ({len(entries)} entries)...")

        batch_size = 40
        num_batches = (len(entries) + batch_size - 1) // batch_size
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            part_num = i // batch_size
            batch_id = f"{chapter}" if len(entries) <= batch_size else f"{chapter}_part{part_num}"
            print(f"    batch {part_num + 1}/{num_batches}...", flush=True)
            concepts, relations = extract_chapter(batch, batch_id, model=model, force=force)
            all_concepts.extend(concepts)
            all_relations.extend(relations)

    print(f"  Total: {len(all_concepts)} concepts, {len(all_relations)} relations")
    return all_concepts, all_relations


if __name__ == "__main__":
    DATA_DIR = Path(__file__).parent / "data"

    aligned_path = DATA_DIR / "processed" / "aligned.json"
    aligned = json.loads(aligned_path.read_text(encoding="utf-8"))

    concepts, relations = extract_all(aligned)

    out_c = DATA_DIR / "processed" / "concepts_raw.json"
    out_r = DATA_DIR / "processed" / "relations_raw.json"
    out_c.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    out_r.write_text(json.dumps(relations, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {out_c} and {out_r}")
