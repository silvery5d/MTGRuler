"""
LLM cross-validation of extracted concepts/relations using DeepSeek.

Samples concepts and relations from concepts.db, looks up the source rule text
in the raw comp_rules_en.txt, and asks DeepSeek whether the extraction is
correct/suspicious/wrong. Outputs a markdown report.

Usage:
    python validate.py --sample 5          # smoke test with 5 of each
    python validate.py --sample 100        # full run
    python validate.py --sample 100 --seed 42
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).parent
RAW_RULES = ROOT / "data" / "raw" / "comp_rules_en.txt"
DB_PATH = ROOT / "data" / "concepts.db"
REPORT_PATH = ROOT.parent / "docs" / "validation_report.md"

# Rule line patterns:
#   "100. General"             → chapter header, key "100"
#   "100.1. ..." / "100.1 ..." → section, key "100.1"
#   "100.1a ..."               → subrule, key "100.1a"
RULE_LINE_RE = re.compile(r"^(\d{3}(?:\.\d+[a-z]?)?)\.?\s+(.*)$")


def load_rule_texts(path: Path) -> dict[str, str]:
    """Parse raw rules file into {rule_ref: text} dict.

    Each rule_ref maps to the full paragraph (a rule may span multiple lines
    in the raw file, though usually one). Continuation lines (not starting
    with a rule number) are appended to the previous rule.
    """
    rules: dict[str, str] = {}
    current_ref: Optional[str] = None
    current_buf: list[str] = []

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = RULE_LINE_RE.match(line)
            if m:
                # flush previous
                if current_ref:
                    rules[current_ref] = " ".join(current_buf).strip()
                current_ref = m.group(1)
                current_buf = [m.group(2)]
            elif current_ref and line.strip():
                current_buf.append(line.strip())
        if current_ref:
            rules[current_ref] = " ".join(current_buf).strip()
    return rules


@dataclass
class DeepSeekClient:
    api_key: str
    base_url: str
    model: str

    def chat(self, system: str, user: str, max_tokens: int = 600) -> str:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "max_tokens": max_tokens,
        }
        with httpx.Client(timeout=60.0) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]


CONCEPT_SYSTEM = """You are a Magic: The Gathering rules expert validating an automated extraction.

You will be given:
1. An extracted CONCEPT (id, name, type, definition) that was derived from the comprehensive rules.
2. The SOURCE RULE TEXT from the official MTG comprehensive rules (referenced by rule_ref).

Valid concept types are: Chapter, Concept, Zone, CardType, Phase, Step, Keyword, Action, MechanicPattern, Variant, Symbol, Object.

Judge whether the concept is an accurate extraction from the source rule text.
Respond with ONLY a single JSON object, no markdown, no prose:
{
  "verdict": "correct" | "suspicious" | "wrong",
  "issue": "<short description, or null if correct>",
  "suggested_fix": "<short suggestion, or null>"
}

Guidelines:
- "correct": name, type, and definition all match the source text accurately.
- "suspicious": minor issues (e.g. slightly off definition, borderline type).
- "wrong": name doesn't exist in source, type is clearly wrong (e.g. a multiplayer variant labelled as Keyword), or definition contradicts source.
"""

RELATION_SYSTEM = """You are a Magic: The Gathering rules expert validating an automated extraction.

You will be given:
1. An extracted RELATION between two concepts (source -> type -> target).
2. The SOURCE RULE TEXT from the official rules that supposedly justifies this relation.

Valid relation types are the 8 canonical types: CONTAINS, DEPENDS_ON, REFERENCES, OCCURS_IN, MODIFIES, INTERACTS_WITH, MOVES_TO, PATTERN_OF. The extractor sometimes invented other types — if you see one of those, mark it suspicious and suggest the closest canonical type.

