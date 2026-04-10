# MTGRuler Extraction Validation Report

- Model: `deepseek-chat`
- Sample size: 100 concepts, 100 relations
- Seed: 42
- Generated: 2026-04-09 23:55:44

## Summary

- **Concepts**: correct=56/100 (56%), suspicious=40, wrong=4
- **Relations**: correct=33/100 (33%), suspicious=44, wrong=23

## Concept validation

### ✅ `keyword.foretell` — Foretell (Keyword)
- rule_ref: `702.143`
- verdict: **correct**

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
- issue: Definition is inferred but not explicitly stated in the given source text.
- suggested fix: Definition should be based solely on the provided source text, which only gives the name.

### ✅ `action.convert` — Convert (Action)
- rule_ref: `701.50a`
- verdict: **correct**

### ❌ `concept.attacking` — Attacking (Action)
- rule_ref: `302.5`
- verdict: **wrong**
- issue: Definition describes attacking but source rule only states creatures can attack and block, not when or what they attack.
- suggested fix: Change definition to 'Creatures can attack and block.' or change type to Concept and adjust definition.

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
- suggested fix: Definition should focus on state-based actions for losing conditions (0 or less life, 15+ poison) as per rule 704.6a and 704.6b.

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
- issue: Definition includes extra details not in the source rule text.
- suggested fix: Definition should be: 'A fused split spell has the combined characteristics of its two halves.'

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
- suggested fix: definition_en: To turn a permanent over so that its other face is up. Only transforming tokens and permanents represented by transforming double-faced cards can transform.

### ✅ `multiplayer_mechanic.combined_attack` — Combined Attack (Concept)
- rule_ref: `805.10b`
- verdict: **correct**

### ✅ `mechanic.linked_word_choice` — Linked Word Choice (MechanicPattern)
- rule_ref: `607.2f`
- verdict: **correct**

### ⚠️ `keyword.monstrosity` — Monstrosity (Keyword)
- rule_ref: `701.31`
- verdict: **suspicious**
- issue: Definition omits the 'N' parameter and the conditional 'if it isn't already monstrous' structure.
- suggested fix: Definition should reflect the conditional and parameter: 'If a permanent isn't monstrous, put N +1/+1 counters on it and it becomes monstrous. Monstrous is a designation marker.'

### ✅ `concept.consolation_owner` — Conspiracy Card Owner (Concept)
- rule_ref: `315.6`
- verdict: **correct**

### ✅ `concept.target_restriction` — Target Restriction (Range of Influence) (Concept)
- rule_ref: `801.4`
- verdict: **correct**

### ✅ `variant.super_villain_rumble` — Supervillain Rumble (Variant)
- rule_ref: `904.12`
- verdict: **correct**

### ⚠️ `game_option.shared_team_turns` — Shared Team Turns (Concept)
- rule_ref: `805`
- verdict: **suspicious**
- issue: Definition is inferred/extended beyond the source text, which only provides the name.
- suggested fix: Definition should be based on the source text. Could be 'A multiplayer option where teams take turns collectively.' or similar, but the full definition provided is not directly supported by the given source.

### ⚠️ `concept.copiable_values_on_reveal` — Copiable Values on Reveal (Concept)
- rule_ref: `708.8`
- verdict: **suspicious**
- issue: Definition omits important details about abilities relating to entering the battlefield.
- suggested fix: When a face-down permanent is turned face up, its copiable values revert to normal, applied effects still apply, and abilities relating to entering the battlefield don't trigger or have effect.

### ✅ `keyword.goad` — Goad (Keyword)
- rule_ref: `701.38`
- verdict: **correct**

### ⚠️ `keyword.doctors_companion` — Doctor's companion (Keyword)
- rule_ref: `702.124m`
- verdict: **suspicious**
- issue: Definition omits 'cards' and uses 'creatures' instead of 'creature cards', and uses 'commander' instead of 'your commander'.
- suggested fix: Definition should be: 'You may designate two legendary creature cards as your commander rather than one if one of them is this card and the other is a legendary Time Lord Doctor creature card that has no other creature types.'

### ✅ `concept.combat_ending` — Ending the Combat Phase (MechanicPattern)
- rule_ref: `722.2-722.2g`
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
- issue: Definition is slightly off; source text describes cards for casual play, not the concept of casual play itself.
- suggested fix: Definition should focus on the cards intended for casual play, not the play format. E.g., 'Cards intended for non-tournament play, with features not covered by standard rules, including silver-bordered and acorn-stamped cards.'

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
- issue: Definition is incomplete and slightly misleading. It only mentions 'card or spell' and 'card's owner unless it is a copy', but the source text details specific rules for spell ownership (especially for copies) and introduces the concept of a spell's controller.
- suggested fix: Refine definition to more accurately reflect the source: 'The player who owns a card or spell. For a spell, this is the owner of the card that represents it, unless it is a copy. For a copy of a spell, the owner is the player under whose control it was put on the stack.'

