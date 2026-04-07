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
    cn_path = DATA_DIR / "raw" / "entries_cn_raw.json"

    en_chapters = json.loads(en_path.read_text(encoding="utf-8"))
    cn_chapters = json.loads(cn_path.read_text(encoding="utf-8"))

    aligned = align_entries(en_chapters, cn_chapters)
    grouped = group_by_chapter(aligned)

    out = DATA_DIR / "processed" / "aligned.json"
    out.write_text(json.dumps(grouped, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(aligned)
    matched = sum(1 for a in aligned if a["text_cn"])
    pct = matched * 100 // max(total, 1)
    print(f"Aligned {total} entries, {matched} have CN translation ({pct}%).")
    print(f"Saved to {out}")
