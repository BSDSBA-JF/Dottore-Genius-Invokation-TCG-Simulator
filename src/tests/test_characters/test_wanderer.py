import unittest

from src.tests.test_characters.common_imports import *


class TestWanderer(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Wanderer,
        char_id=2,
        card=GalesOfReverie,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertEqual(dmg.target, StaticTarget.from_char_id(Pid.P2, 1))

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            cost=ActualDice({Element.ANEMO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ANEMO)
        p1ac = p1_active_char(game_state)
        self.assertIn(WindfavoredStatus, p1ac.character_statuses)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            cost=ActualDice({Element.ANEMO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 7)
        self.assertIs(dmg.element, Element.ANEMO)

    def test_windfavored_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=WindfavoredStatus,
        ).execute(game_state)
        status = p1_active_char(game_state).character_statuses.just_find(WindfavoredStatus)
        self.assertEqual(status.usages, 2)

        # test skill1 deals 2 more dmg and targets next character
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertEqual(dmg.target, StaticTarget.from_char_id(Pid.P2, 2))
        status = p1_active_char(game_state).character_statuses.just_find(WindfavoredStatus)
        self.assertEqual(status.usages, 1)

        # tests skill1 targets active if next is not available
        game_state = kill_character(game_state, 2, Pid.P2)
        game_state = kill_character(game_state, 3, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertEqual(dmg.target, StaticTarget.from_char_id(Pid.P2, 1))
        self.assertNotIn(WindfavoredStatus, p1_active_char(game_state).character_statuses)

        # test burst deals 1 more dmg and removes this status when possible
        game_state = grant_all_infinite_revival(game_state)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=WindfavoredStatus,
        ).execute(game_state)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            cost=ActualDice({Element.ANEMO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 8)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertNotIn(WindfavoredStatus, p1_active_char(game_state).character_statuses)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GalesOfReverie,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 4})),
        ))
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertIn(GalesOfReverieStatus, p1_active_char(game_state).character_statuses)

        # test talent doesn't trigger when not charged attack
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 5}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertNotIn(DescentStatus, p1_active_char(game_state).character_statuses)

        # test talent triggers when charged attack
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 6}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertIn(DescentStatus, p1_active_char(game_state).character_statuses)

    def test_descent_status(self):
        # test cost reduction only works when status owner is active
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P1),
            status=DescentStatus,
        ).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
        game_state = step_swap(game_state, Pid.P1, 1, cost=0)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ANEMO)
        self.assertNotIn(
            DescentStatus,
            game_state.player1.characters.just_get_character(1).character_statuses,
        )
