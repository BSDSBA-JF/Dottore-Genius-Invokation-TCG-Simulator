import unittest

from .common_imports import *

ARTIFACT = ExilesCirclet
ARTIFACT_STATUS = ExilesCircletStatus

def p1_artifact_status(game_state: GameState) -> ARTIFACT_STATUS:
    return p1_active_char(game_state).character_statuses.just_find_type(ARTIFACT_STATUS)

class TestExilesCirclet(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARTIFACT: 1}))
        assert Keqing.from_default().max_energy == 3
        assert Chongyun.from_default().max_energy == 3
        assert RhodeiaOfLoch.from_default().max_energy == 3
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = replace_character(base_state, Pid.P1, Chongyun, 1)
        base_state = replace_character(base_state, Pid.P1, RhodeiaOfLoch, 1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=ARTIFACT,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1}),
            ),
        ))

        # check teammate burst doesn't trigger artifact
        game_state = base_state
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = recharge_energy_for(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertEqual(p1c1.energy, 0)
        self.assertEqual(p1c2.energy, 0)
        self.assertEqual(p1c3.energy, 0)

        # check self burst trigger artifact
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = recharge_energy_for(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertEqual(p1c1.energy, 0)
        self.assertEqual(p1c2.energy, 1)
        self.assertEqual(p1c3.energy, 1)

        # but once per round only
        game_state = recharge_energy_for(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertEqual(p1c1.energy, 0)
        self.assertEqual(p1c2.energy, 1)
        self.assertEqual(p1c3.energy, 1)

        # resets the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = recharge_energy_for(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertEqual(p1c1.energy, 0)
        self.assertEqual(p1c2.energy, 2)
        self.assertEqual(p1c3.energy, 2)

        # once per round
        game_state = recharge_energy_for(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertEqual(p1c1.energy, 0)
        self.assertEqual(p1c2.energy, 2)
        self.assertEqual(p1c3.energy, 2)