### ✅ `concept.control_of_copy` — Control of Copy (Concept)
- rule_ref: `707.10`
- verdict: **correct**

### ✅ `keyword.modular` — Modular (Keyword)
- rule_ref: `702.43`
- verdict: **correct**

### ✅ `concept.front_face_symbol` — Front-Face Symbol (Concept)
- rule_ref: `712.2a`
- verdict: **correct**

### ⚠️ `game_rule.archenemy` — Archenemy (Concept)
- rule_ref: `703.4e`
- verdict: **suspicious**
- issue: Definition oversimplifies and omits reference to rule 904 for full variant details.
- suggested fix: Special multiplayer variant where one player (the archenemy) has a scheme deck and sets the top scheme in motion immediately after their precombat main phase begins. See rule 904.

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

### ✅ `keyword.mentor` — Mentor (Keyword)
- rule_ref: `702.134`
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
- issue: Definition is incomplete; it omits that a legal target must also still satisfy the spell/ability's targeting restrictions.
- suggested fix: Change definition to: A target that remains in the zone it was in when targeted and still satisfies the spell or ability's targeting restrictions.

### ✅ `concept.party` — Party (Concept)
- rule_ref: `700.8`
- verdict: **correct**

### ⚠️ `concept.alternate_name` — Alternate Name (Secondary Title) (Concept)
- rule_ref: `201.6`
- verdict: **suspicious**
- issue: Definition incorrectly states the alternate name has no effect on gameplay, deck construction, or rules. The source rule states the card's name for all purposes is the one in the secondary title bar, and the alternate name is the one in the upper left corner.
- suggested fix: Definition should clarify: The alternate name appears in the upper left corner and is used only for display. The card's true name for all game purposes is the one in the secondary title bar.

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
- issue: definition omits the delayed triggered ability (exile at end of combat) and the 'or a planeswalker they control' wording.
- suggested fix: definition should include: '...attacking that opponent or a planeswalker they control. Exile the tokens at end of combat.'

### ✅ `concept.total_toxic_value` — Total Toxic Value (Concept)
- rule_ref: `702.164b`
- verdict: **correct**

### ✅ `action.fateseal` — Fateseal (Action)
- rule_ref: `701.22`
- verdict: **correct**

### ✅ `keyword.retrace` — Retrace (Keyword)
- rule_ref: `702.81`
- verdict: **correct**

### ✅ `concept.permanent_card` — Permanent Card (Concept)
- rule_ref: `110.4a`
- verdict: **correct**

### ✅ `concept.lit_up_numbers` — Lit-Up Numbers (Concept)
- rule_ref: `717.1`
- verdict: **correct**

### ❌ `mechanic.venture_marker` — Venture Marker (MechanicPattern)
- rule_ref: `701.46a`
- verdict: **wrong**
- issue: The source rule text does not define 'Venture Marker' as a concept; it only mentions a 'venture marker' in passing as part of the venture mechanic.
- suggested fix: Change type to 'Keyword' or 'Action' and adjust definition to describe the action of venturing into the dungeon, or remove as a standalone concept.

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

### ❌ `zone.battlefield` — Battlefield (Zone)
- rule_ref: `112.1`
- verdict: **wrong**
- issue: Rule 112.1 is about spells, not the battlefield zone.
- suggested fix: Use rule 400.1 or 400.2 for the battlefield zone definition.

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
- issue: Definition is overly broad; source text lists specific ways to lose, not just 'condition that eliminates'.
- suggested fix: Definition should reference the various conditions (life total, poison, drawing from empty library, etc.) that cause a player to lose.

### ⚠️ `concept.meld` — Meld (Action)
- rule_ref: `701.37`
- verdict: **suspicious**
- issue: Definition omits that meld is a keyword action and that the cards are put onto the battlefield from their current zones.
- suggested fix: Meld is a keyword action that appears on one card in a meld pair. To meld, put the two cards from the pair onto the battlefield with their back faces up and combined into a single permanent.

### ⚠️ `keyword.reinforce` — Reinforce (Keyword)
- rule_ref: `702.77a`
- verdict: **suspicious**
- issue: Definition omits 'Reinforce N—[cost]' structure and incorrectly states 'persists in all zones'.
- suggested fix: Definition should be: "An activated ability 'Reinforce N—[cost]' which means '[Cost], Discard this card: Put N +1/+1 counters on target creature.' Functions only while the card is in a player's hand."

### ✅ `concept.multiple_card_types` — Multiple Card Types (Concept)
- rule_ref: `300.2`
- verdict: **correct**

### ✅ `keyword.collect_evidence` — Collect Evidence (Keyword)
- rule_ref: `701.57`
- verdict: **correct**

### ⚠️ `concept.variant.archenemy` — Archenemy Variant (Concept)
- rule_ref: `103.4e`
- verdict: **suspicious**
- issue: Definition includes schemes and higher life total, but source only mentions life total.
- suggested fix: Definition should focus on the life total rule, or reference the broader variant definition elsewhere.

