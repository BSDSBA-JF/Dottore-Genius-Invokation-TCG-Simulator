import unittest

from .common_imports import *


class TestElementalResonanceFerventFlames(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE, Pid.P1, KaedeharaKazuha,
        char_id=1, card=ElementalResonanceFerventFlames
    )

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceFerventFlames.valid_in_deck(
                MutableDeck(chars=[Klee, Keqing, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceFerventFlames.valid_in_deck(
                MutableDeck(chars=[Bennett, Klee, Keqing], cards={})
            )
        )

    def test_card_adds_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=ElementalResonanceFerventFlames,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1}))
        ))
        self.assertIn(
            ElementalResonanceFerventFlamesStatus,
            game_state.player1.combat_statuses
        )

    def test_status_behaviour(self):
        base_state = AddCombatStatusEffect(Pid.P1, ElementalResonanceFerventFlamesStatus).execute(
            self.BASE_GAME
        )
        base_state = oppo_aura_elem(base_state, Element.PYRO)
        # None reaction damage doesn't trigger status
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 8)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)

        # Reaction does boost the damage that triggers the reaction
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 4)

        # Summon doesn't trigger
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(base_state)
        game_state = next_round(game_state)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2ac = game_state.player2.just_get_active_character()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2ac.hp, 7)  # raptor 1 + vaporize 2

        # status naturally disappears next round
        game_state = next_round(base_state)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)

        # swirled pyro reaction can be buffed
        game_state = apply_elemental_aura(base_state, Element.HYDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2, char_id=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.player1.combat_statuses
        p2c1, p2c2, p2c3 = game_state.player2.characters.get_characters()
        self.assertNotIn(ElementalResonanceFerventFlamesStatus, p1_combat_statuses)
        self.assertEqual(p2c1.hp, 9)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 4)
