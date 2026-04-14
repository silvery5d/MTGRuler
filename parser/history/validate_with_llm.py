"""Cross-LLM validation of history DBs using DeepSeek (different LLM than extraction).

For each version's DB:
- Sample N concepts (those with rule_ref) and N relations
- Look up source rule text from the version's cached CR text
- Ask DeepSeek whether the extraction is correct/suspicious/wrong
- Aggregate results into a per-version accuracy score

Output: parser/data/history/llm_validation_report.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .walk_versions import load_versions_index
from .baseline_extract import CONCEPT_DBS_DIR
from .fetch import VERSIONS_DIR

load_dotenv(Path(__file__).parent.parent.parent / ".env")

REPORT_PATH = CONCEPT_DBS_DIR.parent / "llm_validation_report.json"

RULE_LINE_RE = re.compile(r"^(\d{3}(?:\.\d+[a-z]?)?)\.?\s+(.*)$")


def load_rule_texts(set_code: str) -> dict[str, str]:
    """Load and parse the cached CR text for a version."""
    path = VERSIONS_DIR / f"{set_code.upper()}.txt"
    if not path.exists():
        return {}
    rules: dict[str, str] = {}
    current_ref: str | None = None
    current_buf: list[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = RULE_LINE_RE.match(line)
            if m:
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

    def chat(self, system: str, user: str, max_tokens: int = 500) -> str:
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
        with httpx.Client(timeout=60.0) as c:
            r = c.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]


CONCEPT_SYSTEM = """You are a Magic: The Gathering rules expert validating an automated extraction.

You'll be given an extracted CONCEPT and the SOURCE RULE TEXT it was derived from.

Respond with ONLY a JSON object, no markdown, no prose:
{"verdict": "correct" | "suspicious" | "wrong", "issue": "<short description or null>"}

Guidelines:
- "correct": name, type, and definition all match source text accurately
- "suspicious": minor issues (slightly off definition, borderline type)
- "wrong": name doesn't exist in source, type is clearly wrong, or definition contradicts source
"""


def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in response: {text[:200]}")
    return json.loads(text[start : end + 1])


def lookup_rule_text(ref: str, rule_texts: dict[str, str]) -> str:
    if not ref or ref not in rule_texts:
        # Try stripping subrule letter
        if ref:
            base = ref.rstrip("abcdefghijklmnopqrstuvwxyz")
            if base in rule_texts:
                return rule_texts[base]
        return "<not found>"
    return rule_texts[ref]


def sample_concepts(db_path: Path, n: int, rng: random.Random) -> list[dict]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, name_en, type, rule_ref, definition_en FROM concepts WHERE rule_ref IS NOT NULL"
        ).fetchall()
    finally:
        conn.close()
    items = [
        {"id": r[0], "name_en": r[1], "type": r[2], "rule_ref": r[3], "definition_en": r[4]}
        for r in rows
    ]
    rng.shuffle(items)
    return items[:n]


def validate_version(
    client: DeepSeekClient,
    set_code: str,
    sample_size: int,
    rng: random.Random,
) -> dict:
    """Sample N concepts from a version's DB and validate them against source CR."""
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"
    if not db_path.exists():
        return {"set_code": set_code, "status": "missing"}

    rule_texts = load_rule_texts(set_code)
    if not rule_texts:
        return {"set_code": set_code, "status": "no_rule_texts"}

    samples = sample_concepts(db_path, sample_size, rng)
    if not samples:
        return {"set_code": set_code, "status": "empty", "sampled": 0}

    results = {"correct": 0, "suspicious": 0, "wrong": 0, "error": 0}
    details: list[dict] = []
    for c in samples:
        ref = c["rule_ref"]
        source = lookup_rule_text(ref, rule_texts)
        user = (
            f"CONCEPT:\n"
            f"  id: {c['id']}\n"
            f"  name_en: {c['name_en']}\n"
            f"  type: {c['type']}\n"
            f"  rule_ref: {ref}\n"
            f"  definition_en: {c.get('definition_en') or '<none>'}\n\n"
            f"SOURCE RULE TEXT ({ref}):\n{source}\n"
        )
        try:
            resp = client.chat(CONCEPT_SYSTEM, user)
            verdict = parse_json_response(resp)
            v = verdict.get("verdict", "error")
            if v not in results:
                v = "error"
            results[v] += 1
            if v in ("suspicious", "wrong"):
                details.append({
                    "id": c["id"],
                    "rule_ref": ref,
                    "verdict": v,
                    "issue": verdict.get("issue"),
                })
        except Exception as e:
            results["error"] += 1
            details.append({"id": c["id"], "error": str(e)[:200]})
        time.sleep(0.3)  # rate limit gentleness

    total = len(samples)
    accuracy = results["correct"] / total if total else 0.0

    return {
        "set_code": set_code,
        "status": "validated",
        "sampled": total,
        "accuracy": round(accuracy, 3),
        "breakdown": results,
        "issues": details[:15],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=20, help="Concepts per version (default 20)")
    ap.add_argument("--versions", type=str, default=None, help="Comma-separated set codes (default all)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set in .env", flush=True)
        return 1
    client = DeepSeekClient(api_key=api_key, base_url=base_url, model=model)

    # Version selection
    if args.versions:
        target_codes = [c.strip().upper() for c in args.versions.split(",")]
    else:
        versions = load_versions_index()
        target_codes = [v["set_code"] for v in versions]

    rng = random.Random(args.seed)
    reports: list[dict] = []

    print(f"Validating {len(target_codes)} versions with {model} (sample={args.sample} per version)\n")
    print(f"{'SET':8} {'STATUS':12} {'ACC':>6} {'CORRECT':>7} {'SUSPECT':>7} {'WRONG':>5} {'ERR':>4}")
    print("-" * 60)

    for code in target_codes:
        r = validate_version(client, code, args.sample, rng)
        reports.append(r)
        if r["status"] == "validated":
            b = r["breakdown"]
            print(f"{code:8} {'OK':12} {r['accuracy']:>6.1%} {b['correct']:>7} {b['suspicious']:>7} {b['wrong']:>5} {b['error']:>4}")
        else:
            print(f"{code:8} {r['status']:12}")

    REPORT_PATH.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport saved: {REPORT_PATH}")

    # Aggregate
    validated = [r for r in reports if r.get("status") == "validated"]
    if validated:
        avg_acc = sum(r["accuracy"] for r in validated) / len(validated)
        total_sampled = sum(r["sampled"] for r in validated)
        total_correct = sum(r["breakdown"]["correct"] for r in validated)
        total_wrong = sum(r["breakdown"]["wrong"] for r in validated)
        print(f"\nOverall: {total_correct}/{total_sampled} correct ({avg_acc:.1%} avg), {total_wrong} wrong")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