### ✅ `multiplayer_variant.grand_melee` — Grand Melee (Variant)
- rule_ref: `807.1`
- verdict: **correct**

### ⚠️ `cardtype.attraction` — Attraction (CardType)
- rule_ref: `717`
- verdict: **suspicious**
- issue: Definition includes details not present in the source rule text.
- suggested fix: Definition should be based solely on the provided source text. Suggested: 'A card type for Attraction cards.'

### ✅ `keyword.behold` — Behold (Keyword)
- rule_ref: `701.61`
- verdict: **correct**

### ⚠️ `keyword.daybound` — Daybound (Keyword)
- rule_ref: `702.145b`
- verdict: **suspicious**
- issue: Definition is a slightly imprecise paraphrase; it says 'three static abilities on transforming double-faced card front faces that cause transformation at night and prevent other transformations.' The source text is more specific about the timing and conditions.
- suggested fix: Definition should more closely match the source: "Daybound' means 'If it is night and this permanent is represented by a transforming double-faced card, it enters transformed,' 'As it becomes night, if this permanent is front face up, transform it,' and 'This permanent can’t transform except due to its daybound ability.'"

### ⚠️ `card_type.kindred` — Kindred (CardType)
- rule_ref: `300.1`
- verdict: **suspicious**
- issue: Definition adds details not present in source rule text.
- suggested fix: Definition should be a simple description like 'A card type.' or match the list-only nature of the source.

### ⚠️ `concept.flipping` — Flipping (MechanicPattern)
- rule_ref: `710.4`
- verdict: **suspicious**
- issue: Definition omits key details about memory of status when leaving battlefield.
- suggested fix: Add 'If it leaves the battlefield, it retains no memory of its flipped status.' to the definition.

### ❌ `concept.copy_spell` — Copy Spell (Concept)
- rule_ref: `706.2`
- verdict: **wrong**
- issue: Source rule text is about die rolls, not copying spells.
- suggested fix: Check correct rule reference for 'Copy Spell' concept.

### ✅ `concept.substitute_card` — Substitute Card (Concept)
- rule_ref: `713.1`
- verdict: **correct**

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

### ✅ `keyword.intimidate` — Intimidate (Keyword)
- rule_ref: `702.13`
- verdict: **correct**

### ⚠️ `ability.evasion` — Evasion Ability (MechanicPattern)
- rule_ref: `702.9a`
- verdict: **suspicious**
- issue: Definition is a general description, but source text only states 'Flying is an evasion ability.' as an example, not a definition.
- suggested fix: Definition should be more general, e.g., 'An ability that makes a creature harder to block, such as flying.'

### ⚠️ `card_type.lesson` — Lesson (CardType)
- rule_ref: `701.45a`
- verdict: **suspicious**
- issue: Definition incorrectly states Lesson is a card type found in the Sideboard; source rule says 'Lesson card you own from outside the game'.
- suggested fix: Change definition to: A card subtype that can be revealed from outside the game and put into your hand via the Learn keyword action.

### ✅ `concept.constructed_play` — Constructed play (MechanicPattern)
- rule_ref: `100.2a`
- verdict: **correct**

### ⚠️ `keyword.hideaway` — Hideaway (Keyword)
- rule_ref: `702.75a`
- verdict: **suspicious**
- issue: Definition slightly misstates the look-at rights; source says exiled card gains ability granting look-at rights to the controlling player, not 'grants look-at rights to players who control the hiding permanent'.
- suggested fix: Change definition to: When this permanent enters, look at the top N cards of your library, exile one face down, and put the rest on the bottom in random order. The exiled card gains 'The player who controls the permanent that exiled this card may look at this card in the exile zone.'

### ✅ `zone.command` — Command (Zone)
- rule_ref: `400.1`
- verdict: **correct**

### ✅ `concept.card_type` — Card Type (CardType)
- rule_ref: `205.2-205.2c`
- verdict: **correct**

## Relation validation

### ⚠️ `mechanic.linked_multicard` --[OCCURS_IN]--> `concept.spell_resolution`
- rule_ref: `607.3`
- verdict: **suspicious**
- issue: The rule text describes how multiple exiled cards are handled during resolution, but the relation type OCCURS_IN is not the best fit. The mechanic pattern occurs *during* resolution, but the rule is more about how the mechanic interacts with the resolution process.
- suggested type: `INTERACTS_WITH`

### ⚠️ `game_type.conspiracy_draft` --[DEPENDS_ON]--> `card_type.conspiracy`
- rule_ref: `905.4`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes that Conspiracy Draft games use conspiracy cards, which is more like OCCURS_IN or CONTAINS.
- suggested type: `OCCURS_IN`

### ✅ `keyword.dash` --[MODIFIES]--> `keyword.haste`
- rule_ref: `702.109a`
- verdict: **correct**

