import unittest

from .common_imports import *

SUPPORT = StormterrorsLair
SUPPORT_STATUS = StormterrorsLairSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestStormterrorsLair(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards((
            Paimon, ThunderingPenance, Paimon,  # talent at the middle
        )))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 2,
        }))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({
            ThunderingPenance: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = replace_character(base_state, Pid.P1, RhodeiaOfLoch, 2)
        base_state = replace_character(base_state, Pid.P1, Ganyu, 3)
        base_state = replace_character(base_state, Pid.P2, Keqing, 1)
        base_state = replace_character(base_state, Pid.P2, RhodeiaOfLoch, 2)
        base_state = grant_all_infinite_revival(base_state)

        assert ThunderingPenance._DICE_COST.num_dice() == 3
        assert Keqing.skill_cost(CharacterSkill.SKILL2).num_dice() == 3
        assert Keqing.skill_cost(CharacterSkill.ELEMENTAL_BURST).num_dice() == 4
        assert RhodeiaOfLoch.skill_cost(CharacterSkill.SKILL3).num_dice() == 5
        assert Ganyu.skill_cost(CharacterSkill.SKILL3).num_dice() == 5

        # check playing the card draws a talent card
        game_state = base_state
        game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=2)
        self.assertEqual(game_state.player1.hand_cards[ThunderingPenance], 1)
        self.assertEqual(game_state.player1.hand_cards[Paimon], 0)

        # check skill cost < 3 is not affected
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.OMNI: 3}))

        # check opponent cannot get discounted
        game_state = reactivate_player(game_state, Pid.P2)
        game_state = end_round(game_state, Pid.P1)
        game_state = play_dice_only_card(game_state, Pid.P2, ThunderingPenance, cost=3)
        game_state = step_swap(game_state, Pid.P2, 2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL3, cost=5)
        self.assertEqual(p1_support_status(game_state, 1).usages, 3)
        game_state = reactivate_player(game_state, Pid.P1)
        game_state = end_round(game_state, Pid.P2)

        # check talent get discounted (once per round)
        self.assertEqual(p1_support_status(game_state, 1).usages, 3)
        game_state = play_dice_only_card(game_state, Pid.P1, ThunderingPenance, cost=2)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        game_state = add_hand_card(game_state, Pid.P1, ThunderingPenance)
        game_state = play_dice_only_card(game_state, Pid.P1, ThunderingPenance, cost=3)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)

        # check "once per round" is shared between skills
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3, cost=5)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)

        # check resets the next round (cost 5 skill get discounted)
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3, cost=4)
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3, cost=5)
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)

        # check resets the next round (cost 4 skill get discounted) (and both lairs work)
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = recharge_energy_for(game_state, Pid.P1, 1)
        game_state = play_support_card(game_state, Pid.P1, SUPPORT, cost=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, 2)
        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 1))
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)
