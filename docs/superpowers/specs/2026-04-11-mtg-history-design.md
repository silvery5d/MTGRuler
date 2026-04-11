# MTG History — Complexity Evolution Analysis Design Spec

**Date**: 2026-04-11
**Status**: Approved
**Project**: New `parser/history/` subpackage inside MTGRuler, plus new server route and client view.

## Goal

Build a system that ingests every historical version of Magic: The Gathering Comprehensive Rules, computes multi-dimensional complexity metrics across versions, automatically detects complexity spikes, and uses LLM analysis to identify which mechanics or rule changes caused those spikes. Surface the results in an interactive visualization integrated into the existing MTGRuler app.

## Data Source

**Academy Ruins API** (`https://api.academyruins.com`)
- Open-source community archive of all historical CR versions (verified working through 2026-02 → back to at least 2001 Odyssey)
- `GET /file/cr/{set_code}` — raw CR text by set code (UTF-8 TXT for most versions, PDF for some pre-2003 versions)
- `GET /diff/cr?old=X&new=Y` — pre-computed structured diff between adjacent versions, includes per-rule additions, deletions, modifications, and rule moves
- `GET /diff/cr?nav=true` — returns the latest diff with `nav.prevSourceCode` pointer; walking the linked list backward enumerates all available versions
- No authentication, no rate limits beyond reasonable courtesy
- Backed by Backblaze B2 mirror, so reliability is high

This source eliminates two huge problems: scraping/format normalization (Academy Ruins already serves clean TXT) and diff computation (already done structurally, including rule renumbering detection).

## Architecture: Incremental Extraction Pipeline

```
Academy Ruins API
        │
   ┌────▼────┐
   │ 1. Fetch │  Walk version chain backward from latest, download all
   │          │  CR TXTs and pre-computed diffs to local cache
   └────┬────┘
        ▼
   ┌────▼────┐
   │ 2. Parse │  Split each version's TXT into chapters/rules using
   │          │  existing MTGRuler parsing logic (chapter_pattern,
   │          │  rule_pattern apply to all CR versions identically)
   └────┬────┘
        ▼
   ┌────▼────────────────────────┐
   │ 3. Baseline Extract          │  Pick earliest version (e.g. ODY 2001),
   │                              │  run full LLM extraction → ODY.db
   └────┬─────────────────────────┘
        ▼
   ┌────▼────────────────────────┐
   │ 4. Incremental Extract       │  For each subsequent version:
   │                              │    a. Copy prev_set.db → curr_set.db
   │                              │    b. Read Academy Ruins diff
   │                              │    c. Identify affected rule_refs
   │                              │    d. Find affected concepts
   │                              │    e. Re-run LLM extraction ONLY for
   │                              │       chapters containing affected refs
   │                              │    f. Merge new concepts/relations,
   │                              │       drop orphans, update definitions
   │                              │    g. Replace rule_texts table with
   │                              │       NEW version's full text
   │                              │    h. Re-normalize relations
   └────┬─────────────────────────┘
        ▼
   ┌────▼────────────────────────┐
   │ 5. Compute Metrics           │  For each {set_code}.db, compute
   │                              │  multi-dimensional complexity metrics
   │                              │  → metrics.json (time series)
   └────┬─────────────────────────┘
        ▼
   ┌────▼────────────────────────┐
   │ 6. Detect Spikes             │  Find statistical outliers in growth
   │                              │  rate (z-score > 2) per metric, then
   │                              │  LLM-analyze each spike to identify
   │                              │  culprit mechanics → spikes.json
   └────┬─────────────────────────┘
        ▼
   metrics.json + spikes.json + per-version dbs
        │
   Express API (/api/v1/history/*) → React HistoryView
```

## Project Structure

