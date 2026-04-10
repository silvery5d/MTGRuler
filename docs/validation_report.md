# MTGRuler Extraction Validation Report

- Model: `deepseek-chat`
- Sample size: 100 concepts, 100 relations
- Seed: 42
- Generated: 2026-04-09 22:50:50

## Summary

- **Concepts**: correct=41/100 (41%), suspicious=42, wrong=17
- **Relations**: correct=33/100 (33%), suspicious=52, wrong=15

## Concept validation

### ⚠️ `keyword.foretell` — Foretell (Keyword)
- rule_ref: `702.143`
- verdict: **suspicious**
- issue: Definition is inferred; source text only provides the keyword name.
- suggested fix: Definition should be based on the full rule text for 702.143, not just the header.

### ✅ `concept.damage` — Damage (Concept)
- rule_ref: `120.1`
- verdict: **correct**

### ✅ `concept.aura_trigger` — Aura Zone-Change Trigger (MechanicPattern)
- rule_ref: `603.6e`
- verdict: **correct**

### ✅ `concept.impossible_instruction` — Impossible instruction (Concept)
- rule_ref: `101.3`
- verdict: **correct**

### ⚠️ `action.unattach` — Unattach (Action)
- rule_ref: `701.3d`
- verdict: **suspicious**
- issue: Definition omits that 'unattach' also applies to Auras and Fortifications, not just Equipment.
- suggested fix: Update definition to: 'To move an attached permanent (Aura, Equipment, or Fortification) away from the object or player it was attached to, so it is on the battlefield but not attached to anything. Includes any case where an attached card ceases to be attached.'

### ❌ `game_option.limited_range_of_influence` — Limited Range of Influence (Concept)
- rule_ref: `801`
- verdict: **wrong**
- issue: Rule reference 801 not found in provided source text.
- suggested fix: Verify the correct rule reference for Limited Range of Influence.

### ✅ `action.convert` — Convert (Action)
- rule_ref: `701.50a`
- verdict: **correct**

### ⚠️ `concept.attacking` — Attacking (Action)
- rule_ref: `302.5`
- verdict: **suspicious**
- issue: Definition is more specific than source text; source only states creatures can attack and block, not when or what they attack.
- suggested fix: Definition should be: Creatures can attack and block.

### ⚠️ `concept.win_the_game` — Win the Game (MechanicPattern)
- rule_ref: `104.2`
- verdict: **suspicious**
- issue: Definition is broader than source text; source only states there are several ways to win, not the condition itself.
- suggested fix: Definition could be: 'There are several ways to win the game.'

### ✅ `concept.effect_reference_by_name` — Effect Reference by Name (Concept)
- rule_ref: `707.11`
- verdict: **correct**

### ⚠️ `concept.passing_priority` — Passing Priority (Concept)
- rule_ref: `117.4`
- verdict: **suspicious**
- issue: Definition is a description of the action, but the source rule text defines the consequence of all players passing.
- suggested fix: Definition should focus on the consequence: 'When all players pass in succession, the top object on the stack resolves or, if the stack is empty, the phase or step ends.'

### ✅ `concept.card_ownership` — Card Ownership (Concept)
- rule_ref: `108.3`
- verdict: **correct**

### ✅ `concept.poison_counter` — Poison Counter (Concept)
- rule_ref: `104.3d`
- verdict: **correct**

### ❌ `game.two_headed_giant` — Two-Headed Giant Variant (Concept)
- rule_ref: `704.6`
- verdict: **wrong**
- issue: Concept name and definition reference Two-Headed Giant, but source rule text only mentions variant games in general, not specific variant details.
- suggested fix: Either change concept to a general 'Variant State-Based Actions' concept, or use a rule reference that actually defines Two-Headed Giant.

### ✅ `ability.activated_mana` — Activated Mana Ability (Concept)
- rule_ref: `605.1a`
- verdict: **correct**

### ✅ `concept.removed_from_combat` — Removed from Combat (Concept)
- rule_ref: `511.3`
- verdict: **correct**

### ✅ `concept.rarity_letter` — Rarity Letter (Concept)
- rule_ref: `213.1b`
- verdict: **correct**

### ⚠️ `mechanic.fused_split_spell` — Fused Split Spell (MechanicPattern)
- rule_ref: `702.102b`
- verdict: **suspicious**
- issue: definition includes extra details not in source rule text
- suggested fix: Definition should be: 'A fused split spell has the combined characteristics of its two halves.'

### ⚠️ `subtype.equipment` — Equipment (CardType)
- rule_ref: `301.5`
- verdict: **suspicious**
- issue: Definition mentions 'equip ability' but source rule text does not explicitly mention the equip ability.
- suggested fix: Change definition to: 'An artifact subtype. An Equipment can be attached to a creature. It can’t legally be attached to anything that isn’t a creature.'

### ✅ `concept.instruction_order` — Instruction Order (Concept)
- rule_ref: `608.2c`
- verdict: **correct**

### ✅ `concept.snow_mana` — Snow Mana (Concept)
- rule_ref: `107.4h`
- verdict: **correct**

### ⚠️ `concept.variant.planechase` — Planechase Variant (Concept)
- rule_ref: `103.7`
- verdict: **suspicious**
- issue: Definition is a high-level summary, but the source rule text describes a specific setup procedure.
- suggested fix: Definition could be more specific, e.g., 'A variant using planar decks. The starting player reveals cards from their planar deck until a plane card is revealed, which becomes the starting plane.'

### ⚠️ `concept.zone_restriction_ability` — Zone Restriction Ability (Concept)
- rule_ref: `113.6e`
- verdict: **suspicious**
- issue: Definition omits the distinction between the ability itself and an ability that grants such an ability.
- suggested fix: An ability that restricts or modifies how that particular object can be played or cast functions in any zone from which it could be played or cast and also on the stack.

### ⚠️ `action.transform` — Transform (Action)
- rule_ref: `701.28`
- verdict: **suspicious**
- issue: Definition is incomplete; source rule text is just the keyword name, not the full definition.
- suggested fix: Check rule 701.28 for the full definition of the Transform action.

### ✅ `multiplayer_mechanic.combined_attack` — Combined Attack (Concept)
- rule_ref: `805.10b`
- verdict: **correct**

### ✅ `mechanic.linked_word_choice` — Linked Word Choice (MechanicPattern)
- rule_ref: `607.2f`
- verdict: **correct**

