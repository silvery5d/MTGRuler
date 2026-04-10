"""
Side-by-side validation of two databases using DeepSeek.

Takes --db-before and --db-after, samples the same set of ids/pairs, validates
each in both DBs, and reports how verdicts shifted. Avoids parsing markdown
reports — a single run gives the full before/after picture.

Usage:
    python compare_dbs.py --db-before data/concepts_raw.db --db-after data/concepts.db --sample 50
    python compare_dbs.py --sample 100 --seed 42
"""
from __future__ import annotations

import argparse
import os
import random
import sqlite3
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from validate import (  # noqa: E402
    DeepSeekClient,
    load_rule_texts,
    validate_concept,
    validate_relation,
    get_concept,
)

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "comp_rules_en.txt"
DEFAULT_BEFORE = ROOT / "data" / "concepts_raw.db"
DEFAULT_AFTER = ROOT / "data" / "concepts.db"
DEFAULT_OUTPUT = ROOT.parent / "docs" / "db_comparison.md"

RANK = {"correct": 2, "suspicious": 1, "wrong": 0, "error": -1, "missing": -2}


def fetch_concept(conn: sqlite3.Connection, cid: str) -> dict | None:
    row = conn.execute(
        "SELECT id, name_en, name_cn, type, rule_ref, definition_en, definition_cn "
        "FROM concepts WHERE id = ?",
        (cid,),
    ).fetchone()
    if row is None:
        return None
    cols = ["id", "name_en", "name_cn", "type", "rule_ref", "definition_en", "definition_cn"]
    return dict(zip(cols, row))


def fetch_relation(conn: sqlite3.Connection, src: str, tgt: str) -> dict | None:
    """Find a relation by (src, tgt). Also tries reversed direction since some
    normalizations intentionally flip direction (e.g. ATTRIBUTE_OF → CONTAINS).
    """
    cols = ["source_id", "target_id", "type", "rule_ref", "description"]
    row = conn.execute(
        "SELECT source_id, target_id, type, rule_ref, description "
        "FROM relations WHERE source_id = ? AND target_id = ?",
        (src, tgt),
    ).fetchone()
    if row is not None:
        return dict(zip(cols, row))
    # Try reversed direction
    row = conn.execute(
        "SELECT source_id, target_id, type, rule_ref, description "
        "FROM relations WHERE source_id = ? AND target_id = ?",
        (tgt, src),
    ).fetchone()
    if row is not None:
        d = dict(zip(cols, row))
        d["_direction_reversed"] = True
        return d
    return None


def sample_concept_ids(conn: sqlite3.Connection, n: int, rng: random.Random) -> list[str]:
    rows = conn.execute(
        "SELECT id FROM concepts WHERE rule_ref IS NOT NULL ORDER BY id"
    ).fetchall()
    ids = [r[0] for r in rows]
    rng.shuffle(ids)
    return ids[:n]


def sample_relation_pairs(
    conn: sqlite3.Connection, n: int, rng: random.Random
) -> list[tuple[str, str]]:
    rows = conn.execute(
        "SELECT source_id, target_id FROM relations "
        "WHERE rule_ref IS NOT NULL ORDER BY source_id, target_id"
    ).fetchall()
    pairs = [(r[0], r[1]) for r in rows]
    rng.shuffle(pairs)
    return pairs[:n]


def verdict_from(result: dict | None) -> str:
    if result is None:
        return "missing"
    return result.get("verdict", "error")


