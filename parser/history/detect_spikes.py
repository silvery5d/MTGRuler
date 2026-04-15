"""Detect complexity spikes between adjacent versions and ask the LLM
to identify the culprit mechanics."""

import json
import os
import re
import sqlite3
from pathlib import Path
from statistics import mean, median, stdev

import anthropic
from dotenv import load_dotenv

from .fetch import DATA_DIR, fetch_diff
from .baseline_extract import CONCEPT_DBS_DIR

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
SPIKES_FILE = DATA_DIR / "spikes.json"
Z_THRESHOLD = 2.0

METRIC_PATHS = [
    "scale.rule_count",
    "graph.concept_count",
    "graph.relation_count",
    "cognitive.uc_total",
    "mechanic.keyword_count",
]


def _get_nested(d: dict, path: str) -> float:
    parts = path.split(".")
    val = d
    for p in parts:
        if not isinstance(val, dict):
            return 0.0
        val = val.get(p, 0)
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def find_spikes(metrics: list[dict]) -> list[dict]:
    """Find versions where any metric grew more than Z_THRESHOLD sigmas above mean."""
    if len(metrics) < 3:
        return []

    spikes_by_version: dict[str, dict] = {}

    for metric_path in METRIC_PATHS:
        values = [_get_nested(m, metric_path) for m in metrics]
        deltas = []
        for i in range(1, len(values)):
            prev = values[i - 1]
            if prev > 0:
                deltas.append((values[i] - prev) / prev)
            else:
                deltas.append(0.0)

        if len(deltas) < 2:
            continue
        # Use median + MAD (median absolute deviation) for robust outlier
        # detection — a single large spike won't inflate its own threshold.
        med = median(deltas)
        mad = median([abs(d - med) for d in deltas]) or 1e-9
        # 1.4826 * MAD approximates stdev for normal distributions
        robust_sigma = 1.4826 * mad
        threshold = med + Z_THRESHOLD * robust_sigma

        for i, delta in enumerate(deltas):
            if delta > threshold and delta > 0.05:
                version = metrics[i + 1]
                key = version["set_code"]
                if key not in spikes_by_version:
                    spikes_by_version[key] = {
                        "set_code": key,
                        "set_name": version["set_name"],
                        "release_date": version.get("release_date"),
                        "prev_set_code": metrics[i]["set_code"],
                        "spiked_metrics": [],
                        "deltas": {},
                    }
                spikes_by_version[key]["spiked_metrics"].append(metric_path)
                spikes_by_version[key]["deltas"][metric_path] = {
                    "pct": round(delta, 4),
                    "abs": values[i + 1] - values[i],
                }

    return list(spikes_by_version.values())


def _summarize_added_concepts(prev_set: str, curr_set: str, max_items: int = 15) -> list[dict]:
    prev_db = CONCEPT_DBS_DIR / f"{prev_set}.db"
    curr_db = CONCEPT_DBS_DIR / f"{curr_set}.db"
    if not prev_db.exists() or not curr_db.exists():
        return []

    prev_conn = sqlite3.connect(prev_db)
    curr_conn = sqlite3.connect(curr_db)
    try:
        prev_ids = {r[0] for r in prev_conn.execute("SELECT id FROM concepts").fetchall()}
        added_rows = curr_conn.execute(
            "SELECT id, name_en, type, complexity, definition_en FROM concepts"
        ).fetchall()
        added = [
            {"id": r[0], "name_en": r[1], "type": r[2], "complexity": r[3], "definition_en": r[4]}
            for r in added_rows if r[0] not in prev_ids
        ]
        return added[:max_items]
    finally:
        prev_conn.close()
        curr_conn.close()


def _summarize_rule_diff(prev_set: str, curr_set: str, max_items: int = 15) -> str:
    try:
        diff = fetch_diff(prev_set, curr_set)
    except Exception:
        return "(diff unavailable)"
    lines = []
    for change in diff.get("changes", [])[:max_items]:
        old = change.get("old")
        new = change.get("new")
        if old is None and new:
            lines.append(f"  + {new['ruleNumber']}: {new['ruleText'][:120]}")
        elif new is None and old:
            lines.append(f"  - {old['ruleNumber']}: {old['ruleText'][:120]}")
        elif old and new:
            lines.append(f"  ~ {new['ruleNumber']}: (modified)")
    return "\n".join(lines)