### ⚠️ `keyword.amass` --[CREATES]--> `token.army`
- rule_ref: `701.44a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, but the rule text does describe creating an Army token.
- suggested type: `CREATES`

### ⚠️ `concept.melded_permanent` --[MODIFIES]--> `concept.front_face`
- rule_ref: `712.8g`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a property (mana value) derived from the front faces, which is more like a DEPENDS_ON or REFERENCES.
- suggested type: `DEPENDS_ON`

### ✅ `card_type.instant` --[MOVES_TO]--> `zone.graveyard`
- rule_ref: `304.2`
- verdict: **correct**

### ❌ `concept.cost` --[CONTAINS]--> `concept.mana_cost`
- rule_ref: `118.2`
- verdict: **wrong**
- issue: The rule text describes that a cost 'may include' mana payments, but the relation direction is reversed: mana cost is a component of cost, not the other way around. CONTAINS implies source contains target, but here the target (mana cost) is contained within the source (cost).

### ⚠️ `concept.response` --[MODIFIES]--> `concept.stack`
- rule_ref: `117.7`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes ordering and resolution, not modification.
- suggested type: `OCCURS_IN`

### ⚠️ `keyword.venture_into_dungeon` --[DEPENDS_ON]--> `mechanic.venture_marker`
- rule_ref: `701.46a`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule describes the action of placing the venture marker, which is more of an OCCURS_IN or PATTERN_OF relationship.
- suggested type: `OCCURS_IN`

### ✅ `keyword.surveil` --[MOVES_TO]--> `zone.library`
- rule_ref: `701.42a`
- verdict: **correct**

### ⚠️ `keyword.offspring` --[CREATES]--> `concept.token`
- rule_ref: `702.175a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical; the relation is real but should be a canonical type.
- suggested type: `CREATES`

### ✅ `keyword.companion` --[PATTERN_OF]--> `action.special_action`
- rule_ref: `702.139a`
- verdict: **correct**

### ⚠️ `rule.effect_interaction_order` --[MODIFIES]--> `effect.self_replacement`
- rule_ref: `616.1a`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes ordering priority, not modification.
- suggested type: `OCCURS_IN`

### ❌ `keyword.read_ahead` --[DEPENDS_ON]--> `concept.lore_counter`
- rule_ref: `702.155a`
- verdict: **wrong**
- issue: The rule text does not mention lore counters at all; it only describes the timing restriction for chapter ability triggers.

### ✅ `concept.game` --[CONTAINS]--> `concept.multiplayer_game`
- rule_ref: `100.1b`
- verdict: **correct**

### ✅ `keyword.shadow` --[PATTERN_OF]--> `keyword.evasion`
- rule_ref: `702.28a`
- verdict: **correct**

### ✅ `keyword.transmute` --[DEPENDS_ON]--> `zone.hand`
- rule_ref: `702.53a`
- verdict: **correct**

### ❌ `concept.game` --[CONTAINS]--> `concept.deck`
- rule_ref: `100.2`
- verdict: **wrong**
- issue: The rule describes what players need to play the game, not that the game contains decks. The relation direction is backwards: decks are used in the game, not contained by it.

### ⚠️ `card_type.sorcery` --[REFERENCES]--> `action.cast_spell`
- rule_ref: `307.1`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule text describes that sorceries are cast, which is an action they perform, so a more appropriate canonical type would be 'INTERACTS_WITH' or 'OCCURS_IN'.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.extra_turn` --[INTERACTS_WITH]--> `concept.turn`
- rule_ref: `500.7`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes how extra turns are added relative to turns, which is more specific.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.sticker` --[INTERACTS_WITH]--> `concept.melded_permanent`
- rule_ref: `123.5a`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes stickers moving to a melded permanent, which fits MOVES_TO better.
- suggested type: `MOVES_TO`

### ❌ `concept.back_face` --[CONTAINS]--> `concept.double_faced_card`
- rule_ref: `712.8`
- verdict: **wrong**
- issue: The relation direction is reversed: a double-faced card contains a back face, not the other way around.

### ⚠️ `keyword.escalate` --[MODIFIES]--> `action.cast`
- rule_ref: `702.120a`
- verdict: **suspicious**
- issue: The type MODIFIES is not the best fit; the relation is more about adding an additional cost to an action (casting) when choosing modes, which aligns better with MODIFIES but the canonical type INTERACTS_WITH might be more appropriate as it describes a keyword affecting an action.
- suggested type: `INTERACTS_WITH`

### ✅ `layer.layer_7` --[CONTAINS]--> `layer.layer_7c`
- rule_ref: `613.4c`
- verdict: **correct**

### ✅ `concept.type_line` --[CONTAINS]--> `concept.supertype`
- rule_ref: `205.1`
- verdict: **correct**

