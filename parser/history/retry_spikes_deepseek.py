"""Retry failed spike analyses using DeepSeek instead of Anthropic."""

import json
import os
import re
import sqlite3
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .detect_spikes import (
    SPIKES_FILE, _summarize_added_concepts, _summarize_rule_diff,
)

load_dotenv(Path(__file__).parent.parent.parent / ".env")


def analyze_with_deepseek(spike: dict) -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        return {"primary_culprits": [], "secondary_factors": [], "summary": "(no DEEPSEEK_API_KEY)"}

    added_concepts = _summarize_added_concepts(spike["prev_set_code"], spike["set_code"])
    rule_diff = _summarize_rule_diff(spike["prev_set_code"], spike["set_code"])

    deltas_str = "\n".join(
        f"- {path}: +{round(d['pct'] * 100, 1)}% (abs change: {d['abs']})"
        for path, d in spike["deltas"].items()
    )
    added_str = "\n".join(
        f"  - {c['id']} ({c['type']}): {c['name_en']}"
        for c in added_concepts[:12]
    ) or "  (none)"

    prompt = f"""Analyze this MTG Comprehensive Rules complexity spike between {spike['prev_set_code']} and {spike['set_code']} ({spike.get('set_name', '?')}).

Metrics that spiked:
{deltas_str}

New concepts added:
{added_str}

Key rule changes (top 15):
{rule_diff}

Which mechanic(s) or rule change(s) caused the complexity increase?

Respond with ONLY valid JSON:
{{"primary_culprits": [{{"name": "...", "type": "Keyword|Mechanic|RuleSystem", "explanation": "...", "affected_concepts": [], "estimated_contribution_pct": 0}}], "secondary_factors": [], "summary": "one sentence"}}"""

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 2048,
    }

    for attempt in range(3):
        try:
            with httpx.Client(timeout=60.0) as client:
                r = client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                raw = r.json()["choices"][0]["message"]["content"]

            if not raw.strip():
                print(f"    empty response attempt {attempt + 1}/3")
                time.sleep(2)
                continue

            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                cleaned = cleaned[start : end + 1]
            # Fix trailing commas
            cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"    attempt {attempt + 1}/3 failed: {type(e).__name__}: {str(e)[:100]}")
            time.sleep(2)

    return {"primary_culprits": [], "secondary_factors": [], "summary": "(DeepSeek analysis failed)"}


def main():
    spikes = json.loads(SPIKES_FILE.read_text(encoding="utf-8"))
    failed = [
        (i, s) for i, s in enumerate(spikes)
        if "failed" in s.get("analysis", {}).get("summary", "")
        or "_raw_response" in s.get("analysis", {})
    ]
    print(f"Retrying {len(failed)}/{len(spikes)} failed spike analyses with DeepSeek...")

    success = 0
    for idx, (i, s) in enumerate(failed):
        print(f"  [{idx + 1}/{len(failed)}] {s['set_code']}...")
        result = analyze_with_deepseek(s)
        if "failed" not in result.get("summary", "") and result.get("primary_culprits"):
            spikes[i]["analysis"] = result
            success += 1
            print(f"    OK: {result['summary'][:80]}")
        else:
            print(f"    Still failed")
        time.sleep(0.5)

    SPIKES_FILE.write_text(json.dumps(spikes, indent=2, ensure_ascii=False), encoding="utf-8")
    total_good = sum(1 for s in spikes if "failed" not in s.get("analysis", {}).get("summary", ""))
    print(f"\nDone. {total_good}/{len(spikes)} spikes now have valid analysis (+{success} new)")


if __name__ == "__main__":
    main()