### ⚠️ `keyword.monstrosity` — Monstrosity (Keyword)
- rule_ref: `701.31`
- verdict: **suspicious**
- issue: Definition is incomplete; source only provides the keyword name, not the full rules text.
- suggested fix: Definition should be based on the full rule text for 701.31, not just the header.

### ✅ `concept.consolation_owner` — Conspiracy Card Owner (Concept)
- rule_ref: `315.6`
- verdict: **correct**

### ✅ `concept.target_restriction` — Target Restriction (Range of Influence) (Concept)
- rule_ref: `801.4`
- verdict: **correct**

### ❌ `variant.super_villain_rumble` — Supervillain Rumble (Concept)
- rule_ref: `904.12`
- verdict: **wrong**
- issue: Name mismatch and insufficient definition
- suggested fix: Change name to 'Supervillain Rumble Option' and adjust definition to match the source text, which only names the variant.

### ❌ `game_option.shared_team_turns` — Shared Team Turns (Concept)
- rule_ref: `805`
- verdict: **wrong**
- issue: Rule reference 805 not found in source text; concept cannot be validated.

### ⚠️ `concept.copiable_values_on_reveal` — Copiable Values on Reveal (Concept)
- rule_ref: `708.8`
- verdict: **suspicious**
- issue: Definition omits important details about abilities relating to entering the battlefield.
- suggested fix: When a face-down permanent is turned face up, its copiable values revert to normal, applied effects still apply, and abilities relating to entering the battlefield don't trigger or have effect.

### ⚠️ `keyword.goad` — Goad (Keyword)
- rule_ref: `701.38`
- verdict: **suspicious**
- issue: Definition is incomplete; source rule text is truncated and only shows the keyword name.
- suggested fix: Definition should be based on the full rule text for 701.38, not just the header.

### ⚠️ `keyword.doctors_companion` — Doctor's companion (Keyword)
- rule_ref: `702.124m`
- verdict: **suspicious**
- issue: Definition uses 'creatures' instead of 'creature cards' and omits 'your' before commander.
- suggested fix: Definition should be: 'You may designate two legendary creature cards as your commander rather than one if one of them is this card and the other is a legendary Time Lord Doctor creature card that has no other creature types.'

### ❌ `concept.combat_ending` — Ending the Combat Phase (MechanicPattern)
- rule_ref: `722.2-722.2g`
- verdict: **wrong**
- issue: rule_ref not found in source text
- suggested fix: Verify the correct rule reference for ending the combat phase.

### ✅ `concept.activation_cost` — Activation Cost (Concept)
- rule_ref: `602.1a`
- verdict: **correct**

### ⚠️ `concept.variant.conspiracy_draft` — Conspiracy Draft Variant (Concept)
- rule_ref: `103.2e`
- verdict: **suspicious**
- issue: Definition is slightly off; the source rule specifies 'any number of conspiracy cards from their sideboard' and is a specific rule for Conspiracy Draft games, not a general description of the variant.
- suggested fix: Definition should more closely match the source: 'In a Conspiracy Draft game, each player may put any number of conspiracy cards from their sideboard into the command zone.'

### ⚠️ `concept.casual_play` — Casual play (Concept)
- rule_ref: `100.7`
- verdict: **suspicious**
- issue: Definition is slightly reductive and omits some card types mentioned in the source.
- suggested fix: Definition should include 'Mystery Booster playtest cards' and 'promotional cards' alongside silver-bordered and acorn-stamped cards.

### ❌ `keyword.multi_headed_giant` — Multi-Headed Giant Variants (Keyword)
- rule_ref: `810.11`
- verdict: **wrong**
- issue: Type should be Variant, not Keyword
- suggested fix: Change type to 'Variant'

### ✅ `zone.hidden` — Hidden Zone (Concept)
- rule_ref: `400.2`
- verdict: **correct**

### ✅ `concept.regeneration` — Regeneration (MechanicPattern)
- rule_ref: `614.8`
- verdict: **correct**

### ⚠️ `concept.ownership` — Ownership (Concept)
- rule_ref: `112.2`
- verdict: **suspicious**
- issue: Definition is incomplete and slightly misaligned with source text.
- suggested fix: Definition should specify: 'The player who owns a card or spell. For a spell, this is the owner of the card that represents it, unless it is a copy. For a copy, the owner is the player under whose control it was put on the stack.'

### ✅ `concept.control_of_copy` — Control of Copy (Concept)
- rule_ref: `707.10`
- verdict: **correct**

### ⚠️ `keyword.modular` — Modular (Keyword)
- rule_ref: `702.43`
- verdict: **suspicious**
- issue: Definition is incomplete; missing details about the number of counters and the target restriction.
- suggested fix: Update definition to: 'Static and triggered ability where a creature enters the battlefield with a number of +1/+1 counters equal to its printed modular number. When it dies, you may move those counters onto target artifact creature.'

### ✅ `concept.front_face_symbol` — Front-Face Symbol (Concept)
- rule_ref: `712.2a`
- verdict: **correct**

### ⚠️ `game_rule.archenemy` — Archenemy (Concept)
- rule_ref: `703.4e`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits reference to rule 904 for full variant details.
- suggested fix: Special multiplayer variant where the archenemy player uses a scheme deck and sets the top scheme in motion immediately after their precombat main phase begins. See rule 904.

### ✅ `concept.teammate` — Teammate (Concept)
- rule_ref: `102.3`
- verdict: **correct**

### ❌ `keyword.start_your_engines` — Start Your Engines! (Keyword)
- rule_ref: `702.179`
- verdict: **wrong**
- issue: Definition is fabricated; source rule text only shows the keyword name, no definition provided.
- suggested fix: Definition should be empty or indicate that no definition is available in the provided source.

### ✅ `concept.loyalty_symbol` — Loyalty Symbol (Concept)
- rule_ref: `107.7`
- verdict: **correct**

### ⚠️ `keyword.mentor` — Mentor (Keyword)
- rule_ref: `702.134`
- verdict: **suspicious**
- issue: Definition is incomplete; missing details about 'when this creature attacks' trigger and 'may' choice.
- suggested fix: A triggered ability that triggers when this creature attacks. It may put a +1/+1 counter on an attacking creature with less power than this creature.

### ✅ `designation.monstrous` — Monstrous (Concept)
- rule_ref: `701.31b`
- verdict: **correct**