### ⚠️ `mechanic.restart_game` --[MODIFIES]--> `game_option.limited_range_of_influence`
- rule_ref: `801.17`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule states that restart game effects are exempt from limited range of influence, which is more accurately a DEPENDS_ON or INTERACTS_WITH relation.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.drawing_the_game` --[OCCURS_IN]--> `concept.limited_range_of_influence`
- rule_ref: `104.4e`
- verdict: **suspicious**
- issue: The relation type OCCURS_IN is not the best fit; the rule describes how a draw effect is modified by Limited Range of Influence, so MODIFIES is more accurate.
- suggested type: `MODIFIES`

### ✅ `concept.game` --[CONTAINS]--> `concept.supplementary_deck`
- rule_ref: `100.2d`
- verdict: **correct**

### ✅ `card_type.phenomenon` --[MOVES_TO]--> `zone.command_zone`
- rule_ref: `312.2`
- verdict: **correct**

### ❌ `concept.blocked_creature` --[REFERENCES]--> `mechanic.attack_and_unblocked_trigger`
- rule_ref: `509.3g`
- verdict: **wrong**
- issue: The rule text explains when an 'attacks and isn't blocked' ability triggers, but it does not reference the concept of a 'blocked creature' as a source. The relation is backwards: the mechanic references the concept, not the concept references the mechanic.

### ⚠️ `concept.convert` --[MODIFIES]--> `concept.transforming_double_faced_card`
- rule_ref: `712.9`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule text states that only transforming double-faced cards can convert, which is more of a DEPENDS_ON or OCCURS_IN relation.
- suggested type: `DEPENDS_ON`

### ❌ `concept.life_total` --[DEPENDS_ON]--> `concept.zero_cost`
- rule_ref: `119.1`
- verdict: **wrong**
- issue: Rule text only defines starting life totals for various formats; no mention of zero costs or any dependency between life total and zero costs.

### ⚠️ `card_type.kindred` --[REFERENCES]--> `card_type.creature`
- rule_ref: `300.2b`
- verdict: **suspicious**
- issue: The relation type 'REFERENCES' is not the best fit; the rule states that a Kindred card has another card type, which is a direct inclusion relationship.
- suggested type: `CONTAINS`

### ✅ `variant.emperor` --[DEPENDS_ON]--> `concept.range_of_influence`
- rule_ref: `809.3a`
- verdict: **correct**

### ❌ `concept.state_based_action` --[MODIFIES]--> `concept.siege`
- rule_ref: `704.5x`
- verdict: **wrong**
- issue: The rule text describes a state-based action that modifies the protector of a Siege, not the Siege itself. The relation incorrectly targets 'concept.siege' instead of the protector role or player.

### ⚠️ `concept.permanent` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `110.2a`
- verdict: **suspicious**
- issue: The rule describes a permanent entering the battlefield, but MOVES_TO implies a transition from one zone to another, which is not explicitly stated here. The rule focuses on control upon entry, not the movement itself.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.merged_permanent` --[INTERACTS_WITH]--> `concept.token`
- rule_ref: `728.2d`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a conditional property (token status) based on composition, which fits PATTERN_OF better.
- suggested type: `PATTERN_OF`

### ⚠️ `concept.ability` --[CREATES]--> `concept.one_shot_effect`
- rule_ref: `113.2d`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type, but the rule text supports that abilities generate one-shot effects.
- suggested type: `INTERACTS_WITH`

### ❌ `subtype.auras` --[PATTERN_OF]--> `card_type.enchantment`
- rule_ref: `303.1`
- verdict: **wrong**
- issue: The rule text provided does not mention Auras or their relationship to enchantments; it only describes casting enchantments in general.

### ✅ `keyword.bands_with_other` --[PATTERN_OF]--> `keyword.banding`
- rule_ref: `702.22b`
- verdict: **correct**

### ⚠️ `designation.ring_bearer` --[REFERENCES]--> `emblem.the_ring`
- rule_ref: `701.52c`
- verdict: **suspicious**
- issue: The relation is real but the type REFERENCES is not the best fit; the emblem grants abilities to the Ring-bearer, which is more like MODIFIES or INTERACTS_WITH.
- suggested type: `MODIFIES`

### ❌ `action.shuffle` --[OCCURS_IN]--> `action.planeswalk`
- rule_ref: `701.24b`
- verdict: **wrong**
- issue: The rule text describes planeswalking as moving cards to the bottom of the planar deck and turning the top card face up, but it does not mention shuffling. The relation incorrectly claims that planeswalking involves shuffling, which is not supported by the given rule.

### ✅ `keyword.ravenous` --[PATTERN_OF]--> `concept.triggered_ability`
- rule_ref: `702.156a`
- verdict: **correct**

### ⚠️ `concept.triggered_ability` --[MOVES_TO]--> `concept.stack`
- rule_ref: `117.5`
- verdict: **suspicious**
- issue: The rule text describes triggered abilities being put on the stack, but MOVES_TO is not the best canonical type; OCCURS_IN is more appropriate for abilities existing on the stack.
- suggested type: `OCCURS_IN`

