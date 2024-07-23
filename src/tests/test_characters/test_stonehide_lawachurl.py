import unittest

from src.tests.test_characters.common_imports import *


class TestStonehideLawachurl(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        StonehideLawachurl,
        char_id=2,
        card=StonehideReforged,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StoneForceStatus,
        ).execute(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.PYRO: 1, Element.HYDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StoneForceStatus,
        ).execute(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_elemental_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StoneForceStatus,
        ).execute(game_state)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_stonehide_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        stonehide_status = p1_active_char(game_state).character_statuses.just_find(StonehideStatus)
        self.assertEqual(stonehide_status.usages, 3)

        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=0)
        stonehide_status = p1_active_char(game_state).character_statuses.just_find(StonehideStatus)
        self.assertEqual(stonehide_status.usages, 2)

        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1)
        stonehide_status = p1_active_char(game_state).character_statuses.just_find(StonehideStatus)
        self.assertEqual(stonehide_status.usages, 1)

        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
        self.assertNotIn(StonehideStatus, p1_active_char(game_state).character_statuses)
    
    def test_stone_force_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = end_round(game_state, Pid.P2)

        def assert_dmgs_with_no_buff(game_state: GameState) -> GameState:
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
            assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
            assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
            game_state = recharge_energy_for_all(game_state)
            game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
            assert_last_dmg(self, game_state, Pid.P1, amount=5, elem=Element.PHYSICAL)
            return game_state

        # checks normal attack gets buffed once per round
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.GEO)
        game_state = assert_dmgs_with_no_buff(game_state)

        # checks skill2 gets buffed once the next round
        game_state = end_round(next_round_with_great_omni(game_state), Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=4, elem=Element.GEO)
        game_state = assert_dmgs_with_no_buff(game_state)

        # checks burst gets buffed once the next round
        game_state = end_round(next_round_with_great_omni(game_state), Pid.P2)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        assert_last_dmg(self, game_state, Pid.P1, amount=6, elem=Element.GEO)
        game_state = assert_dmgs_with_no_buff(game_state)

        # check it disappears when Stonehide Status disappears
        game_state = end_round(next_round_with_great_omni(game_state), Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        assert StonehideStatus in p1_active_char(game_state).character_statuses
        self.assertIn(StoneForceStatus, p1_active_char(game_state).character_statuses)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        assert StonehideStatus in p1_active_char(game_state).character_statuses
        self.assertIn(StoneForceStatus, p1_active_char(game_state).character_statuses)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        assert StonehideStatus not in p1_active_char(game_state).character_statuses
        self.assertNotIn(StoneForceStatus, p1_active_char(game_state).character_statuses)

    def test_talent_card(self):
        game_state = end_round(self.BASE_GAME, Pid.P2)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StonehideStatus,
        ).execute(game_state)
        game_state = RemoveCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=StoneForceStatus,
        ).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=StonehideReforged,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 4})),
        ))
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertTrue(dmg.damage_type.elemental_burst)
        talented_state = game_state

        # check ordinary kill reattch lawachurl with Stonehide and StoneForce statuses
        game_state = set_hp(talented_state, Pid.P2, hp=1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertIn(StonehideStatus, p1_active_char(game_state).character_statuses)
        self.assertIn(StoneForceStatus, p1_active_char(game_state).character_statuses)

        # check non-character dmg from self doesn't count
        game_state = AddCombatStatusEffect(Pid.P1, PyronadoStatus).execute(talented_state)
        game_state = set_hp(talented_state, Pid.P2, hp=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertNotIn(StonehideStatus, p1_active_char(game_state).character_statuses)
        self.assertNotIn(StoneForceStatus, p1_active_char(game_state).character_statuses)
