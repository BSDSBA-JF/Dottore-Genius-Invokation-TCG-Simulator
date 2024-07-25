import unittest

from .common_imports import *

SUPPORT = RedFeatherFan
SUPPORT_STATUS = RedFeatherFanSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestRedFeatherFan(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 1, DawnWinery: 1}))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))

        # check first swap adds the combat status with no other effects
        game_state = base_state
        game_state = step_swap(game_state, Pid.P1, 2, 1)
        self.assertIs(game_state.waiting_for(), Pid.P2)
        self.assertIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        ready_state = skip_action_round_until(game_state, Pid.P1)

        # check second swap removes the combat status, making it fast and cheap (-1 die)
        game_state = step_swap(ready_state, Pid.P1, 1, 0)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check reset the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)
        game_state = step_swap(game_state, Pid.P1, 2, 1)
        self.assertIs(game_state.waiting_for(), Pid.P2)
        self.assertIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check cost-free swap removes the red feather status
        game_state = ready_state.factory().f_player1(
            lambda p: p.factory().combat_statuses(
                Statuses((ChangingShiftsStatus(), RedFeatherFanStatus()))
            ).build()
        ).build()
        game_state = step_swap(game_state, Pid.P1, 1, 0)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        self.assertNotIn(ChangingShiftsStatus, game_state.player1.combat_statuses)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check fast swap removes the red feather status
        game_state = ready_state.factory().f_player1(
            lambda p: p.factory().combat_statuses(
                Statuses((LeaveItToMeStatus(), RedFeatherFanStatus()))
            ).build()
        ).build()
        game_state = step_swap(game_state, Pid.P1, 1, 0)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        self.assertNotIn(LeaveItToMeStatus, game_state.player1.combat_statuses)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check fast & cost-free swap doesn't remove red feather status
        game_state = ready_state.factory().f_player1(
            lambda p: p.factory().combat_statuses(
                Statuses((ChangingShiftsStatus(), LeaveItToMeStatus(), RedFeatherFanStatus()))
            ).build()
        ).build()
        game_state = step_swap(game_state, Pid.P1, 1, 0)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        self.assertNotIn(ChangingShiftsStatus, game_state.player1.combat_statuses)
        self.assertNotIn(LeaveItToMeStatus, game_state.player1.combat_statuses)
        self.assertIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check less prioritized fast & cost-free swap removes combat status
        game_state = ready_state.factory().f_player1(
            lambda p: p.factory().combat_statuses(
                Statuses((LeaveItToMeStatus(), RedFeatherFanStatus()))
            ).build()
        ).build()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=DawnWinery,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        game_state = step_swap(game_state, Pid.P1, 1, 0)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        self.assertNotIn(LeaveItToMeStatus, game_state.player1.combat_statuses)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)

        # check red feather status last one round only
        game_state = next_round(ready_state)
        self.assertNotIn(RedFeatherFanStatus, game_state.player1.combat_statuses)