### ✅ `randomization.doubles` — Doubles (Concept)
- rule_ref: `706.5`
- verdict: **correct**

### ⚠️ `concept.legal_target` — Legal Target (Concept)
- rule_ref: `608.2b`
- verdict: **suspicious**
- issue: Definition is incomplete; it omits that a target can become illegal due to changes in characteristics or effect text, not just zone changes.
- suggested fix: Update definition to: A target that remains in the zone it was in when targeted, remains valid according to the spell or ability's targeting restrictions, and has not become illegal due to changes in characteristics or effect text.

### ✅ `concept.party` — Party (Concept)
- rule_ref: `700.8`
- verdict: **correct**

### ⚠️ `concept.alternate_name` — Alternate Name (Secondary Title) (Concept)
- rule_ref: `201.6`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits key details about the relationship between the alternate name and the Oracle name.
- suggested fix: Clarify that the alternate name appears in the upper left, the Oracle name is in the secondary bar, and for all game purposes, the card has only the Oracle name. The alternate name is used only in display and has no gameplay effect.

### ✅ `concept.life_gain_event` — Life Gain Event (Concept)
- rule_ref: `119.9`
- verdict: **correct**

### ⚠️ `concept.ability_removal` — Ability Removal (Concept)
- rule_ref: `113.10b`
- verdict: **suspicious**
- issue: Definition adds 'stated as the object "losing" that ability' which is not in the source text.
- suggested fix: Definition should be: 'Effects that remove an ability remove all instances of it.'

### ✅ `action.face_villainous_choice` — Face a Villainous Choice (Action)
- rule_ref: `701.53a`
- verdict: **correct**

### ⚠️ `keyword.myriad` — Myriad (Keyword)
- rule_ref: `702.116`
- verdict: **suspicious**
- issue: Definition is incomplete; missing details about token exile and 'if one or more tokens are created' clause.
- suggested fix: Update definition to include full text: 'Whenever this creature attacks, for each opponent other than the defending player, you may create a token that's a copy of this creature that's tapped and attacking that opponent or a planeswalker they control. Exile the tokens at end of combat.'

### ✅ `concept.total_toxic_value` — Total Toxic Value (Concept)
- rule_ref: `702.164b`
- verdict: **correct**

### ❌ `action.fateseal` — Fateseal (Action)
- rule_ref: `701.22`
- verdict: **wrong**
- issue: Definition does not match source rule text; source only provides the keyword name without definition.
- suggested fix: Definition should be derived from the full rule text for 'Fateseal' (likely 701.22a or similar), not just the header.

### ⚠️ `keyword.retrace` — Retrace (Keyword)
- rule_ref: `702.81`
- verdict: **suspicious**
- issue: definition incomplete; missing details about casting from graveyard and land discard as additional cost.
- suggested fix: Update definition to: 'Retrace is a keyword ability that allows you to cast a card from your graveyard by discarding a land card as an additional cost.'

### ✅ `concept.permanent_card` — Permanent Card (Concept)
- rule_ref: `110.4a`
- verdict: **correct**

### ✅ `concept.lit_up_numbers` — Lit-Up Numbers (Concept)
- rule_ref: `717.1`
- verdict: **correct**

### ❌ `mechanic.venture_marker` — Venture Marker (MechanicPattern)
- rule_ref: `701.46a`
- verdict: **wrong**
- issue: The source rule text does not define 'Venture Marker' as a concept; it only mentions 'venture marker' as a game piece used in the process.
- suggested fix: Change type to 'Object' or remove the concept, as it's not a defined rules concept but a physical marker.

### ⚠️ `concept.life_loss` — Life Loss (Concept)
- rule_ref: `119.3`
- verdict: **suspicious**
- issue: Definition adds 'typically from damage' which is not in the source rule text.
- suggested fix: Definition should be: 'A reduction in a player's life total.'

### ❌ `concept.timing_priority` — Timing and Priority (Concept)
- rule_ref: `117`
- verdict: **wrong**
- issue: Rule reference 117 not found in source text; concept cannot be validated.

### ⚠️ `action.planeswalk` — Planeswalk (Action)
- rule_ref: `701.24`
- verdict: **suspicious**
- issue: definition incomplete; source rule text only shows keyword name, not full definition.
- suggested fix: Check rule 701.24's full text for the complete definition of Planeswalk.

### ❌ `zone.battlefield` — Battlefield (Zone)
- rule_ref: `112.1`
- verdict: **wrong**
- issue: Source rule text is about spells and the stack, not the battlefield zone.
- suggested fix: Check rule 400.1 for zone definitions, or rule 110.1 for the battlefield.

### ✅ `phase.ending` — Ending Phase (Phase)
- rule_ref: `500.1`
- verdict: **correct**

### ⚠️ `card_type.scheme` — Scheme (CardType)
- rule_ref: `300.1`
- verdict: **suspicious**
- issue: Definition adds extra details not present in the source rule text.
- suggested fix: Definition should be a simple statement of the card type, e.g., 'A card type.'

### ✅ `zone.hand` — Hand (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ✅ `concept.battle_defense` — Battle Defense (Concept)
- rule_ref: `210.1`
- verdict: **correct**

### ❌ `mechanic.protector` — Protector (MechanicPattern)
- rule_ref: `310.10`
- verdict: **wrong**
- issue: Definition incorrectly states battle is exiled; source says put into owner's graveyard.
- suggested fix: Change definition to: 'A player designated to defend a battle. Must be an opponent of the battle's controller for Sieges. If no valid protector exists, the battle is put into its owner's graveyard.'

### ⚠️ `concept.lose_the_game` — Lose the Game (MechanicPattern)
- rule_ref: `104.3`
- verdict: **suspicious**
- issue: Definition is overly broad; source text only states there are several ways to lose, not the definition of losing.
- suggested fix: Definition should be more precise, e.g., 'The state or event that results in a player or team being eliminated from the game.'

### ⚠️ `concept.meld` — Meld (Action)
- rule_ref: `701.37`
- verdict: **suspicious**
- issue: Definition is incomplete; source only provides the keyword name, not the full action description.
- suggested fix: Definition should be derived from the full rules text for meld (likely 701.37a), not just the keyword header.