def analyze_spike(spike: dict, model: str | None = None) -> dict:
    model = model or DEFAULT_MODEL
    client = anthropic.Anthropic()

    added_concepts = _summarize_added_concepts(spike["prev_set_code"], spike["set_code"])
    rule_diff = _summarize_rule_diff(spike["prev_set_code"], spike["set_code"])

    deltas_str = "\n".join(
        f"- {path}: +{round(d['pct'] * 100, 1)}% (abs change: {d['abs']})"
        for path, d in spike["deltas"].items()
    )

    added_str = "\n".join(
        f"  - {c['id']} ({c['type']}, complexity {c['complexity']}): {c['name_en']}"
        for c in added_concepts
    ) or "  (none)"

    user_prompt = f"""You are analyzing a complexity spike in MTG Comprehensive Rules between
{spike['prev_set_code']} and {spike['set_code']} ({spike.get('set_name', '?')}, released {spike.get('release_date', '?')}).

Metrics that spiked above 2 standard deviations:
{deltas_str}

Concepts and keywords newly added in this version:
{added_str}

Rules added or significantly modified (from Academy Ruins diff, top 30):
{rule_diff}

Question: Which specific mechanic(s), keyword(s), or rule subsystem(s) introduced
in this version are the primary causes of the complexity increase? Focus on
mechanics that introduce new game-state interactions, recursive effects, or
system-wide ripples.

Respond ONLY with valid JSON, no markdown fences:
{{
  "primary_culprits": [
    {{
      "name": "<mechanic/keyword name>",
      "type": "Keyword|Mechanic|RuleSystem",
      "explanation": "<why this caused complexity to jump>",
      "affected_concepts": [<concept ids>],
      "estimated_contribution_pct": <0-100>
    }}
  ],
  "secondary_factors": [],
  "summary": "<one sentence>"
}}"""

    import time
    raw = ""
    for attempt in range(3):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = next((b.text for b in message.content if getattr(b, "type", None) == "text"), "")
            if raw.strip():
                break
            print(f"    WARN: empty response for {spike['set_code']} attempt {attempt + 1}/3, retrying...")
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            print(f"    WARN: LLM error for {spike['set_code']} ({type(e).__name__}), retry {attempt + 1}/3")
            time.sleep(2 * (attempt + 1))

    # Strip markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    # Extract just the outermost JSON object (LLMs sometimes add prose before/after)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Retry with trailing commas stripped
        try:
            retry = re.sub(r",(\s*[}\]])", r"\1", cleaned)
            return json.loads(retry)
        except json.JSONDecodeError:
            pass
        print(f"    WARN: JSON parse failed for {spike['set_code']} ({e}). Raw response first 300 chars: {raw[:300]!r}")
        return {
            "primary_culprits": [],
            "secondary_factors": [],
            "summary": "(analysis failed to parse)",
            "_raw_response": raw[:2000],
        }


def detect_and_analyze(metrics: list[dict], force: bool = False) -> list[dict]:
    if SPIKES_FILE.exists() and not force:
        return json.loads(SPIKES_FILE.read_text(encoding="utf-8"))

    spikes = find_spikes(metrics)
    print(f"  Found {len(spikes)} version-level spikes")

    for spike in spikes:
        print(f"  Analyzing {spike['set_code']}: {', '.join(spike['spiked_metrics'])}")
        spike["analysis"] = analyze_spike(spike)
        spike["delta_summary"] = ", ".join(
            f"+{round(d['pct'] * 100)}% {p.split('.')[-1]}"
            for p, d in spike["deltas"].items()
        )

    SPIKES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SPIKES_FILE.write_text(json.dumps(spikes, ensure_ascii=False, indent=2), encoding="utf-8")
    return spikes
