import unittest

from .common_imports import *

SUPPORT = Timmie
SUPPORT_STATUS = TimmieSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestTimmie(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 2}))
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards.from_dict_ordered({
            Paimon: 10,
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice.from_empty())

        # check timmie starts with one usages
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)

        # check timmie gets 1 usage at the start of each round
        game_state = end_round(next_round(game_state), Pid.P2)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertEqual(p1_support_status(game_state, 2).usages, 1)

        # check timmie draws a card and gives one omni dice
        game_state = just(game_state.action_step(Pid.P1, EndRoundAction()))
        game_state = auto_step_to_start_of_phase(game_state, game_state.mode.action_phase)
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            Jeht, Jeht, Jeht, Jeht,
        )))
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))
        game_state = replace_dice(game_state, Pid.P1, ActualDice.from_empty())
        game_state = auto_step(game_state)
        self.assertEqual(game_state.player1.hand_cards, Cards({Jeht: 1}))
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))

        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 1))
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)

        # check next Timmie behaves the same
        game_state = end_round(game_state, Pid.P2)
        game_state = just(game_state.action_step(Pid.P1, EndRoundAction()))
        game_state = auto_step_to_start_of_phase(game_state, game_state.mode.action_phase)
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards((
            Jeht, Jeht, Jeht, Jeht,
        )))
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))
        game_state = replace_dice(game_state, Pid.P1, ActualDice.from_empty())
        game_state = auto_step(game_state)
        self.assertEqual(game_state.player1.hand_cards, Cards({Jeht: 1}))
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))

        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 1))
        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 2))
