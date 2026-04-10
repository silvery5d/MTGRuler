# MTGRuler Extraction Validation Report

- Model: `deepseek-chat`
- Sample size: 300 concepts, 300 relations
- Seed: 42
- Generated: 2026-04-10 01:07:14

## Summary

- **Concepts**: correct=179/300 (60%), suspicious=104, wrong=17
- **Relations**: correct=125/300 (42%), suspicious=125, wrong=50

## Concept validation

### ⚠️ `keyword.demonstrate` — Demonstrate (Keyword)
- rule_ref: `702.144`
- verdict: **suspicious**
- issue: Definition oversimplifies; misses 'you may copy it and choose new targets' and the opponent's copy aspect.
- suggested fix: Definition should be: 'A triggered ability on a spell meaning "When you cast this spell, you may copy it and choose new targets for the copy. If you copy the spell, choose an opponent. That player copies the spell and may choose new targets for that copy."'

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
- issue: Definition is incomplete; it omits Auras, Fortifications, and cases where the attached card leaves the battlefield or the object leaves the zone.
- suggested fix: Update definition to include Auras and Fortifications, and clarify that 'becoming unattached' includes cases where the attached card leaves the battlefield, the object leaves the zone, or the player leaves the game.

### ⚠️ `game_option.limited_range_of_influence` — Limited Range of Influence (Concept)
- rule_ref: `801`
- verdict: **suspicious**
- issue: Definition is inferred/extrapolated beyond the source text.
- suggested fix: Definition should be based solely on the provided source text, e.g., 'A multiplayer option.'

### ✅ `action.incubate` — Incubate (Action)
- rule_ref: `701.51a`
- verdict: **correct**

### ❌ `concept.attacking` — Attacking (Action)
- rule_ref: `508.1`
- verdict: **wrong**
- issue: Type mismatch: 'Attacking' is not an Action but a state/status of creatures.
- suggested fix: Change type to Concept or MechanicPattern, and adjust definition to reflect that attacking is a status creatures gain during combat.

### ⚠️ `concept.win_the_game` — Win the Game (MechanicPattern)
- rule_ref: `104.2`
- verdict: **suspicious**
- issue: Definition is overly broad; source text lists specific ways to win, not just 'the condition'.
- suggested fix: Definition could be: 'A state or effect that ends the game with a player or team as the victor, as described in rule 104.2.'

### ✅ `concept.effect_reference_by_name` — Effect Reference by Name (Concept)
- rule_ref: `707.11`
- verdict: **correct**

### ⚠️ `concept.passing_priority` — Passing Priority (Concept)
- rule_ref: `117.4`
- verdict: **suspicious**
- issue: Definition is a description of the action, but the source rule text describes the consequence of all players passing.
- suggested fix: Definition should more directly reflect the rule text: 'When all players pass in succession, the top object on the stack resolves or, if the stack is empty, the phase or step ends.'

### ⚠️ `concept.card_ownership` — Card Ownership (Concept)
- rule_ref: `108.3`
- verdict: **suspicious**
- issue: definition omits sideboard case and planar deck special case
- suggested fix: The player who started the game with a card in their deck, sideboard, or command zone, or who brought it into the game from outside the game. In a Planechase game with a single planar deck, the planar controller owns those cards.

### ✅ `concept.poison_counter` — Poison Counter (Concept)
- rule_ref: `104.3d`
- verdict: **correct**

### ⚠️ `game.two_headed_giant` — Two-Headed Giant Variant (Concept)
- rule_ref: `704.6`
- verdict: **suspicious**
- issue: Definition mentions 'teams share life total and poison counters' which is not in the source rule text; source only describes losing conditions.
- suggested fix: Definition should focus on state-based actions for losing conditions (0 or less life, 15+ poison) as per 704.6a and 704.6b.

### ✅ `ability.activated_mana` — Activated Mana Ability (Concept)
- rule_ref: `605.1a`
- verdict: **correct**

### ✅ `concept.removed_from_combat` — Removed from Combat (Concept)
- rule_ref: `511.3`
- verdict: **correct**

### ✅ `concept.rarity_letter` — Rarity Letter (Concept)
- rule_ref: `213.1b`
- verdict: **correct**

### ✅ `mechanic.bestowed_aura` — Bestowed Aura (MechanicPattern)
- rule_ref: `702.103b`
- verdict: **correct**

### ⚠️ `subtype.equipment` — Equipment (CardType)
- rule_ref: `301.5`
- verdict: **suspicious**
- issue: Equipment is a subtype, not a card type.
- suggested fix: Change type from 'CardType' to 'Subtype'.

### ✅ `concept.instruction_order` — Instruction Order (Concept)
- rule_ref: `608.2c`
- verdict: **correct**

### ✅ `concept.snow_mana` — Snow Mana (Concept)
- rule_ref: `107.4h`
- verdict: **correct**

### ⚠️ `concept.variant.planechase` — Planechase Variant (Concept)
- rule_ref: `103.7`
- verdict: **suspicious**
- issue: Definition is too broad and not directly supported by the provided rule text.
- suggested fix: Definition should reference the specific setup action described, e.g., 'A variant where players use planar decks; the starting player reveals cards from their deck until a plane card is found to become the starting plane.'

### ⚠️ `concept.zone_restriction_ability` — Zone Restriction Ability (Concept)
- rule_ref: `113.6e`
- verdict: **suspicious**
- issue: definition omits the distinction between the ability itself and an ability that grants such an ability, and the 'functioning in zones where it could be played' is incomplete without mentioning the stack.
- suggested fix: An ability that restricts or modifies how its object can be played or cast functions in any zone from which it could be played or cast and also on the stack. An ability that grants such an ability functions only on the stack.

### ⚠️ `action.transform` — Transform (Action)
- rule_ref: `701.28`
- verdict: **suspicious**
- issue: definition omits 'permanents represented by transforming double-faced cards' and includes 'double-faced cards' without 'transforming' qualifier
- suggested fix: definition should be: To turn a permanent over so that its other face is up. Only transforming tokens and permanents represented by transforming double-faced cards can transform.

### ✅ `multiplayer_mechanic.combined_attack` — Combined Attack (Concept)
- rule_ref: `805.10b`
- verdict: **correct**

### ✅ `mechanic.linked_word_choice` — Linked Word Choice (MechanicPattern)
- rule_ref: `607.2f`
- verdict: **correct**

### ⚠️ `keyword.monstrosity` — Monstrosity (Keyword)
- rule_ref: `701.31`
- verdict: **suspicious**
- issue: Definition omits the 'N' parameter and slightly misstates the condition.
- suggested fix: Definition should be: 'If this permanent isn't monstrous, put N +1/+1 counters on it and it becomes monstrous. Monstrous is a designation marker.'

### ✅ `concept.consolation_owner` — Conspiracy Card Owner (Concept)
- rule_ref: `315.6`
- verdict: **correct**

### ✅ `concept.continuous_effect_duration` — Continuous Effect Duration (Concept)
- rule_ref: `800.4m`
- verdict: **correct**

### ✅ `variant.super_villain_rumble` — Supervillain Rumble (Variant)
- rule_ref: `904.12`
- verdict: **correct**

### ✅ `concept.new_targets_for_copy` — New Targets for Copy (Concept)
- rule_ref: `707.10c`
- verdict: **correct**

### ⚠️ `concept.copiable_values_on_reveal` — Copiable Values on Reveal (Concept)
- rule_ref: `708.8`
- verdict: **suspicious**
- issue: Definition omits important details about abilities relating to entering the battlefield.
- suggested fix: When a face-down permanent is turned face up, its copiable values revert to normal, applied effects still apply, and abilities relating to entering the battlefield don't trigger or have effect.

### ✅ `keyword.goad` — Goad (Keyword)
- rule_ref: `701.38`
- verdict: **correct**

### ✅ `keyword.undaunted` — Undaunted (Keyword)
- rule_ref: `702.125`
- verdict: **correct**

### ✅ `rule.world_rule` — World Rule (MechanicPattern)
- rule_ref: `704.5k`
- verdict: **correct**

### ✅ `concept.activation_cost` — Activation Cost (Concept)
- rule_ref: `602.1a`
- verdict: **correct**

### ⚠️ `concept.variant.conspiracy_draft` — Conspiracy Draft Variant (Concept)
- rule_ref: `103.2e`
- verdict: **suspicious**
- issue: Definition is slightly off; the source rule says players put conspiracy cards from their sideboard into the command zone, not that the variant uses conspiracy cards placed in the command zone.
- suggested fix: A draft variant where each player may put any number of conspiracy cards from their sideboard into the command zone.

### ⚠️ `concept.casual_play` — Casual play (Concept)
- rule_ref: `100.7`
- verdict: **suspicious**
- issue: Definition is slightly off; source text describes cards intended for casual play, not the concept of casual play itself.
- suggested fix: Definition should focus on the cards: 'Cards intended for non-tournament play, which may have features and text not covered by the standard rules, such as silver-bordered cards, acorn-stamped cards, and playtest cards.'

### ✅ `keyword.multi_headed_giant` — Multi-Headed Giant Variants (Variant)
- rule_ref: `810.11`
- verdict: **correct**

### ✅ `zone.hidden` — Hidden Zone (Concept)
- rule_ref: `400.2`
- verdict: **correct**

### ✅ `concept.regeneration` — Regeneration (MechanicPattern)
- rule_ref: `614.8`
- verdict: **correct**

### ⚠️ `concept.ownership` — Ownership (Concept)
- rule_ref: `112.2`
- verdict: **suspicious**
- issue: Definition is incomplete and slightly misleading. It only mentions 'card or spell' and 'card's owner unless it is a copy', but the source text details ownership rules for spells (including copies) and introduces the concept of a spell's controller.
- suggested fix: Refine definition to: 'The player who owns a card or spell. For a spell, this is the owner of the card that represents it, unless it is a copy. The owner of a copy is the player who created it. A spell's controller is separate from its owner.'

### ✅ `concept.control_of_copy` — Control of Copy (Concept)
- rule_ref: `707.10`
- verdict: **correct**

### ⚠️ `keyword.sunburst` — Sunburst (Keyword)
- rule_ref: `702.44`
- verdict: **suspicious**
- issue: Definition omits key conditions: only works from stack, only if colored mana spent, and only as object enters battlefield.
- suggested fix: Static ability that functions as an object enters the battlefield from the stack, placing +1/+1 counters (on creatures) or charge counters (on noncreatures) based on the number of colors of mana spent to cast it, but only if colored mana was spent.

### ✅ `concept.front_face_symbol` — Front-Face Symbol (Concept)
- rule_ref: `712.2a`
- verdict: **correct**

### ⚠️ `concept.split_card` — Split Card (CardType)
- rule_ref: `709.1`
- verdict: **suspicious**
- issue: Definition includes 'each half can be cast separately' which is not stated in the given source rule text.
- suggested fix: Definition should be limited to: 'A card with two card faces on a single card.'

### ✅ `concept.teammate` — Teammate (Concept)
- rule_ref: `102.3`
- verdict: **correct**

### ⚠️ `keyword.start_your_engines` — Start Your Engines! (Keyword)
- rule_ref: `702.179`
- verdict: **suspicious**
- issue: Definition omits state-based action nature and includes inherent triggered ability which is separate.
- suggested fix: Definition should state: 'A static ability that, if a player controls a permanent with it and has no speed, sets that player's speed to 1 as a state-based action.'

### ✅ `concept.loyalty_symbol` — Loyalty Symbol (Concept)
- rule_ref: `107.7`
- verdict: **correct**

### ✅ `keyword.afterlife` — Afterlife (Keyword)
- rule_ref: `702.135`
- verdict: **correct**

### ✅ `designation.monstrous` — Monstrous (Concept)
- rule_ref: `701.31b`
- verdict: **correct**

### ✅ `randomization.doubles` — Doubles (Concept)
- rule_ref: `706.5`
- verdict: **correct**

### ⚠️ `concept.legal_target` — Legal Target (Concept)
- rule_ref: `608.2b`
- verdict: **suspicious**
- issue: Definition is incomplete; it omits that a target can become illegal due to changes in characteristics or text, not just zone changes.
- suggested fix: Update definition to: A target that remains in the zone it was in when targeted, remains valid according to the spell or ability's targeting restrictions, and has not become illegal due to changes in characteristics or effects.

### ✅ `concept.party` — Party (Concept)
- rule_ref: `700.8`
- verdict: **correct**

### ⚠️ `concept.alternate_name` — Alternate Name (Secondary Title) (Concept)
- rule_ref: `201.6`
- verdict: **suspicious**
- issue: Definition oversimplifies and slightly misstates the relationship between the alternate name and the Oracle name.
- suggested fix: Clarify that the alternate name is displayed in the upper left, the Oracle name is in the secondary title bar, and for all game purposes, the card has only the Oracle name. The alternate name in rules text refers to the Oracle name.

### ✅ `concept.life_gain_event` — Life Gain Event (Concept)
- rule_ref: `119.9`
- verdict: **correct**

### ⚠️ `concept.ability_removal` — Ability Removal (Concept)
- rule_ref: `113.10b`
- verdict: **suspicious**
- issue: Definition adds 'stated as the object "losing" that ability' which is not in the source text.
- suggested fix: Definition should be: 'Effects that remove an ability remove all instances of it.'

### ⚠️ `action.time_travel` — Time Travel (Action)
- rule_ref: `701.54a`
- verdict: **suspicious**
- issue: definition omits 'any number' and 'you control/you own' restrictions
- suggested fix: definition should be: To choose any number of permanents you control with time counters and/or suspended cards you own in exile with time counters, and for each, add or remove a time counter.

### ✅ `keyword.surge` — Surge (Keyword)
- rule_ref: `702.117`
- verdict: **correct**

### ✅ `concept.total_toxic_value` — Total Toxic Value (Concept)
- rule_ref: `702.164b`
- verdict: **correct**

### ✅ `action.fateseal` — Fateseal (Action)
- rule_ref: `701.22`
- verdict: **correct**

### ⚠️ `keyword.devour` — Devour (Keyword)
- rule_ref: `702.82`
- verdict: **suspicious**
- issue: definition omits the 'N' parameter and the optional quality variant
- suggested fix: definition should be: 'Devour is a static ability. "Devour N" means "As this object enters, you may sacrifice any number of creatures. This permanent enters with N +1/+1 counters on it for each creature sacrificed this way."'

### ✅ `concept.permanent_card` — Permanent Card (Concept)
- rule_ref: `110.4a`
- verdict: **correct**

### ✅ `concept.lit_up_numbers` — Lit-Up Numbers (Concept)
- rule_ref: `717.1`
- verdict: **correct**

### ✅ `keyword.connive` — Connive (Keyword)
- rule_ref: `701.47`
- verdict: **correct**

### ⚠️ `concept.life_loss` — Life Loss (Concept)
- rule_ref: `119.3`
- verdict: **suspicious**
- issue: Definition adds 'typically from damage' which is not in the source rule text.
- suggested fix: Definition should be: 'A reduction in a player's life total, as caused by an effect.'

### ⚠️ `concept.timing_priority` — Timing and Priority (Concept)
- rule_ref: `117`
- verdict: **suspicious**
- issue: Definition is inferred/expanded beyond the source text, which only provides the concept name.
- suggested fix: Definition should be more directly based on the source, e.g., 'The rules for when players can cast spells and activate abilities, centered on the concept of priority.'

### ⚠️ `action.planeswalk` — Planeswalk (Action)
- rule_ref: `701.24`
- verdict: **suspicious**
- issue: definition omits key details: only in Planechase, only planar controller, and specifics about moving cards.
- suggested fix: definition should include: 'In a Planechase game, the planar controller puts each face-up plane/phenomenon card on the bottom of its owner's planar deck face down, then moves the top card of their planar deck off and turns it face up.'

### ✅ `zone.battlefield` — Battlefield (Zone)
- rule_ref: `403.1`
- verdict: **correct**

### ✅ `phase.ending` — Ending Phase (Phase)
- rule_ref: `500.1`
- verdict: **correct**

### ⚠️ `card_type.scheme` — Scheme (CardType)
- rule_ref: `300.1`
- verdict: **suspicious**
- issue: Definition adds extra information not present in the source rule text.
- suggested fix: Definition should be a simple statement of the card type, e.g., 'A card type.'

### ✅ `zone.hand` — Hand (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ✅ `concept.battle_defense` — Battle Defense (Concept)
- rule_ref: `210.1`
- verdict: **correct**

### ⚠️ `mechanic.protector` — Protector (MechanicPattern)
- rule_ref: `310.10`
- verdict: **suspicious**
- issue: Definition is incomplete and partially inaccurate; it omits the state-based action and the graveyard outcome, and incorrectly states 'exiled'.
- suggested fix: Definition should describe the state-based action that chooses a protector if none exists or the current one is invalid, and the battle is put into its owner's graveyard if no player can be chosen.

### ⚠️ `concept.lose_the_game` — Lose the Game (MechanicPattern)
- rule_ref: `104.3`
- verdict: **suspicious**
- issue: Definition is overly broad; rule 104.3 lists specific ways to lose, not just 'the condition that eliminates'.
- suggested fix: Definition should reference the specific conditions listed in rule 104.3, such as life total 0 or less, drawing from empty library, etc.