### ⚠️ `keyword.poisonous` --[CREATES]--> `counter.poison`
- rule_ref: `702.70a`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical; the relation is that the keyword ability results in poison counters being placed.
- suggested type: `CREATES`

### ⚠️ `action.play` --[MOVES_TO]--> `zone.stack`
- rule_ref: `701.14b`
- verdict: **suspicious**
- issue: The rule text does not explicitly mention moving to the stack; it defines 'play' but doesn't describe the zone change. The relation is real but the given rule text doesn't support MOVES_TO directly.
- suggested type: `MOVES_TO`

### ⚠️ `action.exchange` --[INTERACTS_WITH]--> `action.attach`
- rule_ref: `701.10e`
- verdict: **suspicious**
- issue: The type INTERACTS_WITH is too generic; the rule describes a specific dependency where an Exchange action causes an Attach action to occur.
- suggested type: `DEPENDS_ON`

### ⚠️ `concept.spell_to_token` --[CREATES]--> `concept.token`
- rule_ref: `111.13`
- verdict: **suspicious**
- issue: Type 'CREATES' is non-canonical, but the rule text describes a conversion from a spell copy to a token, which aligns with the pattern.
- suggested type: `PATTERN_OF`

### ⚠️ `keyword.renown` --[CREATES]--> `designation.renowned`
- rule_ref: `702.112b`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type; the underlying relation is real but should be expressed with a canonical type.
- suggested type: `PATTERN_OF`

### ✅ `layer.layer_7` --[CONTAINS]--> `layer.layer_7b`
- rule_ref: `613.4b`
- verdict: **correct**

