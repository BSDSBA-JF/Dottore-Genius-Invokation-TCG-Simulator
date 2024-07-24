import unittest

from .common_imports import *

ARTIFACT = OceanHuedClam
ARTIFACT_STATUS = OceanHuedClamStatus

def p1_artifact_status(game_state: GameState) -> ARTIFACT_STATUS:
    return p1_active_char(game_state).character_statuses.just_find_type(ARTIFACT_STATUS)

class TestOceanHuedClam(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARTIFACT: 1}))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)

        # check equipping ocean-hued clam heals the character by 2 and stacks the artifact
        game_state = base_state
        game_state = set_hp(game_state, Pid.P1, hp=5)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ARTIFACT,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.GEO: 1}),
            ),
        ))
        self.assertEqual(p1_active_char(game_state).hp, 7)
        self.assertEqual(p1_artifact_status(game_state).usages, 0)

        # one more healing should make the stack
        game_state = simulate_status_heal(game_state, 1, Pid.P1)
        self.assertEqual(p1_active_char(game_state).hp, 8)
        self.assertEqual(p1_artifact_status(game_state).usages, 1)

        # as it shares code with Crown of Watatsumi, the rest of the test are in test_crown_of_watatsumi.py
