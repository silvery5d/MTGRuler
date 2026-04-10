# Database Comparison: Before vs After

- Before DB: `/Users/deosigner/Documents/claude/MTGRuler/parser/data/concepts.db`
- After DB:  `/Users/deosigner/Documents/claude/MTGRuler/parser/data/concepts_validated.db`
- Model: `deepseek-chat`
- Sample: 30 concepts, 30 relations
- Seed: 7
- Generated: 2026-04-10 01:11:00

## Concepts

| | correct | suspicious | wrong | missing |
|---|---|---|---|---|
| before | 15 (50%) | 14 | 1 | 0 |
| after  | 15 (50%) | 14 | 1 | 0 |

- Flipped toward correct: **0**
- Flipped toward wrong:   0
- Changes in DB triggered re-validation: 1

## Relations

| | correct | suspicious | wrong | missing |
|---|---|---|---|---|
| before | 8 (27%) | 20 | 2 | 0 |
| after  | 11 (37%) | 16 | 2 | 1 |

- Flipped toward correct: **3**
- Flipped toward wrong:   1
- Changes in DB triggered re-validation: 11

## Concepts — flipped items


## Relations — flipped items

- ↑ `action.companion → concept.special_action`: suspicious → **correct**
- ↑ `keyword.impending → concept.time_counter`: suspicious → **correct**
- ↑ `multiplayer_variant.grand_melee → multiplayer_option.limited_range_of_influence`: suspicious → **correct**
- ↓ `concept.back_face → concept.double_faced_card`: suspicious → **missing**
