import unittest

from src.tests.test_characters.common_imports import *


class TestQiqi(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Qiqi,
        char_id=2,
        card=RiteOfResurrection,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is Qiqi

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
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
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(HeraldOfFrostSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(HeraldOfFrostSummon).usages, 3)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and generates status
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertIn(FortunePreservingTalismanStatus, p1.combat_statuses)
        self.assertEqual(
            p1.combat_statuses.just_find(FortunePreservingTalismanStatus).usages,
            3
        )

    def test_herald_of_frost_summon(self):
        game_state = AddSummonEffect(Pid.P1, HeraldOfFrostSummon).execute(self.BASE_GAME)
        game_state = replace_character(game_state, Pid.P1, ElectroHypostasis, char_id=3)
        game_state = simulate_status_dmg(game_state, dmg_amount=3, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, dmg_amount=3, pid=Pid.P1, char_id=2)
        game_state = grant_all_thick_shield(game_state)

        # test heals in activity order (and heals based on lost hp instead of max_hp)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 8)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 8)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 8)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 9)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 8)

        game_state = heal_for_all(game_state)
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        assert game_state.player1.summons.just_find(HeraldOfFrostSummon).usages == 2

        game_state = simulate_status_dmg(game_state, dmg_amount=2, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, dmg_amount=2, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, dmg_amount=3, pid=Pid.P1, char_id=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 8)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 6)

        # test summon deals damage
        game_state = remove_all_thick_shield(game_state)
        game_state = next_round(game_state)
        p1_summons = game_state.player1.summons
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertIn(HeraldOfFrostSummon, p1_summons)
        self.assertEqual(p1_summons.just_find(HeraldOfFrostSummon).usages, 1)

        # non Qiqi character's normal attack doesn't trigger
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=3)
        game_state = fill_dice_with_omni(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 8)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 6)

    def test_fortune_preserving_talisman_status(self):
        game_state = AddCombatStatusEffect(
            Pid.P1, FortunePreservingTalismanStatus
        ).execute(self.BASE_GAME)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertIn(FortunePreservingTalismanStatus, p1_combat_statuses)
        self.assertEqual(p1_combat_statuses.just_find(FortunePreservingTalismanStatus).usages, 3)

        # test full hp doesn't consume talisman
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertIn(FortunePreservingTalismanStatus, p1_combat_statuses)
        self.assertEqual(p1_combat_statuses.just_find(FortunePreservingTalismanStatus).usages, 3)

        # test non-full hp gets heal
        game_state = grant_all_thick_shield(game_state)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=3)
        game_state = simulate_status_dmg(game_state, 5, pid=Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.player1.just_get_active_character()
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1ac.hp, 7)
        self.assertIn(FortunePreservingTalismanStatus, p1_combat_statuses)
        self.assertEqual(p1_combat_statuses.just_find(FortunePreservingTalismanStatus).usages, 2)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.player1.just_get_active_character()
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1ac.hp, 9)
        self.assertIn(FortunePreservingTalismanStatus, p1_combat_statuses)
        self.assertEqual(p1_combat_statuses.just_find(FortunePreservingTalismanStatus).usages, 1)

        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1ac = game_state.player1.just_get_active_character()
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1ac.hp, 10)
        self.assertNotIn(FortunePreservingTalismanStatus, p1_combat_statuses)

    def test_talent_card(self):
        game_state = self.BASE_GAME
        game_state = grant_all_thick_shield(game_state)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=3)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_defeated())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_defeated())
        self.assertEqual(p1c1.hp, 0)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 0)

        # test talent card burst revives teammates
        game_state = recharge_energy_for_all(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=RiteOfResurrection,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 4}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_alive())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_alive())
        self.assertEqual(p1c1.hp, 2)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 2)
        revive_once_state = game_state

        # test burst can revive teammates a second time
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=3)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_alive())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_alive())
        self.assertEqual(p1c1.hp, 2)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 2)

        # test burst cannot revive teammates a third time
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=3)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_defeated())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_defeated())
        self.assertEqual(p1c1.hp, 0)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 0)
        revival_consumed_state = game_state

        # re-equiping talent card doesn't reset revival chances
        game_state = recharge_energy_for_all(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=RiteOfResurrection,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 4}))
        ))
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_defeated())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_defeated())
        self.assertEqual(p1c1.hp, 0)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 0)

        # no revival burst doesn't consume revival chances
        game_state = recharge_energy_for_all(revive_once_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_alive())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_alive())
        self.assertEqual(p1c1.hp, 2)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 2)

        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=3)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_alive())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_alive())
        self.assertEqual(p1c1.hp, 2)
        self.assertEqual(p1c2.hp, 9)
        self.assertEqual(p1c3.hp, 2)

        # qiqi revival can reset revival chances
        game_state = replace_character(revival_consumed_state, Pid.P1, Keqing, char_id=3)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=3)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=2)
        game_state = PublicAddCardEffect(Pid.P1, TeyvatFriedEgg).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TeyvatFriedEgg,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            )
        ))
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, BIG_INT, pid=Pid.P1, char_id=3)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=RiteOfResurrection,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 4}))
        ))
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertTrue(p1c1.is_alive())
        self.assertTrue(p1c2.is_alive())
        self.assertTrue(p1c3.is_alive())
        self.assertEqual(p1c1.hp, 2)
        self.assertEqual(p1c2.hp, 1)  # due to fried egg
        self.assertEqual(p1c3.hp, 2)