def compare_run(
    client: DeepSeekClient,
    rule_texts: dict,
    conn_before: sqlite3.Connection,
    conn_after: sqlite3.Connection,
    sample: int,
    rng: random.Random,
) -> dict:
    # Concepts: sample from BEFORE (the superset), then look up AFTER
    concept_ids = sample_concept_ids(conn_before, sample, rng)
    print(f"Sampling {len(concept_ids)} concepts...")
    concept_results: list[dict] = []
    for i, cid in enumerate(concept_ids, 1):
        entry = {"id": cid, "before_verdict": None, "after_verdict": None, "changed": False}
        c_before = fetch_concept(conn_before, cid)
        c_after = fetch_concept(conn_after, cid)
        try:
            r_before = validate_concept(client, c_before, rule_texts) if c_before else None
            entry["before_verdict"] = verdict_from(r_before)
            time.sleep(0.2)
            if c_after is None:
                entry["after_verdict"] = "missing"
            elif (
                c_before is None
                or c_before["type"] == c_after["type"]
                and c_before["rule_ref"] == c_after["rule_ref"]
                and c_before["definition_en"] == c_after["definition_en"]
            ):
                # Unchanged: reuse before verdict
                entry["after_verdict"] = entry["before_verdict"]
            else:
                entry["changed"] = True
                r_after = validate_concept(client, c_after, rule_texts)
                entry["after_verdict"] = verdict_from(r_after)
                time.sleep(0.2)
        except Exception as e:
            entry["error"] = str(e)
            entry["before_verdict"] = entry["before_verdict"] or "error"
            entry["after_verdict"] = entry["after_verdict"] or "error"
        concept_results.append(entry)
        marker = "*" if entry["changed"] else " "
        print(
            f"  [{i}/{len(concept_ids)}]{marker} {cid}: "
            f"{entry['before_verdict']} → {entry['after_verdict']}"
        )

    # Relations
    relation_pairs = sample_relation_pairs(conn_before, sample, rng)
    print(f"\nSampling {len(relation_pairs)} relations...")
    relation_results: list[dict] = []
    for i, (src, tgt) in enumerate(relation_pairs, 1):
        entry = {
            "source_id": src,
            "target_id": tgt,
            "before_verdict": None,
            "after_verdict": None,
            "changed": False,
        }
        r_before = fetch_relation(conn_before, src, tgt)
        r_after = fetch_relation(conn_after, src, tgt)
        try:
            if r_before:
                s = get_concept(conn_before, src)
                t = get_concept(conn_before, tgt)
                v_before = validate_relation(client, r_before, s, t, rule_texts)
                entry["before_verdict"] = verdict_from(v_before)
                time.sleep(0.2)
            else:
                entry["before_verdict"] = "missing"

            if r_after is None:
                entry["after_verdict"] = "missing"
            elif r_before is not None and r_before["type"] == r_after["type"]:
                entry["after_verdict"] = entry["before_verdict"]
            else:
                entry["changed"] = True
                s = get_concept(conn_after, src)
                t = get_concept(conn_after, tgt)
                v_after = validate_relation(client, r_after, s, t, rule_texts)
                entry["after_verdict"] = verdict_from(v_after)
                time.sleep(0.2)
        except Exception as e:
            entry["error"] = str(e)
            entry["before_verdict"] = entry["before_verdict"] or "error"
            entry["after_verdict"] = entry["after_verdict"] or "error"
        relation_results.append(entry)
        marker = "*" if entry["changed"] else " "
        print(
            f"  [{i}/{len(relation_pairs)}]{marker} {src}->{tgt}: "
            f"{entry['before_verdict']} → {entry['after_verdict']}"
        )

    return {"concepts": concept_results, "relations": relation_results}


def summarize(results: list[dict]) -> dict:
    before = {"correct": 0, "suspicious": 0, "wrong": 0, "error": 0, "missing": 0}
    after = {"correct": 0, "suspicious": 0, "wrong": 0, "error": 0, "missing": 0}
    flips_up = 0
    flips_down = 0
    for r in results:
        b = r["before_verdict"] or "error"
        a = r["after_verdict"] or "error"
        before[b] = before.get(b, 0) + 1
        after[a] = after.get(a, 0) + 1
        if RANK.get(a, -1) > RANK.get(b, -1):
            flips_up += 1
        elif RANK.get(a, -1) < RANK.get(b, -1):
            flips_down += 1
    return {"before": before, "after": after, "flips_up": flips_up, "flips_down": flips_down}


