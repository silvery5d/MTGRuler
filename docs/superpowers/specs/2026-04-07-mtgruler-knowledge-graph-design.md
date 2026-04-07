# MTGRuler: Magic: The Gathering Comprehensive Rules Knowledge Graph

## Overview

An interactive web application that presents the complete Magic: The Gathering Comprehensive Rules as a navigable knowledge graph. Serves two audiences: players learning the rules, and game designers studying MTG's rule system for reference.

Bilingual (English + Chinese) with concept-based nodes and rich interactive features.

## Data Sources

- **English**: Official Comprehensive Rules text file from Wizards of the Coast (`MagicCompRules_YYYYMMDD.txt`)
- **Chinese**: Community translation at https://wiki.mtgjudge.cn/cr

## Architecture

```
┌───────────────┬──────────────┬───────────────────────────┐
│    Parser     │   Backend    │        Frontend           │
│   (Python)    │  (Express +  │  (React + Cytoscape.js)   │
│               │   SQLite)    │                           │
├───────────────┼──────────────┼───────────────────────────┤
│ 1. Fetch EN/CN│ REST API:    │ - Graph visualization     │
│ 2. Regex split│ /concepts    │ - Search & filter          │
│ 3. LLM extract│ /relations  │ - Detail panel (bilingual) │
│ 4. Write DB   │ /search     │ - Expand/collapse layers   │
│               │ /path       │ - Path query               │
│               │ /graph      │ - Designer views           │
└───────────────┴──────────────┴───────────────────────────┘
```

Data flow:
```
EN Rules Text ──┐
                ├→ Regex preprocessing (split by chapter/entry)
CN Translation ─┘         │
                          ↓
                 LLM Concept Extraction (Claude API)
                 - Core concepts + definitions
                 - Inter-concept relationships
                 - Category and hierarchy tagging
                          │
                          ↓
                 Structured data → SQLite (concepts.db)
                          │
                          ↓
                   Express API → React + Cytoscape.js
```

## Concept Model

### Node Types

| Type | Description | Examples |
|------|-------------|----------|
| Chapter | Top-level rule chapters | 1. Game Concepts, 5. Turn Structure, 7. Additional Rules |
| Concept | Core game concepts | Stack, Priority, State-Based Actions, Battlefield |
| Zone | Game zones | Battlefield, Graveyard, Hand, Library, Exile, Stack |
| CardType | Card types | Creature, Instant, Sorcery, Enchantment, Artifact, Planeswalker, Land |
| Phase/Step | Turn phases/steps | Beginning Phase, Combat Phase, Main Phase, Upkeep Step |
| Keyword | Keyword abilities | Flying, Trample, Flash, Deathtouch, Double Strike, Ward |
| Action | Game actions | Cast, Resolve, Declare Attackers, Pay Costs |
| MechanicPattern | Design patterns (designer view) | Replacement Effects, Triggered Abilities, ETB Effects |

### Relation Types

| Relation | Meaning | Example |
|----------|---------|---------|
| CONTAINS | Contains / belongs to | Chapter → Concept |
| DEPENDS_ON | Understanding A requires B | "Stack" → "Priority" |
| REFERENCES | A's rule text references B | "Flying" → "Combat Damage" |
| OCCURS_IN | Action occurs in phase/zone | "Declare Attackers" → "Combat Phase" |
| MODIFIES | Keyword modifies behavior | "Trample" → "Combat Damage Assignment" |
| INTERACTS_WITH | Two mechanics interact | "Flying" ↔ "Reach" |
| MOVES_TO | Card/object moves between zones | "Destroy" → Battlefield to Graveyard |
| PATTERN_OF | Instance of design pattern | "Enter-the-Battlefield ability" ← "ETB Effects" |

### Node Schema

```json
{
  "id": "keyword.flying",
  "name_en": "Flying",
  "name_cn": "飞行",
  "type": "Keyword",
  "rule_ref": "702.9",
  "definition_en": "This creature can't be blocked except by...",
  "definition_cn": "此生物不能被不具飞行或延势的生物阻挡...",
  "chapter": "7",
  "complexity": 2,
  "design_notes": "Core evasion mechanic, present in almost every set"
}
```

## Database Schema (SQLite)

```sql
CREATE TABLE concepts (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    type TEXT NOT NULL,
    rule_ref TEXT,
    definition_en TEXT,
    definition_cn TEXT,
    chapter TEXT,
    complexity INTEGER,
    design_notes TEXT
);

CREATE TABLE relations (
    source_id TEXT,
    target_id TEXT,
    type TEXT NOT NULL,
    rule_ref TEXT,
    description TEXT,
    PRIMARY KEY (source_id, target_id, type),
    FOREIGN KEY (source_id) REFERENCES concepts(id),
    FOREIGN KEY (target_id) REFERENCES concepts(id)
);

CREATE TABLE rule_texts (
    rule_ref TEXT PRIMARY KEY,
    text_en TEXT,
    text_cn TEXT,
    parent_concept_id TEXT,
    FOREIGN KEY (parent_concept_id) REFERENCES concepts(id)
);
```

## Backend API