### ⚠️ `concept.meld` — Meld (Action)
- rule_ref: `701.37`
- verdict: **suspicious**
- issue: Definition omits that meld is a keyword action and that the cards are put onto battlefield from their current zones.
- suggested fix: Meld is a keyword action that appears on one card in a meld pair. To meld, put the two cards from the pair onto the battlefield with their back faces combined into a single permanent.

### ❌ `cardtype.fortification` — Fortification (CardType)
- rule_ref: `702.67b`
- verdict: **wrong**
- issue: Definition is not supported by the source rule text; source only references another rule.
- suggested fix: Check rule 301 for the definition of Fortification.

### ✅ `concept.multiple_card_types` — Multiple Card Types (Concept)
- rule_ref: `300.2`
- verdict: **correct**

### ❌ `keyword.suspect` — Suspect (Keyword)
- rule_ref: `701.58`
- verdict: **wrong**
- issue: Definition incorrectly describes turning a creature face-down, which is not part of suspecting.
- suggested fix: Definition should state: 'A designation a permanent can have. A suspected permanent has menace and "This creature can't block" for as long as it's suspected.'

### ⚠️ `concept.variant.archenemy` — Archenemy Variant (Concept)
- rule_ref: `103.4e`
- verdict: **suspicious**
- issue: Definition includes schemes and higher life total, but source only mentions life total.
- suggested fix: Definition should focus on the life total rule, or reference the broader variant definition elsewhere.

### ✅ `multiplayer_variant.grand_melee` — Grand Melee (Variant)
- rule_ref: `807.1`
- verdict: **correct**

### ✅ `keyword.collect_evidence` — Collect Evidence (Keyword)
- rule_ref: `701.57`
- verdict: **correct**

### ✅ `keyword.endure` — Endure (Keyword)
- rule_ref: `701.62`
- verdict: **correct**

### ✅ `keyword.nightbound` — Nightbound (Keyword)
- rule_ref: `702.145e`
- verdict: **correct**

### ⚠️ `card_type.kindred` — Kindred (CardType)
- rule_ref: `300.1`
- verdict: **suspicious**
- issue: Definition adds details not present in source rule text.
- suggested fix: Definition should be a simple description like 'A card type.' or match the list-only nature of the source.

### ⚠️ `concept.flipping` — Flipping (MechanicPattern)
- rule_ref: `710.4`
- verdict: **suspicious**
- issue: Definition omits key details about memory of status when leaving battlefield.
- suggested fix: Add: 'If a flipped permanent leaves the battlefield, it retains no memory of its flipped status.'

### ⚠️ `variant.brawl` — Brawl (Variant)
- rule_ref: `903.12`
- verdict: **suspicious**
- issue: definition oversimplifies and omits key details like deck size, life totals, mulligan rule, and other modifications.
- suggested fix: A style of Commander game using Standard format cards where commanders can be legendary planeswalkers or legendary creatures, with a 60-card deck, specific starting life totals, and modified mulligan rules.

### ⚠️ `keyword.omen` — Omen (Keyword)
- rule_ref: `720.3d-720.5`
- verdict: **suspicious**
- issue: Definition incorrectly states Omen is a 'card type ability' and gives alternative characteristics; source only describes resolution effect.
- suggested fix: Definition should focus on resolution effect: 'As an Omen spell resolves, its controller shuffles it into its owner's library instead of putting it into the graveyard.'

### ✅ `layer.layer_6` — Layer 6 - Ability Adding/Removing (Concept)
- rule_ref: `613.1f`
- verdict: **correct**

### ✅ `concept.information_restriction` — Information Gathering Restriction (Concept)
- rule_ref: `801.11`
- verdict: **correct**

### ✅ `concept.shortcut` — Shortcut (Concept)
- rule_ref: `730.1`
- verdict: **correct**

### ✅ `concept.default_face_down_characteristics` — Default Face-Down Characteristics (Concept)
- rule_ref: `708.2a`
- verdict: **correct**

### ✅ `concept.transform` — Transform (Action)
- rule_ref: `701.28`
- verdict: **correct**

### ✅ `keyword.landwalk` — Landwalk (Keyword)
- rule_ref: `702.14`
- verdict: **correct**

### ❌ `concept.aura` — Aura (CardType)
- rule_ref: `702.5b`
- verdict: **wrong**
- issue: Definition is not derived from the given source rule text; source only references another rule.
- suggested fix: Definition should be based on rule 303, not rule 702.5b.

### ⚠️ `card_type.lesson` — Lesson (CardType)
- rule_ref: `701.45a`
- verdict: **suspicious**
- issue: Definition incorrectly states Lesson is a card type found in the Sideboard; source rule says 'Lesson card you own from outside the game'.
- suggested fix: Change definition to: A card subtype that can be revealed from outside the game and put into your hand via the Learn keyword action.

### ✅ `concept.constructed_play` — Constructed play (MechanicPattern)
- rule_ref: `100.2a`
- verdict: **correct**

### ⚠️ `keyword.prowl` — Prowl (Keyword)
- rule_ref: `702.76a`
- verdict: **suspicious**
- issue: Definition omits that Prowl functions on the stack and the precise timing condition for the source's creature types.
- suggested fix: Update definition to: 'A static ability that functions on the stack. It lets you pay an alternative cost if a player was dealt combat damage this turn by a source that, at the time it dealt that damage, was under your control and had any of this spell's creature types.'

### ✅ `zone.command` — Command (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ✅ `concept.card_type` — Card Type (CardType)
- rule_ref: `205.2-205.2c`
- verdict: **correct**

### ✅ `keyword.fear` — Fear (Keyword)
- rule_ref: `702.36`
- verdict: **correct**

### ✅ `phase.precombat_main` — Precombat Main Phase (Phase)
- rule_ref: `505.1`
- verdict: **correct**

### ✅ `concept.venture_marker` — Venture Marker (Concept)
- rule_ref: `309.4`
- verdict: **correct**

### ✅ `concept.teammate_card_manipulation` — Teammate Card Manipulation Restriction (MechanicPattern)
- rule_ref: `811.5`
- verdict: **correct**

### ✅ `phase.postcombat_main` — Postcombat Main Phase (Phase)
- rule_ref: `505.1`
- verdict: **correct**

### ⚠️ `designation.ring_bearer` — Ring-bearer (Concept)
- rule_ref: `701.52b`
- verdict: **suspicious**
- issue: Definition includes extra details not present in the source rule text.
- suggested fix: Definition should be: 'A designation a permanent can have. Being a Ring-bearer is not a copiable value.'

### ✅ `keyword.disturb` — Disturb (Keyword)
- rule_ref: `702.146`
- verdict: **correct**

### ✅ `timing.sorcery` — Sorcery Timing (MechanicPattern)
- rule_ref: `602.5d`
- verdict: **correct**

### ✅ `concept.controller` — Controller (Concept)
- rule_ref: `405.4`
- verdict: **correct**

### ✅ `effect.requirement` — Attack Requirement (Concept)
- rule_ref: `508.1d`
- verdict: **correct**

### ✅ `mechanic.linked_replacement_exile` — Linked Replacement Exile (MechanicPattern)
- rule_ref: `607.2b`
- verdict: **correct**

### ✅ `keyword.mentor` — Mentor (Keyword)
- rule_ref: `702.134`
- verdict: **correct**

### ⚠️ `keyword.transform` — Transform (Keyword)
- rule_ref: `701.28d-g`
- verdict: **suspicious**
- issue: Definition is incomplete; source rule only covers a specific case of transform not working.
- suggested fix: Definition should be based on the primary transform rule (701.28a), not this exception clause.

### ⚠️ `keyword.offering` — Offering (Keyword)
- rule_ref: `702.48`
- verdict: **suspicious**
- issue: Definition includes 'grants instant timing' which oversimplifies; rule says 'you may cast this spell any time you could cast an instant' (conditional on paying the cost).
- suggested fix: Change definition to: 'Static ability requiring sacrificing a quality permanent as an additional cost; reduces spell's total cost by the sacrificed permanent's mana cost and, if the cost was paid, allows casting at instant timing.'

### ✅ `concept.match` — Match (Concept)
- rule_ref: `100.6a`
- verdict: **correct**

### ⚠️ `designation.saddled` — Saddled (Concept)
- rule_ref: `702.171b`
- verdict: **suspicious**
- issue: definition omits key restrictions: only permanents, lasts until end of turn or leaves battlefield, not part of copiable values.
- suggested fix: A designation with no inherent rules meaning that serves as a marker for spells and abilities to identify. Only permanents can be saddled, and it lasts until end of turn or until the permanent leaves the battlefield. Not part of copiable values.

### ✅ `mechanic.chaos_ability` — Chaos Ability (MechanicPattern)
- rule_ref: `311.7`
- verdict: **correct**

### ⚠️ `concept.negative_value` — Negative Value (Concept)
- rule_ref: `107.1b`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits key nuance about when zero is used.
- suggested fix: Clarify that zero is used only for the *result of an effect* from a calculation yielding a negative number, with exceptions for doubling/setting life totals or power/toughness.

### ✅ `copy_effect.copiable_values` — Copiable Values (Concept)
- rule_ref: `707.2`
- verdict: **correct**

### ❌ `concept.battle` — Battle (CardType)
- rule_ref: `704.5v, 704.5w, 704.5x`
- verdict: **wrong**
- issue: Source rule text not found; cannot validate extraction.

### ✅ `concept.devotion` — Devotion (MechanicPattern)
- rule_ref: `700.5`
- verdict: **correct**

### ✅ `concept.defense_counter` — Defense Counter (Concept)
- rule_ref: `310.4b`
- verdict: **correct**

### ✅ `concept.token_characteristics` — Token Characteristics (Concept)
- rule_ref: `111.3`
- verdict: **correct**

### ✅ `keyword.commander_damage` — Commander Damage (Concept)
- rule_ref: `903.10`
- verdict: **correct**

### ✅ `concept.outside_game` — Outside the Game (Concept)
- rule_ref: `400.11`
- verdict: **correct**

### ✅ `concept.mana` — Mana (Concept)
- rule_ref: `106.1`
- verdict: **correct**

### ⚠️ `mechanic_pattern.day_night_transform` — Day/Night Transform (MechanicPattern)
- rule_ref: `702.145`
- verdict: **suspicious**
- issue: Definition oversimplifies; day/night is a game state, not just permanents transforming automatically.
- suggested fix: Mechanic where permanents with Daybound/Nightbound transform based on the day/night game state, which can change via spells/abilities and affects all such permanents.

### ❌ `action.open_attraction` — Open an Attraction (Action)
- rule_ref: `701.48a-b`
- verdict: **wrong**
- issue: Definition does not match source rule text; source only mentions when you may open, not what opening does.
- suggested fix: Definition should describe the condition (when you may open), not the effect of opening.

### ❌ `concept.junkyard` — Junkyard (Zone)
- rule_ref: `717.6a`
- verdict: **wrong**
- issue: The source explicitly states 'The pile is not its own zone', contradicting the concept's type of 'Zone'.
- suggested fix: Change type to 'Concept' or 'MechanicPattern' and adjust definition to reflect it's a pile within the command zone, not a separate zone.

### ✅ `action.conspiracy_face_up` — Turn Conspiracy Face Up (Action)
- rule_ref: `116.2j`
- verdict: **correct**

### ✅ `action.fight` — Fight (Action)
- rule_ref: `701.12`
- verdict: **correct**

### ⚠️ `keyword.jump_start` — Jump-Start (Keyword)
- rule_ref: `702.133`
- verdict: **suspicious**
- issue: Definition incorrectly states 'split cards' and omits key details about exile condition.
- suggested fix: Change definition to: 'Keyword ability found on some instants and sorceries allowing casting from the graveyard by discarding a card as an additional cost; if cast this way, it is exiled instead of going elsewhere when leaving the stack.'

### ✅ `concept.same_name` — Same Name (Concept)
- rule_ref: `201.2a`
- verdict: **correct**

### ⚠️ `cardtype.artifact` — Artifact (CardType)
- rule_ref: `301.1`
- verdict: **suspicious**
- issue: Definition includes extra information not in the source rule text.
- suggested fix: Definition should focus on the casting rule: 'A card type. Artifacts are cast as spells from a player's hand during their main phase when the stack is empty.'

### ✅ `randomization.natural_result` — Natural Result (Concept)
- rule_ref: `706.2`
- verdict: **correct**

### ✅ `mechanic.duration_for_as_long_as` — "For As Long As" Duration (MechanicPattern)
- rule_ref: `611.2b`
- verdict: **correct**

### ✅ `concept.turn` — Turn (Concept)
- rule_ref: `500.1`
- verdict: **correct**

### ⚠️ `step.end_of_combat` — End of Combat Step (Step)
- rule_ref: `506.1`
- verdict: **suspicious**
- issue: definition includes extra details not in the source rule text
- suggested fix: Definition should be: 'The final step of the combat phase.'

### ❌ `counter.charge` — Charge Counter (Concept)
- rule_ref: `122.1`
- verdict: **wrong**
- issue: The source rule text does not mention 'Charge Counter' at all.
- suggested fix: Either the concept name is incorrect, or the rule_ref is wrong. The source defines counters in general, not a specific type like 'Charge Counter'.

### ⚠️ `concept.one_shot_effect` — One-Shot Effect (Concept)
- rule_ref: `113.2d`
- verdict: **suspicious**
- issue: definition is incomplete; source only mentions existence, not definition
- suggested fix: definition should reference rule 609 for details, e.g., 'An effect that occurs once and is not continuous. See rule 609.'

### ✅ `keyword.renown` — Renown (Keyword)
- rule_ref: `702.112`
- verdict: **correct**

### ✅ `concept.legendary_spell_restriction` — Legendary Spell Restriction (Concept)
- rule_ref: `205.4e`
- verdict: **correct**

### ⚠️ `concept.basic_land` — Basic Land (Concept)
- rule_ref: `205.4c`
- verdict: **suspicious**
- issue: Definition includes extra detail not in source (mana production).
- suggested fix: Remove 'Can produce mana of their associated color.'

### ⚠️ `keyword.transfigure` — Transfigure (Keyword)
- rule_ref: `702.71a`
- verdict: **suspicious**
- issue: Definition omits 'Then shuffle your library' and uses 'activated only as a sorcery' instead of 'Activate only as a sorcery'.
- suggested fix: Update definition to: 'Sacrifice this permanent and search your library for a creature card with the same mana value, then put it onto the battlefield. Then shuffle your library. Activate only as a sorcery.'

### ⚠️ `concept.pawprint_symbol` — Pawprint Symbol (Keyword)
- rule_ref: `107.18`
- verdict: **suspicious**
- issue: Type 'Keyword' is likely incorrect; this is a Symbol.
- suggested fix: Change type from 'Keyword' to 'Symbol'.

### ✅ `concept.expansion_symbol` — Expansion Symbol (Concept)
- rule_ref: `206.1`
- verdict: **correct**

### ✅ `concept.status_category` — Status Category (Concept)
- rule_ref: `110.5`
- verdict: **correct**

### ✅ `concept.action_from_opening_hand` — Action from Opening Hand (Concept)
- rule_ref: `103.6`
- verdict: **correct**

### ✅ `card_type.flip_card` — Flip Card (CardType)
- rule_ref: `710.1`
- verdict: **correct**

### ❌ `concept.modal_double_faced_card` — Modal Double-Faced Card (Concept)
- rule_ref: `712.2`
- verdict: **wrong**
- issue: Source rule text describes transforming double-faced cards, not modal double-faced cards.
- suggested fix: Change concept to 'Transforming Double-Faced Card' with definition based on 712.2.

### ✅ `action.shuffle` — Shuffle (Action)
- rule_ref: `701.20`
- verdict: **correct**

### ⚠️ `cardtype.attraction` — Attraction (CardType)
- rule_ref: `717`
- verdict: **suspicious**
- issue: Definition includes details not present in the source rule text.
- suggested fix: Definition should be based solely on the provided source text. Suggested: 'A card type for Attraction cards.'

### ✅ `condition.commander_damage` — Commander Damage (Concept)
- rule_ref: `903.10a`
- verdict: **correct**

### ✅ `modifier.hand_modifier` — Hand Modifier (Concept)
- rule_ref: `902.5`
- verdict: **correct**

### ⚠️ `keyword.ninjutsu` — Ninjutsu (Keyword)
- rule_ref: `702.49`
- verdict: **suspicious**
- issue: definition omits that the ability functions only while in hand, and that the creature is put onto battlefield unblocked (not just tapped and attacking).
- suggested fix: Activated ability that functions only while the card is in a player's hand. "Ninjutsu [cost]" means "[Cost], Reveal this card from your hand, Return an unblocked attacking creature you control to its owner's hand: Put this card onto the battlefield tapped and attacking." The creature is put onto the battlefield unblocked, attacking the same player, planeswalker, or battle as the returned creature.

### ✅ `keyword.fading` — Fading (Keyword)
- rule_ref: `702.32`
- verdict: **correct**

### ✅ `concept.mana_type` — Mana Type (Concept)
- rule_ref: `106.1b`
- verdict: **correct**