def write_report(path: Path, data: dict, meta: dict) -> None:
    c_sum = summarize(data["concepts"])
    r_sum = summarize(data["relations"])

    def fmt_row(label: str, counts: dict) -> str:
        n = sum(counts.values()) or 1
        return (
            f"| {label} | {counts.get('correct', 0)} ({counts.get('correct', 0)/n:.0%}) "
            f"| {counts.get('suspicious', 0)} | {counts.get('wrong', 0)} "
            f"| {counts.get('missing', 0)} |"
        )

    lines = [
        "# Database Comparison: Before vs After",
        "",
        f"- Before DB: `{meta['db_before']}`",
        f"- After DB:  `{meta['db_after']}`",
        f"- Model: `{meta['model']}`",
        f"- Sample: {meta['sample']} concepts, {meta['sample']} relations",
        f"- Seed: {meta['seed']}",
        f"- Generated: {meta['timestamp']}",
        "",
        "## Concepts",
        "",
        "| | correct | suspicious | wrong | missing |",
        "|---|---|---|---|---|",
        fmt_row("before", c_sum["before"]),
        fmt_row("after ", c_sum["after"]),
        "",
        f"- Flipped toward correct: **{c_sum['flips_up']}**",
        f"- Flipped toward wrong:   {c_sum['flips_down']}",
        f"- Changes in DB triggered re-validation: "
        f"{sum(1 for r in data['concepts'] if r['changed'])}",
        "",
        "## Relations",
        "",
        "| | correct | suspicious | wrong | missing |",
        "|---|---|---|---|---|",
        fmt_row("before", r_sum["before"]),
        fmt_row("after ", r_sum["after"]),
        "",
        f"- Flipped toward correct: **{r_sum['flips_up']}**",
        f"- Flipped toward wrong:   {r_sum['flips_down']}",
        f"- Changes in DB triggered re-validation: "
        f"{sum(1 for r in data['relations'] if r['changed'])}",
        "",
    ]

    # Per-item flip details (only items that changed or moved)
    def flip_section(title: str, items: list[dict], key_fmt) -> list[str]:
        out = [f"## {title} — flipped items", ""]
        for r in items:
            b = r["before_verdict"] or "?"
            a = r["after_verdict"] or "?"
            if b == a:
                continue
            direction = "↑" if RANK.get(a, -1) > RANK.get(b, -1) else "↓"
            out.append(f"- {direction} `{key_fmt(r)}`: {b} → **{a}**")
        out.append("")
        return out

    lines.extend(flip_section("Concepts", data["concepts"], lambda r: r["id"]))
    lines.extend(
        flip_section(
            "Relations", data["relations"], lambda r: f"{r['source_id']} → {r['target_id']}"
        )
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-before", type=Path, default=DEFAULT_BEFORE)
    ap.add_argument("--db-after", type=Path, default=DEFAULT_AFTER)
    ap.add_argument("--sample", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    load_dotenv(ROOT.parent / ".env")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set", file=sys.stderr)
        return 1

    client = DeepSeekClient(api_key=api_key, base_url=base_url, model=model)
    print(f"Loading rule texts from {RAW}...")
    rule_texts = load_rule_texts(RAW)

    conn_before = sqlite3.connect(args.db_before)
    conn_after = sqlite3.connect(args.db_after)
    rng = random.Random(args.seed)
    try:
        data = compare_run(
            client, rule_texts, conn_before, conn_after, args.sample, rng
        )
    finally:
        conn_before.close()
        conn_after.close()

    write_report(
        args.output,
        data,
        meta={
            "db_before": args.db_before,
            "db_after": args.db_after,
            "model": model,
            "sample": args.sample,
            "seed": args.seed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    print(f"\nReport written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
