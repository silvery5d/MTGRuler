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
    pct = matched * 100 // max(len(aligned), 1)
    print(f"  {len(aligned)} entries aligned, {matched} with CN ({pct}%)")

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
