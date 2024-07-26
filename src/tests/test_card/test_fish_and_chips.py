import unittest

from .common_imports import *

EVENT_CARD = FishAndChips

class TestFishAndChips(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 2}))
        base_state = replace_character(base_state, Pid.P1, Chongyun, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Keqing, 3)
        base_state = grant_all_infinite_revival(base_state)

        c1, c2, c3 = p1_chars(base_state)
        assert c1.skill_cost(CharacterSkill.SKILL1).num_dice() == 3
        assert c2.skill_cost(CharacterSkill.SKILL2).num_dice() == 3
        assert c3.skill_cost(CharacterSkill.ELEMENTAL_BURST).num_dice() == 4

        # check fish and chips discount all skills (once per char)
        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=ActualDice({Element.GEO: 1, Element.PYRO: 1}))
        c1, c2, c3 = p1_chars(game_state)
        self.assertIn(FishAndChipsStatus, c1.character_statuses)
        self.assertIn(FishAndChipsStatus, c2.character_statuses)
        self.assertIn(FishAndChipsStatus, c3.character_statuses)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, cost=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, cost=3)

        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=3)

        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=3)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=4)

        c1, c2, c3 = p1_chars(game_state)
        self.assertNotIn(FishAndChipsStatus, c1.character_statuses)
        self.assertNotIn(FishAndChipsStatus, c2.character_statuses)
        self.assertNotIn(FishAndChipsStatus, c3.character_statuses)

        # check fish and chips status disappear the next round if not used
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=2)
        c1, c2, c3 = p1_chars(game_state)
        self.assertIn(FishAndChipsStatus, c1.character_statuses)
        self.assertIn(FishAndChipsStatus, c2.character_statuses)
        self.assertIn(FishAndChipsStatus, c3.character_statuses)
        
        game_state = next_round(game_state)
        c1, c2, c3 = p1_chars(game_state)
        self.assertNotIn(FishAndChipsStatus, c1.character_statuses)
        self.assertNotIn(FishAndChipsStatus, c2.character_statuses)
        self.assertNotIn(FishAndChipsStatus, c3.character_statuses)