```
MTGRuler/
├── parser/
│   ├── (existing files: extract.py, build_db.py, normalize_relations.py, ...)
│   ├── history/                       # NEW subpackage
│   │   ├── __init__.py
│   │   ├── fetch.py                  # Academy Ruins API client
│   │   ├── walk_versions.py          # Enumerate set codes via nav linked list
│   │   ├── parse_version.py          # Reuse existing parser on a single version's TXT
│   │   ├── incremental_extract.py    # Core incremental extraction algorithm
│   │   ├── metrics.py                # Multi-dimensional complexity computation
│   │   ├── detect_spikes.py          # Statistical outlier detection + LLM analysis
│   │   ├── build_timeline_db.py      # (optional) Aggregate timeline DB
│   │   └── run_history_pipeline.py   # CLI orchestrator
│   └── data/
│       ├── concepts.db               # (existing) Latest curated single-version DB
│       ├── concepts_raw.db           # (existing)
│       └── history/                  # NEW
│           ├── versions/             # Cached raw TXT per set_code
│           ├── diffs/                # Cached Academy Ruins diff JSON
│           ├── concept_dbs/          # Per-version SQLite DBs
│           ├── metrics.json          # Multi-dimensional time series
│           └── spikes.json           # Detected spikes + LLM analysis
├── server/
│   └── src/routes/history.ts         # NEW route module
└── client/
    └── src/components/HistoryView/   # NEW view module
        ├── HistoryView.tsx           # Container with sub-view switcher
        ├── ComplexityChart.tsx       # Default sub-view: line chart
        ├── TimelineSlider.tsx        # Sub-view: slider + single graph
        ├── DiffCompare.tsx           # Sub-view: side-by-side comparison
        └── useHistory.ts             # Shared state hook
```

## Incremental Extraction Algorithm

The core innovation. Avoids running full LLM extraction on every version (~80 versions × 9 chapters = 720 calls) by exploiting the fact that consecutive CR versions only differ in a small fraction of rules.

```python
def incremental_extract(prev_set: str, curr_set: str, profile: dict) -> None:
    # 1. Copy previous version DB as starting point
    copy_db(history_dir / "concept_dbs" / f"{prev_set}.db",
            history_dir / "concept_dbs" / f"{curr_set}.db")
    db = open_db(curr_set)

    # 2. Load pre-computed Academy Ruins diff
    diff = load_diff(prev_set, curr_set)

    # 3. Collect all affected rule_refs (added, removed, modified, moved)
    affected_refs = set()
    for change in diff["changes"]:
        if change["old"]: affected_refs.add(change["old"]["ruleNumber"])
        if change["new"]: affected_refs.add(change["new"]["ruleNumber"])
    for move in diff.get("moves", []):
        affected_refs.add(move["fromRule"])
        affected_refs.add(move["toRule"])

    # 4. Find concepts whose rule_ref points into affected refs
    affected_concept_ids = db.query("""
        SELECT DISTINCT id FROM concepts WHERE rule_ref IN (?, ?, ...)
    """, list(affected_refs))

    # 5. Determine which chapters need re-extraction
    affected_chapters = set()
    for ref in affected_refs:
        chapter = derive_chapter(ref)  # e.g. "702.9a" → "7"
        affected_chapters.add(chapter)

    # 6. For each affected chapter, run LLM extraction with NEW version's text
    new_rule_texts = load_curr_version_rule_texts(curr_set)
    for chapter in affected_chapters:
        chapter_entries = [r for r in new_rule_texts if r["chapter"] == chapter]
        new_concepts, new_relations = extract_chapter(
            chapter_entries, chapter, profile,
            cache_key=f"history_{curr_set}_ch{chapter}"
        )
        merge_into_db(db, new_concepts, new_relations, chapter)

    # 7. Drop orphan concepts (those that pointed to removed rule_refs and
    #    weren't replaced by extraction)
    drop_orphan_concepts(db)

    # 8. Replace rule_texts table entirely with NEW version's full text
    replace_rule_texts(db, new_rule_texts)

    # 9. Re-normalize relations (canonicalize types, drop self-loops)
    normalize_db(curr_set)
```

### Merge Strategy Details

- **Added rules**: New concepts from LLM extraction inserted via `INSERT OR REPLACE`
- **Removed rules**: If a concept's `rule_ref` no longer exists in the new version AND no new extraction produced a concept with the same id, drop it. If the concept is referenced by other concepts (via relations), keep it and mark `rule_ref = null` rather than orphaning relations
- **Modified rules**: New concepts overwrite old ones with same id; relations are recomputed for affected chapters
- **Concept identity**: Anchored to `id` (`type.snake_name`). LLM is instructed via system prompt to use the same id for the same concept across versions. Fallback identity matching by `name_en` if id drift occurs

