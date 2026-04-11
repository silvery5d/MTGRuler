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