### ⚠️ `keyword.reinforce` — Reinforce (Keyword)
- rule_ref: `702.77a`
- verdict: **suspicious**
- issue: Definition omits 'Reinforce N—[cost]' structure and incorrectly states 'persists in all zones'.
- suggested fix: Definition should be: 'An activated ability "Reinforce N—[cost]" which means "[Cost], Discard this card: Put N +1/+1 counters on target creature." Functions only while the card is in a player’s hand.'

### ✅ `concept.multiple_card_types` — Multiple Card Types (Concept)
- rule_ref: `300.2`
- verdict: **correct**

### ⚠️ `keyword.collect_evidence` — Collect Evidence (Keyword)
- rule_ref: `701.57`
- verdict: **suspicious**
- issue: Definition is incomplete; missing the 'to cast a spell' context.
- suggested fix: Definition should be: 'To cast a spell by paying its collect evidence cost, exile any number of cards from your graveyard with total mana value N or greater.'

### ⚠️ `concept.variant.archenemy` — Archenemy Variant (Concept)
- rule_ref: `103.4e`
- verdict: **suspicious**
- issue: Definition includes schemes and higher life total, but source only mentions life total.
- suggested fix: Definition should focus on the life total rule, or cite a more comprehensive rule.

### ⚠️ `multiplayer_variant.grand_melee` — Grand Melee (Concept)
- rule_ref: `807.1`
- verdict: **suspicious**
- issue: Definition is '<none>' but source provides a description.
- suggested fix: Set definition_en to: 'A modification of the Free-for-All variant for a group of players competing as individuals, normally used with ten or more players.'

### ❌ `cardtype.attraction` — Attraction (CardType)
- rule_ref: `717`
- verdict: **wrong**
- issue: Rule reference 717 not found in provided source text.
- suggested fix: Verify the correct rule reference for the Attraction card type.

### ❌ `keyword.behold` — Behold (Keyword)
- rule_ref: `701.61`
- verdict: **wrong**
- issue: Definition does not match source rule text; source only contains the keyword name without definition.
- suggested fix: Definition should be empty or indicate that the keyword is defined elsewhere, as rule 701.61 only lists the keyword name.

### ⚠️ `keyword.daybound` — Daybound (Keyword)
- rule_ref: `702.145b`
- verdict: **suspicious**
- issue: Definition is slightly off; it says 'three static abilities on transforming double-faced card front faces that cause transformation at night and prevent other transformations.' The source says Daybound *represents* three static abilities and lists them, but the definition should more directly reflect that it's a keyword ability that encompasses those three abilities.
- suggested fix: Daybound is a keyword ability found on the front faces of some transforming double-faced cards. It represents three static abilities: one for entering transformed if it's night, one for transforming as it becomes night, and one preventing other transformations.

### ⚠️ `card_type.kindred` — Kindred (CardType)
- rule_ref: `300.1`
- verdict: **suspicious**
- issue: Definition adds details not present in the source rule text.
- suggested fix: Definition should be a simple statement of its existence as a card type, e.g., 'One of the card types listed in the comprehensive rules.'

### ⚠️ `concept.flipping` — Flipping (MechanicPattern)
- rule_ref: `710.4`
- verdict: **suspicious**
- issue: Definition omits that flipping switches between normal and alternative characteristics.
- suggested fix: Add 'that switches a permanent from its normal characteristics to its alternative characteristics' to the definition.

### ❌ `concept.copy_spell` — Copy Spell (Concept)
- rule_ref: `706.2`
- verdict: **wrong**
- issue: Source rule text is about die rolls, not copying spells.
- suggested fix: Check rule 706.2 for the correct definition of copying objects.

### ✅ `concept.substitute_card` — Substitute Card (Concept)
- rule_ref: `713.1`
- verdict: **correct**

### ✅ `layer.layer_6` — Layer 6 - Ability Adding/Removing (Concept)
- rule_ref: `613.1f`
- verdict: **correct**

### ✅ `concept.information_restriction` — Information Gathering Restriction (Concept)
- rule_ref: `801.11`
- verdict: **correct**

### ⚠️ `concept.shortcut` — Shortcut (Concept)
- rule_ref: `730.1`
- verdict: **suspicious**
- issue: Definition is more detailed than source text; source only describes typical use, not formal definition.
- suggested fix: Definition should reflect that shortcuts are mutually understood sequences used instead of explicitly identifying each game choice.

### ✅ `concept.default_face_down_characteristics` — Default Face-Down Characteristics (Concept)
- rule_ref: `708.2a`
- verdict: **correct**

### ⚠️ `concept.transform` — Transform (Action)
- rule_ref: `701.28`
- verdict: **suspicious**
- issue: Definition is incomplete; source rule text is just the keyword name, not the full definition.
- suggested fix: Check rule 701.28 for the full definition text, or reference the appropriate rule section (e.g., 712) for the transform action details.

### ❌ `keyword.intimidate` — Intimidate (Keyword)
- rule_ref: `702.13`
- verdict: **wrong**
- issue: Definition provided, but source rule text is incomplete (only shows the name). Cannot verify accuracy.
- suggested fix: Provide the full source rule text for 702.13 to validate the definition.

### ⚠️ `ability.evasion` — Evasion Ability (MechanicPattern)
- rule_ref: `702.9a`
- verdict: **suspicious**
- issue: Definition is a general description, but source text only states 'Flying is an evasion ability.' as an example.
- suggested fix: Definition should be more specific to the rule text, e.g., 'An ability that makes a creature harder to block, such as flying.'

### ⚠️ `card_type.lesson` — Lesson (CardType)
- rule_ref: `701.45a`
- verdict: **suspicious**
- issue: Definition incorrectly states Lesson is a card type found in the Sideboard; source rule text refers to 'Lesson card' but does not define it as a card type or specify it is found in the Sideboard.
- suggested fix: Definition should clarify that Lesson is a subtype of card types (like Sorcery) that can be revealed from outside the game via Learn, not necessarily only from the Sideboard.

### ✅ `concept.constructed_play` — Constructed play (MechanicPattern)
- rule_ref: `100.2a`
- verdict: **correct**

### ⚠️ `keyword.hideaway` — Hideaway (Keyword)
- rule_ref: `702.75a`
- verdict: **suspicious**
- issue: Definition slightly misstates the look-at rights; source says exiled card gains ability granting look-at rights to controller of the hiding permanent, not 'grants look-at rights to players who control the hiding permanent'.
- suggested fix: Change definition to: When this permanent enters, look at the top N cards of your library, exile one face down, and put the rest on the bottom in random order. The exiled card gains 'The player who controls the permanent that exiled this card may look at this card in the exile zone.'

