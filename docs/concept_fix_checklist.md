# Concept Fix Checklist

Human review checklist for concepts flagged as **wrong** by the DeepSeek cross-validator, after re-running with a fixed `load_rule_texts()` parser (which had been dropping chapter-level rule_refs like `117` and range refs like `205.2-205.2c`).

## How the list was built

1. Initial 100-concept random sample validated by `deepseek-chat` → 17 flagged wrong.
2. Parser bug discovered: chapter headers and ranges weren't being loaded. Fixed in `parser/validate.py:RULE_LINE_RE`.
3. Re-validated the 17 with the fix. Result:
   - **1 flipped to correct** (false positive): `concept.card_type` — no action needed
   - **6 flipped to suspicious** — definition could be tightened but not factually wrong, listed in section B
   - **10 still wrong** — real data issues, listed in section A

Note: this is a **sample-based** check. The same issue patterns likely repeat elsewhere in the full 1141-concept set. Fixing the ten below is a starting point; see "Systemic patterns" at the end for broader actions.

---

## A. Confirmed wrong (10) — action required

Grouped by fix type.

### A1. Wrong type label (1)

- [ ] **`keyword.multi_headed_giant`** (rule_ref `810.11`)
  - Issue: Type is `Keyword` but this is a multiplayer Variant
  - Fix: `UPDATE concepts SET type='Variant' WHERE id='keyword.multi_headed_giant';`
  - Consider also renaming id to `variant.multi_headed_giant` for consistency with other variants

### A2. Wrong rule_ref (2)

- [ ] **`zone.battlefield`** (rule_ref `112.1` → should be `400.1` or `403.1`)
  - Issue: `112.1` is about spells/stack, not the battlefield zone
  - Fix: Update rule_ref to `403` (Battlefield section) or its subrule
  - This is a **high-impact** fix — battlefield is one of the most important zones

- [ ] **`concept.copy_spell`** (rule_ref `706.2` → should be `707.x`)
  - Issue: `706.2` is about die rolls, not spell copying
  - Fix: Verify rule 707 "Copying Objects" and update rule_ref

### A3. Hallucinated definition from keyword-only header (4)

For these, the rule_ref points to a header line that only contains the keyword name (e.g., `701.22. Fateseal`). The actual definition lives in subrules like `701.22a`. The LLM invented a definition instead of following the subrule. **These concepts are real; only the definition is wrong.**

- [ ] **`action.fateseal`** (rule_ref `701.22`)
  - Fix: Set definition from `701.22a`, or change rule_ref to `701.22a`
- [ ] **`keyword.behold`** (rule_ref `701.61`)
  - Fix: Look up `701.61a` for the real definition
- [ ] **`keyword.intimidate`** (rule_ref `702.13`)
  - Fix: Look up `702.13a` for the real definition
- [ ] **`keyword.start_your_engines`** (rule_ref `702.179`)
  - Fix: Look up `702.179a` for the real definition

### A4. Scope/name mismatch (2)

- [ ] **`game.two_headed_giant`** (rule_ref `704.6`)
  - Issue: `704.6` is variant-general state-based actions, not 2HG-specific
  - Fix: Change rule_ref to `810` (Two-Headed Giant Variant) or its subrule
  - Also consider migrating id to `variant.two_headed_giant` for consistency

- [ ] **`variant.super_villain_rumble`** (rule_ref `904.12`)
  - Issue: Name is "Supervillain Rumble" but source uses "Supervillain Rumble **Option**"; definition goes beyond what source supports
  - Fix: Rename to "Supervillain Rumble Option"; trim definition to just what `904.12` states

### A5. Not actually a concept (1)

- [ ] **`mechanic.venture_marker`** (rule_ref `701.46a`)
  - Issue: "Venture marker" is a physical game piece, not a defined rules concept
  - Fix: **Delete this concept** (and any relations referencing it), or convert to `type='Object'`
  - Cascade: check `SELECT * FROM relations WHERE source_id='mechanic.venture_marker' OR target_id='mechanic.venture_marker'`

---

## B. Flagged suspicious on re-validation (6) — lower priority

These are not strictly wrong but have weak/inferred definitions. Worth cleaning up in a second pass.

| id | issue (summary) |
|---|---|
| `cardtype.attraction` | Definition includes details not in source rule `717` |
| `concept.combat_ending` | Definition oversimplifies combat-ending edge cases |
| `concept.timing_priority` | Definition is interpretation rather than extraction |
| `game_option.limited_range_of_influence` | Inferred definition; source only gives the name |
| `game_option.shared_team_turns` | Same as above |
| `mechanic.protector` | Definition incomplete; omits state-based-action graveyard outcome |

---

## C. What this list does NOT cover

- **42 concepts originally flagged suspicious** in `validation_report.md` (not re-checked, not included here)
- **15 relations flagged wrong** in the same report — most of these were non-canonical types, likely fixed by `normalize_relations.py` already. Worth a quick re-run of relation validation against `concepts_validated.db` to confirm.
- **The other 1041 concepts** that weren't in the 100-concept sample

---

## D. Systemic patterns worth scripted fixes

Three patterns repeat enough to be worth a script rather than manual edits:

1. **Keyword/action rule_ref pointing at header instead of subrule** (section A3).
   Detection: `SELECT id, rule_ref FROM concepts WHERE rule_ref GLOB '70[12].*[!a-z]' AND definition_en IS NOT NULL`.
   For each match, if `{rule_ref}a` exists in rule_texts, re-check the definition against `{rule_ref}a`.

2. **Variant concepts mislabelled as `Keyword`**.
   Detection: `SELECT id FROM concepts WHERE type='Keyword' AND rule_ref LIKE '8%' OR rule_ref LIKE '9%'`.
   Chapters 8xx and 9xx are Multiplayer and Casual Variants — nothing there should be a Keyword.

3. **Concepts with rule_ref but hallucinated definition** when source text is just the name.
   This is the hardest to detect automatically. Could compare definition length against source text length — if `len(definition) > 3 * len(source_text)`, flag as suspicious.

If you want, I can implement (1) and (2) as automated fixes and rerun validation on the result.
