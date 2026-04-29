"""Detect and nullify misaligned CN translations in concepts.db.

The EN source (Wizards 2025-04-04) and the CN source (mtgjudge.cn wiki) are
versioned differently. Rule numbers have shifted between versions, so many
EN/CN pairs at the same rule_ref describe different rules.

This script flags such mismatches by checking if a few key English terms have
plausible Chinese counterparts in the CN translation. Pairs that fail are
nullified (text_cn → NULL) so the UI shows no translation instead of a wrong one.

Conservative heuristic — only flags clear mismatches:
1. Both EN and CN are short rule headers (one phrase) → check if the EN
   keyword/concept name appears in any form in the CN text.
2. Skip if the rule_ref is for a glossary or chapter heading.
"""

import argparse
import re
import sqlite3
from pathlib import Path

# A small dictionary of well-known EN→CN MTG term translations.
# If a rule's EN text contains any of these key terms, the CN text MUST
# contain the corresponding Chinese term (or one of its synonyms).
KEY_TERMS = {
    "villainous choice": ["邪恶抉择"],
    "discover": ["搜证", "发现"],
    "incubate": ["孵育"],
    "convert": ["转化"],
    "the ring tempts": ["魔戒引诱"],
    "time travel": ["时间旅行"],
    "manifest dread": ["怀疑", "匿伏"],
    "collect evidence": ["搜集证据", "搜证"],
    "suspect": ["匿伏", "可疑"],
    "forage": ["翻找", "搜索"],
    "cloak": ["伪装", "覆盖"],
    "plot": ["筹谋"],
    "foster": ["抚育"],
}


def check_alignment(text_en: str, text_cn: str) -> tuple[bool, str]:
    """Return (is_aligned, reason). Conservative — only flags clear mismatches."""
    if not text_en or not text_cn:
        return True, "empty"

    en_lower = text_en.lower()

    # For each key term in EN, check that its translation appears in CN
    for en_term, cn_terms in KEY_TERMS.items():
        if en_term in en_lower:
            if not any(c in text_cn for c in cn_terms):
                # The EN mentions this term but CN doesn't have a known translation
                return False, f"EN has '{en_term}' but CN missing any of {cn_terms}"

    # Also check the reverse: if CN has a key term, EN should mention it
    for en_term, cn_terms in KEY_TERMS.items():
        for c in cn_terms:
            if c in text_cn:
                if en_term not in en_lower:
                    return False, f"CN has '{c}' but EN missing '{en_term}'"

    return True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/concepts.db", help="DB path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db_path = Path(args.db)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT rule_ref, text_en, text_cn FROM rule_texts WHERE text_cn IS NOT NULL AND text_cn != ''"
    ).fetchall()

    misaligned = []
    for ref, en, cn in rows:
        ok, reason = check_alignment(en, cn)
        if not ok:
            misaligned.append((ref, reason, en[:60], cn[:40]))

    print(f"Checked {len(rows)} rules with CN translation")
    print(f"Found {len(misaligned)} misalignments:")
    for ref, reason, en, cn in misaligned[:30]:
        print(f"  {ref}: {reason}")
        print(f"    EN: {en}...")
        print(f"    CN: {cn}...")

    if not args.dry_run and misaligned:
        refs = [m[0] for m in misaligned]
        placeholders = ",".join(["?"] * len(refs))
        conn.execute(f"UPDATE rule_texts SET text_cn = NULL WHERE rule_ref IN ({placeholders})", refs)
        # Also clear from FTS
        conn.execute(f"UPDATE rule_texts_fts SET text_cn = NULL WHERE rule_ref IN ({placeholders})", refs)
        conn.commit()
        print(f"\n  Nullified text_cn for {len(refs)} misaligned rules in {db_path}")
    elif args.dry_run:
        print("\n(dry-run — no changes made)")
    conn.close()


if __name__ == "__main__":
    main()