### ✅ `designation.suspected` — Suspected (Concept)
- rule_ref: `701.58b`
- verdict: **correct**

### ✅ `concept.team_win_loss` — Team Win/Loss Condition (Concept)
- rule_ref: `810.8`
- verdict: **correct**

### ✅ `concept.trigger_event` — Trigger Event (Concept)
- rule_ref: `603.2`
- verdict: **correct**

### ✅ `concept.draw_replacement` — Draw Replacement Effect (MechanicPattern)
- rule_ref: `121.6`
- verdict: **correct**

### ⚠️ `concept.face_down_spell` — Face-Down Spell (Concept)
- rule_ref: `708.1`
- verdict: **suspicious**
- issue: Definition is more specific than source text; source only introduces concept, doesn't define it fully.
- suggested fix: Definition should be more general, e.g., 'A spell or permanent that is turned so its face is not visible, as allowed by specific cards or effects.'

### ⚠️ `concept.variant.emperor` — Emperor Variant (Concept)
- rule_ref: `104.2d`
- verdict: **suspicious**
- issue: Definition is broader than the source rule text, which only defines a win condition.
- suggested fix: Definition should focus on the win condition: 'A multiplayer variant where a team wins if its emperor wins the game.'

### ⚠️ `action.tap` — Tap (Action)
- rule_ref: `701.21`
- verdict: **suspicious**
- issue: Definition incorrectly describes tap as a static cost symbol; rule 701.21a defines tap as turning a permanent sideways.
- suggested fix: Change definition to: 'To tap a permanent, turn it sideways from an upright position. Only untapped permanents can be tapped.'

### ⚠️ `keyword.epic` — Epic (Keyword)
- rule_ref: `702.50`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits key details: epic is two spell abilities (one creating a delayed triggered ability), and the copy excludes the epic ability.
- suggested fix: Definition should be: 'Two-part ability that means “For the rest of the game, you can’t cast spells,” and “At the beginning of each of your upkeeps for the rest of the game, copy this spell except for its epic ability. If the spell has any targets, you may choose new targets for the copy.”'

### ⚠️ `keyword.more_than_meets_the_eye` — More Than Meets the Eye (Keyword)
- rule_ref: `702.162`
- verdict: **suspicious**
- issue: Definition incorrectly states 'converted by paying an alternative cost' instead of 'converted by paying [cost] rather than its mana cost'.
- suggested fix: Change definition to: 'A static ability that allows a spell to be cast converted by paying a specified cost rather than its mana cost.'

### ✅ `concept.new_target_selection` — New Target Selection (Concept)
- rule_ref: `115.7d`
- verdict: **correct**

### ✅ `counter.defense` — Defense Counter (Concept)
- rule_ref: `120.3h`
- verdict: **correct**

### ⚠️ `concept.no_mana_cost` — No Mana Cost (Concept)
- rule_ref: `202.1b`
- verdict: **suspicious**
- issue: Definition is slightly imprecise; it says 'cannot be cast through normal means' but the source text describes it as 'an unpayable cost' and notes lands are played, not cast.
- suggested fix: Change definition to: 'An unpayable cost representing that certain objects (lands, tokens, nontraditional cards, etc.) have no mana cost.'

### ✅ `concept.vanguard_hand_modifier` — Vanguard Hand Modifier (Concept)
- rule_ref: `211.1`
- verdict: **correct**

### ⚠️ `concept.phyrexian_mana_symbol` — Phyrexian Mana Symbol (Concept)
- rule_ref: `106.9`
- verdict: **suspicious**
- issue: Definition describes payment, but source rule text describes effect adding mana.
- suggested fix: Definition should reference the symbol's property: can be paid with life, and how it's treated when added to mana pool.

### ✅ `keyword.embalm` — Embalm (Keyword)
- rule_ref: `702.128`
- verdict: **correct**

### ✅ `mechanic.champion` — Champion (Keyword)
- rule_ref: `702.72`
- verdict: **correct**

### ✅ `keyword.battle_cry` — Battle Cry (Keyword)
- rule_ref: `702.91`
- verdict: **correct**

### ✅ `keyword.dethrone` — Dethrone (Keyword)
- rule_ref: `702.105`
- verdict: **correct**

### ✅ `concept.fully_unlock` — Fully Unlock (Concept)
- rule_ref: `709.5i`
- verdict: **correct**

### ✅ `keyword.vanishing` — Vanishing (Keyword)
- rule_ref: `702.63`
- verdict: **correct**

### ✅ `concept.oracle` — Oracle (Concept)
- rule_ref: `108.1`
- verdict: **correct**

### ⚠️ `keyword.echo` — Echo (Keyword)
- rule_ref: `702.30`
- verdict: **suspicious**
- issue: Definition slightly misstates timing condition and omits Oracle errata note.
- suggested fix: Definition should be: 'A triggered ability meaning "At the beginning of your upkeep, if this permanent came under your control since the beginning of your last upkeep, sacrifice it unless you pay [cost]." Some older cards have an echo cost equal to their mana cost.'

### ⚠️ `concept.mana_value` — Mana Value (Concept)
- rule_ref: `202.3`
- verdict: **suspicious**
- issue: Definition incomplete; missing details about special cases (no mana cost, X, hybrid, Phyrexian, split/meld/transform).
- suggested fix: Add summary of key special cases or note that definition is a simplified version of the full rule.

### ✅ `concept.melded_permanent` — Melded Permanent (Concept)
- rule_ref: `712.4a`
- verdict: **correct**

### ⚠️ `ability.evasion` — Evasion Ability (MechanicPattern)
- rule_ref: `702.9a`
- verdict: **suspicious**
- issue: Definition is a general description, but source text only states 'Flying is an evasion ability.' as an example, not a definition.
- suggested fix: Definition should be more general, e.g., 'An ability that makes a creature harder to block, such as flying.'

### ❌ `ability.enchant` — Enchant Ability (Keyword)
- rule_ref: `303.1`
- verdict: **wrong**
- issue: Rule 303.1 does not mention 'Enchant' ability; it describes casting enchantments.
- suggested fix: Check rules for Auras (e.g., 303.4) for 'enchant' ability definition.

### ⚠️ `keyword.affinity` — Affinity (Keyword)
- rule_ref: `702.41`
- verdict: **suspicious**
- issue: Definition is slightly imprecise; it omits that the ability functions only on the stack and the exact wording of the cost reduction.
- suggested fix: A static ability that functions while the spell is on the stack. 'Affinity for [text]' means 'This spell costs you {1} less to cast for each [text] you control.'

### ✅ `state.phased_out` — Phased Out (Concept)
- rule_ref: `702.26b`
- verdict: **correct**

### ✅ `keyword.rampage` — Rampage (Keyword)
- rule_ref: `702.23`
- verdict: **correct**

### ⚠️ `action.discover` — Discover (Action)
- rule_ref: `701.55a`
- verdict: **suspicious**
- issue: Definition omits final library placement step.
- suggested fix: Add '...then put the remaining exiled cards on the bottom of your library in a random order.'

### ✅ `concept.mana_color` — Mana Color (Concept)
- rule_ref: `106.1a`
- verdict: **correct**

### ⚠️ `mechanic.linked_ability` — Linked Abilities (MechanicPattern)
- rule_ref: `607`
- verdict: **suspicious**
- issue: Definition is an interpretation, not a direct extraction from the given source text.
- suggested fix: Definition should be based on the full rule 607 text, not just the header.

### ✅ `concept.ability_controller` — Ability Controller (Concept)
- rule_ref: `113.8`
- verdict: **correct**

### ⚠️ `concept.losing_the_game` — Losing the Game (Concept)
- rule_ref: `104.3`
- verdict: **suspicious**
- issue: Definition includes specific examples but omits several listed ways to lose (e.g., drawing from empty library, poison counters, concession, effects stating loss).
- suggested fix: Broaden definition to reflect the general concept of losing the game, referencing the various conditions listed in rule 104.3 without listing all specifics.

### ✅ `keyword.cascade` — Cascade (Keyword)
- rule_ref: `702.85`
- verdict: **correct**

### ✅ `concept.battle_protector` — Battle Protector (Concept)
- rule_ref: `310.8`
- verdict: **correct**

### ✅ `concept.world_permanent` — World Permanent (Concept)
- rule_ref: `205.4f`
- verdict: **correct**

### ✅ `concept.extra_step` — Extra Step (Concept)
- rule_ref: `500.9`
- verdict: **correct**

### ✅ `keyword.siege` — Siege (Keyword)
- rule_ref: `310.11`
- verdict: **correct**

### ⚠️ `ability.characteristic_defining` — Characteristic-Defining Ability (Keyword)
- rule_ref: `113.6a`
- verdict: **suspicious**
- issue: Definition slightly off; source says 'function everywhere', not 'defines characteristics and functions everywhere'.
- suggested fix: Definition should be: 'An ability that functions everywhere, even outside the game and before the game begins.'

### ❌ `zone.graveyard` — Graveyard (Zone)
- rule_ref: `403`
- verdict: **wrong**
- issue: Source rule text does not mention graveyard at all; it only mentions 'Battlefield'.
- suggested fix: Check rule 404 for Graveyard definition.

### ⚠️ `concept.merged_permanent_sticker` — Merged Permanent Sticker Timestamp (Concept)
- rule_ref: `613.7k`
- verdict: **suspicious**
- issue: Definition is slightly off; source rule describes stickers receiving new timestamps when the object becomes part of a merged permanent, but the concept name and definition imply a specific 'Merged Permanent Sticker Timestamp' concept, which is not explicitly named in the rule.
- suggested fix: Consider renaming to 'Sticker Timestamp on Merged Permanent' and adjusting definition to: 'When an object a sticker is on becomes part of a merged permanent, the sticker receives a new timestamp at that time, while the relative order of multiple stickers remains unchanged.'

### ✅ `concept.base_toughness` — Base Toughness (Concept)
- rule_ref: `208.4`
- verdict: **correct**

### ✅ `action.tapping_for_mana` — Tapping for Mana (Action)
- rule_ref: `106.12`
- verdict: **correct**

### ⚠️ `zone.object_arrangement` — Zone Object Arrangement (MechanicPattern)
- rule_ref: `400.5`
- verdict: **suspicious**
- issue: Type 'MechanicPattern' is not appropriate; this describes a rule about zone arrangement, not a gameplay mechanic pattern.
- suggested fix: Change type to 'Concept' or 'Zone' property.

### ✅ `concept.permanent_controller` — Permanent's Controller (Concept)
- rule_ref: `110.2`
- verdict: **correct**

### ✅ `card_type.transforming_double_faced_card` — Transforming Double-Faced Card (CardType)
- rule_ref: `712.2`
- verdict: **correct**

### ✅ `concept.card_pool` — Card Pool (Concept)
- rule_ref: `903.13e`
- verdict: **correct**

### ⚠️ `symbol.planeswalker` — Planeswalker Symbol (Symbol)
- rule_ref: `901.3a`
- verdict: **suspicious**
- issue: Definition adds extra interpretation not present in source text.
- suggested fix: Definition should simply state it is one of the faces of the planar die. E.g., 'One of the faces of the planar die, alongside the chaos symbol and blank faces.'

### ✅ `concept.mandatory_loop` — Mandatory Loop (Concept)
- rule_ref: `104.4b`
- verdict: **correct**

### ✅ `keyword.shroud` — Shroud (Keyword)
- rule_ref: `702.18`
- verdict: **correct**

### ✅ `concept.life_payment` — Paying Life (Action)
- rule_ref: `118.3b`
- verdict: **correct**

### ⚠️ `trigger.zone_change` — Zone-Change Trigger (Keyword)
- rule_ref: `603.10a`
- verdict: **suspicious**
- issue: Definition is incomplete and misses key details about specific types of zone-change triggers.
- suggested fix: Definition should specify: 'Triggers that look back in time, including leaves-the-battlefield abilities, abilities that trigger when a card leaves a graveyard, and abilities that trigger when an object that all players can see is put into a hand or library.'

### ✅ `concept.ability_cost` — Ability Cost (Concept)
- rule_ref: `113.3b`
- verdict: **correct**

### ⚠️ `concept.start_your_engines` — Start Your Engines! (Keyword)
- rule_ref: `704.5z`
- verdict: **suspicious**
- issue: Definition is accurate but type is likely wrong; 'Start Your Engines!' is a static ability, not a keyword ability.
- suggested fix: Change type from 'Keyword' to 'MechanicPattern' or 'Concept'.

### ✅ `action.unlock` — Pay Unlock Cost (Action)
- rule_ref: `116.2m`
- verdict: **correct**

### ✅ `keyword.mobilize` — Mobilize (Keyword)
- rule_ref: `702.181`
- verdict: **correct**

### ⚠️ `concept.opening_hand` — Opening Hand (Concept)
- rule_ref: `103.5`
- verdict: **suspicious**
- issue: definition is incomplete; it omits the condition that a player must choose not to take a mulligan for the hand to become the opening hand.
- suggested fix: The final hand a player keeps after choosing not to take a mulligan, once the mulligan process is complete.

### ⚠️ `concept.simultaneous_resolution` — Simultaneous Resolution (Concept)
- rule_ref: `608.2f`
- verdict: **suspicious**
- issue: definition oversimplifies and omits key details about APNAP order and individual processing when simultaneous is impossible
- suggested fix: Multiple actions are processed simultaneously unless they cannot be, in which case they are processed individually, using APNAP order primarily and controller choice secondarily for same-player objects.

### ✅ `zone.exile` — Exile (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ❌ `variant.team_vs_team` — Team vs. Team Variant (Variant)
- rule_ref: `808.4`
- verdict: **wrong**
- issue: Definition does not match source rule text; source only describes turn order determination, not team structure or resource sharing.
- suggested fix: Update definition to reflect the specific rule about determining which player goes first in a team vs. team game.

### ✅ `characteristic.loyalty` — Loyalty (Concept)
- rule_ref: `306.5`
- verdict: **correct**

### ✅ `concept.toughness` — Toughness (Concept)
- rule_ref: `208.1`
- verdict: **correct**

### ⚠️ `cardtype.tribal` — Tribal (CardType)
- rule_ref: `308.3`
- verdict: **suspicious**
- issue: definition states 'errata'd to kindred' but source says 'printed with the “tribal” card type' and 'have received errata' without specifying the target type.
- suggested fix: Definition could be: 'An obsolete card type that has been errata'd; cards with this type are now kindred cards.'

### ✅ `keyword.horsemanship` — Horsemanship (Keyword)
- rule_ref: `702.31`
- verdict: **correct**

### ❌ `cardtype.sorcery` — Sorcery (CardType)
- rule_ref: `307.3`
- verdict: **wrong**
- issue: Definition does not match source rule text; source describes subtypes, not casting restrictions.
- suggested fix: Definition should describe sorcery subtypes, or use a different rule reference for casting restrictions.

### ⚠️ `concept.last_known_information` — Last Known Information (Concept)
- rule_ref: `113.7a`
- verdict: **suspicious**
- issue: Definition is a general description, but the source text provides a specific context for when last known information is used.
- suggested fix: Definition could be more specific: 'Information about an object used when it is no longer in the expected zone at the time an ability checks it, derived from its characteristics at the last time it was in that zone.'

### ✅ `layer.layer_7d` — Layer 7d - Power/Toughness Switch (Concept)
- rule_ref: `613.4d`
- verdict: **correct**

### ⚠️ `concept.continuous_effect` — Continuous Effect (Concept)
- rule_ref: `113.2d`
- verdict: **suspicious**
- issue: Definition is a general description but not directly from the cited rule text.
- suggested fix: Definition should more closely reflect the source: 'An effect generated by an ability that modifies characteristics or game rules over a period of time, as opposed to a one-shot effect.'

### ✅ `concept.starting_player` — Starting player (Concept)
- rule_ref: `103.1`
- verdict: **correct**

### ✅ `concept.meld_card` — Meld Card (Concept)
- rule_ref: `712.4`
- verdict: **correct**

### ⚠️ `keyword.exploit` — Exploit (Keyword)
- rule_ref: `702.110`
- verdict: **suspicious**
- issue: Definition incorrectly states the creature gains 'exploited a creature' after resolution; the rule defines what 'exploits a creature' means, not a gained ability.
- suggested fix: Definition should be: 'A triggered ability that means "When this creature enters, you may sacrifice a creature." A creature "exploits a creature" when its controller sacrifices a creature as the ability resolves.'

### ⚠️ `concept.opponent` — Opponent (Concept)
- rule_ref: `102.2`
- verdict: **suspicious**
- issue: Definition is broader than source text; source only defines opponent for two-player games.
- suggested fix: Definition should specify 'In a two-player game, a player's opponent is the other player.'

### ⚠️ `concept.life_gain` — Life Gain (Concept)
- rule_ref: `119.3`
- verdict: **suspicious**
- issue: Definition is too narrow; source rule describes the result of life gain/loss, not the effect itself.
- suggested fix: Definition could be: 'The result of an effect that increases a player's life total, causing their life total to be adjusted accordingly.'