```
Base URL: /api/v1

GET  /concepts                    List concepts
     ?type=Keyword                Filter by type
     ?chapter=7                   Filter by chapter
     ?limit=50&offset=0           Pagination

GET  /concepts/:id                Single concept with rule texts and related concepts

GET  /concepts/:id/neighbors      Direct neighbors
     ?depth=2                     Relationship depth

GET  /relations                   List relations
     ?type=DEPENDS_ON             Filter by relation type
     ?source=keyword.flying       Filter by source

GET  /search                      Full-text search (FTS5)
     ?q=飞行                       Chinese/English keywords
     ?type=Keyword                Scope filter

GET  /path                        Shortest path query
     ?from=keyword.flying
     &to=action.combat_damage

GET  /graph                       Cytoscape-compatible graph data
     ?chapter=5                   Subgraph by chapter
     ?center=concept.stack&depth=3  Ego-centric subgraph

GET  /stats                       Statistics (type counts, chapter distribution, complexity)
```

Response format for `/graph`:
```json
{
  "nodes": [
    { "id": "keyword.flying", "name_cn": "飞行", "name_en": "Flying",
      "type": "Keyword", "complexity": 2 }
  ],
  "edges": [
    { "source": "keyword.flying", "target": "keyword.reach",
      "type": "INTERACTS_WITH" }
  ]
}
```

Key implementation details:
- `/graph` returns Cytoscape.js-compatible format, zero transformation on frontend
- `/path` uses BFS in SQLite, computed server-side
- `/search` uses SQLite FTS5 for bilingual full-text search

## Frontend

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Search bar       [Chapter ▾] [Type ▾]    [View ▾]  │
├────────────────────────────────┬────────────────────┤
│                                │  Detail Panel      │
│   Cytoscape.js Graph Area      │  - Bilingual defs  │
│                                │  - Related concepts │
│   (zoom, pan, drag, click)     │  - Rule references  │
│                                │  - Design notes     │
├────────────────────────────────┴────────────────────┤
│  Status bar: Showing 42 / 387 concepts │ Path mode  │
└─────────────────────────────────────────────────────┘
```

### Interactive Features

1. **Search & Filter**: Keyword search (bilingual fuzzy match), filter by chapter/type, highlight results in graph
2. **Expand/Collapse**: Default shows Chapter nodes, click to expand children, double-click to collapse, "expand to level N"
3. **Path Query**: Enter path mode, select start/end nodes, highlight shortest path with explanation
4. **Detail Panel**: Click node to open right sidebar with bilingual rule text, related concepts (clickable), rule references
5. **Designer Views** (via view switcher):
   - Dependency Graph: center on a mechanic, show all dependencies
   - Complexity Heatmap: color nodes by complexity (green→yellow→red)
   - Chapter Overview: tree map with concept counts per chapter
   - Interaction Matrix: keyword interaction network (Flying↔Reach, First Strike↔Double Strike)

## Project Structure

```
MTGRuler/
├── parser/                     # Python data pipeline
│   ├── requirements.txt
│   ├── fetch_rules.py          # Fetch EN rules + scrape CN translation
│   ├── preprocess.py           # Regex split, EN/CN alignment
│   ├── extract.py              # LLM concept extraction (Claude API)
│   ├── build_db.py             # Validate, dedupe, write SQLite
│   ├── cache/                  # LLM output cache
│   └── data/
│       ├── raw/                # Raw rule texts
│       ├── processed/          # Structured intermediates
│       └── concepts.db         # Final SQLite database
│
├── server/                     # Node.js backend
│   ├── package.json
│   ├── src/
│   │   ├── index.ts            # Express entry
│   │   ├── routes/
│   │   │   ├── concepts.ts
│   │   │   ├── relations.ts
│   │   │   ├── search.ts
│   │   │   ├── path.ts
│   │   │   └── graph.ts
│   │   ├── db.ts               # SQLite connection (better-sqlite3)
│   │   └── utils/
│   │       └── pathfinder.ts   # BFS / shortest path
│   └── tsconfig.json
│
├── client/                     # React frontend
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── GraphView.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── DetailPanel.tsx
│   │   │   ├── PathQuery.tsx
│   │   │   ├── DesignerView/
│   │   │   │   ├── DependencyGraph.tsx
│   │   │   │   ├── HeatMap.tsx
│   │   │   │   ├── ChapterOverview.tsx
│   │   │   │   └── InteractionMatrix.tsx
│   │   │   └── ViewSwitcher.tsx
│   │   ├── hooks/
│   │   │   ├── useGraph.ts
│   │   │   └── useSearch.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs/
├── LICENSE (MIT)
└── README.md
```

## Deployment

| Component | Platform | Notes |
|-----------|----------|-------|
| Parser | Local | Run once or on rule updates, produces `concepts.db` |
| Server | Railway / Render | Free tier sufficient, SQLite file deployed with code |
| Client | Vercel / Cloudflare Pages | Static frontend, auto CI/CD |

## Development Order

1. `parser/` first → produces `concepts.db`
2. `server/` second → reads db, exposes API
3. `client/` third → calls API, builds interactions

## Open Source

- License: MIT
- Repository: GitHub (public)
- Contributions: frontend and backend can be developed independently
