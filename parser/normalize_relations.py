"""
Normalize relation types in concepts_raw.db, producing concepts.db.

- Maps 144+ non-canonical relation types to 9 canonical types.
- Splits `USES` by target: zone.* → OCCURS_IN, else → DEPENDS_ON.
- Drops self-loop and negative (BECOMES_NEVER) relations.
- Reverses direction for ATTRIBUTE_OF when mapping to CONTAINS.
- Writes concepts.db without touching concepts_raw.db.

Usage:
    python normalize_relations.py --dry-run    # report only, no DB writes
    python normalize_relations.py               # reads concepts_raw.db, writes concepts.db
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DB = ROOT / "data" / "concepts_raw.db"
OUT_DB = ROOT / "data" / "concepts.db"

CANONICAL = {
    "CONTAINS",
    "DEPENDS_ON",
    "REFERENCES",
    "OCCURS_IN",
    "MODIFIES",
    "INTERACTS_WITH",
    "MOVES_TO",
    "PATTERN_OF",
    "CREATES",
}

# Non-canonical -> canonical.
# USES is handled separately (context-dependent) and must not appear here.
MAPPING: dict[str, str] = {
    # --- CONTAINS ---
    "OWNES": "CONTAINS",  # typo for OWNS
    "HAS_FEATURE": "CONTAINS",
    "HAS_PART": "CONTAINS",
    "HAS": "CONTAINS",
    "HAS_PROPERTY": "CONTAINS",
    "HAS_DURATION": "CONTAINS",
    "HAS_SOURCE": "CONTAINS",
    "HAS_DEFAULT": "CONTAINS",
    "MAY_HAVE": "CONTAINS",
    "MAY_INCLUDE": "CONTAINS",
    "CAN_CONTAIN": "CONTAINS",
    "PART_OF": "CONTAINS",
    "BELONGS_TO": "CONTAINS",
    "MODIFIED_BY": "CONTAINS",
    # ATTRIBUTE_OF handled in normalize_type() — direction is reversed
    # MAY_CONTAIN handled in normalize_type() — maps to PATTERN_OF for drafting variants
    # --- DEPENDS_ON ---
    "DEPENDES_ON": "DEPENDS_ON",  # typo
    "USED_BY": "DEPENDS_ON",
    "USED_FOR": "DEPENDS_ON",
    "USED_IN": "DEPENDS_ON",
    "USED_TO_PAY": "DEPENDS_ON",
    "CAN_BE_PAID_WITH": "DEPENDS_ON",
    "REQUIRES": "DEPENDS_ON",
    "REQUIRED_FOR": "DEPENDS_ON",
    "ENABLES": "DEPENDS_ON",
    "ENABLED_BY": "DEPENDS_ON",
    "CONDITION_OF": "DEPENDS_ON",
    "CHECKED_WHEN": "DEPENDS_ON",
    "NOT_REQUIRED_FOR": "DEPENDS_ON",
    "CAN_BE_OVERCOME_BY": "DEPENDS_ON",
    "CAN_BE_REMOVED": "DEPENDS_ON",
    "MAY_REQUIRE": "DEPENDS_ON",
    "MUST_NOT_VIOLATE": "DEPENDS_ON",
    # --- REFERENCES ---
    "INDICATES": "REFERENCES",
    "REPRESENTS": "REFERENCES",
    "DEFINES": "REFERENCES",
    "DISTINGUISHED_FROM": "REFERENCES",
    "DISTINCT_FROM": "REFERENCES",
    "SIMILAR_TO": "REFERENCES",
    "COMPARES_TO": "REFERENCES",
    "SPECIAL_CASE": "REFERENCES",
    "SPECIAL_RULE_FOR": "REFERENCES",
    "EXCEPTION_TO": "REFERENCES",
    "IMPLEMENTS": "REFERENCES",
    "SUBJECT_OF": "REFERENCES",
    # --- OCCURS_IN ---
    "FUNCTION_IN": "OCCURS_IN",
    "RESIDES_IN": "OCCURS_IN",
    "LOCATED_IN": "OCCURS_IN",
    "STARTS_IN": "OCCURS_IN",
    "APPLIES_IN": "OCCURS_IN",
    "ACTIVATES_ON": "OCCURS_IN",
    "CAN_BE_CAST_FROM": "OCCURS_IN",
    "CAN_RETURN_TO": "OCCURS_IN",
    "ALWAYS_USED_IN": "OCCURS_IN",
    # --- MODIFIES ---
    "TRIGGERS": "MODIFIES",
    "TRIGGERS_FROM": "MODIFIES",
    "ENFORCES": "MODIFIES",
    "AFFECTS": "MODIFIES",
    "APPLIES_TO": "MODIFIES",
    "GRANTS": "MODIFIES",
    "IMPLICITLY_GRANTS": "MODIFIES",
    "RESULTS_IN": "MODIFIES",
    "RESULT_IN": "MODIFIES",
    "RESULT_OF": "MODIFIES",
    "CAUSES": "MODIFIES",
    "SETS": "MODIFIES",
    "LIMITS": "MODIFIES",
    "LIMITED_BY": "MODIFIES",
    "RESTRICTS": "MODIFIES",
    "PREVENTS": "MODIFIES",
    "CHECKS": "MODIFIES",
    "CANCELS": "MODIFIES",
    "SUPERSEDES": "MODIFIES",
    "OVERRIDES": "MODIFIES",
    "REPLACES": "MODIFIES",
    "CONTROLS": "MODIFIES",
    "CONTROLLED_BY": "MODIFIES",
    "ASSIGNS": "MODIFIES",
    "CALCULATES": "MODIFIES",
    "CALCULATES_MANA_FROM": "MODIFIES",
    "TRACKS": "MODIFIES",
    "INTERRUPTS": "MODIFIES",
    "ENDS_STEP": "MODIFIES",
    "SKIPS_TO": "MODIFIES",
    "STACKS_ABOVE": "MODIFIES",
    "EXEMPTS_FROM": "MODIFIES",
    "NOT_APPLICABLE": "MODIFIES",
    "AVOIDS": "MODIFIES",
    "INCREASES": "MODIFIES",
    "INCREASES_BY": "MODIFIES",
    "REDUCED_BY": "MODIFIES",
    "ALLOWS": "MODIFIES",
    "MANAGES": "MODIFIES",
    "CANNOT": "MODIFIES",
    "CANNOT_TARGET": "MODIFIES",
    "DEALS": "MODIFIES",
    "DEALS_NO": "MODIFIES",
    "DOES_NOT_CREATE": "MODIFIES",
    "CAN_ATTACK": "MODIFIES",
    "TUTORS": "MODIFIES",
    "ESTABLISHES": "MODIFIES",
    "PRIORITY_RULE": "MODIFIES",
    "FALLBACK_TO": "MODIFIES",
    "DETERMINED_BY": "MODIFIES",
    "CHOOSES": "MODIFIES",
    "ANNOUNCES": "MODIFIES",
    "SUBJECT_TO": "MODIFIES",
    "CHOICE_BETWEEN": "MODIFIES",
    # --- INTERACTS_WITH ---
    "ORDERS": "INTERACTS_WITH",
    "PRECEDES": "INTERACTS_WITH",
    "OCCURS_BEFORE": "INTERACTS_WITH",
    "EXPIRES_AT": "INTERACTS_WITH",
    "ADJACENT_TO": "INTERACTS_WITH",
    "ADDED_TO": "INTERACTS_WITH",
    "RECEIVES": "INTERACTS_WITH",
    "RECEIVES_AFTER": "INTERACTS_WITH",
    "RECEIVES_FIRST": "INTERACTS_WITH",
    "INDEPENDENT": "INTERACTS_WITH",
    "INDEPENDENT_OF": "INTERACTS_WITH",
    "ALTERNATIVE_OF": "INTERACTS_WITH",
    "COMPLEMENTS": "INTERACTS_WITH",
    "COCCURS_ON": "INTERACTS_WITH",  # typo
    "EQUALS": "INTERACTS_WITH",
    # --- MOVES_TO ---
    "MOVES_FROM": "MOVES_TO",
    "ENTERS": "MOVES_TO",
    "VISITS": "MOVES_TO",
    "BRANCHES_TO": "MOVES_TO",
    "RESOLVES": "MOVES_TO",
    "RESOLVES_IN": "MOVES_TO",
    # --- PATTERN_OF ---
    "IS_TYPE": "PATTERN_OF",
    "IS_TYPE_OF": "PATTERN_OF",
    "IS_A": "PATTERN_OF",
    "IS_VARIANT_OF": "PATTERN_OF",
    "IS_VARIATION": "PATTERN_OF",
    "VARIANT_OF": "PATTERN_OF",
    "EXTENDS": "PATTERN_OF",
    "IS_PATTERN": "PATTERN_OF",
    "IS_PATTERN_OF": "PATTERN_OF",
    "BECOMES": "PATTERN_OF",
    "CAN_BECOME": "PATTERN_OF",
    "BECOMES_NEVER": "PATTERN_OF",
    "CAN_BE": "PATTERN_OF",
    # --- CREATES (9th canonical) ---
    # The original CREATES type stays as-is (58 relations already use it).
    "GENERATES": "CREATES",
    "PRODUCES": "CREATES",
    "PRODUCED_BY": "CREATES",
    "MAY_CREATE": "CREATES",
}


def normalize_type(
    rel_type: str, source_id: str, target_id: str
) -> tuple[str | None, str, tuple[str, str] | None]:
    """Return (new_type, reason, maybe_swapped_endpoints).

    new_type=None means drop this relation.
    maybe_swapped_endpoints=None means keep (source, target) as-is, otherwise
    it's the new (source, target) tuple to use.
    """
    # 1. Self-loop → drop
    if source_id == target_id:
        return None, "self-loop", None

    # 2. BECOMES_NEVER has negative semantics — no canonical type fits → drop
    if rel_type == "BECOMES_NEVER":
        return None, "BECOMES_NEVER (negative, no canonical fit)", None

    # 3. ATTRIBUTE_OF reverses direction when mapped to CONTAINS
    # "X is attribute of Y" → "Y CONTAINS X"
    if rel_type == "ATTRIBUTE_OF":
        return "CONTAINS", "ATTRIBUTE_OF→CONTAINS (reversed)", (target_id, source_id)

    # 4. MAY_CONTAIN is weak containment — better as PATTERN_OF for variant relations
    if rel_type == "MAY_CONTAIN":
        return "PATTERN_OF", "MAY_CONTAIN→PATTERN_OF", None

    # 5. Already canonical → keep
    if rel_type in CANONICAL:
        return rel_type, "canonical", None

    # 6. USES splits by target type
    if rel_type == "USES":
        if target_id.startswith("zone."):
            return "OCCURS_IN", "USES→OCCURS_IN (target is zone)", None
        return "DEPENDS_ON", "USES→DEPENDS_ON", None

    # 7. Lookup mapping
    if rel_type in MAPPING:
        return MAPPING[rel_type], f"{rel_type}→{MAPPING[rel_type]}", None

    # 8. Unknown — keep as-is but flag
    return rel_type, f"UNMAPPED ({rel_type})", None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    ap.add_argument("--src", type=Path, default=SRC_DB)
    ap.add_argument("--out", type=Path, default=OUT_DB)
    args = ap.parse_args()

    src_conn = sqlite3.connect(args.src)
    rows = src_conn.execute(
        "SELECT source_id, target_id, type, rule_ref, description FROM relations"
    ).fetchall()
    src_conn.close()

    # Plan the transform.
    kept: list[tuple] = []          # (src, tgt, new_type, rule_ref, desc)
    dropped: list[tuple] = []       # (src, tgt, type, reason)
    unmapped: Counter = Counter()
    type_before: Counter = Counter()
    type_after: Counter = Counter()
    reasons: Counter = Counter()

    for src, tgt, t, rule_ref, desc in rows:
        type_before[t] += 1
        new_type, reason, swapped = normalize_type(t, src, tgt)
        reasons[reason] += 1
        if new_type is None:
            dropped.append((src, tgt, t, reason))
            continue
        if reason.startswith("UNMAPPED"):
            unmapped[t] += 1
        if swapped is not None:
            src, tgt = swapped
        kept.append((src, tgt, new_type, rule_ref, desc))
        type_after[new_type] += 1

    # Dedupe: same (source, target, type) may collide after normalization.
    # Keep the first rule_ref/description encountered.
    deduped: dict[tuple, tuple] = {}
    for src, tgt, t, rule_ref, desc in kept:
        key = (src, tgt, t)
        if key not in deduped:
            deduped[key] = (src, tgt, t, rule_ref, desc)
    deduped_rows = list(deduped.values())
    collapsed = len(kept) - len(deduped_rows)

    # Report.
    print(f"Input relations: {len(rows)}")
    print(f"  dropped:                 {len(dropped)}")
    print(f"  collapsed by dedup:      {collapsed}")
    print(f"  output relations:        {len(deduped_rows)}")
    print()
    print("Type distribution AFTER normalization:")
    for t, c in sorted(type_after.items(), key=lambda x: -x[1]):
        marker = "✓" if t in CANONICAL else "✗"
        print(f"  {marker} {t:20s} {c}")
    print()
    if unmapped:
        print("Unmapped types (kept as-is, add to MAPPING dict):")
        for t, c in unmapped.most_common():
            print(f"  - {t}: {c}")
        print()
    if dropped:
        print(f"Dropped relations ({len(dropped)}):")
        for src, tgt, t, reason in dropped[:20]:
            print(f"  - {src} --[{t}]--> {tgt}  ({reason})")
        if len(dropped) > 20:
            print(f"  ...and {len(dropped) - 20} more")
        print()

    if args.dry_run:
        print("(dry-run mode — no DB written)")
        return 0

    # Copy source DB, then rewrite the relations table in place.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(args.src, args.out)
    out_conn = sqlite3.connect(args.out)
    out_conn.execute("DELETE FROM relations")
    out_conn.executemany(
        "INSERT INTO relations (source_id, target_id, type, rule_ref, description) "
        "VALUES (?, ?, ?, ?, ?)",
        deduped_rows,
    )
    out_conn.commit()
    out_conn.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