### ⚠️ `concept.mulligan` — Mulligan (Action)
- rule_ref: `103.5`
- verdict: **suspicious**
- issue: definition omits key details: number of cards put on bottom depends on mulligan count, and process repeats until no player mulligans.
- suggested fix: The process of shuffling hand back into library, drawing a new hand, then putting a number of cards equal to the number of mulligans taken on the bottom of the library, repeated until no player takes a mulligan.

### ⚠️ `concept.spell_proposal` — Spell Proposal (Concept)
- rule_ref: `601.2a`
- verdict: **suspicious**
- issue: definition includes actions beyond the scope of rule 601.2a (modes, targets, costs are in later subrules)
- suggested fix: definition should focus on moving the card to the stack and becoming the topmost object, as per 601.2a.

### ✅ `keyword.wither` — Wither (Keyword)
- rule_ref: `702.80`
- verdict: **correct**

### ✅ `concept.interchangeable_names` — Interchangeable Names (Concept)
- rule_ref: `201.3`
- verdict: **correct**

### ⚠️ `keyword.partner` — Partner (Keyword)
- rule_ref: `702.124`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits key details about partner abilities being keyword abilities that modify deck construction rules and function before the game begins.
- suggested fix: A keyword ability that modifies deck construction in the Commander variant, allowing you to designate two legendary cards as your commander rather than one, with specific variants (partner, partner with [name], friends forever, choose a Background, Doctor’s companion).

### ✅ `concept.planeswalker_loyalty` — Planeswalker Loyalty (Concept)
- rule_ref: `209.1`
- verdict: **correct**

### ⚠️ `card_type.modal_double_faced_card` — Modal Double-Faced Card (CardType)
- rule_ref: `712.3`
- verdict: **suspicious**
- issue: Definition includes 'can be chosen when casting or using the card, typically in modal effects' which is not explicitly stated in the source rule text.
- suggested fix: Definition should focus on the independent faces and the physical markings, e.g., 'A double-faced card with two independent Magic card faces, each marked with a distinct symbol in the upper left corner.'

### ⚠️ `variant.emperor` — Emperor Variant (Variant)
- rule_ref: `804.1`
- verdict: **suspicious**
- issue: Definition includes 'Emperor player is protected by flanking teammates' which is not in the source rule text.
- suggested fix: Definition should focus on the use of the deploy creatures option and its application in team-based variants.

### ✅ `effect.unpreventable_damage` — Unpreventable Damage (MechanicPattern)
- rule_ref: `615.12`
- verdict: **correct**

### ⚠️ `concept.permanent_type` — Permanent Type (CardType)
- rule_ref: `110.4`
- verdict: **suspicious**
- issue: type should be Concept, not CardType
- suggested fix: Change type to 'Concept' as it describes a category of permanent types, not a card type itself.

### ✅ `state_action.replacement_multiple` — State-Based Action Replacement Effect (Concept)
- rule_ref: `704.7`
- verdict: **correct**

### ✅ `multiplayer_option.limited_range_of_influence` — Limited Range of Influence (Concept)
- rule_ref: `801.1`
- verdict: **correct**

### ✅ `mechanic.linked_ability_exile` — Linked Exile Ability (MechanicPattern)
- rule_ref: `607.2a`
- verdict: **correct**

### ✅ `keyword.ward` — Ward (Keyword)
- rule_ref: `702.21`
- verdict: **correct**

### ❌ `concept.blocking_creature` — Blocking Creature (Concept)
- rule_ref: `506.3d`
- verdict: **wrong**
- issue: Definition does not match source rule text; source discusses creatures entering blocking, not general definition of blocking creature.
- suggested fix: Definition should reflect the specific case in rule 506.3d: A creature that enters the battlefield blocking but is not considered a blocking creature if the target isn't attacking appropriately.

### ✅ `keyword.ingest` — Ingest (Keyword)
- rule_ref: `702.115`
- verdict: **correct**

### ✅ `mechanic.typecycling` — Typecycling (MechanicPattern)
- rule_ref: `702.29e`
- verdict: **correct**

### ✅ `keyword.retrace` — Retrace (Keyword)
- rule_ref: `702.81`
- verdict: **correct**

### ✅ `concept.face_down_cast` — Face-Down Cast (Concept)
- rule_ref: `708.4`
- verdict: **correct**

### ✅ `randomization.coin_flip_outcome` — Coin Flip Outcome (Concept)
- rule_ref: `705.2`
- verdict: **correct**

### ✅ `concept.counter_placement` — Placing Counters (Action)
- rule_ref: `122.6`
- verdict: **correct**

### ✅ `concept.merged_permanent` — Merged Permanent (Concept)
- rule_ref: `728.2`
- verdict: **correct**

### ⚠️ `zone.commander` — Command zone (Zone)
- rule_ref: `702.124b`
- verdict: **suspicious**
- issue: Definition is partially correct but incomplete; rule 702.124b only mentions commanders beginning in command zone, not casting from it.
- suggested fix: Update definition to: 'The zone where commanders begin the game, as referenced in rule 702.124b.'

### ⚠️ `mechanic.player_control` — Controlling Another Player (MechanicPattern)
- rule_ref: `721.1-721.9`
- verdict: **suspicious**
- issue: Definition includes examples (casting spells, attacking) not present in source text.
- suggested fix: Definition should focus on the core rule: an effect that allows a player to control another player during that player's next turn.

### ⚠️ `concept.life_total` — Life Total (Concept)
- rule_ref: `103.4`
- verdict: **suspicious**
- issue: definition mentions 'starting at a defined amount' but source focuses on starting life totals for various formats, not the general concept of life total as a current value.
- suggested fix: Adjust definition to focus on the starting values per variant, or reference that it's the initial life value before modifications.

### ✅ `concept.fragmented_loop` — Fragmented Loop (Concept)
- rule_ref: `730.3`
- verdict: **correct**

### ⚠️ `ability.activated` — Activated Ability (Keyword)
- rule_ref: `113.3b`
- verdict: **suspicious**
- issue: definition omits mention of activation instructions and the stack, and type 'Keyword' is borderline (activated ability is a concept, not a keyword).
- suggested fix: Change type to 'Concept' and include full definition: 'An ability with a cost and an effect, written as “[Cost]: [Effect.] [Activation instructions (if any).]” A player may activate such an ability whenever they have priority. Doing so puts it on the stack.'

### ⚠️ `variant.archenemy` — Archenemy (Variant)
- rule_ref: `904`
- verdict: **suspicious**
- issue: Definition is accurate but the source rule text provided is incomplete (only shows the title).
- suggested fix: Verify the full text of rule 904 to ensure the definition matches the official, complete description.

### ✅ `randomization.stored_result` — Stored Result (Concept)
- rule_ref: `706.8a`
- verdict: **correct**

### ⚠️ `concept.front_face` — Front Face (Concept)
- rule_ref: `712.8`
- verdict: **suspicious**
- issue: definition is oversimplified and omits key details about zones and meld cards
- suggested fix: The primary face of a double-faced card. While a double-faced card is outside the game or in a zone other than the battlefield or stack, it has only the characteristics of its front face. (See 712.8a)

### ✅ `concept.untap_symbol` — Untap Symbol (Concept)
- rule_ref: `107.6`
- verdict: **correct**

### ❌ `concept.stack` — The Stack (Concept)
- rule_ref: `115.10`
- verdict: **wrong**
- issue: Rule 115.10 does not define the stack; it's about non-target effects.
- suggested fix: Use rule 405 (The Stack) for the stack definition.

### ✅ `concept.token` — Token (Concept)
- rule_ref: `111.1`
- verdict: **correct**

### ✅ `keyword.bestow` — Bestow (Keyword)
- rule_ref: `702.103`
- verdict: **correct**

### ✅ `rule.legend_rule` — Legend Rule (MechanicPattern)
- rule_ref: `704.5j`
- verdict: **correct**

### ✅ `keyword.casualty` — Casualty (Keyword)
- rule_ref: `702.153`
- verdict: **correct**

### ⚠️ `ability.loyalty` — Loyalty Ability (Keyword)
- rule_ref: `113.5`
- verdict: **suspicious**
- issue: Definition omits 'of a permanent they control' and 'any time they have priority' from the source.
- suggested fix: Definition should be: Activated ability of a planeswalker that a player may activate any time they have priority and the stack is empty during a main phase of their turn, but only once per turn for that permanent.

### ⚠️ `keyword.amplify` — Amplify (Keyword)
- rule_ref: `702.38`
- verdict: **suspicious**
- issue: Definition is slightly off; it says 'determine +1/+1 counters' but the rule specifies the permanent enters with N counters per revealed card.
- suggested fix: When this permanent enters the battlefield, you may reveal any number of cards from your hand that share a creature type with it. It enters with N +1/+1 counters on it for each card revealed this way.

### ✅ `concept.planar_controller` — Planar Controller (Concept)
- rule_ref: `800.4p`
- verdict: **correct**

### ⚠️ `keyword.tribute` — Tribute (Keyword)
- rule_ref: `702.104`
- verdict: **suspicious**
- issue: Definition incorrectly calls tribute a static ability that triggers; it is a static ability that functions as the creature enters, and the linked ability is a triggered ability that checks if tribute wasn't paid.
- suggested fix: A static ability that functions as a creature enters the battlefield, giving an opponent the choice to put +1/+1 counters on it; if they don't, a linked triggered ability may activate.

### ✅ `keyword.flying` — Flying (Keyword)
- rule_ref: `702.9`
- verdict: **correct**

### ✅ `concept.battle_type` — Battle Type (Concept)
- rule_ref: `205.3q`
- verdict: **correct**

### ⚠️ `keyword.gravestorm` — Gravestorm (Keyword)
- rule_ref: `702.69a`
- verdict: **suspicious**
- issue: Definition omits conditional clause about targets
- suggested fix: Add conditional: 'If the spell has any targets, you may choose new targets for any of the copies.'

### ✅ `concept.creature_type` — Creature Type (Concept)
- rule_ref: `205.3m`
- verdict: **correct**

### ✅ `concept.outlaw` — Outlaw (MechanicPattern)
- rule_ref: `700.12`
- verdict: **correct**

### ❌ `mechanic.restart_game` — Restart Game Effect (MechanicPattern)
- rule_ref: `725/801.17`
- verdict: **wrong**
- issue: Rule reference not found in source text.
- suggested fix: Verify the correct rule reference for restart game effects.

### ✅ `concept.color_indicator` — Color Indicator (Concept)
- rule_ref: `107.13`
- verdict: **correct**

### ❌ `mechanic.planeswalk` — Planeswalk (MechanicPattern)
- rule_ref: `312.7`
- verdict: **wrong**
- issue: Definition does not match source rule text; source describes state-based action for phenomena, not general planeswalk mechanic.
- suggested fix: Definition should describe the state-based action when a phenomenon card is face up and no triggered ability is pending.

### ✅ `keyword.assemble` — Assemble (Keyword)
- rule_ref: `701.41`
- verdict: **correct**

### ✅ `concept.unlocked_designation` — Unlocked Designation (Concept)
- rule_ref: `709.5c`
- verdict: **correct**

### ⚠️ `keyword.open_attraction` — Open an Attraction (Keyword)
- rule_ref: `701.48`
- verdict: **suspicious**
- issue: definition is incomplete and mentions command zone incorrectly
- suggested fix: Definition should be: 'A keyword action that allows a player to move the top card of their Attraction deck off the deck, turn it face up, and put it onto the battlefield under their control.'

### ✅ `state_action.planeswalker.planar_controller_planeswalks` — Planar Controller Planeswalks (Concept)
- rule_ref: `704.6f`
- verdict: **correct**

### ✅ `mechanic.attack_trigger` — Attack Trigger (MechanicPattern)
- rule_ref: `508.3`
- verdict: **correct**

### ✅ `keyword.cleave` — Cleave (Keyword)
- rule_ref: `702.148`
- verdict: **correct**

### ✅ `concept.split_card_names` — Split Card Names (Concept)
- rule_ref: `709.4a`
- verdict: **correct**

### ⚠️ `keyword.investigate` — Investigate (Keyword)
- rule_ref: `701.36`
- verdict: **suspicious**
- issue: definition adds extra description not in the source rule text
- suggested fix: Definition should be: 'Create a Clue token.'

### ⚠️ `concept.excess_damage` — Excess Damage (Concept)
- rule_ref: `120.4a`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits planeswalker, battle, and multi-type cases.
- suggested fix: Damage beyond what would be lethal to a permanent (creature, planeswalker, or battle). For a creature, lethal damage considers marked damage and simultaneous damage; any damage >1 is excess if the source has deathtouch. For a planeswalker, excess is damage beyond its loyalty. For a battle, excess is damage beyond its defense.

### ✅ `concept.deck_construction_ability` — Deck Construction Ability (Concept)
- rule_ref: `113.6n`
- verdict: **correct**

### ✅ `concept.prototype_spell` — Prototyped Spell (Concept)
- rule_ref: `718.3`
- verdict: **correct**

### ✅ `layer.layer_3` — Layer 3 - Text Changing (Concept)
- rule_ref: `613.1c`
- verdict: **correct**

### ✅ `step.draw` — Draw Step (Step)
- rule_ref: `504.1`
- verdict: **correct**

### ⚠️ `concept.owner` — Owner (Concept)
- rule_ref: `407.4`
- verdict: **suspicious**
- issue: Definition includes extraneous deck reference not in source rule.
- suggested fix: Definition should be: 'The player who is the only person who can ante objects they own.'

### ⚠️ `zone.planar_deck` — Planar Deck (Zone)
- rule_ref: `901`
- verdict: **suspicious**
- issue: definition references Planechase but source rule text only contains the word 'Planechase'
- suggested fix: Check rule 901's full text for the definition of the Planar Deck zone.

### ✅ `subtype.vehicle` — Vehicle (CardType)
- rule_ref: `301.7`
- verdict: **correct**

### ⚠️ `keyword.companion` — Companion (Keyword)
- rule_ref: `702.139`
- verdict: **suspicious**
- issue: Definition omits 'special action' and 'once during the game' nuance, and slightly misstates timing.
- suggested fix: Definition should include: '...once during the game, any time you have priority and the stack is empty during a main phase of your turn, you may pay {3} as a special action to put it into your hand.'

### ✅ `concept.ticket_counter` — Ticket Counter (Concept)
- rule_ref: `107.17`
- verdict: **correct**

### ✅ `concept.face_down_as_enters` — Face-Down as It Enters (Concept)
- rule_ref: `708.3`
- verdict: **correct**

### ⚠️ `concept.effect_chain` — Effect Chain Combination (Concept)
- rule_ref: `616.2`
- verdict: **suspicious**
- issue: Definition is incomplete and omits prevention effects.
- suggested fix: Definition should be: 'Multiple replacement or prevention effects that each become applicable as a result of another effect modifying the event.'

### ✅ `keyword.freerunning` — Freerunning (Keyword)
- rule_ref: `702.173`
- verdict: **correct**

## Relation validation

### ⚠️ `concept.attacking_creature` --[MODIFIES]--> `concept.combat_damage`
- rule_ref: `510.1`
- verdict: **suspicious**
- issue: MODIFIES is not the best fit; the relation is more about assignment/dealing of damage, not modification.
- suggested type: `INTERACTS_WITH`

### ❌ `concept.state_based_action` --[MODIFIES]--> `concept.attachment_legality`
- rule_ref: `704.5m, 704.5n, 704.5p`
- verdict: **wrong**
- issue: Rule text not found; cannot verify relation. Even if found, state-based actions do not modify attachment legality; they check and cause actions based on it.

### ⚠️ `concept.alternative_cost` --[INTERACTS_WITH]--> `concept.additional_cost`
- rule_ref: `118.9d`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is vague; the rule describes how additional costs apply to an alternative cost, which is more specifically a DEPENDS_ON or MODIFIES relationship.
- suggested type: `MODIFIES`

### ✅ `concept.case_card` --[CONTAINS]--> `concept.case_solved_ability`
- rule_ref: `719.3c`
- verdict: **correct**

### ⚠️ `game.multiplayer` --[DEPENDS_ON]--> `concept.seating_order`
- rule_ref: `800.5`
- verdict: **suspicious**
- issue: The rule text describes how seating order is determined, not that a multiplayer game depends on it. The relation is more accurately 'CONTAINS' (a multiplayer game includes the concept of seating order) or 'REFERENCES'.
- suggested type: `CONTAINS`

### ⚠️ `system.layer` --[CONTAINS]--> `layer.layer_1`
- rule_ref: `613.1a`
- verdict: **suspicious**
- issue: The rule text describes what happens in Layer 1 but does not explicitly state that the layer system contains Layer 1; the relation is more accurately OCCURS_IN (Layer 1 occurs in the layer system).
- suggested type: `OCCURS_IN`

### ✅ `keyword.champion` --[DEPENDS_ON]--> `ability.linked`
- rule_ref: `702.72b`
- verdict: **correct**

### ✅ `concept.targeting` --[REFERENCES]--> `concept.non_target_effect`
- rule_ref: `115.10a`
- verdict: **correct**

### ⚠️ `card_type.phenomenon` --[REFERENCES]--> `mechanic.planar_controller`
- rule_ref: `312.4`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule text describes a control relationship, not a reference.
- suggested type: `INTERACTS_WITH`