### Cache Reuse

- Reuse MTGRuler's existing `chapter_<chapter>_<content_hash>.json` cache files
- Cache key includes content hash, so identical chapters across versions hit the cache
- Estimated saving: ~40-50% of LLM calls hit cache

### Validation Checkpoints

- Every 10 versions, run a full extraction as a validation checkpoint
- Compare incremental result vs. full extraction; alert on significant divergence
- Provides escape hatch when incremental drifts

## Multi-Dimensional Complexity Metrics

`metrics.py` computes a `MetricsRecord` per version. The output `metrics.json` is an ordered array.

```python
{
    "set_code": "ODY",
    "set_name": "Odyssey",
    "release_date": "2001-09-24",

    "scale": {
        "rule_count": 723,
        "rule_total_words": 89_421,
        "rule_avg_length": 123.7,
        "chapter_count": 9,
        "max_rule_depth": 4,
    },

    "graph": {
        "concept_count": 612,
        "concept_count_by_type": {"Keyword": 87, "Concept": 245, ...},
        "relation_count": 891,
        "relation_count_by_type": {"DEPENDS_ON": 142, ...},
        "isolated_concepts": 18,
        "highly_connected_count": 31,  # degree > 10
    },

    "cognitive": {
        "uc_total": 4231,            # sum of understanding_complexity across all concepts
        "uc_max": 89,
        "uc_avg": 6.9,
        "uc_p50": 4, "uc_p90": 18, "uc_p99": 64,
        "uc_top10_concepts": [
            {"id": "concept.layered_effects", "uc": 89, "name_en": "Layered Effects"},
            ...
        ],
        "depends_on_chain_max": 6,
    },

    "mechanic": {
        "keyword_count": 87,
        "keywords_added_since_prev": ["keyword.threshold", "keyword.flashback"],
        "keywords_removed_since_prev": [],
        "card_type_count": 14,
        "evergreen_keyword_count": 11,
        "high_complexity_keywords": 22,  # complexity >= 4
    }
}
```

Computed purely from the per-version DBs — no LLM calls needed for metrics.

## Spike Detection

`detect_spikes.py` finds version-to-version growth-rate outliers per metric, groups them by version, and asks an LLM to identify culprits.

### Detection Algorithm

For each metric path (e.g., `cognitive.uc_total`, `scale.rule_count`):
1. Compute relative growth rates between adjacent versions
2. Compute mean and standard deviation across the full series
3. Mark a version as a spike if `delta > mean + 2σ`
4. Group spikes by version (a single version may spike in multiple metrics)

### LLM Analysis Prompt

For each grouped spike, send this prompt to Claude:

```
You are analyzing a complexity spike in MTG Comprehensive Rules between
{prev_set} ({prev_release_date}) and {curr_set} ({curr_release_date}).

Metrics that spiked above 2 standard deviations:
- {metric_path_1}: +{delta_1_pct}% (absolute change: {abs_change_1})
- {metric_path_2}: +{delta_2_pct}% (absolute change: {abs_change_2})

Concepts and keywords newly added in this version:
{added_concepts_summary}

Rules added or significantly modified (from Academy Ruins diff):
{rule_diff_summary}  // truncated to top 30 changes by rule_text length

Question: Which specific mechanic(s), keyword(s), or rule subsystem(s) introduced
in this version are the primary causes of the complexity increase? Focus on
mechanics that introduce new game-state interactions, recursive effects, or
system-wide ripples.

Respond in JSON:
{
  "primary_culprits": [
    {
      "name": "<mechanic/keyword name>",
      "type": "Keyword|Mechanic|RuleSystem",
      "explanation": "<why this caused complexity to jump>",
      "affected_concepts": [<concept ids>],
      "estimated_contribution_pct": <0-100>
    }
  ],
  "secondary_factors": [...],
  "summary": "<one sentence>"
}
```

### Output `spikes.json`