Respond with ONLY a single JSON object:
{
  "verdict": "correct" | "suspicious" | "wrong",
  "issue": "<short description, or null>",
  "suggested_type": "<one of the 8 canonical types, or null if verdict is correct>"
}

Guidelines:
- "correct": the rule text clearly supports this source->target relation and the type is one of the 8 canonical and fits.
- "suspicious": type is non-canonical but the underlying relation is real; or canonical type but not the best fit.
- "wrong": the rule text doesn't support this relation at all, or source/target are backwards.
"""


def parse_json_response(text: str) -> dict:
    """Extract a JSON object from LLM response (strips markdown fences if present)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    # find first { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in response: {text[:200]}")
    return json.loads(text[start : end + 1])


def _collect_subrules(
    section: str, rule_texts: dict[str, str], cap: int = 12
) -> list[str]:
    """Return list of 'ref: text' lines for all subrules under a section.

    E.g. section='701.22' collects '701.22a', '701.22b', etc.
    """
    out: list[str] = []
    # match refs that START with the section followed by a letter
    for k, v in sorted(rule_texts.items()):
        if k == section:
            continue
        if k.startswith(section) and len(k) > len(section):
            # must be a subrule (next char is a letter) not a sibling section
            # (e.g. section '701.2' should not pull in '701.20')
            next_char = k[len(section)]
            if next_char.isalpha():
                out.append(f"{k}: {v}")
                if len(out) >= cap:
                    break
    return out


def lookup_rule_text(ref: str, rule_texts: dict[str, str]) -> str:
    """Look up rule text for a concept/relation rule_ref.

    Handles three cases:
    1. Exact match: return the paragraph.
    2. Section header (e.g. '701.22'): also include its subrules ('701.22a'...)
       because the header line alone is often just the name.
    3. Range ref like '205.2-205.2c': expand the starting point + subrules.
    """
    if not ref:
        return "<no rule_ref>"

    # Range form
    if "-" in ref:
        start = ref.split("-", 1)[0].strip()
        if start in rule_texts:
            chunks = [f"{start}: {rule_texts[start]}"]
            chunks.extend(_collect_subrules(start, rule_texts))
            return "\n".join(chunks)
        return "<not found in raw rules>"

    if ref in rule_texts:
        header = rule_texts[ref]
        # If this is a section header (short text, likely just the name),
        # pull in subrules for full context.
        subrules = _collect_subrules(ref, rule_texts)
        if subrules:
            return f"{ref}: {header}\n" + "\n".join(subrules)
        return header

    return "<not found in raw rules>"


def validate_concept(client: DeepSeekClient, concept: dict, rule_texts: dict[str, str]) -> dict:
    ref = concept["rule_ref"]
    source_text = lookup_rule_text(ref, rule_texts)
    user_msg = (
        f"CONCEPT:\n"
        f"  id: {concept['id']}\n"
        f"  name_en: {concept['name_en']}\n"
        f"  type: {concept['type']}\n"
        f"  rule_ref: {ref}\n"
        f"  definition_en: {concept.get('definition_en') or '<none>'}\n\n"
        f"SOURCE RULE TEXT ({ref}):\n{source_text}\n"
    )
    resp = client.chat(CONCEPT_SYSTEM, user_msg)
    return parse_json_response(resp)


def validate_relation(
    client: DeepSeekClient,
    relation: dict,
    source_concept: dict,
    target_concept: dict,
    rule_texts: dict[str, str],
) -> dict:
    ref = relation["rule_ref"]
    source_text = lookup_rule_text(ref, rule_texts) if ref else "<no rule_ref provided>"
    user_msg = (
        f"RELATION:\n"
        f"  source: {source_concept['id']} ({source_concept['name_en']}, type={source_concept['type']})\n"
        f"  target: {target_concept['id']} ({target_concept['name_en']}, type={target_concept['type']})\n"
        f"  type: {relation['type']}\n"
        f"  rule_ref: {ref}\n"
        f"  description: {relation.get('description') or '<none>'}\n\n"
        f"SOURCE RULE TEXT ({ref}):\n{source_text}\n"
    )
    resp = client.chat(RELATION_SYSTEM, user_msg)
    return parse_json_response(resp)


