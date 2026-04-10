"""
Audit concept rule_refs against the canonical section headers in comp_rules_en.txt.

For each concept whose rule_ref points at a section header in chapters 701/702
(keyword actions / keyword abilities — the most error-prone area), compare the
concept's English name against the section's canonical name. Flag mismatches.

Usage:
    python audit_rule_refs.py                       # report only
    python audit_rule_refs.py --suggest-fixes       # also try to find correct refs
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "comp_rules_en.txt"
DB = ROOT / "data" / "concepts.db"

SECTION_RE = re.compile(r"^(\d{3}\.\d+)\.\s+(.+?)\s*$")


def load_section_headers(path: Path) -> dict[str, str]:
    """Parse raw rules file for section headers like '702.22. Banding'."""
    sections: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            m = SECTION_RE.match(line)
            if not m:
                continue
            ref, title = m.group(1), m.group(2).strip()
            # Skip if "title" looks like prose (contains too many words or ends with period)
            # Real section headers are short, like "Infect" or "First Strike"
            if len(title) > 60 or title.endswith("."):
                continue
            # Prefer shortest title if duplicate (sometimes a rule is quoted in prose)
            if ref not in sections or len(title) < len(sections[ref]):
                sections[ref] = title
    return sections


def normalize(name: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace for fuzzy comparison."""
    s = re.sub(r"[^\w\s]", " ", name.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def build_name_index(sections: dict[str, str]) -> dict[str, str]:
    """Reverse index: normalized name → ref (for suggesting correct refs)."""
    idx: dict[str, str] = {}
    for ref, title in sections.items():
        idx[normalize(title)] = ref
    return idx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DB)
    ap.add_argument("--suggest-fixes", action="store_true")
    ap.add_argument(
        "--chapters",
        type=str,
        default="701,702",
        help="Comma-separated chapter prefixes to audit (e.g. '701,702')",
    )
    args = ap.parse_args()

    chapter_prefixes = tuple(c.strip() + "." for c in args.chapters.split(","))

    sections = load_section_headers(RAW)
    print(f"Loaded {len(sections)} section headers from raw rules")

    name_index = build_name_index(sections) if args.suggest_fixes else {}

    conn = sqlite3.connect(args.db)
    rows = conn.execute(
        "SELECT id, name_en, type, rule_ref FROM concepts "
        "WHERE rule_ref IS NOT NULL AND definition_en IS NOT NULL"
    ).fetchall()
    conn.close()

    # Keep only concepts whose rule_ref is a plain section header in target chapters
    # (i.e. no trailing letter) and exists in our section headers.
    targets: list[tuple[str, str, str, str]] = []
    for cid, name, ctype, ref in rows:
        if not any(ref.startswith(p) for p in chapter_prefixes):
            continue
        if re.search(r"[a-z]$", ref):  # skip subrules
            continue
        if ref not in sections:
            continue
        targets.append((cid, name, ctype, ref))

    print(f"Auditing {len(targets)} concepts in chapters {chapter_prefixes}\n")

    matches: list[tuple] = []
    mismatches: list[tuple] = []
    for cid, name, ctype, ref in targets:
        canonical = sections[ref]
        sim = similar(name, canonical)
        if sim >= 0.75:
            matches.append((cid, name, canonical, ref, sim))
        else:
            suggested = None
            if args.suggest_fixes:
                # Look up normalized name in index
                nname = normalize(name)
                # exact match first
                if nname in name_index:
                    suggested = name_index[nname]
                else:
                    # fuzzy: try each section, pick best
                    best_ref, best_sim = None, 0.8
                    for sref, stitle in sections.items():
                        if not any(sref.startswith(p) for p in chapter_prefixes):
                            continue
                        s = similar(name, stitle)
                        if s > best_sim:
                            best_ref, best_sim = sref, s
                    suggested = best_ref
            mismatches.append((cid, name, canonical, ref, sim, suggested))

    print(f"✓ Matches    : {len(matches)}")
    print(f"✗ Mismatches : {len(mismatches)}\n")

    if mismatches:
        print("=" * 80)
        print("MISMATCHES")
        print("=" * 80)
        for cid, name, canonical, ref, sim, suggested in mismatches:
            print(f"\n  {cid}")
            print(f"    concept name  : {name}")
            print(f"    rule_ref      : {ref}")
            print(f"    section title : {canonical!r}")
            print(f"    similarity    : {sim:.2f}")
            if suggested:
                print(f"    SUGGEST ref   : {suggested}  ({sections[suggested]!r})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
