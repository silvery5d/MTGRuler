# Relation Type Normalization Mapping

The LLM extraction produced 150+ relation types, but the spec defines only 8 canonical types. This table proposes a mapping from each non-canonical type → one of the 8 canonical types, based on inspection of source→target examples in the DB.

**Canonical types (9):** `CONTAINS`, `DEPENDS_ON`, `REFERENCES`, `OCCURS_IN`, `MODIFIES`, `INTERACTS_WITH`, `MOVES_TO`, `PATTERN_OF`, `CREATES`

> **Decision log:**
> 1. Added 9th canonical type **`CREATES`** for relations like `keyword.investigate → clue_token`. The original `CREATES` category (58 relations) stays as-is, plus absorbs `GENERATES`, `PRODUCES`, `MAY_CREATE`.
> 2. **`USES` is split by target type**: if target id starts with `zone.` → `OCCURS_IN`, else → `DEPENDS_ON`.
> 3. **Self-loop relations are dropped**, not remapped (e.g. `tribute→tribute`).

The 8 canonical types together cover 1075/1501 relations (71.6%). The remaining 426 relations (28.4%) use 144 invented types — this table normalizes them.

---

## Mapping rationale

| Canonical → | Meaning | Catches |
|---|---|---|
| **CONTAINS** | structural part-whole / has-feature / ownership | HAS_*, MAY_*, PART_OF, BELONGS_TO, ATTRIBUTE_OF, OWNES |
| **DEPENDS_ON** | A needs B to function / requires / uses | USES, REQUIRES, ENABLES, NEEDS, USED_*, CONDITION_OF, CHECKED_WHEN |
| **REFERENCES** | A mentions / cites / points to B | INDICATES, REPRESENTS, DEFINES, DISTINGUISHED_FROM, SPECIAL_CASE, EXCEPTION_TO, IMPLEMENTS, SIMILAR_TO |
| **OCCURS_IN** | A (event/action) happens in B (zone/phase/step) | FUNCTION_IN, RESIDES_IN, LOCATED_IN, STARTS_IN, APPLIES_IN, ACTIVATES_ON, CAN_BE_CAST_FROM, ALWAYS_USED_IN |
| **MODIFIES** | A changes state/behavior of B (creates, triggers, affects, restricts) | CREATES, TRIGGERS, ENFORCES, AFFECTS, GRANTS, RESULTS_IN, CAUSES, GENERATES, PRODUCES, SETS, LIMITS, RESTRICTS, PREVENTS, CHECKS, CANCELS, SUPERSEDES, OVERRIDES, REPLACES, CONTROLS, ASSIGNS, CALCULATES, TRACKS, APPLIES_TO, INTERRUPTS, ENDS_STEP |
| **INTERACTS_WITH** | sibling-level coexistence / ordering / coordination | ORDERS, PRECEDES, OCCURS_BEFORE, EXPIRES_AT, ADJACENT_TO, ADDED_TO, RECEIVES_*, INDEPENDENT, ALTERNATIVE_OF, COMPLEMENTS |
| **MOVES_TO** | zone change / resolution path | MOVES_FROM, ENTERS, VISITS, BRANCHES_TO, RESOLVES, RESOLVES_IN |
| **PATTERN_OF** | A is-a / is-instance-of / is-variant-of B | IS_TYPE, IS_TYPE_OF, IS_A, IS_VARIANT_OF, VARIANT_OF, EXTENDS, BECOMES, CAN_BE, IS_PATTERN |

---

## Full mapping (144 → 8)

### → CONTAINS (18 types)
```
OWNES                  → CONTAINS   # typo, player→deck
HAS_FEATURE            → CONTAINS
HAS_PART               → CONTAINS
HAS                    → CONTAINS
HAS_PROPERTY           → CONTAINS
HAS_DURATION           → CONTAINS
HAS_SOURCE             → CONTAINS
HAS_DEFAULT            → CONTAINS
MAY_HAVE               → CONTAINS
MAY_INCLUDE            → CONTAINS
MAY_CONTAIN            → CONTAINS
CAN_CONTAIN            → CONTAINS
PART_OF                → CONTAINS
BELONGS_TO             → CONTAINS
ATTRIBUTE_OF           → CONTAINS
MODIFIED_BY            → CONTAINS   # A holds a slot for modifier B
```

