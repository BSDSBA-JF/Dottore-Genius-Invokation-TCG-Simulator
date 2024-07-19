import unittest

from src.tests.test_characters.common_imports import *


class TestAlbedo(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Albedo,
        char_id=2,
        card=DescentOfDivinity,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Albedo

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.GEO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(SolarIsotomaSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(SolarIsotomaSummon).usages, 3)

    def test_elemental_burst(self):
        # burst without summon deals 4 damage
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.GEO)
        self.assertEqual(dmg.damage, 4)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # burst with summon
        game_state = AddSummonEffect(Pid.P1, SolarIsotomaSummon).execute(self.BASE_GAME)
        game_state = recharge_energy_for_all(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.GEO)
        self.assertEqual(dmg.damage, 6)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

    def test_solar_isotoma_summon(self):
        game_state = AddSummonEffect(Pid.P1, SolarIsotomaSummon).execute(self.BASE_GAME)
        game_state = grant_all_thick_shield(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)

        # test all swaps are fast action
        game_state = step_swap(game_state, Pid.P1, 3)
        self.assertIs(game_state.waiting_for(), Pid.P1)
        game_state = step_swap(game_state, Pid.P1, 2)
        self.assertIs(game_state.waiting_for(), Pid.P1)

        # test summon damage and usages behaves correctly
        game_state = remove_all_thick_shield(game_state)
        game_state = next_round_with_great_omni(game_state)
        game_state = grant_all_thick_shield(game_state)
        p1_summons = game_state.player1.summons
        self.assertIn(SolarIsotomaSummon, p1_summons)
        self.assertEqual(p1_summons.just_find(SolarIsotomaSummon).usages, 2)
        last_summon_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(last_summon_dmg.element, Element.GEO)
        self.assertEqual(last_summon_dmg.damage, 1)
        self.assertEqual(
            last_summon_dmg.target,
            StaticTarget.from_player_active(game_state, Pid.P2),
        )
        solar_summon = p1_summons.just_find(SolarIsotomaSummon)
        self.assertEqual(solar_summon.usages, 2)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=DescentOfDivinity,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 3}))
        ))
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = add_dmg_listener(game_state, Pid.P1)

        # test plunge gets more damage and cost reduction
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 2})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 3)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # test all plunges gets more damage and reduction
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 2})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 3)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # test non-plunges doesn't get boost and reduction
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 2)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # test plunge with no summon gets no boost and reduction
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = RemoveSummonEffect(Pid.P1, SolarIsotomaSummon).execute(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 2)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))