### ✅ `zone.command` — Command (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ❌ `concept.card_type` — Card Type (CardType)
- rule_ref: `205.2-205.2c`
- verdict: **wrong**
- issue: rule_ref not found in source
- suggested fix: Check rule reference validity or provide actual source text.

## Relation validation

### ⚠️ `concept.skipping` --[MODIFIES]--> `step.combat_damage`
- rule_ref: `506.1`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes skipping as a possible event that occurs in the combat damage step, not that the concept of skipping modifies the step.
- suggested type: `OCCURS_IN`

### ❌ `keyword.tribute` --[DEPENDS_ON]--> `keyword.tribute`
- rule_ref: `702.104b`
- verdict: **wrong**
- issue: Source and target are identical; relation cannot be self-referential in this context.

### ⚠️ `concept.card_draw` --[PATTERN_OF]--> `concept.face_down_drawn_card`
- rule_ref: `121.8`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical. The rule describes a specific scenario (card draw during spell/ability casting) that results in a face-down drawn card, which is more accurately a 'MODIFIES' or 'OCCURS_IN' relation.
- suggested type: `MODIFIES`

### ⚠️ `concept.class_card` --[CONTAINS]--> `concept.class_level_bar`
- rule_ref: `716.2a`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes the meaning of the level bar text, not a containment relationship.
- suggested type: `REFERENCES`

### ⚠️ `action.counter` --[MOVES_TO]--> `zone.graveyard`
- rule_ref: `701.5a`
- verdict: **suspicious**
- issue: The relation type MOVES_TO is not the best fit; the rule describes the result of countering a spell, not the action of countering itself moving to the graveyard.
- suggested type: `PATTERN_OF`

### ⚠️ `variant.emperor` --[USES]--> `concept.flanking_attack_rule`
- rule_ref: `809.3c`
- verdict: **suspicious**
- issue: The relation type 'USES' is non-canonical. The rule text shows the Emperor variant imposes a restriction on attacks, which is a property of the variant, not a direct 'uses' of the flanking attack rule.
- suggested type: `PATTERN_OF`

### ❌ `concept.spell_proposal` --[DEPENDS_ON]--> `concept.illegal_casting`
- rule_ref: `601.5`
- verdict: **wrong**
- issue: The rule describes that illegal casting is a consequence of a failed legality check after proposal, not that spell proposal depends on illegal casting. The relation direction is reversed or mischaracterized.

### ✅ `concept.permanent` --[REFERENCES]--> `concept.permanent_type`
- rule_ref: `110.4`
- verdict: **correct**

### ⚠️ `ability.linked` --[CONTAINS]--> `ability.triggered`
- rule_ref: `603.11`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes that linked abilities can include triggered abilities, but it's more of a 'PATTERN_OF' or 'INTERACTS_WITH' relationship rather than a containment hierarchy.
- suggested type: `PATTERN_OF`

### ⚠️ `designation.initiative` --[TRIGGERS]--> `keyword.venture_into_dungeon`
- rule_ref: `724.2`
- verdict: **suspicious**
- issue: TRIGGERS is not a canonical relation type, but the rule text supports that having the initiative triggers venturing into Undercity.
- suggested type: `TRIGGERS`

### ✅ `keyword.ingest` --[MOVES_TO]--> `zone.exile`
- rule_ref: `702.115a`
- verdict: **correct**

### ⚠️ `concept.plane` --[CONTAINS]--> `concept.planar_deck`
- rule_ref: `103.7`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes the planar deck containing plane cards, but the source is 'concept.plane' (the card type) and the target is 'concept.planar_deck' (the deck). This is backwards for CONTAINS (the deck contains the cards, not the card type contains the deck). A better type would be OCCURS_IN (plane cards occur in a planar deck) or PATTERN_OF (plane cards are a pattern found in planar decks).
- suggested type: `OCCURS_IN`

### ⚠️ `action.drafting` --[MAY_CONTAIN]--> `action.face_up_draft`
- rule_ref: `905.2c`
- verdict: **suspicious**
- issue: MAY_CONTAIN is not a canonical relation type. The rule describes a specific variant of drafting (face up) that can occur within the general drafting action.
- suggested type: `PATTERN_OF`

### ⚠️ `subtype.role` --[INTERACTS_WITH]--> `state.attachment`
- rule_ref: `303.7a`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a state-based action triggered by multiple Roles, which is a PATTERN_OF relation (Roles trigger a specific state-based action).
- suggested type: `PATTERN_OF`

### ⚠️ `keyword.protection` --[INTERACTS_WITH]--> `concept.state_based_action`
- rule_ref: `702.16c`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too broad; the rule text specifically describes protection causing auras to be put into graveyards via a state-based action, which is better captured by DEPENDS_ON or MODIFIES.
- suggested type: `DEPENDS_ON`

### ✅ `concept.toughness` --[REFERENCES]--> `concept.base_toughness`
- rule_ref: `208.4`
- verdict: **correct**

### ❌ `concept.merged_permanent` --[INTERACTS_WITH]--> `concept.illegal_action`
- rule_ref: `728.3`
- verdict: **wrong**
- issue: Rule text describes zone change for merged permanents, not illegal actions or interactions.

### ✅ `concept.zone_change_trigger` --[REFERENCES]--> `zone.stack`
- rule_ref: `603.6`
- verdict: **correct**

### ⚠️ `concept.card_rarity` --[INDICATES]--> `concept.expansion_symbol`
- rule_ref: `206.2`
- verdict: **suspicious**
- issue: INDICATES is not a canonical relation type, but the rule text clearly states that expansion symbol color indicates rarity.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.deck` --[PATTERN_OF]--> `concept.constructed_play`
- rule_ref: `100.2a`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not one of the 8 canonical types. The rule describes Constructed play as a pattern that involves decks, but the canonical type should be OCCURS_IN or MODIFIES.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.ability` --[CREATES]--> `zone.exile`
- rule_ref: `406.6`
- verdict: **suspicious**
- issue: Type CREATES is non-canonical; the relation is about an ability exiling cards to a zone, which fits OCCURS_IN or MOVES_TO.
- suggested type: `MOVES_TO`

### ✅ `keyword.ripple` --[DEPENDS_ON]--> `zone.stack`
- rule_ref: `702.60a`
- verdict: **correct**

