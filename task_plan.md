# Task Plan: MTGRuler Knowledge Graph

## Goal
Build an interactive web application presenting the complete MTG Comprehensive Rules as a bilingual (EN/CN) navigable knowledge graph for players and game designers.

## Current Phase
Phase 2 — Planning complete, ready for implementation

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent (knowledge graph for MTG rules)
- [x] Identify constraints (full rules, bilingual, open source)
- [x] Document findings in findings.md
- [x] Review reference article on knowledge graph building
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define technical approach (React + Cytoscape.js + Express + SQLite + Python parser)
- [x] Design concept model (8 node types, 8 relation types)
- [x] Design API endpoints
- [x] Design frontend interactions
- [x] Write design spec
- [x] Write implementation plans (3 phases)
- **Status:** complete

### Phase 3: Implementation
- [ ] Phase 1: Parser (8 tasks) — `docs/superpowers/plans/2026-04-07-mtgruler-phase1-parser.md`
- [ ] Phase 2: Server (9 tasks) — `docs/superpowers/plans/2026-04-07-mtgruler-phase2-server.md`
- [ ] Phase 3: Client (12 tasks) — `docs/superpowers/plans/2026-04-07-mtgruler-phase3-client.md`
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] End-to-end testing
- [ ] Verify all features work
- **Status:** pending

### Phase 5: Delivery
- [ ] Deploy to hosting platform
- [ ] Publish GitHub repo
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| React + Cytoscape.js | Purpose-built for graph/network visualization |
| Express + SQLite backend | Lightweight, SQLite file can ship with repo |
| Python parser with LLM extraction | Python better for text processing; LLM captures semantic relationships |
| Concept-based nodes (not rule entries) | Better abstraction for understanding and navigating rules |
| Full-stack separation (3 sub-projects) | Independent development and deployment |
| Bilingual EN/CN | Official EN source + community CN translation |
| MIT open source | Maximum community accessibility |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| WeChat article blocked by verification | 1 | User provided PDF, read via image conversion |

## Notes
- CN rules source: https://wiki.mtgjudge.cn/cr
- Reference article approach: LLM-driven concept extraction from notes → interactive web graph
- Implementation plans are in `docs/superpowers/plans/`
