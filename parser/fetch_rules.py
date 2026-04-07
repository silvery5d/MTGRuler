"""Fetch and parse MTG Comprehensive Rules (EN + CN)."""

import re
import json
import httpx
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"

EN_RULES_URL = "https://media.wizards.com/2025/downloads/MagicCompRules%2020250404.txt"


def fetch_en_rules(force: bool = False) -> str:
    """Download the official EN Comprehensive Rules text file."""
    out = RAW_DIR / "comp_rules_en.txt"
    if out.exists() and not force:
        return out.read_text(encoding="utf-8")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    resp = httpx.get(EN_RULES_URL, follow_redirects=True, timeout=60)
    resp.raise_for_status()
    text = resp.content.decode("utf-8-sig")
    # Normalize line endings: \r\n -> \n, then lone \r -> \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out.write_text(text, encoding="utf-8")
    return text


def parse_en_chapters(text: str) -> dict[str, list[dict]]:
    """
    Parse EN rules text into a dict keyed by chapter number.
    Each value is a list of {"rule_ref": "100.1a", "text": "..."}.
    """
    chapters: dict[str, list[dict]] = {}
    lines = text.split("\n")

    in_rules = False
    has_rules = False
    current_chapter = None

    # Top-level chapters: "1. Game Concepts", "2. Parts of a Card", etc.
    chapter_pattern = re.compile(r"^(\d{1,2})\.\s+[A-Z]")
    # Section headings: "100. General", "101. The Magic Golden Rules", etc.
    section_pattern = re.compile(r"^(\d{3})\.\s+(.+)$")
    # Individual rules: "100.1. text" or "100.1a text" (subrules have no trailing dot)
    rule_pattern = re.compile(r"^(\d{3}\.\d+[a-z]?)\.?\s+(.+)")

    current_rule_ref = None
    current_rule_lines: list[str] = []

    def flush_rule():
        nonlocal current_rule_ref, current_rule_lines, has_rules
        if current_rule_ref and current_chapter is not None:
            chapters.setdefault(current_chapter, []).append({
                "rule_ref": current_rule_ref,
                "text": " ".join(current_rule_lines).strip(),
            })
            has_rules = True
        current_rule_ref = None
        current_rule_lines = []

    for line in lines:
        stripped = line.strip()

        # Stop at the Glossary section (but only after we've parsed actual rules,
        # since "Glossary" also appears in the Table of Contents).
        if stripped.lower() == "glossary" and has_rules:
            flush_rule()
            break

        # Check for top-level chapter heading (e.g. "1. Game Concepts")
        ch_match = chapter_pattern.match(stripped)
        if ch_match and not rule_pattern.match(stripped) and not section_pattern.match(stripped):
            flush_rule()
            current_chapter = ch_match.group(1)
            in_rules = True
            continue

        # Skip section headings (e.g. "100. General") — they don't change chapter
        if section_pattern.match(stripped) and not rule_pattern.match(stripped):
            flush_rule()
            continue

        if not in_rules:
            continue

        rule_match = rule_pattern.match(stripped)
        if rule_match:
            flush_rule()
            current_rule_ref = rule_match.group(1)
            current_rule_lines = [rule_match.group(2)]
        elif current_rule_ref and stripped:
            current_rule_lines.append(stripped)

    flush_rule()
    return chapters


if __name__ == "__main__":
    print("Fetching EN rules...")
    text = fetch_en_rules()
    chapters = parse_en_chapters(text)
    out_dir = DATA_DIR / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entries_en.json"
    out.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(v) for v in chapters.values())
    print(f"Parsed {len(chapters)} chapters, {total} rule entries.")
    print(f"Saved to {out}")