def sample_concepts(conn: sqlite3.Connection, n: int, rng: random.Random) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name_en, name_cn, type, rule_ref, definition_en, definition_cn "
        "FROM concepts WHERE rule_ref IS NOT NULL"
    ).fetchall()
    cols = ["id", "name_en", "name_cn", "type", "rule_ref", "definition_en", "definition_cn"]
    all_items = [dict(zip(cols, r)) for r in rows]
    rng.shuffle(all_items)
    return all_items[:n]


def sample_relations(conn: sqlite3.Connection, n: int, rng: random.Random) -> list[dict]:
    rows = conn.execute(
        "SELECT source_id, target_id, type, rule_ref, description "
        "FROM relations WHERE rule_ref IS NOT NULL"
    ).fetchall()
    cols = ["source_id", "target_id", "type", "rule_ref", "description"]
    all_items = [dict(zip(cols, r)) for r in rows]
    rng.shuffle(all_items)
    return all_items[:n]


def get_concept(conn: sqlite3.Connection, concept_id: str) -> dict:
    row = conn.execute(
        "SELECT id, name_en, type FROM concepts WHERE id = ?", (concept_id,)
    ).fetchone()
    if not row:
        return {"id": concept_id, "name_en": "<missing>", "type": "<missing>"}
    return {"id": row[0], "name_en": row[1], "type": row[2]}


