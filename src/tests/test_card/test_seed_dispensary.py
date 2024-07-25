import unittest

from .common_imports import *

SUPPORT = SeedDispensary
SUPPORT_STATUS = SeedDispensarySupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestSeedDispensary(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 2,
            Vanarana: 2,  # cost 0
            LiuSu: 2,  # cost 1
            ParametricTransformer: 2,  # cost 2
            Paimon: 2, # cost 3
        }))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))

        assert Vanarana._DICE_COST.num_dice() == 0
        assert LiuSu._DICE_COST.num_dice() == 1
        assert ParametricTransformer._DICE_COST.num_dice() == 2
        assert Paimon._DICE_COST.num_dice() == 3

        # check 0 cost card is still zero
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Vanarana,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Vanarana,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = keep_only_support(game_state, Pid.P1, SeedDispensarySupport)

        # check 1 cost card is still 1
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LiuSu,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LiuSu,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        game_state = keep_only_support(game_state, Pid.P1, SeedDispensarySupport)

        # check >= 2 cost card will cost 1 (once per round)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ParametricTransformer,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        game_state = keep_only_support(game_state, Pid.P1, SeedDispensarySupport)

        # check resets next round, and two seed dispensary can work together
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ParametricTransformer,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 1))
        self.assertEqual(p1_support_status(game_state, 2).usages, 1)
