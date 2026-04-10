"""
Before/after comparison of relation quality, using the same (source, target) pairs.

Parses docs/validation_report.md (v1) to extract the 100 relations that were
validated against the original concepts.db. For each one:
  - looks up the current type in concepts_validated.db
  - if the type changed, re-validates against DeepSeek and records the new verdict
  - if the type is the same, the verdict is unchanged

Outputs a summary showing how many verdicts flipped and in which direction.
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Reuse helpers from validate.py
sys.path.insert(0, str(Path(__file__).parent))
from validate import (  # noqa: E402
    DeepSeekClient,
    load_rule_texts,
    lookup_rule_text,
    validate_relation,
    get_concept,
)

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "comp_rules_en.txt"
V1_REPORT = ROOT.parent / "docs" / "validation_report.md"
VALIDATED_DB = ROOT / "data" / "concepts.db"
OUT = ROOT.parent / "docs" / "relation_comparison.md"

# Match `src` --[type]--> `tgt` anywhere on a ### line (emoji prefix is
# multi-codepoint for ⚠️ so we don't match it explicitly).
RELATION_HEADER_RE = re.compile(r"^###.*?`([^`]+)`\s+--\[([^\]]+)\]-->\s+`([^`]+)`")


def parse_v1_relations(path: Path) -> list[dict]:
    """Parse v1 validation_report.md → list of dicts with v1 data."""
    in_relations = False
    entries: list[dict] = []
    current: dict | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## Relation validation"):
            in_relations = True
            continue
        if raw_line.startswith("## "):
            in_relations = False
            continue
        if not in_relations:
            continue

        m = RELATION_HEADER_RE.match(raw_line)
        if m:
            if current:
                entries.append(current)
            current = {
                "source_id": m.group(1),
                "type": m.group(2),
                "target_id": m.group(3),
                "rule_ref": None,
                "verdict": None,
                "issue": None,
            }
            continue

        if current is None:
            continue
        if raw_line.startswith("- rule_ref:"):
            rm = re.search(r"`([^`]+)`", raw_line)
            if rm:
                current["rule_ref"] = rm.group(1)
        elif raw_line.startswith("- verdict:"):
            vm = re.search(r"\*\*(\w+)\*\*", raw_line)
            if vm:
                current["verdict"] = vm.group(1)
        elif raw_line.startswith("- issue:"):
            current["issue"] = raw_line.split(":", 1)[1].strip()

    if current:
        entries.append(current)
    return entries


def find_current_relation(
    conn: sqlite3.Connection, source_id: str, target_id: str, old_type: str
) -> dict | None:
    """Find the relation in the validated DB. Handles normalized types."""
    # First try any relation between these two (may have changed type)
    rows = conn.execute(
        "SELECT source_id, target_id, type, rule_ref, description "
        "FROM relations WHERE source_id = ? AND target_id = ?",
        (source_id, target_id),
    ).fetchall()
    if not rows:
        return None
    cols = ["source_id", "target_id", "type", "rule_ref", "description"]
    # If multiple (unlikely after dedup), prefer the one whose type was normalized from old_type
    return dict(zip(cols, rows[0]))


def main() -> int:
    load_dotenv(ROOT.parent / ".env")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set", file=sys.stderr)
        return 1
    client = DeepSeekClient(api_key=api_key, base_url=base_url, model=model)

    print(f"Loading rule texts...")
    rule_texts = load_rule_texts(RAW)

    print(f"Parsing v1 report {V1_REPORT}...")
    v1 = parse_v1_relations(V1_REPORT)
    print(f"  parsed {len(v1)} v1 relations")

    conn = sqlite3.connect(VALIDATED_DB)

    unchanged_type = 0
    changed_type = 0
    dropped = 0
    revalidated: list[tuple[dict, dict, dict]] = []  # (v1, current, new_verdict)

    for v1_rel in v1:
        current = find_current_relation(
            conn, v1_rel["source_id"], v1_rel["target_id"], v1_rel["type"]
        )
        if current is None:
            dropped += 1
            continue
        if current["type"] == v1_rel["type"]:
            unchanged_type += 1
            continue
        changed_type += 1
        # Re-validate with new type
        src = get_concept(conn, current["source_id"])
        tgt = get_concept(conn, current["target_id"])
        try:
            result = validate_relation(client, current, src, tgt, rule_texts)
        except Exception as e:
            print(f"  ERROR on {v1_rel['source_id']}->{v1_rel['target_id']}: {e}")
            result = {"verdict": "error", "issue": str(e)}
        revalidated.append((v1_rel, current, result))
        flip_marker = "→" if result["verdict"] != v1_rel["verdict"] else "="
        print(
            f"  {v1_rel['source_id']} --[{v1_rel['type']}→{current['type']}]--> "
            f"{v1_rel['target_id']}: {v1_rel['verdict']} {flip_marker} {result['verdict']}"
        )
        time.sleep(0.3)

    conn.close()

    # Derive final v3 verdicts: unchanged = v1 verdict; changed = revalidated verdict
    v1_counts = {"correct": 0, "suspicious": 0, "wrong": 0, "error": 0}
    v3_counts = {"correct": 0, "suspicious": 0, "wrong": 0, "error": 0}
    flips = {"up": 0, "same": 0, "down": 0}  # up = correct-ward, down = wrong-ward
    rank = {"correct": 2, "suspicious": 1, "wrong": 0, "error": -1}

    # Process unchanged (verdict stayed)
    for v1_rel in v1:
        current = find_current_relation(
            conn := sqlite3.connect(VALIDATED_DB),
            v1_rel["source_id"],
            v1_rel["target_id"],
            v1_rel["type"],
        )
        conn.close()
        v1_verdict = v1_rel["verdict"] or "error"
        v1_counts[v1_verdict] = v1_counts.get(v1_verdict, 0) + 1

    for v1_rel, current, result in revalidated:
        new_v = result.get("verdict", "error")
        old_v = v1_rel.get("verdict", "error")
        v3_counts[new_v] = v3_counts.get(new_v, 0) + 1
        if rank.get(new_v, -1) > rank.get(old_v, -1):
            flips["up"] += 1
        elif rank.get(new_v, -1) < rank.get(old_v, -1):
            flips["down"] += 1
        else:
            flips["same"] += 1

    # Fill v3 counts: unchanged ones keep v1 verdict
    for v1_rel in v1:
        conn = sqlite3.connect(VALIDATED_DB)
        current = find_current_relation(
            conn, v1_rel["source_id"], v1_rel["target_id"], v1_rel["type"]
        )
        conn.close()
        if current is None or current["type"] != v1_rel["type"]:
            continue
        v = v1_rel["verdict"] or "error"
        v3_counts[v] = v3_counts.get(v, 0) + 1

    print("\n" + "=" * 60)
    print("SUMMARY (same 100 relations, before vs after normalization)")
    print("=" * 60)
    print(f"  unchanged type:      {unchanged_type}")
    print(f"  type changed:        {changed_type}  (revalidated)")
    print(f"  dropped (missing):   {dropped}  (self-loop or collapsed)")
    print()
    total_v1 = sum(v1_counts.values())
    total_v3 = sum(v3_counts.values())
    print(f"  v1 verdict counts:   {v1_counts}  (n={total_v1})")
    print(f"  v3 verdict counts:   {v3_counts}  (n={total_v3})")
    print()
    print(f"  Among type-changed ({changed_type}):")
    print(f"    flipped toward correct: {flips['up']}")
    print(f"    flipped toward wrong:   {flips['down']}")
    print(f"    unchanged verdict:      {flips['same']}")

    # Write markdown report
    lines = [
        "# Relation Normalization: Before / After",
        "",
        "Same 100 (source, target) pairs from v1 validation, compared against concepts_validated.db.",
        "",
        "## Summary",
        "",
        f"- Relations unchanged (type stayed same): **{unchanged_type}**",
        f"- Relations with type changed (re-validated): **{changed_type}**",
        f"- Relations dropped (self-loop / collapsed): **{dropped}**",
        "",
        f"| verdict | v1 | v3 (after normalize) |",
        f"|---|---|---|",
        f"| correct | {v1_counts['correct']} | {v3_counts['correct']} |",
        f"| suspicious | {v1_counts['suspicious']} | {v3_counts['suspicious']} |",
        f"| wrong | {v1_counts['wrong']} | {v3_counts['wrong']} |",
        "",
        f"**Among the {changed_type} type-changed relations:**",
        f"- {flips['up']} flipped toward correct (good)",
        f"- {flips['down']} flipped toward wrong (bad)",
        f"- {flips['same']} kept same verdict (neutral)",
        "",
        "## Details of type-changed relations",
        "",
    ]
    for v1_rel, current, result in revalidated:
        old_v = v1_rel.get("verdict", "?")
        new_v = result.get("verdict", "?")
        icon = {"correct": "✅", "suspicious": "⚠️", "wrong": "❌"}.get(new_v, "?")
        lines.append(
            f"### {icon} `{v1_rel['source_id']}` --> `{v1_rel['target_id']}`"
        )
        lines.append(f"- type: `{v1_rel['type']}` → `{current['type']}`")
        lines.append(f"- verdict: {old_v} → **{new_v}**")
        if result.get("issue"):
            lines.append(f"- issue: {result['issue']}")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