### ⚠️ `keyword.phasing` --[CREATES]--> `state.phased_in`
- rule_ref: `702.26c`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type, but the rule text supports that phasing causes a change to phased-in status.
- suggested type: `MOVES_TO`

### ⚠️ `card_type.kindred` --[REFERENCES]--> `card_type.creature`
- rule_ref: `300.2b`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule states that a Kindred card has another card type, which is a direct inclusion relationship.
- suggested type: `CONTAINS`

### ✅ `keyword.manifest` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `701.34a`
- verdict: **correct**

### ✅ `card_type.phenomenon` --[MOVES_TO]--> `zone.command_zone`
- rule_ref: `312.2`
- verdict: **correct**

### ⚠️ `keyword.space_sculptor` --[CREATES]--> `concept.sector_designation`
- rule_ref: `702.158a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical; the relation is that the keyword ability causes creatures to gain sector designations, which fits MODIFIES or INTERACTS_WITH.
- suggested type: `MODIFIES`

### ✅ `concept.game` --[CONTAINS]--> `concept.multiplayer_game`
- rule_ref: `100.1b`
- verdict: **correct**

### ✅ `action.regenerate` --[MODIFIES]--> `permanent.permanent`
- rule_ref: `701.15a`
- verdict: **correct**

### ⚠️ `zone.library` --[PATTERN_OF]--> `zone.hidden`
- rule_ref: `400.2`
- verdict: **suspicious**
- issue: The type PATTERN_OF is non-canonical; the relation is more accurately a CONTAINS (membership) or OCCURS_IN (zone is an instance of a category).
- suggested type: `OCCURS_IN`

### ❌ `concept.game` --[CONTAINS]--> `concept.deck`
- rule_ref: `100.2`
- verdict: **wrong**
- issue: The rule describes what players need to play the game, not that the game contains decks. The relation direction is backwards: decks are used in the game, not that the game contains decks as a component.

### ⚠️ `game_option.attack_multiple_players` --[CREATES]--> `concept.defending_player`
- rule_ref: `802.2`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, but the rule text supports that the option results in multiple defending players.
- suggested type: `CREATES`

### ❌ `ability.activated_mana` --[INTERACTS_WITH]--> `zone.stack`
- rule_ref: `605.3b`
- verdict: **wrong**
- issue: The rule text states that activated mana abilities do NOT go on the stack, so there is no interaction with the stack as a zone.

### ❌ `concept.cost` --[CONTAINS]--> `concept.mana_cost`
- rule_ref: `118.2`
- verdict: **wrong**
- issue: The rule text describes that a cost 'may include' mana payments, but the relation direction is reversed: mana cost is a component of cost, not the other way around. CONTAINS implies source contains target, but here the target (mana cost) is contained within the source (cost).

### ✅ `action.create` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `701.6a`
- verdict: **correct**

### ✅ `keyword.connive` --[PATTERN_OF]--> `keyword.connive_n`
- rule_ref: `701.47e`
- verdict: **correct**

### ⚠️ `concept.spell_to_token` --[CREATES]--> `concept.token`
- rule_ref: `111.13`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, and the rule text explicitly states the token is not 'created' for certain purposes, though the process does result in a token.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.defense_counter` --[MODIFIES]--> `concept.defense`
- rule_ref: `310.4c`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule states equality, not modification.
- suggested type: `REFERENCES`

### ⚠️ `mechanic.bestowed_aura` --[INTERACTS_WITH]--> `action.attach`
- rule_ref: `702.103f`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a state change (ceasing to be bestowed) when unattached, which is more specific than general interaction.
- suggested type: `DEPENDS_ON`

### ⚠️ `concept.drawing_the_game` --[OCCURS_IN]--> `concept.limited_range_of_influence`
- rule_ref: `104.4e`
- verdict: **suspicious**
- issue: The relation type OCCURS_IN is not the best fit; the rule describes how a draw effect is modified by Limited Range of Influence, so MODIFIES is more accurate.
- suggested type: `MODIFIES`

### ✅ `concept.game` --[CONTAINS]--> `concept.supplementary_deck`
- rule_ref: `100.2d`
- verdict: **correct**

### ⚠️ `concept.state_based_action` --[MODIFIES]--> `concept.saga`
- rule_ref: `704.5s`
- verdict: **suspicious**
- issue: The type MODIFIES is not the best fit; the relation is more about triggering an action (sacrifice) based on a condition, which fits PATTERN_OF (a pattern of behavior for Sagas) or OCCURS_IN (the sacrifice occurs in the context of Sagas).
- suggested type: `PATTERN_OF`

### ✅ `keyword.compleated` --[DEPENDS_ON]--> `concept.phyrexian_mana_payment`
- rule_ref: `702.150a`
- verdict: **correct**

### ✅ `action.sacrifice` --[REFERENCES]--> `permanent.permanent`
- rule_ref: `701.17a`
- verdict: **correct**

### ✅ `concept.type_line` --[CONTAINS]--> `concept.supertype`
- rule_ref: `205.1`
- verdict: **correct**

### ⚠️ `concept.subtype` --[PATTERN_OF]--> `concept.artifact_type`
- rule_ref: `205.3g`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is non-canonical; the rule describes artifact types as a specific set of subtypes, which fits the canonical type CONTAINS.
- suggested type: `CONTAINS`

### ✅ `cardtype.dungeon` --[MOVES_TO]--> `zone.command_zone`
- rule_ref: `309.2b`
- verdict: **correct**

### ✅ `concept.state_based_action` --[DEPENDS_ON]--> `concept.priority`
- rule_ref: `704.3`
- verdict: **correct**

### ⚠️ `concept.permanent` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `110.2a`
- verdict: **suspicious**
- issue: The rule describes a permanent entering the battlefield, but MOVES_TO is not the best canonical type; OCCURS_IN is more appropriate for a permanent being on the battlefield.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.attacking_alone` --[DEPENDS_ON]--> `step.declare_attackers`
- rule_ref: `506.5`
- verdict: **suspicious**
- issue: The relation is real but DEPENDS_ON is not the best fit; the concept is defined by an event occurring in that step.
- suggested type: `OCCURS_IN`

### ⚠️ `designation.suspected` --[MODIFIES]--> `keyword.suspect`
- rule_ref: `701.58c`
- verdict: **suspicious**
- issue: The type MODIFIES is not the best fit; the relation is more about how the keyword 'Suspect' defines the state 'suspected'.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.subgame` --[REFERENCES]--> `concept.main_game`
- rule_ref: `727.4a`
- verdict: **suspicious**
- issue: The rule text describes an interaction where abilities in the main game reference events in the subgame, but the relation type 'REFERENCES' is too broad and not the best canonical fit.
- suggested type: `INTERACTS_WITH`

### ⚠️ `keyword.gift_ability` --[PATTERN_OF]--> `keyword.gift_an_octopus`
- rule_ref: `702.174i`
- verdict: **suspicious**
- issue: The type PATTERN_OF is not one of the 8 canonical types. The relation described is that 'Gift an Octopus' is a specific keyword ability that follows the pattern of a 'gift ability'.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.alternative_cost` --[MODIFIES]--> `concept.mana_cost`
- rule_ref: `118.9`
- verdict: **suspicious**
- issue: The relation is real, but MODIFIES is not the best fit because the rule explicitly states that an alternative cost does not change the mana cost; it replaces what is paid.
- suggested type: `REFERENCES`

### ⚠️ `keyword.equip` --[PATTERN_OF]--> `subtype.equipment`
- rule_ref: `301.5`
- verdict: **suspicious**
- issue: PATTERN_OF is not a canonical relation type; the relation is more accurately DEPENDS_ON or REFERENCES.
- suggested type: `DEPENDS_ON`

### ⚠️ `concept.flipping` --[MODIFIES]--> `card_type.flip_card`
- rule_ref: `710.4`
- verdict: **suspicious**
- issue: The rule text does not mention flip cards or how flipping modifies them; it only describes flipping as a one-way process. The relation is real but MODIFIES is not the best fit.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.unblocked_creature` --[MODIFIES]--> `concept.combat_damage`
- rule_ref: `506.4c`
- verdict: **suspicious**
- issue: The relation is not about modification but about a condition preventing an outcome. The rule states an unblocked creature deals no combat damage if its target is removed, which is a conditional interaction, not a modification.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.subgame` --[CONTAINS]--> `zone.library`
- rule_ref: `727.2`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes movement of cards from main-game library to subgame library, not a containment relationship between subgame and library.
- suggested type: `MOVES_TO`

### ❌ `action.flip_face_up` --[OCCURS_IN]--> `keyword.manifest_dread`
- rule_ref: `701.60a`
- verdict: **wrong**
- issue: The rule text defines 'Manifest dread' but does not mention flipping face up, so it does not support the relation.

### ✅ `concept.damage` --[MODIFIES]--> `concept.marked_damage`
- rule_ref: `120.3e`
- verdict: **correct**

### ❌ `concept.different_names` --[CONTAINS]--> `concept.card_name`
- rule_ref: `201.2b`
- verdict: **wrong**
- issue: The rule text explains what 'different names' means but does not state that 'different names' contains 'card name' as a component. The relation is conceptual, not structural.

### ✅ `keyword.renown` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.112a`
- verdict: **correct**

### ❌ `step.declare_blockers` --[OCCURS_IN]--> `action.declare_blockers`
- rule_ref: `508.8`
- verdict: **wrong**
- issue: The rule text describes skipping the step, not establishing that an action occurs within it. The relation is backwards: the action occurs in the step, so it should be step.declare_blockers CONTAINS action.declare_blockers.

### ❌ `keyword.suspend` --[INTERACTS_WITH]--> `keyword.vanishing`
- rule_ref: `702.62a`
- verdict: **wrong**
- issue: The rule text for suspend does not mention vanishing at all, and there is no direct interaction described between the two keywords.

### ✅ `keyword.enlist` --[PATTERN_OF]--> `concept.linked_abilities`
- rule_ref: `702.154b`
- verdict: **correct**

### ✅ `action.plot` --[PATTERN_OF]--> `concept.special_action`
- rule_ref: `116.2k`
- verdict: **correct**

### ✅ `layer.layer_1` --[CONTAINS]--> `layer.layer_1a`
- rule_ref: `613.2a`
- verdict: **correct**

### ✅ `concept.activated_ability` --[CONTAINS]--> `concept.activation_cost`
- rule_ref: `602.1a`
- verdict: **correct**

### ⚠️ `concept.creature_battlefield_attacking` --[INTERACTS_WITH]--> `concept.attacking_player`
- rule_ref: `508.4`
- verdict: **suspicious**
- issue: The relation is real but INTERACTS_WITH is too vague; the rule describes a dependency where the attacking player must be chosen for the creature to be attacking.
- suggested type: `DEPENDS_ON`

### ✅ `action.ring_tempts_you` --[MODIFIES]--> `designation.ring_bearer`
- rule_ref: `701.52a`
- verdict: **correct**