### → DEPENDS_ON (18 types)
```
DEPENDES_ON            → DEPENDS_ON   # typo
USES                   → DEPENDS_ON
USED_BY                → DEPENDS_ON
USED_FOR               → DEPENDS_ON
USED_IN                → DEPENDS_ON
USED_TO_PAY            → DEPENDS_ON
CAN_BE_PAID_WITH       → DEPENDS_ON
REQUIRES               → DEPENDS_ON
REQUIRED_FOR           → DEPENDS_ON
ENABLES                → DEPENDS_ON
ENABLED_BY             → DEPENDS_ON
CONDITION_OF           → DEPENDS_ON
CHECKED_WHEN           → DEPENDS_ON
NOT_REQUIRED_FOR       → DEPENDS_ON
CAN_BE_OVERCOME_BY     → DEPENDS_ON
CAN_BE_REMOVED         → DEPENDS_ON
MAY_REQUIRE            → DEPENDS_ON
MUST_NOT_VIOLATE       → DEPENDS_ON
```

### → REFERENCES (12 types)
```
INDICATES              → REFERENCES
REPRESENTS             → REFERENCES
DEFINES                → REFERENCES
DISTINGUISHED_FROM     → REFERENCES
DISTINCT_FROM          → REFERENCES
SIMILAR_TO             → REFERENCES
COMPARES_TO            → REFERENCES
SPECIAL_CASE           → REFERENCES
SPECIAL_RULE_FOR       → REFERENCES
EXCEPTION_TO           → REFERENCES
IMPLEMENTS             → REFERENCES
SUBJECT_OF             → REFERENCES
```

### → OCCURS_IN (8 types)
```
FUNCTION_IN            → OCCURS_IN
RESIDES_IN             → OCCURS_IN
LOCATED_IN             → OCCURS_IN
STARTS_IN              → OCCURS_IN
APPLIES_IN             → OCCURS_IN
ACTIVATES_ON           → OCCURS_IN
CAN_BE_CAST_FROM       → OCCURS_IN
CAN_RETURN_TO          → OCCURS_IN
ALWAYS_USED_IN         → OCCURS_IN
```

### → MODIFIES (53 types)  — the biggest bucket
```
CREATES                → MODIFIES
TRIGGERS               → MODIFIES
TRIGGERS_FROM          → MODIFIES
ENFORCES               → MODIFIES
AFFECTS                → MODIFIES
APPLIES_TO             → MODIFIES
GRANTS                 → MODIFIES
IMPLICITLY_GRANTS      → MODIFIES
RESULTS_IN             → MODIFIES
RESULT_IN              → MODIFIES
RESULT_OF              → MODIFIES
CAUSES                 → MODIFIES
GENERATES              → MODIFIES
PRODUCES               → MODIFIES
PRODUCED_BY            → MODIFIES
SETS                   → MODIFIES
LIMITS                 → MODIFIES
LIMITED_BY             → MODIFIES
RESTRICTS              → MODIFIES
PREVENTS               → MODIFIES
CHECKS                 → MODIFIES
CANCELS                → MODIFIES
SUPERSEDES             → MODIFIES
OVERRIDES              → MODIFIES
REPLACES               → MODIFIES
CONTROLS               → MODIFIES
CONTROLLED_BY          → MODIFIES
ASSIGNS                → MODIFIES
CALCULATES             → MODIFIES
CALCULATES_MANA_FROM   → MODIFIES
TRACKS                 → MODIFIES
INTERRUPTS             → MODIFIES
ENDS_STEP              → MODIFIES
SKIPS_TO               → MODIFIES
STACKS_ABOVE           → MODIFIES
EXEMPTS_FROM           → MODIFIES
NOT_APPLICABLE         → MODIFIES
AVOIDS                 → MODIFIES
INCREASES              → MODIFIES
INCREASES_BY           → MODIFIES
REDUCED_BY             → MODIFIES
ALLOWS                 → MODIFIES
MANAGES                → MODIFIES
MAY_CREATE             → MODIFIES
CANNOT                 → MODIFIES
CANNOT_TARGET          → MODIFIES
DEALS                  → MODIFIES
DEALS_NO               → MODIFIES
DOES_NOT_CREATE        → MODIFIES
CAN_ATTACK             → MODIFIES
TUTORS                 → MODIFIES
ESTABLISHES            → MODIFIES
PRIORITY_RULE          → MODIFIES
FALLBACK_TO            → MODIFIES
DETERMINED_BY          → MODIFIES
CHOOSES                → MODIFIES
ANNOUNCES              → MODIFIES
SUBJECT_TO             → MODIFIES
CHOICE_BETWEEN         → MODIFIES
```

