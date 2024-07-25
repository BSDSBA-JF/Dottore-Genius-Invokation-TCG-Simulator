import unittest

from .common_imports import *

SUPPORT = GandharvaVille
SUPPORT_STATUS = GandharvaVilleSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestGandharvaVille(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 2}))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))

        # check pre-action with dice does not trigger Gandharva Ville
        game_state = base_state
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 1}))
        game_state = step_swap(game_state, Pid.P2, 2)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))

        # check pre-action with no dice does trigger 'one' Gandharva Ville
        game_state = step_swap(game_state, Pid.P1, 1)
        self.assertEqual(game_state.player1.dice, ActualDice.from_empty())
        game_state = step_swap(game_state, Pid.P2, 1)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        self.assertEqual(p1_support_status(game_state, 2).usages, 3)

        # check pre-action with no dice does trigger the second Gandharva Ville (because once per round)
        game_state = step_swap(game_state, Pid.P1, 2)
        self.assertEqual(game_state.player1.dice, ActualDice.from_empty())
        game_state = step_swap(game_state, Pid.P2, 2)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)

        # check once per round
        game_state = step_swap(game_state, Pid.P1, 1)
        self.assertEqual(game_state.player1.dice, ActualDice.from_empty())
        game_state = step_swap(game_state, Pid.P2, 1)
        self.assertEqual(game_state.player1.dice, ActualDice.from_empty())

        # check resets the next round
        game_state = next_round(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 1}))
        game_state = replace_dice(game_state, Pid.P2, ActualDice({Element.OMNI: 10}))
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_swap(game_state, Pid.P2, 2)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)

        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P2, 1)
        self.assertEqual(game_state.player1.dice, ActualDice({Element.OMNI: 1}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(p1_support_status(game_state, 2).usages, 1)

        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_swap(game_state, Pid.P2, 2)
        self.assertEqual(game_state.player1.dice, ActualDice.from_empty())
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(p1_support_status(game_state, 2).usages, 1)

        # check disappears eventaully
        game_state = next_round(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 1}))
        game_state = replace_dice(game_state, Pid.P2, ActualDice({Element.OMNI: 10}))
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P2, 1)
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_swap(game_state, Pid.P2, 2)  # first Gandharva Ville is gone
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P2, 1)  # second Gandharva Ville is gone
        self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
