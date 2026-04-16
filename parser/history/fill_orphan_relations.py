"""Use DeepSeek to generate relations for orphan concepts (those with 0 edges).

For each version's DB, find concepts with no relations, batch them,
and ask DeepSeek to infer which other concepts they relate to.
Only emits relations where the target concept exists in the same DB.
"""

import argparse
import json
import os
import re
import sqlite3
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .baseline_extract import CONCEPT_DBS_DIR
from .walk_versions import load_versions_index

load_dotenv(Path(__file__).parent.parent.parent / ".env")

SYSTEM_PROMPT = """You are a Magic: The Gathering rules expert. Given a list of orphan concepts
(concepts with no relations in the knowledge graph) and a list of available target
concepts, generate appropriate relations between them.

Each relation should be one of these types:
DEPENDS_ON, CONTAINS, MODIFIES, CREATES, OCCURS_IN, MOVES_TO, PATTERN_OF, INTERACTS_WITH, REFERENCES

Output ONLY a JSON array of relations:
[{"source_id": "...", "target_id": "...", "type": "...", "description": "short reason"}]

Rules:
- Only use concept IDs from the provided lists
- Each orphan should have 1-3 relations (most important ones)
- Prefer DEPENDS_ON and CONTAINS over REFERENCES
- Do NOT create self-loops
"""


def find_orphans(conn: sqlite3.Connection) -> list[dict]:
    """Find concepts with zero relations."""
    return [
        {"id": r[0], "name_en": r[1], "type": r[2], "rule_ref": r[3]}
        for r in conn.execute("""
            SELECT c.id, c.name_en, c.type, c.rule_ref FROM concepts c
            WHERE c.id NOT IN (SELECT source_id FROM relations)
              AND c.id NOT IN (SELECT target_id FROM relations)
        """).fetchall()
    ]


def get_target_concepts(conn: sqlite3.Connection) -> list[dict]:
    """Get all concepts with at least one relation (potential link targets)."""
    return [
        {"id": r[0], "name_en": r[1], "type": r[2]}
        for r in conn.execute("""
            SELECT DISTINCT c.id, c.name_en, c.type FROM concepts c
            WHERE c.id IN (SELECT source_id FROM relations)
               OR c.id IN (SELECT target_id FROM relations)
        """).fetchall()
    ]


def ask_deepseek(orphan_batch: list[dict], targets: list[dict]) -> list[dict]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        return []

    orphan_str = "\n".join(f"  {c['id']} ({c['type']}): {c['name_en']}" for c in orphan_batch)
    # Sample targets to keep prompt manageable
    target_str = "\n".join(f"  {c['id']} ({c['type']}): {c['name_en']}" for c in targets[:200])

    user_msg = f"""Orphan concepts (no relations yet):
{orphan_str}

Available target concepts (sample):
{target_str}

Generate relations for the orphan concepts. JSON array only, no markdown."""

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.0,
        "max_tokens": 4096,
    }

    for attempt in range(2):
        try:
            with httpx.Client(timeout=90.0) as client:
                r = client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                raw = r.json()["choices"][0]["message"]["content"]

            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start >= 0 and end > start:
                cleaned = cleaned[start : end + 1]
            cleaned = re.sub(r",(\s*[\]\}])", r"\1", cleaned)
            relations = json.loads(cleaned)
            if isinstance(relations, list):
                return relations
        except Exception as e:
            print(f"      attempt {attempt + 1}/2 failed: {e}")
            time.sleep(2)
    return []


def fill_orphans_for_version(set_code: str, dry_run: bool = False) -> dict:
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"
    if not db_path.exists():
        return {"set_code": set_code, "status": "missing"}

    conn = sqlite3.connect(db_path)
    try:
        orphans = find_orphans(conn)
        if not orphans:
            return {"set_code": set_code, "orphans": 0, "added": 0}

        targets = get_target_concepts(conn)
        all_ids = {r[0] for r in conn.execute("SELECT id FROM concepts").fetchall()}

        total_added = 0
        BATCH = 20
        for i in range(0, len(orphans), BATCH):
            batch = orphans[i : i + BATCH]
            relations = ask_deepseek(batch, targets)

            valid = [
                r for r in relations
                if isinstance(r, dict)
                and r.get("source_id") in all_ids
                and r.get("target_id") in all_ids
                and r.get("source_id") != r.get("target_id")
                and r.get("type")
            ]

            if valid and not dry_run:
                for r in valid:
                    r.setdefault("rule_ref", None)
                    r.setdefault("description", r.get("description", ""))
                try:
                    conn.executemany(
                        """INSERT OR IGNORE INTO relations (source_id, target_id, type, rule_ref, description)
                           VALUES (:source_id, :target_id, :type, :rule_ref, :description)""",
                        valid,
                    )
                    conn.commit()
                    total_added += len(valid)
                except Exception as e:
                    print(f"      insert error: {e}")

            time.sleep(0.5)

        remaining = len(find_orphans(conn))
        return {"set_code": set_code, "orphans": len(orphans), "added": total_added, "remaining": remaining}
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", type=str, default=None, help="Comma-separated set codes (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.versions:
        codes = [c.strip().upper() for c in args.versions.split(",")]
    else:
        versions = load_versions_index()
        codes = [v["set_code"] for v in versions]

    print(f"Filling orphan relations for {len(codes)} versions via DeepSeek")
    print(f"{'SET':8} {'ORPHANS':>8} {'ADDED':>7} {'REMAINING':>10}")
    print("-" * 40)

    total_added = 0
    for code in codes:
        r = fill_orphans_for_version(code, dry_run=args.dry_run)
        if r.get("status") == "missing":
            continue
        if r["orphans"] == 0:
            continue
        print(f"{code:8} {r['orphans']:>8} {r['added']:>7} {r.get('remaining', '?'):>10}")
        total_added += r["added"]

    print(f"\nTotal relations added: {total_added}")


if __name__ == "__main__":
    main()