### ⚠️ `concept.saga_card` --[CONTAINS]--> `keyword.read_ahead`
- rule_ref: `714.3a`
- verdict: **suspicious**
- issue: The rule text describes how read ahead works for Saga cards, but it does not state that a Saga card 'contains' the keyword. The relation is more about the keyword being a property or ability that can appear on some Saga cards, which fits the canonical type PATTERN_OF (keyword appears on card type) or MODIFIES (keyword modifies the card's behavior).
- suggested type: `PATTERN_OF`

### ⚠️ `keyword.foretell` --[PATTERN_OF]--> `action.special_action`
- rule_ref: `702.143b`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not canonical; the rule text indicates that foretelling is a specific instance of a special action, which fits OCCURS_IN better.
- suggested type: `OCCURS_IN`

### ⚠️ `card_type.battle` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `310.9`
- verdict: **suspicious**
- issue: The rule text does not mention entering the battlefield; it only discusses attachment restrictions. The MOVES_TO type is not directly supported by this rule.
- suggested type: `OCCURS_IN`

### ❌ `step.declare_defenders` --[OCCURS_IN]--> `phase.combat`
- rule_ref: `507.1`
- verdict: **wrong**
- issue: The rule text describes choosing a defending player in multiplayer, not the relationship between the Declare Defenders step and the Combat phase.

### ✅ `card_type.vanguard` --[MODIFIES]--> `mechanic.hand_modifier`
- rule_ref: `313.6`
- verdict: **correct**

### ⚠️ `ability.reflexive_triggered` --[OCCURS_IN]--> `concept.spell`
- rule_ref: `603.12`
- verdict: **suspicious**
- issue: The relation type OCCURS_IN is not the best fit; the rule describes reflexive triggered abilities being created by spells, not occurring within them.
- suggested type: `DEPENDS_ON`

### ✅ `concept.individual_poison_counters` --[DEPENDS_ON]--> `concept.team_poison_status`
- rule_ref: `810.10d`
- verdict: **correct**

### ⚠️ `concept.ability` --[MODIFIES]--> `action.resolve`
- rule_ref: `405.6c`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes how mana abilities resolve (immediately) rather than modifying the resolve action itself.
- suggested type: `OCCURS_IN`

### ❌ `keyword.transform` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `701.28e`
- verdict: **wrong**
- issue: The rule text describes triggered abilities for 'transforms into' and does not state that transforming only applies to permanents on the battlefield. The relation incorrectly asserts a restriction that is not present in the given rule.

### ✅ `concept.name_sticker` --[PATTERN_OF]--> `concept.text_changing_effect`
- rule_ref: `123.6`
- verdict: **correct**

### ✅ `concept.sorcery_timing` --[DEPENDS_ON]--> `zone.stack`
- rule_ref: `307.5`
- verdict: **correct**

### ❌ `concept.zone_change_trigger` --[REFERENCES]--> `zone.stack`
- rule_ref: `603.6`
- verdict: **wrong**
- issue: The rule text describes zone-change triggers in general, not specifically referencing the Stack zone. The target 'zone.stack' is not mentioned or implied in the given rule text.

### ✅ `concept.life_total` --[MODIFIES]--> `concept.variant.two_headed_giant`
- rule_ref: `103.4a`
- verdict: **correct**

### ❌ `concept.stack` --[OCCURS_IN]--> `step.declare_attackers`
- rule_ref: `506.1`
- verdict: **wrong**
- issue: The rule text describes the structure of the combat phase and its steps, but does not mention the stack or abilities being placed on the stack during the declare attackers step.

### ⚠️ `concept.unlocked_designation` --[DEPENDS_ON]--> `concept.unlock_cost`
- rule_ref: `709.5e`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes that paying the unlock cost results in the unlocked designation, suggesting a causal or enabling relationship, but DEPENDS_ON implies a prerequisite condition. A more precise canonical type might be MODIFIES or PATTERN_OF.
- suggested type: `MODIFIES`

### ⚠️ `keyword.partner` --[CONTAINS]--> `keyword.friends_forever`
- rule_ref: `702.124`
- verdict: **suspicious**
- issue: The relation is not CONTAINS; the rule lists partner abilities, but 'partner' does not contain 'friends forever' as a subset. They are distinct variants under the same umbrella.
- suggested type: `PATTERN_OF`

### ❌ `concept.spell` --[CONTAINS]--> `concept.control`
- rule_ref: `112.2`
- verdict: **wrong**
- issue: The rule text states that every spell has a controller, but it does not state that a spell contains control. The relation type CONTAINS is inappropriate here; the text describes a property or relationship of possession, not containment.

### ⚠️ `concept.triggered_ability` --[MOVES_TO]--> `concept.stack`
- rule_ref: `117.5`
- verdict: **suspicious**
- issue: The rule text states that triggered abilities are put on the stack, which implies a movement, but the canonical type 'MOVES_TO' is typically used for physical movement of objects (like permanents or cards) rather than abstract abilities entering a zone. A more precise canonical type might be 'OCCURS_IN' (since the ability exists on the stack) or 'PATTERN_OF' (as a general behavior pattern).
- suggested type: `OCCURS_IN`

### ✅ `concept.omen_card` --[CONTAINS]--> `concept.omen_alternative_characteristics`
- rule_ref: `720.2`
- verdict: **correct**

### ⚠️ `keyword.evolve` --[CREATES]--> `counter.plus_one_plus_one`
- rule_ref: `702.100a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, but the rule text supports that evolve puts +1/+1 counters.
- suggested type: `MODIFIES`

### ⚠️ `concept.skipping` --[MODIFIES]--> `step.combat_damage`
- rule_ref: `506.1`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes skipping as an action that can happen to the step, which is more like OCCURS_IN or PATTERN_OF.
- suggested type: `OCCURS_IN`

### ✅ `concept.static_ability` --[INTERACTS_WITH]--> `concept.priority`
- rule_ref: `117.2b`
- verdict: **correct**

### ⚠️ `concept.damage` --[MODIFIES]--> `keyword.infect`
- rule_ref: `120.3b`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes how damage from infect sources is replaced with poison counters, which is more like a replacement effect (PATTERN_OF) or a special interaction (INTERACTS_WITH).
- suggested type: `INTERACTS_WITH`

### ❌ `cardtype.fortification` --[CONTAINS]--> `keyword.fortify`
- rule_ref: `702.67b`
- verdict: **wrong**
- issue: The provided rule text does not mention the fortify keyword or support a CONTAINS relation between Fortification and the fortify keyword.

### ⚠️ `keyword.goad` --[CREATES]--> `mechanic.combat_requirement`
- rule_ref: `701.38c`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical; the relation is real but should be a canonical type.
- suggested type: `CREATES`

### ⚠️ `keyword.equip` --[MOVES_TO]--> `card_type.creature`
- rule_ref: `301.5`
- verdict: **suspicious**
- issue: MOVES_TO is not a canonical relation type; the underlying relation is that Equip attaches Equipment to creatures, which is a form of interaction or dependency.
- suggested type: `INTERACTS_WITH`

### ✅ `concept.class_card` --[CONTAINS]--> `keyword.class_level`
- rule_ref: `716.2`
- verdict: **correct**

### ⚠️ `concept.range_of_influence` --[MODIFIES]--> `mechanic.prevention_effect`
- rule_ref: `801.13b`
- verdict: **suspicious**
- issue: Type MODIFIES is not the best fit; the relation is more about limiting scope/range rather than modifying the effect itself
- suggested type: `OCCURS_IN`

### ✅ `keyword.unearth` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `702.84a`
- verdict: **correct**

### ⚠️ `concept.art_sticker` --[PATTERN_OF]--> `concept.sticker`
- rule_ref: `123.9`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not one of the 8 canonical types. The rule text describes Art Sticker as a subtype or specific kind of Sticker.
- suggested type: `CONTAINS`

### ⚠️ `keyword.learn` --[MODIFIES]--> `card_type.lesson`
- rule_ref: `701.45a`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes an interaction where Learn can reveal a Lesson card, which is more like INTERACTS_WITH or REFERENCES.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.plane` --[CONTAINS]--> `concept.planar_deck`
- rule_ref: `103.7`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best canonical fit. The rule describes the planar deck containing plane cards, but the target is the abstract concept 'planar deck', not the specific cards. A more precise canonical type is PATTERN_OF (the planar deck is a pattern/collection of plane cards).
- suggested type: `PATTERN_OF`

### ⚠️ `zone.command` --[PATTERN_OF]--> `zone.public`
- rule_ref: `400.2`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical and not the best fit. The rule states that the command zone is a public zone, indicating a classification or membership relation.
- suggested type: `CONTAINS`

### ✅ `keyword.ascend` --[MODIFIES]--> `concept.citys_blessing`
- rule_ref: `702.131a`
- verdict: **correct**

### ❌ `action.planeswalk` --[OCCURS_IN]--> `zone.command_zone`
- rule_ref: `901.4`
- verdict: **wrong**
- issue: The rule text describes plane/phenomenon cards staying in the command zone, not the action of planeswalking occurring there.

### ⚠️ `concept.team` --[OCCURS_IN]--> `concept.starting_player`
- rule_ref: `103.1a`
- verdict: **suspicious**
- issue: The relation type OCCURS_IN is not the best fit; the rule describes a substitution or replacement relationship, not occurrence.
- suggested type: `MODIFIES`

### ✅ `action.turn_based` --[INTERACTS_WITH]--> `concept.state_based_action`
- rule_ref: `703.3`
- verdict: **correct**

### ⚠️ `concept.face_down_spell` --[CONTAINS]--> `concept.face_down_cast`
- rule_ref: `708.4`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes a temporal/process relationship where face-down casting results in a face-down spell, suggesting a pattern or dependency rather than containment.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.draw_replacement` --[INTERACTS_WITH]--> `concept.card_draw`
- rule_ref: `121.6a`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a replacement effect that specifically modifies the process of drawing a card, making MODIFIES a more precise canonical type.
- suggested type: `MODIFIES`

### ⚠️ `concept.copy` --[CONTAINS]--> `concept.card_type`
- rule_ref: `205.2c`
- verdict: **suspicious**
- issue: The relation type CONTAINS implies a compositional or ownership relationship, but the rule states that copies 'have' card types in the sense of possessing them as attributes, not containing them as parts. A more fitting canonical type might be MODIFIES or PATTERN_OF, but neither perfectly captures 'has attribute'.
- suggested type: `MODIFIES`

### ✅ `concept.team` --[CONTAINS]--> `concept.player`
- rule_ref: `102.3`
- verdict: **correct**

### ✅ `card_type.plane` --[CONTAINS]--> `mechanic.chaos_ability`
- rule_ref: `311.7`
- verdict: **correct**

### ✅ `concept.token` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `111.1`
- verdict: **correct**

### ✅ `concept.text_box` --[CONTAINS]--> `concept.flavor_text`
- rule_ref: `207.2b`
- verdict: **correct**

### ❌ `concept.spell` --[CONTAINS]--> `concept.ownership`
- rule_ref: `112.2`
- verdict: **wrong**
- issue: The rule text states that a spell has an owner, but it does not support that the concept 'spell' contains the concept 'ownership'. CONTAINS implies a compositional or hierarchical relationship, which is not present here.

### ⚠️ `concept.deck` --[PATTERN_OF]--> `concept.limited_play`
- rule_ref: `100.2b`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not the best fit; the rule describes a property of decks in limited play, not that a deck is a pattern of limited play.
- suggested type: `OCCURS_IN`

### ❌ `card_type.conspiracy_card` --[CONTAINS]--> `zone.command_zone`
- rule_ref: `315.6`
- verdict: **wrong**
- issue: The relation direction is reversed; the rule states conspiracy cards begin in the command zone, meaning the command zone contains conspiracy cards, not that conspiracy cards contain the command zone.

### ✅ `keyword.first_strike` --[MODIFIES]--> `step.combat_damage`
- rule_ref: `702.7a`
- verdict: **correct**

### ⚠️ `cardtype.sorcery` --[OCCURS_IN]--> `concept.sorcery_timing`
- rule_ref: `307.5`
- verdict: **suspicious**
- issue: The rule text describes conditions for 'any time they could cast a sorcery' but does not directly state that sorceries occur in sorcery timing; it's more about the concept of sorcery timing referencing sorceries.
- suggested type: `REFERENCES`

### ⚠️ `concept.life_total` --[MODIFIES]--> `concept.variant.archenemy`
- rule_ref: `103.4e`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule text describes a specific starting life total in a variant, which is more about a rule setting than an ongoing modification.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.had_to_attack` --[MODIFIES]--> `step.declare_attackers`
- rule_ref: `506.6`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a condition that is checked during the Declare Attackers Step, which is more like OCCURS_IN or PATTERN_OF.
- suggested type: `OCCURS_IN`

### ⚠️ `ability.linked` --[CONTAINS]--> `ability.triggered`
- rule_ref: `603.11`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes that linked abilities can include triggered abilities, but it's more about composition or inclusion in a broader concept rather than a strict container relationship.
- suggested type: `CONTAINS`

### ❌ `mechanic.block_trigger` --[REFERENCES]--> `concept.blocking_creature`
- rule_ref: `509.3a, 509.3b`
- verdict: **wrong**
- issue: Rule text not found in provided source, so relation cannot be validated.

### ⚠️ `concept.ability` --[CREATES]--> `concept.one_shot_effect`
- rule_ref: `113.2d`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type, but the rule text supports that abilities generate one-shot effects.
- suggested type: `INTERACTS_WITH`

### ❌ `concept.pairing` --[OCCURS_IN]--> `zone.exile`
- rule_ref: `702.95c`
- verdict: **wrong**
- issue: The rule text describes conditions under which pairing does NOT occur, but does not state that pairing occurs in the exile zone. Pairing is a state that exists between creatures on the battlefield, not in exile.

### ✅ `multiplayer_variant.grand_melee` --[DEPENDS_ON]--> `multiplayer_option.limited_range_of_influence`
- rule_ref: `807.2a`
- verdict: **correct**

### ✅ `layer.layer_7` --[CONTAINS]--> `layer.layer_7d`
- rule_ref: `613.4d`
- verdict: **correct**

### ✅ `mechanic.planeswalk` --[OCCURS_IN]--> `card_type.plane`
- rule_ref: `701.24`
- verdict: **correct**

### ✅ `variant.archenemy` --[CONTAINS]--> `deck.scheme_deck`
- rule_ref: `904.3`
- verdict: **correct**

### ❌ `concept.game` --[CONTAINS]--> `concept.player`
- rule_ref: `102.1`
- verdict: **wrong**
- issue: Rule text defines 'player' but does not state that a game contains players; it's a definition, not a containment relation.

### ✅ `concept.game` --[OCCURS_IN]--> `concept.active_player`
- rule_ref: `102.1`
- verdict: **correct**

### ❌ `concept.token` --[CONTAINS]--> `concept.permanent_owner`
- rule_ref: `111.2`
- verdict: **wrong**
- issue: The relation type CONTAINS is inappropriate; the rule describes ownership assignment, not containment.

### ❌ `keyword.melee` --[CREATES]--> `counter.plus_one_plus_one`
- rule_ref: `702.121a`
- verdict: **wrong**
- issue: The rule text describes a temporary +1/+1 boost, not the creation of +1/+1 counters.

### ✅ `keyword.jump_start` --[OCCURS_IN]--> `zone.graveyard`
- rule_ref: `702.133a`
- verdict: **correct**

### ⚠️ `concept.alternate_name` --[MODIFIES]--> `concept.card_name`
- rule_ref: `201.6`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes that the alternate name is distinct and refers to the official card name, which is more like a REFERENCE or PATTERN_OF relation.
- suggested type: `REFERENCES`

### ⚠️ `concept.traditional_magic_card` --[REFERENCES]--> `concept.card_ownership`
- rule_ref: `108.3`
- verdict: **suspicious**
- issue: The relation type REFERENCES is not the best fit; the rule text describes how card ownership is determined for traditional cards, which is more of a DEPENDS_ON or MODIFIES relationship.
- suggested type: `DEPENDS_ON`

### ⚠️ `concept.prototype_spell` --[DEPENDS_ON]--> `concept.prototype_alternative_characteristics`
- rule_ref: `718.3a`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes that a prototyped spell uses its alternative characteristics, which is more like MODIFIES or CONTAINS.
- suggested type: `MODIFIES`

### ⚠️ `keyword.renown` --[CREATES]--> `designation.renowned`
- rule_ref: `702.112b`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type; the underlying relation is real but should be expressed with a canonical type.
- suggested type: `PATTERN_OF`

### ⚠️ `mechanic.block_trigger` --[INTERACTS_WITH]--> `keyword.evasion`
- rule_ref: `509.3f`
- verdict: **suspicious**
- issue: The rule text describes block triggers checking for creature characteristics, but 'evasion' is not explicitly mentioned. The relation is plausible but the type INTERACTS_WITH is vague; a more precise canonical type might be MODIFIES or REFERENCES.
- suggested type: `MODIFIES`

### ⚠️ `keyword.gift_ability` --[MODIFIES]--> `concept.target`
- rule_ref: `702.174m`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a condition for choosing targets, which is more about DEPENDS_ON or OCCURS_IN.
- suggested type: `DEPENDS_ON`

### ✅ `keyword.plot` --[MOVES_TO]--> `zone.exile`
- rule_ref: `702.170a`
- verdict: **correct**

### ❌ `concept.card_part` --[CONTAINS]--> `concept.characteristic`
- rule_ref: `200.3`
- verdict: **wrong**
- issue: The rule states that non-card objects have only the card parts that are also characteristics, implying that characteristics are a subset of card parts, not that card parts contain characteristics.

### ✅ `keyword.bargain` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.166a`
- verdict: **correct**

### ⚠️ `zone.graveyard` --[INTERACTS_WITH]--> `concept.owner`
- rule_ref: `404.1`
- verdict: **suspicious**
- issue: The relation is real but INTERACTS_WITH is too vague; the rule describes a movement to a zone owned by a player.
- suggested type: `MOVES_TO`

### ✅ `concept.mana` --[MOVES_TO]--> `concept.mana_pool`
- rule_ref: `106.4`
- verdict: **correct**

### ✅ `keyword.collect_evidence` --[PATTERN_OF]--> `mechanic.linked_abilities`
- rule_ref: `701.57c`
- verdict: **correct**

### ✅ `keyword.sunburst` --[REFERENCES]--> `counter.plus1_plus1`
- rule_ref: `702.44a`
- verdict: **correct**

### ❌ `card_type.conspiracy` --[CONTAINS]--> `property.owner`
- rule_ref: `905.5`
- verdict: **wrong**
- issue: The rule defines the owner of a conspiracy card, but does not state that the card type 'conspiracy' contains the property 'owner'. The relation is backwards or mischaracterized.

### ⚠️ `concept.spell_resolution` --[MODIFIES]--> `concept.illegal_target`
- rule_ref: `608.2b`
- verdict: **suspicious**
- issue: MODIFIES is not the best fit; the relation is more about how illegal targets affect resolution, not modification.
- suggested type: `INTERACTS_WITH`

### ⚠️ `variant.commander_draft` --[PATTERN_OF]--> `keyword.partner`
- rule_ref: `903.13f`
- verdict: **suspicious**
- issue: The relation type 'PATTERN_OF' is non-canonical, and the rule describes a conditional property assignment rather than a pattern relationship.
- suggested type: `MODIFIES`

### ⚠️ `action.incubate` --[CREATES]--> `token.incubator`
- rule_ref: `701.51a`
- verdict: **suspicious**
- issue: Type 'CREATES' is not canonical; the relation is real but should be 'CREATES' → 'CREATES' is not in the list; closest canonical type is 'CREATES' but since not allowed, suggest 'CREATES' as pattern? Actually canonical types are fixed; 'CREATES' is not one of them. The underlying relation is 'action creates token', which fits 'CREATES' but not canonical. Closest canonical might be 'PATTERN_OF' or 'MODIFIES'? Actually 'CREATES' is a specific action-result, not in list. Suggest 'PATTERN_OF' as generic? But better to flag as suspicious.
- suggested type: `PATTERN_OF`

### ✅ `keyword.venture_into_dungeon` --[MOVES_TO]--> `dungeon.room`
- rule_ref: `701.46b`
- verdict: **correct**

### ✅ `concept.range_of_influence` --[MODIFIES]--> `mechanic.replacement_effect`
- rule_ref: `801.13`
- verdict: **correct**

### ✅ `concept.teammate_hand_review` --[DEPENDS_ON]--> `concept.seating_arrangement`
- rule_ref: `811.5`
- verdict: **correct**

### ⚠️ `concept.outlaw` --[INTERACTS_WITH]--> `concept.crime`
- rule_ref: `700.12a`
- verdict: **suspicious**
- issue: The rule text does not mention 'Crime' at all, so INTERACTS_WITH is not directly supported. The relation might be better as PATTERN_OF or a non-canonical type, but the description suggests an interaction.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.sticker` --[INTERACTS_WITH]--> `concept.melded_permanent`
- rule_ref: `123.5a`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes stickers moving to a melded permanent, which fits MOVES_TO better.
- suggested type: `MOVES_TO`

### ⚠️ `card_type.battle` --[OCCURS_IN]--> `mechanic.protector`
- rule_ref: `310.11a`
- verdict: **suspicious**
- issue: The rule text specifically mentions Sieges, not all Battles, and the relation type OCCURS_IN is not the best fit for the connection between a card type and a mechanic pattern.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.deck` --[INTERACTS_WITH]--> `concept.sideboard`
- rule_ref: `100.4a`
- verdict: **suspicious**
- issue: The relation is real but INTERACTS_WITH is too vague; the rule describes a shared constraint between deck and sideboard, which fits PATTERN_OF (shared pattern/limit) or MODIFIES (mutual restriction).
- suggested type: `PATTERN_OF`

### ⚠️ `concept.mana_ability_trigger` --[REFERENCES]--> `concept.mana_symbol`
- rule_ref: `106.12a`
- verdict: **suspicious**
- issue: The rule text describes triggers for mana abilities, but the relation type 'REFERENCES' is too broad; the more specific canonical type is 'PATTERN_OF' because a mana ability trigger pattern involves mana symbols.
- suggested type: `PATTERN_OF`

### ✅ `keyword.adventure` --[MOVES_TO]--> `zone.exile`
- rule_ref: `715.3d`
- verdict: **correct**

### ✅ `multiplayer_variant.shared_team_turns` --[CONTAINS]--> `multiplayer_mechanic.combined_attack`
- rule_ref: `805.10b`
- verdict: **correct**

### ❌ `concept.card_name` --[REFERENCES]--> `concept.characteristic`
- rule_ref: `201.2`
- verdict: **wrong**
- issue: The rule text does not state that a card's name is a characteristic; it discusses name equivalence and comparisons, not characteristics.

### ⚠️ `card_type.artifact` --[REFERENCES]--> `concept.multiple_card_types`
- rule_ref: `300.2`
- verdict: **suspicious**
- issue: The relation type REFERENCES is not the best fit; the rule text describes artifacts as an example of a card type that can combine with others, which is more about being a component of multiple card types (PATTERN_OF) rather than referencing the concept.
- suggested type: `PATTERN_OF`

### ❌ `concept.life_total` --[DEPENDS_ON]--> `concept.zero_cost`
- rule_ref: `119.1`
- verdict: **wrong**
- issue: Rule text only defines starting life totals for various formats; no mention of zero costs or any dependency between life total and zero costs.

### ✅ `card_type.instant` --[REFERENCES]--> `action.cast_spell`
- rule_ref: `304.1`
- verdict: **correct**

### ✅ `concept.combat_damage_assignment` --[MODIFIES]--> `concept.blocked_creature`
- rule_ref: `510.1c`
- verdict: **correct**

### ✅ `keyword.companion` --[MOVES_TO]--> `zone.hand`
- rule_ref: `702.139a`
- verdict: **correct**

### ⚠️ `zone.command` --[CONTAINS]--> `concept.nontraditional_magic_card`
- rule_ref: `408.3`
- verdict: **suspicious**
- issue: The rule states nontraditional cards start in the command zone, which is a 'starts in' or OCCURS_IN relation, not CONTAINS. CONTAINS implies the zone holds the cards, but the direction is reversed (zone contains cards, not cards contain zone).
- suggested type: `OCCURS_IN`

### ❌ `concept.subgame` --[INTERACTS_WITH]--> `counter.rad`
- rule_ref: `727.4b`
- verdict: **wrong**
- issue: The rule text describes that main-game counters are not part of the subgame and are retained after the subgame ends, but it does not indicate any interaction between the subgame concept and rad counters specifically. The relation incorrectly targets a specific counter type (Rad Counter) without justification.

### ⚠️ `concept.extra_phase` --[INTERACTS_WITH]--> `concept.turn`
- rule_ref: `500.8`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes extra phases being added to a turn, which is better captured by OCCURS_IN.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.response` --[MODIFIES]--> `concept.stack`
- rule_ref: `117.7`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes ordering and resolution, not modification.
- suggested type: `OCCURS_IN`

### ✅ `concept.characteristic_defining_ability` --[MODIFIES]--> `concept.base_toughness`
- rule_ref: `208.2a`
- verdict: **correct**

### ✅ `keyword.transmute` --[DEPENDS_ON]--> `zone.hand`
- rule_ref: `702.53a`
- verdict: **correct**

### ✅ `concept.two_headed_giant` --[MODIFIES]--> `concept.starting_player`
- rule_ref: `800.7`
- verdict: **correct**

### ⚠️ `concept.effect_duration` --[INTERACTS_WITH]--> `phase.ending`
- rule_ref: `500.5`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule text specifically describes when effects expire in relation to phases, which fits OCCURS_IN better.
- suggested type: `OCCURS_IN`

### ✅ `concept.spell_resolution` --[REFERENCES]--> `concept.intervening_if_clause`
- rule_ref: `608.2a`
- verdict: **correct**

### ⚠️ `keyword.vanishing` --[MODIFIES]--> `zone.battlefield`
- rule_ref: `702.63a`
- verdict: **suspicious**
- issue: The type MODIFIES is not the best fit; the rule describes how the keyword affects permanents entering the battlefield, but a more precise canonical type is OCCURS_IN (since vanishing abilities function on the battlefield) or PATTERN_OF (as it defines a behavior pattern).
- suggested type: `OCCURS_IN`

### ✅ `multiplayer_variant.grand_melee` --[DEPENDS_ON]--> `multiplayer_option.attack_left`
- rule_ref: `807.2b`
- verdict: **correct**

### ✅ `keyword.squad` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.157a`
- verdict: **correct**

### ❌ `concept.dependent_effect` --[CONTAINS]--> `concept.dependency_system`
- rule_ref: `613.8a`
- verdict: **wrong**
- issue: The rule text defines when an effect depends on another, but does not state that dependent effects are identified/resolved through the dependency system. The relation direction and type are not supported.

### ✅ `keyword.gift_ability` --[OCCURS_IN]--> `concept.stack`
- rule_ref: `702.174j`
- verdict: **correct**

### ✅ `concept.sector_designation` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `702.158b`
- verdict: **correct**

### ❌ `concept.stack` --[OCCURS_IN]--> `phase.precombat_main`
- rule_ref: `505.6a`
- verdict: **wrong**
- issue: Rule text does not mention the stack at all; it only describes what spells can be cast in the main phase.

### ❌ `concept.state_based_action` --[MODIFIES]--> `concept.token`
- rule_ref: `704.5d`
- verdict: **wrong**
- issue: The rule describes a state-based action that causes tokens to cease to exist, but the relation direction is incorrect; the state-based action modifies the token's existence, but the source and target are reversed for MODIFIES. The correct direction would be token -> MODIFIES -> state_based_action, or a different type like OCCURS_IN.

### ⚠️ `action.reveal` --[PATTERN_OF]--> `action.clash`
- rule_ref: `701.23a`
- verdict: **suspicious**
- issue: PATTERN_OF is not a canonical relation type for this context; the relation is more accurately DEPENDS_ON or OCCURS_IN.
- suggested type: `DEPENDS_ON`

### ⚠️ `action.counter` --[MOVES_TO]--> `zone.graveyard`
- rule_ref: `701.5a`
- verdict: **suspicious**
- issue: The relation type MOVES_TO is not the best fit; the rule describes the result of countering a spell, not the action of countering itself moving to the graveyard.
- suggested type: `PATTERN_OF`

### ⚠️ `keyword.awaken` --[CONTAINS]--> `keyword.haste`
- rule_ref: `702.113a`
- verdict: **suspicious**
- issue: Awaken does not 'contain' Haste as a component; it grants haste as an effect when the condition is met. The relation is real but CONTAINS is not the best fit.
- suggested type: `MODIFIES`

### ✅ `ability.zone_specific_functioning` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `113.6`
- verdict: **correct**

### ⚠️ `concept.extra_turn` --[INTERACTS_WITH]--> `concept.turn`
- rule_ref: `500.7`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes how extra turns are added relative to turns, which is more specific.
- suggested type: `OCCURS_IN`

### ✅ `ability.activated` --[MODIFIES]--> `timing.sorcery`
- rule_ref: `602.5d`
- verdict: **correct**

### ⚠️ `game_type.conspiracy_draft` --[DEPENDS_ON]--> `card_type.conspiracy`
- rule_ref: `905.4`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes that Conspiracy Draft games use conspiracy cards, which is more like OCCURS_IN or CONTAINS.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.range_of_influence` --[MODIFIES]--> `concept.trigger_restriction`
- rule_ref: `801.7`
- verdict: **suspicious**
- issue: MODIFIES is not the best fit; the relation is more about imposing a restriction or condition.
- suggested type: `DEPENDS_ON`

### ❌ `variant.archenemy` --[OCCURS_IN]--> `zone.command_zone`
- rule_ref: `904.4`
- verdict: **wrong**
- issue: The relation is reversed: the rule states that scheme cards (which are part of the Archenemy variant) remain in the command zone, so the correct direction should be from scheme cards to the command zone, not from the variant itself.

### ✅ `concept.player_leaves_game` --[DEPENDS_ON]--> `concept.last_known_information`
- rule_ref: `800.4i`
- verdict: **correct**

### ✅ `card_type.conspiracy` --[MOVES_TO]--> `zone.command`
- rule_ref: `905.4`
- verdict: **correct**

### ⚠️ `concept.mandatory_cost` --[INTERACTS_WITH]--> `concept.optional_cost`
- rule_ref: `118.8b`
- verdict: **suspicious**
- issue: The rule text only distinguishes between mandatory and optional costs but does not explicitly describe an interaction between them. INTERACTS_WITH is not the best fit; a more appropriate type might be PATTERN_OF or REFERENCES.
- suggested type: `PATTERN_OF`

### ❌ `keyword.transform` --[PATTERN_OF]--> `designation.monstrous`
- rule_ref: `701.28f`
- verdict: **wrong**
- issue: The rule text describes a restriction on when a permanent can transform, not that the keyword 'transform' is a pattern of the concept 'monstrous'. There is no relation between these two concepts in the given text.

### ⚠️ `state_action.replacement_multiple` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `704.7`
- verdict: **suspicious**
- issue: The rule text describes a replacement effect for multiple identical state-based actions, but does not explicitly state that this replacement effect occurs in the battlefield zone. The relation is conceptually about the effect's application, not its location.
- suggested type: `MODIFIES`

### ✅ `step.declare_blockers` --[CONTAINS]--> `action.declare_blockers`
- rule_ref: `509.1`
- verdict: **correct**

### ✅ `action.mill` --[MOVES_TO]--> `zone.library`
- rule_ref: `701.13a`
- verdict: **correct**

### ✅ `keyword.soulshift` --[REFERENCES]--> `cardtype.spirit`
- rule_ref: `702.46a`
- verdict: **correct**

### ⚠️ `action.drafting` --[PATTERN_OF]--> `action.face_up_draft`
- rule_ref: `905.2c`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not a canonical type. The rule describes a specific variant (face up drafting) of the general drafting action, which is closer to a 'pattern' or 'subtype' relationship, but the canonical types do not include PATTERN_OF.
- suggested type: `OCCURS_IN`

### ⚠️ `card_type.sorcery` --[REFERENCES]--> `action.cast_spell`
- rule_ref: `307.1`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule text describes that sorceries are cast, which is an action they perform, so a more appropriate canonical type would be 'OCCURS_IN' or 'INTERACTS_WITH'.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.face_down_permanent` --[MODIFIES]--> `concept.transform`
- rule_ref: `712.15a`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule text indicates a restriction or prohibition rather than a modification.
- suggested type: `INTERACTS_WITH`

### ⚠️ `ability.mana` --[CONTAINS]--> `ability.triggered_mana`
- rule_ref: `605.1b`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule defines a subset relationship, but CONTAINS implies a compositional hierarchy rather than a classification hierarchy.
- suggested type: `PATTERN_OF`

### ✅ `keyword.gravestorm` --[REFERENCES]--> `zone.graveyard`
- rule_ref: `702.69a`
- verdict: **correct**

### ⚠️ `keyword.enchant` --[PATTERN_OF]--> `concept.aura`
- rule_ref: `702.5`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not one of the 8 canonical types. The rule text describes 'Enchant' as the defining ability of Auras, which is more accurately a DEPENDS_ON or MODIFIES relationship.
- suggested type: `DEPENDS_ON`

### ⚠️ `keyword.wither` --[REFERENCES]--> `zone.graveyard`
- rule_ref: `702.80b`
- verdict: **suspicious**
- issue: The rule text mentions wither in the context of zone changes, but the relation type REFERENCES is too generic; a more specific canonical type like OCCURS_IN or DEPENDS_ON might better capture the conditional interaction.
- suggested type: `DEPENDS_ON`

### ✅ `card_type.vanguard` --[MODIFIES]--> `mechanic.life_modifier`
- rule_ref: `313.7`
- verdict: **correct**

### ⚠️ `concept.omen_spell` --[PATTERN_OF]--> `concept.omen_card`
- rule_ref: `720.3`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not one of the 8 canonical types. The rule text describes that an Omen spell is a specific way to cast an Omen card, which is more like an OCCURS_IN or MODIFIES relation.
- suggested type: `OCCURS_IN`

### ✅ `concept.double_faced_card` --[CONTAINS]--> `concept.back_face`
- rule_ref: `712.8`
- verdict: **correct**

### ⚠️ `concept.leaves_battlefield` --[PATTERN_OF]--> `concept.zone_change_trigger`
- rule_ref: `603.6c`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not the best fit; the rule describes leaves-the-battlefield triggers as a specific kind of zone-change trigger, suggesting a more hierarchical relationship like CONTAINS or OCCURS_IN.
- suggested type: `CONTAINS`

### ⚠️ `concept.total_cost` --[DEPENDS_ON]--> `concept.mana_ability`
- rule_ref: `601.2g`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes a procedural step (activating mana abilities to pay mana costs), not a dependency between the concepts.
- suggested type: `INTERACTS_WITH`

### ❌ `multiplayer_variant.free_for_all` --[DEPENDS_ON]--> `multiplayer_option.limited_range_of_influence`
- rule_ref: `806.2a`
- verdict: **wrong**
- issue: The rule states that limited range of influence is usually not used in Free-for-All, not that Free-for-All depends on it. The relation direction is incorrect.

### ✅ `card_type.instant` --[MOVES_TO]--> `zone.graveyard`
- rule_ref: `304.2`
- verdict: **correct**

### ❌ `game_type.conspiracy_draft` --[CONTAINS]--> `collection.drafted_cards`
- rule_ref: `905.2b`
- verdict: **wrong**
- issue: The rule text describes adding a drafted card to a player's drafted cards pile, not that Conspiracy Draft contains a drafted cards pile as a conceptual container.

### ⚠️ `keyword.cleave` --[INTERACTS_WITH]--> `action.transform`
- rule_ref: `702.148b`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule text indicates Cleave's ability is a text-changing effect, which is a specific kind of transformation or modification.
- suggested type: `MODIFIES`

### ✅ `keyword.daybound` --[PATTERN_OF]--> `mechanic_pattern.day_night_transform`
- rule_ref: `702.145b`
- verdict: **correct**

### ✅ `object.planar_die` --[CONTAINS]--> `symbol.chaos`
- rule_ref: `901.3a`
- verdict: **correct**

### ✅ `state_action.planeswalker.planar_controller_planeswalks` --[OCCURS_IN]--> `concept.planechase`
- rule_ref: `704.6f`
- verdict: **correct**

### ✅ `keyword.compleated` --[MODIFIES]--> `concept.loyalty_counter_reduction`
- rule_ref: `702.150a`
- verdict: **correct**

### ✅ `keyword.venture_into_dungeon` --[MODIFIES]--> `concept.venture_marker`
- rule_ref: `309.5`
- verdict: **correct**

### ⚠️ `concept.deck` --[PATTERN_OF]--> `concept.commander_deck`
- rule_ref: `100.2c`
- verdict: **suspicious**
- issue: The type PATTERN_OF is not one of the 8 canonical types. The relation describes a specific subtype (Commander deck) of a general concept (deck), which is closer to CONTAINS or a hierarchical subtype relation.
- suggested type: `CONTAINS`

### ❌ `concept.face_down_permanent` --[CONTAINS]--> `concept.looking_at_face_down`
- rule_ref: `708.5`
- verdict: **wrong**
- issue: The rule text describes a permission to look at face-down permanents, not that a face-down permanent contains the concept of looking at face-down objects. The relation direction and type are incorrect.

### ✅ `keyword.exert` --[MODIFIES]--> `phase.untap`
- rule_ref: `701.39a`
- verdict: **correct**

### ⚠️ `variant_option.single_planar_deck` --[DEPENDS_ON]--> `concept.communal_planar_deck`
- rule_ref: `901.15b`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes the single planar deck option using a communal planar deck, which is more like OCCURS_IN or CONTAINS.
- suggested type: `OCCURS_IN`

### ⚠️ `keyword.protection` --[INTERACTS_WITH]--> `keyword.lifelink`
- rule_ref: `702.16e`
- verdict: **suspicious**
- issue: The rule text describes protection preventing damage, which would indirectly prevent lifelink's life gain, but INTERACTS_WITH is too broad; a more precise canonical type like MODIFIES or PATTERN_OF might fit better.
- suggested type: `MODIFIES`

### ❌ `keyword.crew` --[CONTAINS]--> `cardtype.vehicle`
- rule_ref: `702.122`
- verdict: **wrong**
- issue: The relation direction is reversed; the rule states Crew is an ability belonging to Vehicle cards, so Vehicle contains Crew, not Crew contains Vehicle.

### ✅ `concept.additional_cost` --[REFERENCES]--> `concept.mana_cost`
- rule_ref: `118.8d`
- verdict: **correct**

### ✅ `keyword.manifest` --[INTERACTS_WITH]--> `keyword.morph`
- rule_ref: `701.34c`
- verdict: **correct**

### ⚠️ `keyword.skulk` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `702.118a`
- verdict: **suspicious**
- issue: The rule text does not explicitly mention the battlefield, though skulk is an ability that functions on creatures on the battlefield.
- suggested type: `OCCURS_IN`

### ✅ `concept.venture_marker` --[REFERENCES]--> `concept.dungeon_room`
- rule_ref: `309.4`
- verdict: **correct**

### ✅ `concept.marked_damage` --[REFERENCES]--> `concept.lethal_damage`
- rule_ref: `120.6`
- verdict: **correct**

### ⚠️ `keyword.monstrosity` --[CREATES]--> `designation.monstrous`
- rule_ref: `701.31b`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, but the rule text supports that monstrosity action results in the monstrous designation.
- suggested type: `CREATES`

### ✅ `concept.adventure_spell` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `715.3b`
- verdict: **correct**

### ❌ `action.turn_based` --[OCCURS_IN]--> `zone.cleanup_step`
- rule_ref: `703.4n, 703.4p`
- verdict: **wrong**
- issue: Rule text not found in provided source; cannot verify relation.

### ✅ `layer.layer_1` --[CONTAINS]--> `layer.layer_1b`
- rule_ref: `613.2b`
- verdict: **correct**

### ⚠️ `concept.state_trigger` --[MOVES_TO]--> `zone.stack`
- rule_ref: `603.8`
- verdict: **suspicious**
- issue: MOVES_TO implies the source moves to the target, but state triggers (abilities) don't move to the stack; triggered abilities go on the stack, but the pattern itself doesn't move.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.replacement_effect` --[INTERACTS_WITH]--> `concept.timestamp`
- rule_ref: `613.7`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule text specifically states that replacement effects are applied in timestamp order, which is a DEPENDS_ON relation (order dependency).
- suggested type: `DEPENDS_ON`

### ✅ `mechanic.splicing` --[PATTERN_OF]--> `effect.text_changing`
- rule_ref: `612.10`
- verdict: **correct**

### ✅ `keyword.partner` --[CONTAINS]--> `keyword.partner_with`
- rule_ref: `702.124`
- verdict: **correct**

### ✅ `keyword.indestructible` --[INTERACTS_WITH]--> `concept.lethal_damage`
- rule_ref: `702.12b`
- verdict: **correct**

### ✅ `variant.two_headed_giant` --[DEPENDS_ON]--> `concept.team_win_loss`
- rule_ref: `810.8`
- verdict: **correct**

### ⚠️ `concept.cost` --[PATTERN_OF]--> `concept.unpayable_cost`
- rule_ref: `118.6`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is non-canonical; the rule describes a specific subtype or category of cost.
- suggested type: `CONTAINS`

### ❌ `concept.sticker` --[REFERENCES]--> `concept.token`
- rule_ref: `123.1`
- verdict: **wrong**
- issue: The rule text states stickers are not tokens, which contradicts a REFERENCES relation implying a connection or mention; it's a negation, not a reference.

### ✅ `keyword.trample_over_planeswalkers` --[PATTERN_OF]--> `keyword.trample`
- rule_ref: `702.19c`
- verdict: **correct**

### ⚠️ `concept.state_based_action` --[MODIFIES]--> `counter.poison`
- rule_ref: `122.1f`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the state-based action doesn't modify poison counters, it checks their quantity and triggers a loss.
- suggested type: `DEPENDS_ON`

### ❌ `subtype.auras` --[PATTERN_OF]--> `card_type.enchantment`
- rule_ref: `303.1`
- verdict: **wrong**
- issue: The rule text provided does not mention Auras or their relationship to enchantments; it only describes casting enchantments in general.

### ⚠️ `concept.deck` --[PATTERN_OF]--> `concept.constructed_play`
- rule_ref: `100.2a`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not the best fit; the rule describes a pattern (Constructed play) that involves decks, so the direction should be pattern -> concept, not concept -> pattern.
- suggested type: `OCCURS_IN`

### ⚠️ `keyword.multi_headed_giant` --[CONTAINS]--> `keyword.two_headed_giant`
- rule_ref: `810.11`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule describes Multi-Headed Giant variants as extensions of Two-Headed Giant, suggesting a hierarchical or generalization relationship, but CONTAINS implies composition, which is less accurate.
- suggested type: `PATTERN_OF`

### ❌ `concept.transform` --[MODIFIES]--> `concept.melded_permanent`
- rule_ref: `712.16`
- verdict: **wrong**
- issue: The rule text states that melded permanents cannot be turned face down, but it does not describe the 'transform' action modifying melded permanents. Instead, it describes a restriction on turning face down, which is unrelated to the 'transform' action's effect on melded permanents.

### ⚠️ `concept.copiable_values_on_reveal` --[REFERENCES]--> `concept.face_down_zone_change`
- rule_ref: `708.9`
- verdict: **suspicious**
- issue: The rule text describes face-down objects being revealed when changing zones, but the relation type 'REFERENCES' is too generic; a more specific canonical type like 'PATTERN_OF' or 'OCCURS_IN' might better capture that the concept of copiable values on reveal is exemplified or occurs in face-down zone changes.
- suggested type: `PATTERN_OF`

### ✅ `multiplayer_variant.team_vs_team` --[OCCURS_IN]--> `multiplayer_role.defending_team`
- rule_ref: `805.10a`
- verdict: **correct**

### ⚠️ `concept.collector_number` --[INTERACTS_WITH]--> `concept.rarity_letter`
- rule_ref: `213.1b`
- verdict: **suspicious**
- issue: The relation describes a positional or sequential relationship, not an interaction in the game mechanics sense.
- suggested type: `PATTERN_OF`

### ⚠️ `zone.exile` --[INTERACTS_WITH]--> `zone.battlefield`
- rule_ref: `406.5`
- verdict: **suspicious**
- issue: The rule text describes a logistical consideration for tracking exiled cards, not a direct interaction between the zones themselves. The relation type INTERACTS_WITH is too strong and not the best canonical fit.
- suggested type: `MOVES_TO`

### ✅ `effect.continuous` --[PATTERN_OF]--> `effect.replacement`
- rule_ref: `609.6`
- verdict: **correct**

### ⚠️ `effect.modifying_enter_battlefield` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `614.13`
- verdict: **suspicious**
- issue: The relation type MOVES_TO suggests the source moves to the target, but the rule describes how the effect modifies zone changes during battlefield entry, not that the effect itself moves to the battlefield.
- suggested type: `MODIFIES`

### ✅ `keyword.multi_headed_giant` --[MODIFIES]--> `concept.team_life_total`
- rule_ref: `810.11`
- verdict: **correct**

### ❌ `zone.hand` --[PATTERN_OF]--> `zone.hidden`
- rule_ref: `400.2`
- verdict: **wrong**
- issue: The relation is backwards: 'Hand' is an instance of a 'hidden zone', not a pattern of it. The rule states 'hand are hidden zones', meaning hand is a subset/example of hidden zones, not that hand is a pattern of hidden zones.

### ⚠️ `keyword.partner` --[OCCURS_IN]--> `zone.commander`
- rule_ref: `702.124`
- verdict: **suspicious**
- issue: The relation type OCCURS_IN is not the best fit; the rule states commanders begin in the command zone, but the source is the keyword 'partner' itself, not the commanders. The relation is more about enabling or modifying where commanders start.
- suggested type: `MODIFIES`

### ✅ `keyword.mutate` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.140a`
- verdict: **correct**

### ✅ `card_type.vanguard` --[OCCURS_IN]--> `zone.command_zone`
- rule_ref: `902.3`
- verdict: **correct**

### ⚠️ `concept.subtype` --[PATTERN_OF]--> `concept.enchantment_type`
- rule_ref: `205.3h`
- verdict: **suspicious**
- issue: The type 'PATTERN_OF' is not the best fit; the relation is more accurately 'CONTAINS' (subtypes contain enchantment types as a category).
- suggested type: `CONTAINS`

### ✅ `concept.mana_cost` --[CONTAINS]--> `concept.phyrexian_mana_symbol`
- rule_ref: `118.13`
- verdict: **correct**

### ✅ `keyword.flashback` --[MOVES_TO]--> `zone.exile`
- rule_ref: `702.34a`
- verdict: **correct**

### ❌ `concept.skipping` --[MODIFIES]--> `phase.combat`
- rule_ref: `506.1`
- verdict: **wrong**
- issue: The rule text describes the structure of the combat phase and conditions for skipping steps, but does not mention effects causing the entire combat phase to be skipped.

### ⚠️ `effect.continuous` --[DEPENDS_ON]--> `concept.timestamp_creation`
- rule_ref: `613.7a`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes how timestamps are assigned to continuous effects, which is more about OCCURS_IN or PATTERN_OF.
- suggested type: `OCCURS_IN`

### ❌ `keyword.reinforce` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.77b`
- verdict: **wrong**
- issue: The rule text states that the reinforce ability exists in all zones, not specifically in the stack. The relation incorrectly suggests the ability occurs in the stack, which is not supported by the given text.

### ✅ `cardtype.saga` --[INTERACTS_WITH]--> `concept.lore_counter`
- rule_ref: `703.4f`
- verdict: **correct**

### ✅ `keyword.morph` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.37c`
- verdict: **correct**

### ✅ `concept.defending_player` --[OCCURS_IN]--> `phase.combat`
- rule_ref: `506.2`
- verdict: **correct**

### ⚠️ `mechanic.player_control` --[MODIFIES]--> `concept.active_player`
- rule_ref: `721.3`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule states the controlled player 'remains' or 'is still' the active player, indicating no modification of the active player status.
- suggested type: `OCCURS_IN`

### ⚠️ `rule.effect_interaction_order` --[MODIFIES]--> `effect.self_replacement`
- rule_ref: `616.1a`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes ordering priority, not modification.
- suggested type: `OCCURS_IN`

### ✅ `keyword.afterlife` --[OCCURS_IN]--> `zone.graveyard`
- rule_ref: `702.135a`
- verdict: **correct**

### ✅ `concept.spell_proposal` --[DEPENDS_ON]--> `concept.illegal_casting`
- rule_ref: `601.5`
- verdict: **correct**

### ❌ `concept.stack` --[OCCURS_IN]--> `step.upkeep`
- rule_ref: `503.1`
- verdict: **wrong**
- issue: The rule text does not mention the stack occurring in the upkeep step; it only describes triggered abilities being put on the stack at the beginning of the upkeep, not the stack itself occurring in the step.

### ❌ `keyword.fabricate` --[OCCURS_IN]--> `zone.battlefield`
- rule_ref: `702.123a`
- verdict: **wrong**
- issue: The rule text describes what Fabricate does (put counters or create tokens), not where it triggers. The relation incorrectly states Fabricate triggers when a permanent enters the battlefield, but the source is the keyword itself, not an event. OCCURS_IN is misapplied here.

### ⚠️ `concept.combat_damage_step` --[DEPENDS_ON]--> `keyword.first_strike`
- rule_ref: `510.4`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes how the Combat Damage Step's behavior is modified by the presence of First Strike, suggesting MODIFIES or OCCURS_IN.
- suggested type: `MODIFIES`

### ✅ `keyword.disturb` --[OCCURS_IN]--> `action.transform`
- rule_ref: `702.146b`
- verdict: **correct**

### ⚠️ `game_option.shared_team_turns` --[CREATES]--> `team_role.active_team`
- rule_ref: `805.4a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical; the relation is about establishing or defining a concept, which aligns with 'REFERENCES' or 'MODIFIES'.
- suggested type: `REFERENCES`

### ✅ `concept.life_loss` --[MODIFIES]--> `concept.life_total`
- rule_ref: `119.3`
- verdict: **correct**

### ✅ `action.activating_an_ability` --[MOVES_TO]--> `zone.stack`
- rule_ref: `602.2a`
- verdict: **correct**

### ❌ `concept.mana_symbol` --[CONTAINS]--> `concept.snow_mana_symbol`
- rule_ref: `106.11`
- verdict: **wrong**
- issue: The rule text does not support a CONTAINS relation; it describes how snow mana symbols function, not a hierarchical inclusion.

### ✅ `action.fateseal` --[MODIFIES]--> `zone.library`
- rule_ref: `701.22a`
- verdict: **correct**

### ✅ `concept.color_indicator` --[REFERENCES]--> `concept.color`
- rule_ref: `204.2`
- verdict: **correct**

### ✅ `concept.undefined_choice` --[DEPENDS_ON]--> `mechanic.linked_ability`
- rule_ref: `607.5a`
- verdict: **correct**

### ⚠️ `keyword.protection` --[INTERACTS_WITH]--> `concept.state_based_action`
- rule_ref: `702.16c`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too broad; the rule text specifically describes protection causing auras to be put into graveyards via a state-based action, which is better captured by DEPENDS_ON or MODIFIES.
- suggested type: `DEPENDS_ON`

### ⚠️ `mechanic.looking_back_in_time` --[PATTERN_OF]--> `concept.spell`
- rule_ref: `603.10e`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is non-canonical; the rule describes a pattern (looking back in time) that applies to a specific event (a spell being countered), but the target is 'concept.spell' rather than the event itself.
- suggested type: `OCCURS_IN`

### ✅ `keyword.two_headed_giant` --[REFERENCES]--> `concept.team_life_total`
- rule_ref: `810.11`
- verdict: **correct**

### ✅ `keyword.myriad` --[REFERENCES]--> `step.end_of_combat`
- rule_ref: `702.116a`
- verdict: **correct**

### ✅ `phase.ending` --[CONTAINS]--> `step.cleanup`
- rule_ref: `512.1`
- verdict: **correct**

### ⚠️ `game_option.shared_team_turns` --[CREATES]--> `team_role.primary_player`
- rule_ref: `805.2`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical. The rule text describes a definition/assignment that occurs within the context of Shared Team Turns, but the relation is more about establishing a role rather than creating it as an entity.
- suggested type: `CONTAINS`

### ⚠️ `keyword.blitz` --[DEPENDS_ON]--> `concept.additional_cost`
- rule_ref: `702.152b`
- verdict: **suspicious**
- issue: The relation is real but DEPENDS_ON is not the best fit; the rule text describes blitz as an alternative cost, which is a type of additional cost, so a more precise type like CONTAINS or PATTERN_OF might be better.
- suggested type: `CONTAINS`

### ⚠️ `ability.restriction` --[REFERENCES]--> `ability.activated`
- rule_ref: `602.5c`
- verdict: **suspicious**
- issue: The relation type REFERENCES is not the best fit; the rule text describes a restriction applying to a specific acquired ability, which is more like MODIFIES or DEPENDS_ON.
- suggested type: `MODIFIES`

### ✅ `keyword.casualty` --[PATTERN_OF]--> `concept.linked_abilities`
- rule_ref: `702.153a`
- verdict: **correct**

### ✅ `effect.linked_replacement_exile` --[REFERENCES]--> `zone.exile`
- rule_ref: `614.14`
- verdict: **correct**

### ⚠️ `keyword.champion` --[MOVES_TO]--> `zone.exile`
- rule_ref: `702.72a`
- verdict: **suspicious**
- issue: The relation type MOVES_TO is not the best fit; the champion ability exiles a permanent as a cost or condition, not a direct movement effect. The canonical type MODIFIES or INTERACTS_WITH might be more appropriate.
- suggested type: `MODIFIES`

### ✅ `concept.mana` --[REFERENCES]--> `concept.mana_symbol`
- rule_ref: `106.2`
- verdict: **correct**

### ✅ `concept.emblem` --[CONTAINS]--> `concept.static_ability`
- rule_ref: `114.4`
- verdict: **correct**

### ✅ `keyword.improvise` --[OCCURS_IN]--> `zone.stack`
- rule_ref: `702.126a`
- verdict: **correct**

### ✅ `action.proliferate` --[MODIFIES]--> `concept.counter`
- rule_ref: `701.27a`
- verdict: **correct**

### ⚠️ `effect.unpreventable_damage` --[MODIFIES]--> `concept.prevention_shield`
- rule_ref: `615.12`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes how unpreventable damage interacts with prevention shields without reducing them, which is more like INTERACTS_WITH or PATTERN_OF.
- suggested type: `INTERACTS_WITH`

### ❌ `concept.state_based_action` --[REFERENCES]--> `concept.toughness`
- rule_ref: `704.5f, 704.5g`
- verdict: **wrong**
- issue: Rule text not found; cannot verify relation.

### ✅ `action.activating_an_ability` --[DEPENDS_ON]--> `concept.activation_cost`
- rule_ref: `602.2`
- verdict: **correct**

### ❌ `concept.level_symbol` --[DEPENDS_ON]--> `concept.level_up`
- rule_ref: `711.4`
- verdict: **wrong**
- issue: The rule text does not support a DEPENDS_ON relation from Level Symbol to Level Up; it describes that level up abilities exist independently of level symbols.

### ✅ `phase.combat` --[CONTAINS]--> `step.declare_blockers`
- rule_ref: `506.1`
- verdict: **correct**

### ⚠️ `concept.mana_pool` --[MODIFIES]--> `concept.turn`
- rule_ref: `500.4`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a turn-based action that empties the mana pool at specific times, which is more about timing or occurrence than modification.
- suggested type: `OCCURS_IN`

### ✅ `concept.token` --[DEPENDS_ON]--> `concept.token_characteristics`
- rule_ref: `111.3`
- verdict: **correct**

### ✅ `concept.spell_resolution` --[REFERENCES]--> `concept.legal_target`
- rule_ref: `608.2b`
- verdict: **correct**

### ⚠️ `keyword.nightbound` --[MODIFIES]--> `action.transform`
- rule_ref: `702.145f`
- verdict: **suspicious**
- issue: Nightbound triggers a transform action, but MODIFIES is not the best fit; it's more like OCCURS_IN or PATTERN_OF.
- suggested type: `OCCURS_IN`

### ✅ `game_option.deploy_creatures` --[DEPENDS_ON]--> `variant.emperor`
- rule_ref: `804.1`
- verdict: **correct**

### ❌ `concept.planar_controller` --[MODIFIES]--> `card_type.plane`
- rule_ref: `901.6`
- verdict: **wrong**
- issue: The rule text describes who the planar controller is and how it changes, but does not state that the planar controller modifies the Plane card type. The relation is not supported.

### ❌ `counter.rad` --[INTERACTS_WITH]--> `zone.library`
- rule_ref: `726.1`
- verdict: **wrong**
- issue: The rule text describes the triggered ability of rad counters causing a player to mill cards and lose life, but it does not establish any direct interaction between 'counter.rad' and 'zone.library'. The library is mentioned as the zone from which cards are milled, but the relation type INTERACTS_WITH is not supported as the counter itself does not interact with the library; the ability does.