def write_report(
    path: Path,
    concept_results: list[tuple[dict, dict]],
    relation_results: list[tuple[dict, dict]],
    meta: dict,
) -> None:
    lines: list[str] = []
    lines.append("# MTGRuler Extraction Validation Report")
    lines.append("")
    lines.append(f"- Model: `{meta['model']}`")
    lines.append(f"- Sample size: {meta['sample']} concepts, {meta['sample']} relations")
    lines.append(f"- Seed: {meta['seed']}")
    lines.append(f"- Generated: {meta['timestamp']}")
    lines.append("")

    # Concept summary
    c_verdicts = [r["verdict"] for _, r in concept_results]
    r_verdicts = [r["verdict"] for _, r in relation_results]

    def summary(verdicts: list[str]) -> str:
        total = len(verdicts)
        if total == 0:
            return "no samples"
        c = sum(1 for v in verdicts if v == "correct")
        s = sum(1 for v in verdicts if v == "suspicious")
        w = sum(1 for v in verdicts if v == "wrong")
        return f"correct={c}/{total} ({c/total:.0%}), suspicious={s}, wrong={w}"

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Concepts**: {summary(c_verdicts)}")
    lines.append(f"- **Relations**: {summary(r_verdicts)}")
    lines.append("")

    # Concepts section
    lines.append("## Concept validation")
    lines.append("")
    for concept, result in concept_results:
        verdict = result.get("verdict", "?")
        icon = {"correct": "✅", "suspicious": "⚠️", "wrong": "❌"}.get(verdict, "?")
        lines.append(f"### {icon} `{concept['id']}` — {concept['name_en']} ({concept['type']})")
        lines.append(f"- rule_ref: `{concept['rule_ref']}`")
        lines.append(f"- verdict: **{verdict}**")
        if result.get("issue"):
            lines.append(f"- issue: {result['issue']}")
        if result.get("suggested_fix"):
            lines.append(f"- suggested fix: {result['suggested_fix']}")
        lines.append("")

    # Relations section
    lines.append("## Relation validation")
    lines.append("")
    for relation, result in relation_results:
        verdict = result.get("verdict", "?")
        icon = {"correct": "✅", "suspicious": "⚠️", "wrong": "❌"}.get(verdict, "?")
        lines.append(
            f"### {icon} `{relation['source_id']}` --[{relation['type']}]--> `{relation['target_id']}`"
        )
        lines.append(f"- rule_ref: `{relation['rule_ref']}`")
        lines.append(f"- verdict: **{verdict}**")
        if result.get("issue"):
            lines.append(f"- issue: {result['issue']}")
        if result.get("suggested_type"):
            lines.append(f"- suggested type: `{result['suggested_type']}`")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=5, help="Sample size for each table")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    parser.add_argument("--db", type=Path, default=DB_PATH, help="Path to SQLite DB")
    parser.add_argument("--skip-concepts", action="store_true")
    parser.add_argument("--skip-relations", action="store_true")
    parser.add_argument(
        "--ids",
        type=str,
        help="Comma-separated concept ids to validate (bypasses sampling)",
    )
    args = parser.parse_args()

    load_dotenv(ROOT.parent / ".env")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set in .env", file=sys.stderr)
        return 1

    client = DeepSeekClient(api_key=api_key, base_url=base_url, model=model)

    print(f"Loading rule texts from {RAW_RULES}...")
    rule_texts = load_rule_texts(RAW_RULES)
    print(f"  loaded {len(rule_texts)} rule paragraphs")

    conn = sqlite3.connect(args.db)
    print(f"Using DB: {args.db}")
    rng = random.Random(args.seed)

    concept_results: list[tuple[dict, dict]] = []
    if args.ids:
        ids = [s.strip() for s in args.ids.split(",") if s.strip()]
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"SELECT id, name_en, name_cn, type, rule_ref, definition_en, definition_cn "
            f"FROM concepts WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        cols = ["id", "name_en", "name_cn", "type", "rule_ref", "definition_en", "definition_cn"]
        concepts = [dict(zip(cols, r)) for r in rows]
        args.skip_relations = True  # when --ids given, only validate concepts
        print(f"Validating {len(concepts)} specified concepts...")
        for i, c in enumerate(concepts, 1):
            try:
                result = validate_concept(client, c, rule_texts)
                concept_results.append((c, result))
                print(f"  [{i}/{len(concepts)}] {c['id']}: {result.get('verdict')}")
            except Exception as e:
                print(f"  [{i}/{len(concepts)}] {c['id']}: ERROR {e}")
                concept_results.append((c, {"verdict": "error", "issue": str(e)}))
            time.sleep(0.3)
    elif not args.skip_concepts:
        concepts = sample_concepts(conn, args.sample, rng)
        print(f"Validating {len(concepts)} concepts...")
        for i, c in enumerate(concepts, 1):
            try:
                result = validate_concept(client, c, rule_texts)
                concept_results.append((c, result))
                print(f"  [{i}/{len(concepts)}] {c['id']}: {result.get('verdict')}")
            except Exception as e:
                print(f"  [{i}/{len(concepts)}] {c['id']}: ERROR {e}")
                concept_results.append((c, {"verdict": "error", "issue": str(e)}))
            time.sleep(0.3)

    relation_results: list[tuple[dict, dict]] = []
    if not args.skip_relations:
        relations = sample_relations(conn, args.sample, rng)
        print(f"Validating {len(relations)} relations...")
        for i, r in enumerate(relations, 1):
            try:
                src = get_concept(conn, r["source_id"])
                tgt = get_concept(conn, r["target_id"])
                result = validate_relation(client, r, src, tgt, rule_texts)
                relation_results.append((r, result))
                print(f"  [{i}/{len(relations)}] {r['source_id']}->{r['target_id']}: {result.get('verdict')}")
            except Exception as e:
                print(f"  [{i}/{len(relations)}] {r['source_id']}->{r['target_id']}: ERROR {e}")
                relation_results.append((r, {"verdict": "error", "issue": str(e)}))
            time.sleep(0.3)

    conn.close()

    write_report(
        args.output,
        concept_results,
        relation_results,
        meta={
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