```json
[
  {
    "set_code": "SCG",
    "set_name": "Scourge",
    "release_date": "2003-05-26",
    "prev_set_code": "LGN",
    "spiked_metrics": ["cognitive.uc_total", "graph.relation_count"],
    "delta_summary": "+18% UC, +12% relations",
    "analysis": {
      "primary_culprits": [
        {
          "name": "Storm",
          "type": "Keyword",
          "explanation": "Storm creates copies of spells based on spell count this turn, creating recursive interactions with the stack and copy-effect rules subsystems.",
          "affected_concepts": ["keyword.storm", "concept.copy_spell", "concept.stack"],
          "estimated_contribution_pct": 65
        }
      ],
      "secondary_factors": [{"name": "Cycling cost reductions", ...}],
      "summary": "Storm keyword introduction caused major complexity spike via stack interactions"
    }
  }
]
```

## Server API

New module `server/src/routes/history.ts` mounted at `/api/v1/history/*`:

| Endpoint | Returns |
|----------|---------|
| `GET /api/v1/history/versions` | All versions: `[{ set_code, set_name, release_date, prev, next }]` |
| `GET /api/v1/history/metrics` | Full time series (`metrics.json`) |
| `GET /api/v1/history/spikes` | Spike list with LLM analysis (`spikes.json`) |
| `GET /api/v1/history/:set_code/concepts` | All concepts in that version |
| `GET /api/v1/history/:set_code/graph` | Cytoscape graph data for that version |
| `GET /api/v1/history/:set_code/concepts/:id` | Concept detail in that version |
| `GET /api/v1/history/diff?old=X&new=Y` | Structured concept-level diff between two versions |
| `GET /api/v1/history/concept-trace/:id` | Single concept's trajectory across all versions |

### Implementation Notes

- On startup, scan `parser/data/history/concept_dbs/*.db` and open each as a read-only better-sqlite3 connection
- Reuse `understanding-complexity.ts` for per-version UC computation (or precompute and serialize)
- Load `metrics.json` and `spikes.json` once into memory at startup

## Client View

New `HistoryView/` module added to existing client. Integrated as the 6th view in `ViewSwitcher`.

### HistoryView container

Internal sub-view switcher with three modes:

#### Sub-view 1: ComplexityChart (default)

Multi-line chart of metrics over time. X-axis: release date. Y-axis: metric value. Toggleable lines for each metric. Spikes from `spikes.json` rendered as ⚠️ markers; hover shows analysis summary; click jumps to DiffCompare for that version pair.

Implementation: Recharts (lightweight, well-maintained, fits React 19). Cytoscape.js is for graphs, not time series.

#### Sub-view 2: TimelineSlider

Horizontal slider spanning all versions. Drag to select a single version. Below the slider, render that version's full concept graph using existing `GraphView` component. Reuses all existing graph interaction patterns.

#### Sub-view 3: DiffCompare

Side-by-side: two `GraphView` panels showing two versions. Color coding:
- Common concepts: gray
- Removed (only in left): red
- Added (only in right): green
- Modified: yellow

Below: lists of added/removed/modified concepts with their UC values, sortable.

### State Management

```typescript
// client/src/components/HistoryView/useHistory.ts
export function useHistory() {
  const [versions, setVersions] = useState<VersionInfo[]>([]);
  const [metrics, setMetrics] = useState<MetricsTimeline | null>(null);
  const [spikes, setSpikes] = useState<Spike[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  const [compareVersion, setCompareVersion] = useState<string | null>(null);
  const [subView, setSubView] = useState<"chart" | "slider" | "diff">("chart");
  // API methods: loadVersions, loadMetrics, loadSpikes, loadVersionGraph, loadDiff
}
```

### Integration with Existing Views

- HistoryView appears as the 6th option in the existing ViewSwitcher
- Existing 5 views continue to operate on `parser/data/concepts.db` (the latest curated version)
- HistoryView is the only view that touches `parser/data/history/`
- Selecting a version in HistoryView and clicking "Open in Graph View" can pivot to the regular GraphView with version context (future enhancement, not blocking)

## Non-goals

- No real-time pipeline updates (each new CR release triggers a manual pipeline run)
- No card-level data (only Comprehensive Rules text)
- No tournament rules / IPG / MTR analysis (CR only — though Academy Ruins API supports them)
- No diff visualization at the rule-text level (the diff view operates on concepts, not raw rules)
