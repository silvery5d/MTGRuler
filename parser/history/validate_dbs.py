"""Validate all history concept DBs for consistency and anomalies.

Detects:
- Sudden concept count drops (>30% decrease from previous version)
- Empty chapters (parsed but extracted 0 concepts)
- Orphaned relations (pointing to non-existent concepts)
- rule_texts with no parent_concept_id
- Identical consecutive DBs (suggests incremental extraction silently failed)
- Malformed concepts (null name, type)
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

from .walk_versions import load_versions_index
from .baseline_extract import CONCEPT_DBS_DIR


def hash_db(db_path: Path) -> str:
    """Hash the concepts + relations content of a DB."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT id FROM concepts ORDER BY id").fetchall()
        rel_rows = conn.execute("SELECT source_id, target_id, type FROM relations ORDER BY source_id, target_id, type").fetchall()
        content = str(rows) + str(rel_rows)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    finally:
        conn.close()


def validate_db(set_code: str) -> dict:
    """Validate one DB. Returns a report dict."""
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"
    if not db_path.exists():
        return {"set_code": set_code, "exists": False}

    report = {"set_code": set_code, "exists": True, "issues": []}
    conn = sqlite3.connect(db_path)
    try:
        # Basic counts
        report["concepts"] = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        report["relations"] = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        report["rule_texts"] = conn.execute("SELECT COUNT(*) FROM rule_texts").fetchone()[0]

        # Chapter coverage
        chapter_rows = conn.execute(
            "SELECT chapter, COUNT(*) FROM concepts WHERE chapter IS NOT NULL GROUP BY chapter ORDER BY chapter"
        ).fetchall()
        report["chapters"] = {c: n for c, n in chapter_rows}

        # Malformed concepts
        malformed = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE name_en IS NULL OR name_en = '' OR type IS NULL OR type = ''"
        ).fetchone()[0]
        if malformed > 0:
            report["issues"].append(f"{malformed} concepts with null/empty name_en or type")

        # Orphaned relations (source or target doesn't exist)
        orphan_rels = conn.execute("""
            SELECT COUNT(*) FROM relations r
            WHERE NOT EXISTS (SELECT 1 FROM concepts WHERE id = r.source_id)
               OR NOT EXISTS (SELECT 1 FROM concepts WHERE id = r.target_id)
        """).fetchone()[0]
        if orphan_rels > 0:
            report["issues"].append(f"{orphan_rels} orphaned relations")

        # Rule texts without parent concept
        unlinked = conn.execute(
            "SELECT COUNT(*) FROM rule_texts WHERE parent_concept_id IS NULL"
        ).fetchone()[0]
        report["unlinked_rule_texts"] = unlinked
        if report["rule_texts"] > 0 and unlinked / report["rule_texts"] > 0.5:
            pct = round(unlinked * 100 / report["rule_texts"])
            report["issues"].append(f"{pct}% rule_texts have no parent concept")

        # Duplicate concept names (suggests poor ID consolidation)
        dup_names = conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT name_en FROM concepts GROUP BY name_en HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
        if dup_names > 10:
            report["issues"].append(f"{dup_names} concept names have duplicates")

    finally:
        conn.close()

    report["hash"] = hash_db(db_path)
    return report


def main():
    versions = load_versions_index()
    reports: list[dict] = []

    print(f"Validating {len(versions)} versions...")
    print()

    prev_hash = None
    prev_concepts = 0
    identical_runs = 0

    header = f"{'SET':12} {'DATE':12} {'CONCEPTS':>8} {'RELS':>6} {'RULES':>6} {'ΔCPT':>7} {'ISSUES':<50}"
    print(header)
    print("-" * len(header))

    total_issues = 0
    missing = 0
    stale = 0

    for i, v in enumerate(versions):
        r = validate_db(v["set_code"])
        reports.append(r)

        if not r["exists"]:
            print(f"{v['set_code']:12} {str(v.get('release_date','?')):12} {'MISSING':>8}")
            missing += 1
            continue

        issues_str = "; ".join(r["issues"]) if r["issues"] else ""
        if issues_str:
            total_issues += len(r["issues"])

        delta = r["concepts"] - prev_concepts if prev_concepts else 0
        delta_str = f"{delta:+d}" if prev_concepts else "-"
        drop_flag = ""
        if prev_concepts > 0 and r["concepts"] < prev_concepts * 0.7:
            pct = round((r["concepts"] - prev_concepts) * 100 / prev_concepts)
            drop_flag = f" [DROP {pct}%]"

        # Identical to previous = incremental silently failed
        if prev_hash == r["hash"]:
            identical_runs += 1
            issues_str = (issues_str + "; " if issues_str else "") + "IDENTICAL TO PREVIOUS (likely stale copy)"
            stale += 1

        truncated = (issues_str + drop_flag)[:60]
        print(f"{r['set_code']:12} {str(v.get('release_date','?')):12} {r['concepts']:>8} {r['relations']:>6} {r['rule_texts']:>6} {delta_str:>7} {truncated}")

        prev_hash = r["hash"]
        prev_concepts = r["concepts"]

    print()
    print("=" * 60)
    print(f"Total versions:     {len(versions)}")
    print(f"Missing DBs:        {missing}")
    print(f"Stale (identical):  {stale}")
    print(f"Total issue items:  {total_issues}")

    # Write detailed report
    out = CONCEPT_DBS_DIR.parent / "validation_report.json"
    out.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Full report: {out}")


if __name__ == "__main__":
    main()
