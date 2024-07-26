import unittest

from .common_imports import *

EVENT_CARD = SashimiPlatter

class TestSashimiPlatter(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 4}))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Lyney, 2)
        base_state = replace_character(base_state, Pid.P1, Ganyu, 3)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        """ test assertions """
        with self.subTest("prerequisites"):
            # Kaeya
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, base_state, Pid.P1, amount=2, elem=Element.PHYSICAL)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
            assert_last_dmg(self, base_state, Pid.P1, amount=3, elem=Element.CRYO)
            base_state = remove_aura(base_state, Pid.P2)

            # Lyney
            base_state = step_swap(base_state, Pid.P1, 2)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, base_state, Pid.P1, amount=2, elem=Element.PHYSICAL)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
            assert_last_dmg(self, base_state, Pid.P1, last_index=1, amount=2, elem=Element.PYRO)  # last one is self pierce
            base_state = remove_aura(base_state, Pid.P2)

            # Ganyu
            base_state = step_swap(base_state, Pid.P1, 3)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, base_state, Pid.P1, amount=2, elem=Element.PHYSICAL)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
            assert_last_dmg(self, base_state, Pid.P1, amount=1, elem=Element.CRYO)
            base_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL3)
            assert_last_dmg(self, base_state, Pid.P1, last_index=2, amount=2, elem=Element.PIERCING)
            assert_last_dmg(self, base_state, Pid.P1, last_index=1, amount=2, elem=Element.PIERCING)
            assert_last_dmg(self, base_state, Pid.P1, last_index=0, amount=2, elem=Element.CRYO)
            base_state = remove_aura(base_state, Pid.P2)

        """ test sashimi platter boosts all normal attack infinitely many times this round """
        game_state = base_state
        # Kaeya
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD, cost=1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.CRYO)
        for _ in range(10):
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = remove_aura(game_state, Pid.P2)
        # Lyney
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD, cost=1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, amount=3, elem=Element.PYRO)
        game_state = remove_aura(game_state, Pid.P2)
        # Ganyu
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD, cost=1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.CRYO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        assert_last_dmg(self, game_state, Pid.P1, last_index=2, amount=2, elem=Element.PIERCING)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, amount=2, elem=Element.PIERCING)
        assert_last_dmg(self, game_state, Pid.P1, last_index=0, amount=3, elem=Element.CRYO)

        """ sashimi cannot stay over-night (only lasts this round) """
        c1, c2, c3 = p1_chars(game_state)
        self.assertIn(SashimiPlatterStatus, c1.character_statuses)
        self.assertIn(SashimiPlatterStatus, c2.character_statuses)
        self.assertIn(SashimiPlatterStatus, c3.character_statuses)
        game_state = next_round_with_great_omni(game_state)
        c1, c2, c3 = p1_chars(game_state)
        self.assertNotIn(SashimiPlatterStatus, c1.character_statuses)
        self.assertNotIn(SashimiPlatterStatus, c2.character_statuses)
        self.assertNotIn(SashimiPlatterStatus, c3.character_statuses)

        # last one round no matter used or not
        game_state = end_round(game_state, Pid.P2)
        game_state = play_char_target_card(game_state, Pid.P1, EVENT_CARD)
        self.assertIn(SashimiPlatterStatus, p1_active_char(game_state).character_statuses)
        game_state = next_round(game_state)
        self.assertNotIn(SashimiPlatterStatus, p1_active_char(game_state).character_statuses)
