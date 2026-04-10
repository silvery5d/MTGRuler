"""
Apply targeted concept fixes to concepts.db (the curated DB).

Each fix is idempotent (checks current state before modifying).
Run after normalize_relations.py.

Usage:
    python apply_fixes.py                       # apply all fixes
    python apply_fixes.py --dry-run              # show what would change
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "concepts.db"

# Fix 2: Variant concepts mislabelled as Keyword (chapters 8xx/9xx).
# Detected by the validator and confirmed by inspection.
VARIANT_TYPE_FIXES = [
    # Fix 2a: keywords mis-labelled as Keyword, actually variants
    ("keyword.emperor", "Variant"),             # Emperor is a multiplayer variant
    ("keyword.commander_damage", "Concept"),    # Commander damage is a rules concept, not a variant
    ("keyword.two_headed_giant", "Variant"),    # 2HG multiplayer variant
    ("keyword.multi_headed_giant", "Variant"),  # Multi-headed giant variant
    ("keyword.alternating_teams", "Variant"),   # Alternating teams variant

    # Fix 2b: variant.* / multiplayer_variant.* concepts mis-labelled as Concept
    ("variant.emperor", "Variant"),
    ("variant.team_vs_team", "Variant"),
    ("variant.two_headed_giant", "Variant"),
    ("variant.commander", "Variant"),
    ("variant.brawl", "Variant"),
    ("variant.commander_draft", "Variant"),
    ("variant.archenemy", "Variant"),
    ("variant.conspiracy_draft", "Variant"),
    ("variant.super_villain_rumble", "Variant"),
    ("variant.archenemy_commander", "Variant"),
    ("multiplayer_variant.team_vs_team", "Variant"),
    ("multiplayer_variant.free_for_all", "Variant"),
    ("multiplayer_variant.grand_melee", "Variant"),
    # multiplayer_variant.shared_team_turns intentionally NOT changed:
    # rule 805 is "Shared Team Turns Option", an option used by variants,
    # not itself a variant. The id is misleading but the type Concept is right.
]

# Fix 3: rule_ref corrections for keywords pointing at the wrong section header.
# Surfaced by parser/audit_rule_refs.py comparing concept names to section titles.
RULE_REF_FIXES = [
    ("keyword.infect",    "702.90"),  # was 702.2 (Deathtouch)
    ("keyword.wither",    "702.80"),  # was 702.2 (Deathtouch)
    ("keyword.lifelink",  "702.15"),  # was 702.2 (Deathtouch)
    ("action.tap",        "701.21"),  # was 701.20 (Shuffle); 701.21 is "Tap and Untap"
    ("concept.daybound",  "702.145"), # was 702.126 (Improvise); 702.145 is "Daybound and Nightbound"

    # Fix 4: remaining wrong concepts from v3 validation
    ("concept.attacking",  "508.1"),  # was 302.5 (brief "creatures can attack") → 508.1 Declare Attackers
    ("zone.battlefield",   "403.1"),  # was 112.1 (spells) → 403.1 Battlefield
    ("concept.copy_spell", "707.10"), # was 706.2 (die rolls) → 707.10 Copying a Spell specifically

    # Fix 6: rule_ref corrections surfaced by v4_300 validation that audit missed
    ("concept.stack",         "405.1"),  # was 115.10 (affect vs target) → 405.1 Stack chapter
    ("zone.graveyard",        "404.1"),  # was 403 (Battlefield) → 404.1 Graveyard chapter
    ("cardtype.fortification","301.1"),  # was 702.67b (Fortify keyword) → 301.1 Artifacts
    ("concept.aura",          "303.4"),  # was 702.5b (Enchant ref) → 303.4 Aura specifically
]

# Fix 4b: concepts to delete outright (not real rules concepts).
CONCEPTS_TO_DELETE = [
    "mechanic.venture_marker",  # just a physical game piece, not a defined concept
]

# Fix 5: definition rewrites for concepts where the original LLM hallucinated
# details that contradict the rule text. Each entry is (id, new_definition_en).
DEFINITION_FIXES: list[tuple[str, str]] = [
    (
        "concept.copy_spell",
        "Putting a copy of a spell onto the stack without casting it. The copy "
        "inherits the original spell's characteristics and all decisions made for "
        "it (mode, targets, value of X, additional costs). A copy of a spell is "
        "itself a spell even though it has no card. New targets may only be chosen "
        "if the copying effect explicitly allows it.",
    ),
]


def apply(conn: sqlite3.Connection, dry_run: bool) -> None:
    changes: list[str] = []

    # --- Fix 2: type relabels ---
    for concept_id, new_type in VARIANT_TYPE_FIXES:
        row = conn.execute(
            "SELECT type FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if row is None:
            changes.append(f"SKIP  {concept_id}: not in DB")
            continue
        current_type = row[0]
        if current_type == new_type:
            changes.append(f"SKIP  {concept_id}: already type={new_type}")
            continue
        changes.append(
            f"FIX2  {concept_id}: type {current_type!r} → {new_type!r}"
        )
        if not dry_run:
            conn.execute(
                "UPDATE concepts SET type = ? WHERE id = ?",
                (new_type, concept_id),
            )

    # --- Fix 4b: delete concepts that shouldn't exist ---
    for concept_id in CONCEPTS_TO_DELETE:
        row = conn.execute(
            "SELECT id FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if row is None:
            changes.append(f"SKIP  {concept_id}: not in DB (already deleted)")
            continue
        # Count relations that will cascade
        rel_count = conn.execute(
            "SELECT COUNT(*) FROM relations WHERE source_id = ? OR target_id = ?",
            (concept_id, concept_id),
        ).fetchone()[0]
        changes.append(
            f"FIX4  DELETE {concept_id} (+ {rel_count} linked relations)"
        )
        if not dry_run:
            conn.execute(
                "DELETE FROM relations WHERE source_id = ? OR target_id = ?",
                (concept_id, concept_id),
            )
            conn.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
            conn.execute("DELETE FROM rule_texts WHERE parent_concept_id = ?", (concept_id,))

    # --- Fix 3: rule_ref corrections ---
    for concept_id, new_ref in RULE_REF_FIXES:
        row = conn.execute(
            "SELECT rule_ref FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if row is None:
            changes.append(f"SKIP  {concept_id}: not in DB")
            continue
        current_ref = row[0]
        if current_ref == new_ref:
            changes.append(f"SKIP  {concept_id}: already rule_ref={new_ref}")
            continue
        changes.append(
            f"FIX3  {concept_id}: rule_ref {current_ref!r} → {new_ref!r}"
        )
        if not dry_run:
            conn.execute(
                "UPDATE concepts SET rule_ref = ? WHERE id = ?",
                (new_ref, concept_id),
            )

    # --- Fix 5: definition rewrites ---
    for concept_id, new_def in DEFINITION_FIXES:
        row = conn.execute(
            "SELECT definition_en FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if row is None:
            changes.append(f"SKIP  {concept_id}: not in DB")
            continue
        if row[0] == new_def:
            changes.append(f"SKIP  {concept_id}: definition already up to date")
            continue
        changes.append(f"FIX5  {concept_id}: rewrote definition_en")
        if not dry_run:
            conn.execute(
                "UPDATE concepts SET definition_en = ? WHERE id = ?",
                (new_def, concept_id),
            )

    if not dry_run:
        conn.commit()

    for line in changes:
        print(line)
    applied = sum(1 for c in changes if c.startswith("FIX"))
    skipped = sum(1 for c in changes if c.startswith("SKIP"))
    print(f"\n{applied} changes {'would be ' if dry_run else ''}applied, {skipped} skipped")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", type=Path, default=DB_PATH)
    args = ap.parse_args()

    if not args.db.exists():
        print(f"ERROR: {args.db} not found. Run normalize_relations.py first.")
        return 1

    conn = sqlite3.connect(args.db)
    try:
        apply(conn, args.dry_run)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