### → INTERACTS_WITH (12 types)
```
ORDERS                 → INTERACTS_WITH
PRECEDES               → INTERACTS_WITH
OCCURS_BEFORE          → INTERACTS_WITH
EXPIRES_AT             → INTERACTS_WITH
ADJACENT_TO            → INTERACTS_WITH
ADDED_TO               → INTERACTS_WITH
RECEIVES               → INTERACTS_WITH
RECEIVES_AFTER         → INTERACTS_WITH
RECEIVES_FIRST         → INTERACTS_WITH
INDEPENDENT            → INTERACTS_WITH
INDEPENDENT_OF         → INTERACTS_WITH
ALTERNATIVE_OF         → INTERACTS_WITH
COMPLEMENTS            → INTERACTS_WITH
COCCURS_ON             → INTERACTS_WITH   # typo for co-occurs
EQUALS                 → INTERACTS_WITH
```

### → MOVES_TO (6 types)
```
MOVES_FROM             → MOVES_TO
ENTERS                 → MOVES_TO
VISITS                 → MOVES_TO
BRANCHES_TO            → MOVES_TO
RESOLVES               → MOVES_TO
RESOLVES_IN            → MOVES_TO
```

### → PATTERN_OF (14 types)
```
IS_TYPE                → PATTERN_OF
IS_TYPE_OF             → PATTERN_OF
IS_A                   → PATTERN_OF
IS_VARIANT_OF          → PATTERN_OF
IS_VARIATION           → PATTERN_OF
VARIANT_OF             → PATTERN_OF
EXTENDS                → PATTERN_OF
IS_PATTERN             → PATTERN_OF
IS_PATTERN_OF          → PATTERN_OF
BECOMES                → PATTERN_OF
CAN_BECOME             → PATTERN_OF
BECOMES_NEVER          → PATTERN_OF
CAN_BE                 → PATTERN_OF
```

---

## Ambiguous / judgment calls worth reviewing

These were hard to place; you may want to reassign:

1. **`CREATES` (58 relations) → MODIFIES** — The biggest non-canonical bucket. Arguably a 9th type. Examples: `keyword.investigate→concept.clue_token`, `keyword.amass→token.army`. An alternative reading is `CONTAINS` (the keyword "contains" the created thing) but MODIFIES better captures the causal sense.

2. **`USES` (40 relations) → DEPENDS_ON** — "Uses" is ambiguous between DEPENDS_ON ("escape uses alternative cost") and OCCURS_IN ("cast_spell uses the stack"). I defaulted to DEPENDS_ON because most examples express a requirement.

3. **`MODIFIED_BY` → CONTAINS** — Unusual choice; I put it as CONTAINS because `concept.cost MODIFIED_BY concept.additional_cost` reads as "cost has a slot for additional_cost". Could equally be MODIFIES reversed.

4. **`CAN_RETURN_TO` → OCCURS_IN** — The one example is `card_type.commander → zone.command_zone`, which describes where the commander can exist. Could also be MOVES_TO.

5. **Self-loops detected** — The validation found `keyword.tribute → keyword.tribute` (DEPENDS_ON). These should be **deleted**, not remapped. There are likely more. I'll add a self-loop filter to the normalization script.

---

## Next steps

1. **You review this table** and tell me any mappings you'd flip
2. I write `parser/normalize_relations.py` that applies the mapping, drops self-loops, and writes `parser/data/concepts_validated.db`
3. After the validation run finishes, I update the script to also apply any concept-level fixes the LLM flagged