### ⚠️ `concept.merged_permanent_sticker` --[INTERACTS_WITH]--> `concept.timestamp`
- rule_ref: `613.7k`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is too vague; the rule describes a timestamp being assigned to a sticker when its object becomes part of a merged permanent, which is more specifically a MODIFIES relation (the sticker's timestamp is modified).
- suggested type: `MODIFIES`

### ⚠️ `keyword.casualty` --[MODIFIES]--> `concept.copy_spell`
- rule_ref: `702.153a`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the casualty ability creates a copy, which is more like an interaction or a pattern of behavior.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.state_based_action` --[MODIFIES]--> `concept.counter_cancellation`
- rule_ref: `704.5q`
- verdict: **suspicious**
- issue: MODIFIES is not the best canonical type; the relation is more about performing an action that results in removal, which fits OCCURS_IN or PATTERN_OF better.
- suggested type: `OCCURS_IN`

### ⚠️ `concept.alternative_cost` --[INTERACTS_WITH]--> `concept.additional_cost`
- rule_ref: `118.9d`
- verdict: **suspicious**
- issue: The relation type INTERACTS_WITH is vague; the rule describes how additional costs apply to an alternative cost, which is more specifically a DEPENDS_ON or MODIFIES relationship.
- suggested type: `MODIFIES`

### ⚠️ `keyword.fabricate` --[CREATES]--> `token.servo`
- rule_ref: `702.123a`
- verdict: **suspicious**
- issue: CREATES is not a canonical relation type, but the underlying relation is real.
- suggested type: `CREATES`

### ✅ `concept.static_ability` --[INTERACTS_WITH]--> `concept.priority`
- rule_ref: `117.2b`
- verdict: **correct**

### ✅ `keyword.forage` --[REFERENCES]--> `zone.graveyard`
- rule_ref: `701.59a`
- verdict: **correct**

### ❌ `keyword.delve` --[DEPENDS_ON]--> `cost.alternative`
- rule_ref: `702.66b`
- verdict: **wrong**
- issue: The rule text explicitly states that delve is NOT an alternative cost, so a DEPENDS_ON relation from delve to alternative cost is not supported.

### ❌ `concept.stack` --[OCCURS_IN]--> `step.combat_damage`
- rule_ref: `506.1`
- verdict: **wrong**
- issue: The rule text describes the combat damage step as part of the combat phase, not that the stack occurs in the combat damage step. The relation is backwards or misattributed.

### ⚠️ `state.phased_out` --[DEPENDS_ON]--> `keyword.phasing`
- rule_ref: `702.26b`
- verdict: **suspicious**
- issue: The relation type DEPENDS_ON is not the best fit; the rule text describes the state 'phased out' as a consequence or status defined by the keyword 'phasing', suggesting a more precise type like OCCURS_IN or PATTERN_OF.
- suggested type: `OCCURS_IN`

### ❌ `cardtype.fortification` --[CONTAINS]--> `keyword.fortify`
- rule_ref: `702.67b`
- verdict: **wrong**
- issue: The provided rule text does not mention the fortify keyword or support a CONTAINS relation between Fortification and the fortify keyword.

### ⚠️ `keyword.partner` --[CONTAINS]--> `keyword.choose_a_background`
- rule_ref: `702.124`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best fit; the rule lists 'choose a Background' as one of the partner abilities, suggesting a grouping or categorization rather than containment.
- suggested type: `PATTERN_OF`

### ✅ `keyword.foretell` --[DEPENDS_ON]--> `cost.alternative`
- rule_ref: `702.143a`
- verdict: **correct**

### ⚠️ `concept.range_of_influence` --[MODIFIES]--> `concept.information_restriction`
- rule_ref: `801.11`
- verdict: **suspicious**
- issue: MODIFIES is not the best fit; the relation is more about how range of influence restricts information gathering, which aligns with DEPENDS_ON or OCCURS_IN.
- suggested type: `DEPENDS_ON`

### ❌ `keyword.crew` --[CONTAINS]--> `cardtype.vehicle`
- rule_ref: `702.122`
- verdict: **wrong**
- issue: The relation direction is reversed; the rule states Crew is an ability belonging to Vehicle cards, so Vehicle contains Crew, not Crew contains Vehicle.

### ✅ `ability.characteristic_defining` --[OCCURS_IN]--> `layer.layer_7a`
- rule_ref: `613.4a`
- verdict: **correct**

### ❌ `mechanic.attack_and_unblocked_trigger` --[REFERENCES]--> `concept.unblocked_creature`
- rule_ref: `508.3f, 509.3g`
- verdict: **wrong**
- issue: Rule text not found in provided source; cannot validate relation.

### ✅ `concept.venture_marker` --[REFERENCES]--> `concept.dungeon_room`
- rule_ref: `309.4`
- verdict: **correct**

### ⚠️ `ability.triggered` --[MODIFIES]--> `concept.intervening_if_clause`
- rule_ref: `603.4`
- verdict: **suspicious**
- issue: MODIFIES is not the best canonical type; the relation is more about how triggered abilities can contain or use an intervening 'if' clause pattern.
- suggested type: `PATTERN_OF`

### ✅ `concept.life_total` --[MODIFIES]--> `concept.variant.two_headed_giant`
- rule_ref: `103.4a`
- verdict: **correct**

### ❌ `concept.double_faced_card` --[CONTAINS]--> `concept.transforming_double_faced_card`
- rule_ref: `712.3`
- verdict: **wrong**
- issue: The rule text provided (712.3) is about modal double-faced cards, not transforming double-faced cards, so it does not support the relation between double-faced cards and transforming double-faced cards.

### ✅ `card_type.vanguard` --[MODIFIES]--> `mechanic.life_modifier`
- rule_ref: `313.7`
- verdict: **correct**

### ❌ `concept.spell` --[CONTAINS]--> `concept.ownership`
- rule_ref: `112.2`
- verdict: **wrong**
- issue: The rule text states that a spell has an owner, but it does not support that the concept 'spell' contains the concept 'ownership'. CONTAINS implies a compositional or hierarchical relationship, which is not present here.

### ❌ `concept.stack` --[OCCURS_IN]--> `phase.precombat_main`
- rule_ref: `505.6a`
- verdict: **wrong**
- issue: Rule text does not mention the stack at all; it only describes what spells can be cast in the main phase.

### ✅ `concept.spell_resolution` --[REFERENCES]--> `concept.legal_target`
- rule_ref: `608.2b`
- verdict: **correct**

### ⚠️ `concept.subtype` --[PATTERN_OF]--> `concept.enchantment_type`
- rule_ref: `205.3h`
- verdict: **suspicious**
- issue: The type 'PATTERN_OF' is non-canonical; the relation is more accurately 'CONTAINS' (subtypes contain enchantment types).
- suggested type: `CONTAINS`

### ❌ `keyword.venture_into_dungeon` --[OCCURS_IN]--> `zone.command_zone`
- rule_ref: `701.46a`
- verdict: **wrong**
- issue: The rule text does not state that 'venture into the dungeon' occurs in the command zone; it describes a procedure for obtaining a dungeon card and placing it into the command zone, but the action itself (venturing) is not confined to that zone.

### ⚠️ `concept.defense_counter` --[MODIFIES]--> `concept.defense`
- rule_ref: `310.4c`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule states equality, not modification.
- suggested type: `REFERENCES`

### ❌ `concept.back_face` --[CONTAINS]--> `concept.meld_card`
- rule_ref: `712.4b`
- verdict: **wrong**
- issue: The rule text does not support that a back face contains a meld card; it's the opposite: a meld card has a back face.

### ✅ `concept.teammate_hand_review` --[DEPENDS_ON]--> `concept.seating_arrangement`
- rule_ref: `811.5`
- verdict: **correct**

### ✅ `keyword.transfigure` --[REFERENCES]--> `zone.library`
- rule_ref: `702.71a`
- verdict: **correct**

### ⚠️ `concept.ability` --[MODIFIES]--> `action.resolve`
- rule_ref: `405.6c`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes how mana abilities resolve (immediately) rather than modifying the resolve action itself.
- suggested type: `OCCURS_IN`

### ❌ `concept.different_names` --[CONTAINS]--> `concept.card_name`
- rule_ref: `201.2b`
- verdict: **wrong**
- issue: The rule text explains what 'different names' means but does not state that 'different names' contains 'card name' as a component. The relation is conceptual, not structural.

### ❌ `concept.level_symbol` --[DEPENDS_ON]--> `concept.level_up`
- rule_ref: `711.4`
- verdict: **wrong**
- issue: The rule text does not support a DEPENDS_ON relation from level symbol to level up; it describes that level up ability exists independently of level symbols.

### ⚠️ `concept.mandatory_cost` --[INTERACTS_WITH]--> `concept.optional_cost`
- rule_ref: `118.8b`
- verdict: **suspicious**
- issue: The rule text only distinguishes between mandatory and optional costs but does not explicitly describe an interaction between them. INTERACTS_WITH is not the best fit; a more appropriate type might be PATTERN_OF or REFERENCES.
- suggested type: `PATTERN_OF`

### ✅ `keyword.skulk` --[REFERENCES]--> `step.declare_blockers`
- rule_ref: `702.118b`
- verdict: **correct**

### ❌ `concept.card_part` --[CONTAINS]--> `concept.characteristic`
- rule_ref: `200.3`
- verdict: **wrong**
- issue: The rule states that non-card objects have only the card parts that are also characteristics, implying that characteristics are a subset of card parts, not that card parts contain characteristics.

### ❌ `concept.front_face` --[CONTAINS]--> `concept.double_faced_card`
- rule_ref: `712.8`
- verdict: **wrong**
- issue: The relation direction is reversed: a double-faced card contains a front face, not the front face contains a double-faced card.

### ⚠️ `concept.plane` --[CONTAINS]--> `concept.planar_deck`
- rule_ref: `103.7`
- verdict: **suspicious**
- issue: The relation type CONTAINS is not the best canonical fit. The rule describes the planar deck containing plane cards, but the target is the abstract concept 'planar deck', not the specific cards. A more precise canonical type is PATTERN_OF (the planar deck is a pattern/collection of plane cards).
- suggested type: `PATTERN_OF`

### ⚠️ `mechanic.looking_back_in_time` --[PATTERN_OF]--> `trigger.zone_change`
- rule_ref: `603.10a`
- verdict: **suspicious**
- issue: The relation type PATTERN_OF is not one of the 8 canonical types. The rule text describes that certain zone-change triggers (like 'when a card leaves a graveyard') use the look-back-in-time mechanic, which suggests a MODIFIES or OCCURS_IN relation.
- suggested type: `MODIFIES`

### ✅ `game.two_headed_giant` --[MODIFIES]--> `concept.state_based_action`
- rule_ref: `704.6`
- verdict: **correct**

### ⚠️ `game.multiplayer` --[MODIFIES]--> `concept.starting_player`
- rule_ref: `800.7`
- verdict: **suspicious**
- issue: The relation type MODIFIES is not the best fit; the rule describes a specific exception or interaction rather than a modification of the concept itself.
- suggested type: `INTERACTS_WITH`

### ⚠️ `concept.team` --[OCCURS_IN]--> `concept.starting_player`
- rule_ref: `103.1a`
- verdict: **suspicious**
- issue: Type OCCURS_IN is not the best fit; the relation is more about substitution or equivalence in a specific context.
- suggested type: `PATTERN_OF`

### ⚠️ `ability.static` --[OCCURS_IN]--> `zone.hand`
- rule_ref: `604.6`
- verdict: **suspicious**
- issue: The rule text describes static abilities that apply in zones where you could cast/play the card, typically the hand, but the relation type OCCURS_IN is too broad; a more precise canonical type would be MODIFIES or INTERACTS_WITH, as the ability affects how the card can be cast/played from that zone.
- suggested type: `MODIFIES`

### ✅ `concept.class_card` --[CONTAINS]--> `keyword.class_level`
- rule_ref: `716.2`
- verdict: **correct**

### ✅ `keyword.modular` --[REFERENCES]--> `counter.plus1_plus1`
- rule_ref: `702.43`
- verdict: **correct**

### ✅ `layer.layer_1` --[CONTAINS]--> `layer.layer_1b`
- rule_ref: `613.2b`
- verdict: **correct**

### ✅ `concept.team` --[CONTAINS]--> `concept.player`
- rule_ref: `102.3`
- verdict: **correct**

### ✅ `mechanic.planeswalk` --[OCCURS_IN]--> `card_type.plane`
- rule_ref: `701.24`
- verdict: **correct**

### ✅ `concept.token` --[MOVES_TO]--> `zone.battlefield`
- rule_ref: `111.1`
- verdict: **correct**
