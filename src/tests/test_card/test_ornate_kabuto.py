import unittest

from .common_imports import *

ARTIFACT = OrnateKabuto
ARTIFACT_STATUS = OrnateKabutoStatus

def p1_artifact_status(game_state: GameState) -> ARTIFACT_STATUS:
    return p1_active_char(game_state).character_statuses.just_find_type(ARTIFACT_STATUS)

class TestOrnateKabuto(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARTIFACT: 1}))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=ARTIFACT,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 1}),
            ),
        ))

        # check self burst get no recharge
        game_state = recharge_energy_for_all(base_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_chars(game_state)[0].energy, 0)

        # check teammate burst charges equipped character
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_chars(game_state)[0].energy, 1)

        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_chars(game_state)[0].energy, 2)