### ✅ `mechanic.splicing` --[PATTERN_OF]--> `effect.text_changing`
- rule_ref: `612.10`
- verdict: **correct**

### ✅ `concept.game` --[CONTAINS]--> `concept.deck`
- rule_ref: `100.2`
- verdict: **correct**

### ❌ `mechanic_pattern.day_night_transform` --[OCCURS_IN]--> `action.transform`
- rule_ref: `702.145c, 702.145f`
- verdict: **wrong**
- issue: Rule text not found; cannot verify relation without source text.

### ✅ `layer.layer_7` --[CONTAINS]--> `layer.layer_7d`
- rule_ref: `613.4d`
- verdict: **correct**

### ❌ `concept.face_down_permanent` --[CONTAINS]--> `concept.differentiating_face_downs`
- rule_ref: `708.6`
- verdict: **wrong**
- issue: The rule text describes a requirement for players to differentiate multiple face-down permanents, not that a face-down permanent contains the concept of differentiating face-downs. The relation is reversed or mischaracterized.

### ⚠️ `concept.replacement_effect` --[IS_PATTERN_OF]--> `concept.enter_battlefield_replacement`
- rule_ref: `614.1c`
- verdict: **suspicious**
- issue: Type IS_PATTERN_OF is non-canonical; the relation is a valid pattern-of relation but should use canonical PATTERN_OF.
- suggested type: `PATTERN_OF`

### ✅ `concept.battle_protector` --[DEPENDS_ON]--> `concept.battle_type`
- rule_ref: `310.8a`
- verdict: **correct**

### ✅ `cardtype.sorcery` --[REFERENCES]--> `concept.spell_type`
- rule_ref: `307.3`
- verdict: **correct**

### ⚠️ `concept.counter_placement` --[CONTAINS]--> `concept.counter`
- rule_ref: `122.6`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes what 'placing counters' refers to, not that it contains counters as components.
- suggested type: `REFERENCES`

### ⚠️ `concept.range_of_influence` --[MODIFIES]--> `mechanic.replacement_effect`
- rule_ref: `801.13`
- verdict: **suspicious**
- issue: The rule text describes that the limited range of influence option can modify events, but the relation type MODIFIES is not the best fit; it's more about limitation or interaction.
- suggested type: `INTERACTS_WITH`

### ❌ `keyword.unearth` --[DEPENDS_ON]--> `keyword.unearth`
- rule_ref: `702.84a`
- verdict: **wrong**
- issue: The relation is self-referential (source and target are identical) and does not represent a meaningful dependency; the rule text describes the ability's effect, not a dependency on itself.

### ✅ `keyword.disguise` --[DEPENDS_ON]--> `action.special_action`
- rule_ref: `702.168d`
- verdict: **correct**

### ⚠️ `action.conspiracy_face_up` --[IS_TYPE_OF]--> `concept.special_action`
- rule_ref: `116.2j`
- verdict: **suspicious**
- issue: IS_TYPE_OF is not a canonical relation type, but the rule text supports that turning a conspiracy face up is a special action.
- suggested type: `IS_TYPE_OF`

### ⚠️ `keyword.impending` --[USES]--> `concept.time_counter`
- rule_ref: `702.176a`
- verdict: **suspicious**
- issue: Type 'USES' is non-canonical, but the rule text clearly shows the keyword involves time counters.
- suggested type: `INTERACTS_WITH`

### ✅ `concept.cloaked_permanent` --[INTERACTS_WITH]--> `keyword.disguise`
- rule_ref: `701.56d`
- verdict: **correct**

### ⚠️ `concept.sticker` --[CREATES]--> `concept.stickered_object`
- rule_ref: `123.4`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type; the underlying relation is that a sticker being on an object defines that object as stickered, which fits MODIFIES or PATTERN_OF better.
- suggested type: `MODIFIES`

### ⚠️ `keyword.lifelink` --[CAUSES]--> `concept.life_gain`
- rule_ref: `702.15b`
- verdict: **suspicious**
- issue: Type 'CAUSES' is non-canonical, but the relation is real.
- suggested type: `INTERACTS_WITH`

### ✅ `keyword.phasing` --[PATTERN_OF]--> `mechanic.indirect_phasing`
- rule_ref: `702.26g`
- verdict: **correct**

### ⚠️ `concept.state_based_action` --[ENFORCES]--> `concept.counter_cancellation`
- rule_ref: `704.5q`
- verdict: **suspicious**
- issue: ENFORCES is not a canonical relation type; the rule describes a state-based action performing counter cancellation.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.draw_replacement` --[INTERACTS_WITH]--> `concept.card_draw`
- rule_ref: `121.6a`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a specific dependency where the replacement effect applies regardless of the target's feasibility.
- suggested type: `DEPENDS_ON`

### ⚠️ `concept.permanent` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `110.2a`
- verdict: **suspicious**
- issue: The rule describes a permanent entering the battlefield, but MOVES_TO implies a transition from one zone to another, which is not explicitly stated here. The rule focuses on control upon entry, not the movement itself.
- suggested type: `OCCURS_IN`

### ✅ `concept.case_card` --[CONTAINS]--> `concept.case_solve_ability`
- rule_ref: `719.3a`
- verdict: **correct**

### ⚠️ `keyword.devour` --[CREATES]--> `counter.plus_one_plus_one`
- rule_ref: `702.82a`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type; the underlying relation is real but should be expressed with a canonical type.
- suggested type: `MODIFIES`

### ⚠️ `concept.creature_enters_attacking` --[BECOMES_NEVER]--> `concept.attacking_creature`
- rule_ref: `506.3b`
- verdict: **suspicious**
- issue: Type 'BECOMES_NEVER' is non-canonical; the rule describes a scenario where a creature entering attacking fails to become an attacking creature.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.outlaw` --[INTERACTS_WITH]--> `concept.crime`
- rule_ref: `700.12a`
- verdict: **suspicious**
- issue: The rule text does not mention 'Crime' at all, so INTERACTS_WITH is not directly supported. The relation might be better as PATTERN_OF or REFERENCES if the connection is thematic, but the given rule only defines what counts as an outlaw for effects.

### ✅ `concept.spell_proposal` --[OCCURS_IN]--> `concept.targeting`
- rule_ref: `601.2c`
- verdict: **correct**

