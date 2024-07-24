import unittest

from .common_imports import *

ARTIFACT = EmblemOfSeveredFate
ARTIFACT_STATUS = EmblemOfSeveredFateStatus

def p1_artifact_status(game_state: GameState) -> ARTIFACT_STATUS:
    return p1_active_char(game_state).character_statuses.just_find_type(ARTIFACT_STATUS)

class TestEmblemOfSeveredFate(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({ARTIFACT: 1}))
        base_state = replace_character(base_state, Pid.P1, Chongyun, 1)
        base_state = replace_character(base_state, Pid.P1, Chongyun, 2)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # check self-elemental burst deals 2 more damage
        game_state = base_state
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        prev_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ARTIFACT,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        new_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(new_dmg.damage - prev_dmg.damage, 2)
        # ... and no energy recharge for self-burst
        self.assertEqual(p1_active_char(game_state).energy, 0)

        # checks teammate burst gets no boost but recharge energy for equipped character
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        teammate_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(teammate_dmg.damage, prev_dmg.damage)
        self.assertEqual(p1_chars(game_state)[0].energy, 1)

        # check opponent cannot recharge energy
        game_state = reactivate_player(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_chars(game_state)[0].energy, 1)

        # check burst recharge can work as many times as possible
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_chars(game_state)[0].energy, 2)
