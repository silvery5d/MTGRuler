# Relation Normalization: Before / After

Same 100 (source, target) pairs from v1 validation, compared against concepts_validated.db.

## Summary

- Relations unchanged (type stayed same): **74**
- Relations with type changed (re-validated): **22**
- Relations dropped (self-loop / collapsed): **4**

| verdict | v1 | v3 (after normalize) |
|---|---|---|
| correct | 33 | 40 |
| suspicious | 52 | 41 |
| wrong | 15 | 15 |

**Among the 22 type-changed relations:**
- 8 flipped toward correct (good)
- 4 flipped toward wrong (bad)
- 10 kept same verdict (neutral)

## Details of type-changed relations

### ⚠️ `variant.emperor` --> `concept.flanking_attack_rule`
- type: `USES` → `DEPENDS_ON`
- verdict: suspicious → **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule text describes a restriction (a rule) that is part of the Emperor variant, which is better captured by CONTAINS.

### ⚠️ `designation.initiative` --> `keyword.venture_into_dungeon`
- type: `TRIGGERS` → `MODIFIES`
- verdict: suspicious → **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a triggered ability that causes venturing, which is more like OCCURS_IN or DEPENDS_ON.

### ❌ `action.drafting` --> `action.face_up_draft`
- type: `MAY_CONTAIN` → `CONTAINS`
- verdict: suspicious → **wrong**
- issue: The rule text describes a specific variant of drafting (face up drafting) but does not state that the general action of drafting contains the action of face up drafting. Instead, it explains how face up drafting works when it occurs.

### ✅ `concept.card_rarity` --> `concept.expansion_symbol`
- type: `INDICATES` → `REFERENCES`
- verdict: suspicious → **correct**

### ✅ `concept.replacement_effect` --> `concept.enter_battlefield_replacement`
- type: `IS_PATTERN_OF` → `PATTERN_OF`
- verdict: suspicious → **correct**

### ✅ `action.conspiracy_face_up` --> `concept.special_action`
- type: `IS_TYPE_OF` → `PATTERN_OF`
- verdict: suspicious → **correct**

### ✅ `keyword.impending` --> `concept.time_counter`
- type: `USES` → `DEPENDS_ON`
- verdict: suspicious → **correct**

### ⚠️ `keyword.lifelink` --> `concept.life_gain`
- type: `CAUSES` → `MODIFIES`
- verdict: suspicious → **suspicious**
- issue: MODIFIES is not the best fit; Lifelink triggers life gain, which is more like INTERACTS_WITH or PATTERN_OF.

### ⚠️ `concept.state_based_action` --> `concept.counter_cancellation`
- type: `ENFORCES` → `MODIFIES`
- verdict: suspicious → **suspicious**
- issue: MODIFIES is not the best canonical type; the relation is more about performing an action that results in removal, which fits OCCURS_IN or PATTERN_OF better.

### ❌ `concept.creature_enters_attacking` --> `concept.attacking_creature`
- type: `BECOMES_NEVER` → `PATTERN_OF`
- verdict: suspicious → **wrong**
- issue: The rule text describes a scenario where a creature entering attacking fails to become an attacking creature, which contradicts the relation's implication that 'creature enters attacking' is a pattern of 'attacking creature'. The relation is actually reversed or mischaracterized.

### ✅ `action.turn_based` --> `concept.state_based_action`
- type: `OCCURS_BEFORE` → `INTERACTS_WITH`
- verdict: suspicious → **correct**

### ⚠️ `concept.response` --> `concept.stack`
- type: `STACKS_ABOVE` → `MODIFIES`
- verdict: suspicious → **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes ordering and resolution, not modification.

### ⚠️ `concept.ability` --> `concept.one_shot_effect`
- type: `GENERATES` → `CREATES`
- verdict: suspicious → **suspicious**
- issue: CREATES is not a canonical relation type, but the rule text supports that abilities generate one-shot effects.

### ⚠️ `concept.color_indicator` --> `concept.color`
- type: `REFERENCES` → `MODIFIES`
- verdict: correct → **suspicious**
- issue: MODIFIES is not the best canonical type; the relation is more about determining or indicating color rather than modifying it.

### ⚠️ `property.owner` --> `property.controller`
- type: `EQUALS` → `INTERACTS_WITH`
- verdict: suspicious → **suspicious**
- issue: Type INTERACTS_WITH is not the best fit; the rule states controller is always the same as owner, which is a stronger, more specific relationship.

### ✅ `card_type.phenomenon` --> `zone.command_zone`
- type: `RESIDES_IN` → `MOVES_TO`
- verdict: suspicious → **correct**

### ❌ `concept.front_face` --> `concept.double_faced_card`
- type: `ATTRIBUTE_OF` → `CONTAINS`
- verdict: suspicious → **wrong**
- issue: The relation direction is reversed: a double-faced card contains a front face, not the front face contains a double-faced card.

### ✅ `effect.restriction` --> `effect.requirement`
- type: `MUST_NOT_VIOLATE` → `DEPENDS_ON`
- verdict: suspicious → **correct**

### ⚠️ `action.turn_based` --> `concept.priority`
- type: `OCCURS_BEFORE` → `INTERACTS_WITH`
- verdict: suspicious → **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule text describes a strict ordering where turn-based actions happen before priority is received, which is better captured by OCCURS_IN (turn-based actions occur in the step/phase before priority).

### ⚠️ `zone.stack` --> `zone.public`
- type: `IS_TYPE` → `PATTERN_OF`
- verdict: suspicious → **suspicious**
- issue: The relation type PATTERN_OF is non-canonical; the rule states the stack is a public zone, which is a 'type of' or 'is a' relationship, best captured by OCCURS_IN (as a zone type category).

### ✅ `keyword.escape` --> `cost.alternative`
- type: `USES` → `DEPENDS_ON`
- verdict: suspicious → **correct**

### ⚠️ `zone.ante` --> `zone.public`
- type: `IS_TYPE` → `PATTERN_OF`
- verdict: suspicious → **suspicious**
- issue: The relation type PATTERN_OF is non-canonical; the rule states that the ante zone is a public zone, which is a subtype or instance relationship.