### ⚠️ `action.turn_based` --[OCCURS_BEFORE]--> `concept.state_based_action`
- rule_ref: `703.3`
- verdict: **suspicious**
- issue: OCCURS_BEFORE is not a canonical relation type, but the rule text clearly indicates a temporal ordering.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.expend` --[PATTERN_OF]--> `concept.event`
- rule_ref: `700.14`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical, but the rule text describes how the 'expend' mechanic is defined based on cumulative mana spending events.
- suggested type: `DEPENDS_ON`

### ⚠️ `keyword.equip` --[PATTERN_OF]--> `concept.equipment`
- rule_ref: `702.6`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical, but the rule text indicates Equip is the defining ability of Equipment cards.
- suggested type: `REFERENCES`

### ✅ `effect.self_replacement` --[PATTERN_OF]--> `effect.replacement`
- rule_ref: `614.15`
- verdict: **correct**

### ✅ `keyword.omen` --[REFERENCES]--> `concept.card_name`
- rule_ref: `720.5`
- verdict: **correct**

### ❌ `concept.skipping` --[MODIFIES]--> `phase.combat`
- rule_ref: `506.1`
- verdict: **wrong**
- issue: The rule text describes the structure of the combat phase and conditions for skipping steps, but does not mention effects causing the entire combat phase to be skipped.

### ⚠️ `keyword.partner` --[OCCURS_IN]--> `zone.commander`
- rule_ref: `702.124`
- verdict: **suspicious**
- issue: The rule text provided is insufficient to verify the relation; it only states the keyword name without context. However, the description suggests the relation is about deck construction and starting location, which might be better as MODIFIES or REFERENCES rather than OCCURS_IN.
- suggested type: `MODIFIES`

### ✅ `keyword.plot` --[DEPENDS_ON]--> `action.special_action`
- rule_ref: `702.170b`
- verdict: **correct**

### ✅ `multiplayer_variant.shared_team_turns` --[CONTAINS]--> `multiplayer_mechanic.combined_attack`
- rule_ref: `805.10b`
- verdict: **correct**

### ⚠️ `concept.total_cost` --[MODIFIES]--> `concept.cost_modification`
- rule_ref: `601.2f`
- verdict: **suspicious**
- issue: The relation direction is reversed; total_cost is determined by applying cost_modifications, so cost_modification MODIFIES total_cost, not the other way around.
- suggested type: `MODIFIES`

### ⚠️ `concept.response` --[STACKS_ABOVE]--> `concept.stack`
- rule_ref: `117.7`
- verdict: **suspicious**
- issue: STACKS_ABOVE is not a canonical relation type, but the rule text supports a directional ordering relation.
- suggested type: `OCCURS_IN`

### ✅ `concept.team_poison_status` --[OCCURS_IN]--> `keyword.two_headed_giant`
- rule_ref: `810.10d`
- verdict: **correct**

### ✅ `concept.team` --[CONTAINS]--> `concept.player`
- rule_ref: `102.3`
- verdict: **correct**

### ✅ `keyword.offering` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.48a`
- verdict: **correct**

### ⚠️ `keyword.saddle` --[CREATES]--> `designation.saddled`
- rule_ref: `702.171a`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type; the relation is real but type should be canonical.
- suggested type: `MODIFIES`

### ✅ `concept.deck` --[PATTERN_OF]--> `concept.limited_play`
- rule_ref: `100.2b`
- verdict: **correct**

### ✅ `phase.combat` --[CONTAINS]--> `step.combat_damage`
- rule_ref: `506.1`
- verdict: **correct**

### ⚠️ `subtype.vehicle` --[INTERACTS_WITH]--> `card_type.creature`
- rule_ref: `301.7`
- verdict: **suspicious**
- issue: INTERACTS_WITH is not the best canonical type; the relation is more about a conditional transformation (Vehicle becomes a Creature) rather than a general interaction.
- suggested type: `MOVES_TO`

### ❌ `step.cleanup` --[MODIFIES]--> `concept.pseudoblocking`
- rule_ref: `509.4a`
- verdict: **wrong**
- issue: The rule text describes conditions under which a creature put onto the battlefield blocking is NOT considered a blocking creature, but it does not state that the cleanup step modifies this concept. The relation is unsupported.

### ⚠️ `concept.copy` --[CONTAINS]--> `concept.card_type`
- rule_ref: `205.2c`
- verdict: **suspicious**
- issue: The relation type CONTAINS implies a compositional or ownership relationship, but the rule states that copies 'have' card types in the sense of possessing them as attributes, not containing them as parts. A more fitting canonical type might be MODIFIES or PATTERN_OF, but neither perfectly captures 'has attribute'.
- suggested type: `MODIFIES`

### ⚠️ `concept.ability` --[GENERATES]--> `concept.one_shot_effect`
- rule_ref: `113.2d`
- verdict: **suspicious**
- issue: GENERATES is not a canonical relation type, but the rule text supports that abilities produce one-shot effects.
- suggested type: `CONTAINS`

### ✅ `keyword.phasing` --[MODIFIES]--> `phase.untap`
- rule_ref: `702.26a`
- verdict: **correct**

### ✅ `concept.token` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `111.1`
- verdict: **correct**

### ✅ `concept.color_indicator` --[REFERENCES]--> `concept.color`
- rule_ref: `204.2`
- verdict: **correct**

