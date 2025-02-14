import unittest

from src.tests.test_characters.common_imports import *


class TestYoimiya(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Yoimiya,
        char_id=2,
        card=NaganoharaMeteorSwarm,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Yoimiya

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate status without damage or energy recharge
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            cost=ActualDice({Element.PYRO: 1}),
        )
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(NiwabiEnshouStatus, p1ac.character_statuses)
        self.assertEqual(p1ac.character_statuses.just_find(NiwabiEnshouStatus).usages, 3)
        self.assertEqual(p1ac.energy, 0)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and generates status
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            cost=ActualDice({Element.PYRO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(AurousBlazeStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(AurousBlazeStatus).usages, 2)

    def test_niwabi_enshou_status(self):
        # test status has pyro infusion and damage boost
        game_state = AddCharacterStatusEffect(
            StaticTarget.from_char_id(Pid.P1, 2), NiwabiEnshouStatus
        ).execute(self.BASE_GAME)
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.OMNI: 3}),
        )
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(NiwabiEnshouStatus, p1ac.character_statuses)
        self.assertEqual(p1ac.character_statuses.just_find(NiwabiEnshouStatus).usages, 2)

        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert p1_active_char(game_state).character_statuses.just_find(NiwabiEnshouStatus).usages == 1

        # test status disappears on end of usages
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.OMNI: 3}),
        )
        p1ac = game_state.player1.just_get_active_character()
        self.assertNotIn(NiwabiEnshouStatus, p1ac.character_statuses)

    def test_aurous_blaze_status(self):
        # test Yoimiya cannot trigger this status
        game_state = AddCombatStatusEffect(Pid.P1, AurousBlazeStatus).execute(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.OMNI: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(AurousBlazeStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(AurousBlazeStatus).usages, 2)

        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, char_id=3)
        assert isinstance(
            game_state.get_character_target(StaticTarget.from_player_active(game_state, Pid.P1)),
            Keqing
        )
        game_state = skip_action_round(game_state, Pid.P2)

        # test Keqing skill triggers status and then overloaded
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.player1
        p2_last_ac = game_state.player2.characters.just_get_character(1)
        self.assertEqual(p2_last_ac.hp, 2)
        self.assertFalse(p2_last_ac.elemental_aura.has_aura())
        self.assertIn(AurousBlazeStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(AurousBlazeStatus).usages, 2)

        # usages decrement per round
        game_state = next_round(game_state)
        p1 = game_state.player1
        self.assertIn(AurousBlazeStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(AurousBlazeStatus).usages, 1)

        # usages decrement per round and disappears
        game_state = next_round(game_state)
        p1 = game_state.player1
        self.assertNotIn(AurousBlazeStatus, p1.combat_statuses)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=NaganoharaMeteorSwarm,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1}))
        ))
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(NiwabiEnshouStatus, p1ac.character_statuses)
        self.assertEqual(p1ac.character_statuses.just_find(NiwabiEnshouStatus).usages, 3)
        self.assertEqual(p1ac.energy, 0)

        # normal attack triggers follow-up damage
        game_state = oppo_aura_elem(game_state, Element.HYDRO)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            cost=ActualDice({Element.OMNI: 3}),
        )
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 4)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(NiwabiEnshouStatus, p1ac.character_statuses)
        self.assertEqual(p1ac.character_statuses.just_find(NiwabiEnshouStatus).usages, 2)

        # elemental burst doesn't trigger the status
        game_state = recharge_energy_for_all(game_state)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            cost=ActualDice({Element.PYRO: 3}),
        )
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 1)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(NiwabiEnshouStatus, p1ac.character_statuses)
        self.assertEqual(p1ac.character_statuses.just_find(NiwabiEnshouStatus).usages, 2)