### ⚠️ `cardtype.dungeon` --[PATTERN_OF]--> `keyword.venture_into_dungeon`
- rule_ref: `309.5`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical and does not accurately describe the relationship. The rule text indicates that the keyword action is used to interact with the dungeon card type, which is better described as a dependency or interaction.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.sorcery_timing` --[DEPENDS_ON]--> `zone.stack`
- rule_ref: `307.5`
- verdict: **suspicious**
- issue: The relation is real but DEPENDS_ON is not the best fit; the rule states that sorcery timing requires the stack to be empty, which is more accurately a condition or constraint (OCCURS_IN or PATTERN_OF).
- suggested type: `OCCURS_IN`

### ❌ `concept.combat_damage_step` --[OCCURS_IN]--> `step.end_of_combat`
- rule_ref: `510.4`
- verdict: **wrong**
- issue: The rule text describes the combat damage step(s) occurring before the end of combat step, not within it. OCCURS_IN implies containment, but steps are sequential, not nested.

### ❌ `concept.game` --[CONTAINS]--> `concept.player`
- rule_ref: `102.1`
- verdict: **wrong**
- issue: Rule text defines 'player' but does not state that a game contains players; it's a definition, not a containment relation.

### ❌ `action.look_at` --[DEPENDS_ON]--> `concept.consolation_controller`
- rule_ref: `315.7`
- verdict: **wrong**
- issue: The rule text describes who can look at face-down conspiracy cards, but does not establish that the action 'look_at' depends on the concept 'conspiracy_controller'. The relation is about permission, not dependency.

### ⚠️ `property.owner` --[EQUALS]--> `property.controller`
- rule_ref: `905.5`
- verdict: **suspicious**
- issue: EQUALS is not a canonical relation type; the underlying relation is that controller equals owner for conspiracy cards.
- suggested type: `REFERENCES`

### ✅ `role.emperor` --[DEPENDS_ON]--> `concept.team_win_loss`
- rule_ref: `809.5a`
- verdict: **correct**

### ⚠️ `card_type.phenomenon` --[RESIDES_IN]--> `zone.command_zone`
- rule_ref: `901.4`
- verdict: **suspicious**
- issue: RESIDES_IN is not a canonical relation type, but the rule text clearly states that phenomenon cards remain in the command zone.
- suggested type: `OCCURS_IN`

### ❌ `concept.token` --[CONTAINS]--> `concept.permanent_owner`
- rule_ref: `111.2`
- verdict: **wrong**
- issue: The relation type CONTAINS is inappropriate; the rule describes ownership assignment, not containment.

### ✅ `keyword.ingest` --[REFERENCES]--> `zone.library`
- rule_ref: `702.115a`
- verdict: **correct**

### ⚠️ `concept.front_face` --[ATTRIBUTE_OF]--> `concept.double_faced_card`
- rule_ref: `712.8`
- verdict: **suspicious**
- issue: ATTRIBUTE_OF is not a canonical relation type, but the rule text supports that a front face is a characteristic attribute of a double-faced card.
- suggested type: `CONTAINS`

### ⚠️ `effect.restriction` --[MUST_NOT_VIOLATE]--> `effect.requirement`
- rule_ref: `508.1d`
- verdict: **suspicious**
- issue: MUST_NOT_VIOLATE is not a canonical relation type, but the rule text supports a constraint relationship between restrictions and requirements.
- suggested type: `INTERACTS_WITH`

### ❌ `keyword.graft` --[INTERACTS_WITH]--> `keyword.bloodthirst`
- rule_ref: `702.54a`
- verdict: **wrong**
- issue: The rule text for Bloodthirst does not mention Graft at all, and there is no interaction described between the two keywords.

### ✅ `keyword.omen` --[MOVES_TO]--> `zone.library`
- rule_ref: `720.3d`
- verdict: **correct**

### ⚠️ `concept.creature_battlefield_attacking` --[INTERACTS_WITH]--> `concept.attacking_player`
- rule_ref: `508.4`
- verdict: **suspicious**
- issue: The relation is real but INTERACTS_WITH is too broad; the rule describes a dependency where the attacking player is chosen by the creature's controller.
- suggested type: `DEPENDS_ON`

### ⚠️ `action.turn_based` --[OCCURS_BEFORE]--> `concept.priority`
- rule_ref: `703.3`
- verdict: **suspicious**
- issue: OCCURS_BEFORE is not a canonical relation type, but the rule text supports a temporal ordering between turn-based actions and priority.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.card_draw` --[MODIFIES]--> `concept.draw_replacement`
- rule_ref: `121.6`
- verdict: **suspicious**
- issue: The type MODIFIES is not the best canonical fit; the relation is more accurately PATTERN_OF (a pattern of draw replacement) or REFERENCES.
- suggested type: `PATTERN_OF`

### ⚠️ `zone.stack` --[IS_TYPE]--> `zone.public`
- rule_ref: `400.2`
- verdict: **suspicious**
- issue: IS_TYPE is not a canonical relation type; the rule states Stack is a public zone, which is a subtype relationship.
- suggested type: `CONTAINS`

### ❌ `keyword.cascade` --[CONTAINS]--> `keyword.cascade`
- rule_ref: `702.85c`
- verdict: **wrong**
- issue: The relation is self-referential (source and target are identical) and does not represent a CONTAINS relation; the rule text describes separate triggers for multiple instances, not containment.

### ⚠️ `keyword.escape` --[USES]--> `cost.alternative`
- rule_ref: `702.138a`
- verdict: **suspicious**
- issue: USES is not a canonical relation type, but the rule text supports that Escape involves an alternative cost.
- suggested type: `MODIFIES`

### ⚠️ `zone.ante` --[IS_TYPE]--> `zone.public`
- rule_ref: `400.2`
- verdict: **suspicious**
- issue: Type 'IS_TYPE' is non-canonical; the relation is that ante is a subtype of public zone.
- suggested type: `CONTAINS`

### ✅ `concept.case_solved_ability` --[DEPENDS_ON]--> `concept.solved_designation`
- rule_ref: `719.3c`
- verdict: **correct**

### ✅ `action.shuffle` --[MODIFIES]--> `zone.library`
- rule_ref: `701.20`
- verdict: **correct**

### ⚠️ `concept.speed` --[INCREASES_BY]--> `concept.speed`
- rule_ref: `702.179d`
- verdict: **suspicious**
- issue: INCREASES_BY is not a canonical relation type; the rule describes a self-modification event.
- suggested type: `MODIFIES`

### ⚠️ `symbol.chaos` --[INTERACTS_WITH]--> `mechanic.planeswalking_ability`
- rule_ref: `901.9b`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is not the best fit; the chaos symbol triggers or activates the planeswalking ability, which is more like MODIFIES or OCCURS_IN.
- suggested type: `MODIFIES`

### ✅ `keyword.undying` --[REFERENCES]--> `counter.plus_one_plus_one`
- rule_ref: `702.93a`
- verdict: **correct**

### ❌ `concept.mana_value` --[DEPENDS_ON]--> `concept.phyrexian_mana_symbol`
- rule_ref: `202.3g`
- verdict: **wrong**
- issue: The relation direction is reversed; mana value depends on Phyrexian mana symbols, not the other way around.

### ⚠️ `concept.traditional_magic_card` --[REFERENCES]--> `concept.card_ownership`
- rule_ref: `108.3`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule text describes how card ownership is determined for traditional cards, which is more of a DEPENDS_ON or MODIFIES relationship.
- suggested type: `DEPENDS_ON`
