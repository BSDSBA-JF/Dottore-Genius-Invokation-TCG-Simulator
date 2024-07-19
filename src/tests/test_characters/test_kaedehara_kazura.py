import unittest
from typing import ClassVar

from src.tests.test_characters.common_imports import *


class TestKaedeharaKazuha(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE, Pid.P1,
        KaedeharaKazuha,
        char_id=2,
        card=PoeticsOfFuubutsu,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is KaedeharaKazuha

    def test_normal_attack(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_elemental_skill1(self):
        from src.dgisim.status.status import _MIDARE_RANZAN_MAP
        base_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        elems = [Element.ANEMO, Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                if elem.is_aurable():
                    game_state = oppo_aura_elem(base_state, elem)
                else:
                    game_state = base_state

                game_state = step_skill(
                    game_state, Pid.P1, CharacterSkill.SKILL2,
                    ActualDice({Element.ANEMO: 3}),
                )

                # first skill
                p2c1, p2c2, p2c3 = p2_chars(game_state)
                self.assertEqual(p2c1.hp, 9)
                self.assertFalse(p2c1.elemental_aura.has_aura())
                if elem.is_aurable():
                    self.assertEqual(p2c2.hp, 9)
                    self.assertEqual(p2c3.hp, 9)
                    self.assertTrue(p2c2.elemental_aura.has_aura())
                    self.assertTrue(p2c3.elemental_aura.has_aura())
                else:
                    self.assertEqual(p2c2.hp, 10)
                    self.assertEqual(p2c3.hp, 10)
                    self.assertFalse(p2c2.elemental_aura.has_aura())
                    self.assertFalse(p2c3.elemental_aura.has_aura())
                p1ac = p1_active_char(game_state)
                self.assertEqual(p1ac.id, 3)
                kazuha = game_state.player1.characters.just_get_character(2)
                self.assertIn(_MIDARE_RANZAN_MAP[elem], kazuha.character_statuses)

                # swap back and auto plunge attack
                assert game_state.waiting_for() is Pid.P2
                game_state = skip_action_round_until(game_state, Pid.P1)
                game_state = step_swap(game_state, Pid.P1, 2)
                dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
                self.assertIs(dmg.element, elem)
                p2c1, p2c2, p2c3 = p2_chars(game_state)
                self.assertEqual(p2c1.hp, 7)
                if elem.is_aurable():
                    self.assertIn(elem, p2c1.elemental_aura)
                else:
                    self.assertFalse(p2c1.elemental_aura.has_aura())

                p1ac = p1_active_char(game_state)
                self.assertEqual(p1ac.id, 2)
                for status in p1ac.character_statuses:
                    self.assertNotIn(type(status), _MIDARE_RANZAN_MAP.values())

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.max_energy
                    ).build()
                ).build()
            ).build()
        ).build()

        # burst with no swirl
        gsm = GameStateMachine(base_game_state, a1, a2)
        a1.inject_action(
            SkillAction(
                skill=CharacterSkill.ELEMENTAL_BURST,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            )
        )
        gsm.player_step()
        gsm.auto_step()
        p2cs = gsm.get_game_state().player2.characters
        p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
        self.assertEqual(p2c1.hp, 9)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertFalse(p2c1.elemental_aura.has_aura())
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertEqual(
            gsm.get_game_state().player1.just_get_active_character().energy,
            0
        )
        p1 = gsm.get_game_state().player1
        p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
        assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
        self.assertEqual(p1_burst_summon.usages, 2)
        self.assertEqual(p1_burst_summon.curr_elem, Element.ANEMO)
        self.assertEqual(p1_burst_summon.ready_elem, None)

        # burst with swirl
        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                gsm = GameStateMachine(game_state, a1, a2)
                a1.inject_action(
                    SkillAction(
                        skill=CharacterSkill.ELEMENTAL_BURST,
                        instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                    )
                )
                gsm.player_step()
                gsm.step_until_holds(
                    lambda gs: gs.effect_stack.peek() == DeathCheckCheckerEffect()
                )
                p1 = gsm.get_game_state().player1
                p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
                self.assertEqual(p1_burst_summon.usages, 2)
                self.assertEqual(p1_burst_summon.curr_elem, Element.ANEMO)
                self.assertEqual(p1_burst_summon.ready_elem, elem)

                gsm.auto_step()
                p2cs = gsm.get_game_state().player2.characters
                p2c1, p2c2, p2c3 = (p2cs.just_get_character(i) for i in range(1, 4))
                self.assertEqual(p2c1.hp, 9)
                self.assertEqual(p2c2.hp, 9)
                self.assertEqual(p2c3.hp, 9)
                self.assertFalse(p2c1.elemental_aura.has_aura())
                self.assertIn(elem, p2c2.elemental_aura)
                self.assertIn(elem, p2c3.elemental_aura)
                self.assertEqual(
                    gsm.get_game_state().player1.just_get_active_character().energy,
                    0
                )
                p1 = gsm.get_game_state().player1
                p1_burst_summon = p1.summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(p1_burst_summon, AutumnWhirlwindSummon)
                self.assertEqual(p1_burst_summon.usages, 2)
                self.assertEqual(p1_burst_summon.curr_elem, elem)
                self.assertEqual(p1_burst_summon.ready_elem, None)

    def test_midare_ranzan_status(self):
        base_state = AddCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=MidareRanzanStatus,
        ).execute(self.BASE_GAME)
        base_state = silent_fast_swap(base_state, Pid.P1, 1)
        # freeze Kazuha
        base_state = apply_elemental_aura(base_state, Element.HYDRO, Pid.P1, char_id=2)
        base_state = apply_elemental_aura(base_state, Element.CRYO, Pid.P1, char_id=2)

        # check first swap will be fast swap
        game_state = step_swap(base_state, Pid.P1, 2)
        self.assertIs(game_state.waiting_for(), Pid.P1)

        game_state = step_swap(game_state, Pid.P1, 1)
        assert game_state.waiting_for() is Pid.P2
        game_state = skip_action_round_until(game_state, Pid.P1)
        
        # check second or later swap will be normal swap
        game_state = step_swap(game_state, Pid.P1, 2)
        self.assertIs(game_state.waiting_for(), Pid.P2)

    def test_autumn_whirlwind_summon_update_on_character_swirl(self):
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AutumnWhirlwindSummon())
            ).build()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = just(game_state.action_step(Pid.P1, SkillAction(
                    skill=CharacterSkill.SKILL2,
                    instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
                )))
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 2)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

    def test_autumn_whirlwind_summon_on_self_dmg(self):
        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AutumnWhirlwindSummon())
            ).phase(
                Act.PASSIVE_WAIT_PHASE,
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_phase(
            lambda mode: mode.end_phase()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 1)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

                p2_chars = game_state.player2.characters
                p2_c1 = p2_chars.just_get_character(1)
                p2_c2 = p2_chars.just_get_character(2)
                p2_c3 = p2_chars.just_get_character(3)
                self.assertEqual(p2_c1.hp, 9)
                self.assertEqual(p2_c2.hp, 9)
                self.assertEqual(p2_c3.hp, 9)
                self.assertFalse(p2_c1.elemental_aura.has_aura())
                self.assertIn(elem, p2_c2.elemental_aura)
                self.assertIn(elem, p2_c3.elemental_aura)

    def test_autumn_whirlwind_summon_on_summon_swirl(self):
        from src.dgisim.summon.summon import _DmgPerRoundSummon

        class AnemoSummon(_DmgPerRoundSummon):
            usages: int = 2
            DMG: ClassVar[int] = 1
            ELEMENT: ClassVar[Element] = Element.ANEMO

        base_game_state = self.BASE_GAME.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(AnemoSummon()).update_summon(AutumnWhirlwindSummon())
            ).phase(
                Act.PASSIVE_WAIT_PHASE,
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_phase(
            lambda mode: mode.end_phase()
        ).build()

        elems = [Element.PYRO, Element.HYDRO, Element.ELECTRO, Element.CRYO]
        for elem in elems:
            with self.subTest(elem=elem):
                game_state = oppo_aura_elem(base_game_state, elem)
                game_state = auto_step(game_state)
                p1_summons = game_state.player1.summons
                self.assertIn(AutumnWhirlwindSummon, p1_summons)
                summon = p1_summons.just_find(AutumnWhirlwindSummon)
                assert isinstance(summon, AutumnWhirlwindSummon)
                self.assertEqual(summon.usages, 1)
                self.assertEqual(summon.curr_elem, elem)
                self.assertEqual(summon.ready_elem, None)

                p2_chars = game_state.player2.characters
                p2_c1 = p2_chars.just_get_character(1)
                p2_c2 = p2_chars.just_get_character(2)
                p2_c3 = p2_chars.just_get_character(3)
                self.assertEqual(p2_c1.hp, 8)
                self.assertEqual(p2_c2.hp, 9)
                self.assertEqual(p2_c3.hp, 9)
                self.assertIn(elem, p2_c1.elemental_aura)
                self.assertIn(elem, p2_c2.elemental_aura)
                self.assertIn(elem, p2_c3.elemental_aura)

    def test_talent_card(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p2: p2.factory().phase(Act.END_PHASE).build()
        ).build()
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_actions([
            CardAction(
                card=PoeticsOfFuubutsu,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
            ),
            EndRoundAction(),
        ])
        gsm.step_until_next_phase()
        p1ac = gsm.get_game_state().player1.just_get_active_character()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        p1_kazuha = gsm.get_game_state().player1.characters.just_get_character(2)
        self.assertEqual(p2ac.hp, 9)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertEqual(p1ac.id, 3)
        self.assertIn(PoeticsOfFuubutsuStatus, p1_kazuha.character_statuses)

    def test_poetics_of_fuubutsu_status(self):
        base_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P1),
            status=PoeticsOfFuubutsuStatus,
        ).execute(self.BASE_GAME)
        base_state = end_round(base_state, Pid.P2)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)

        game_state = oppo_aura_elem(base_state, Element.ELECTRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)

        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 2)
        self.assertNotIn(PoeticsOfFuubutsuPyroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)

        game_state = add_damage_effect(
            game_state, 1, Element.ELECTRO,
            char_id=3,
            damage_type=DamageType(elemental_skill=True)
        ).auto_step()

        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 1)
        self.assertNotIn(PoeticsOfFuubutsuPyroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)

        game_state = remove_aura(game_state)
        game_state = add_damage_effect(
            game_state, 1, Element.PYRO,
            char_id=3,
            damage_type=DamageType(elemental_skill=True)
        ).auto_step()

        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)

        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        for status in game_state.player1.characters.just_get_character(2).character_statuses:
            if isinstance(status, MidareRanzanStatus):
                game_state = RemoveCharacterStatusEffect(
                    target=StaticTarget.from_char_id(Pid.P1, 2),
                    status=type(status),
                ).execute(game_state)

        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1_combat_statuses = game_state.player1.combat_statuses
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuPyroStatus).usages, 2)
        self.assertEqual(p1_combat_statuses.just_find(PoeticsOfFuubutsuElectroStatus).usages, 1)
        self.assertNotIn(PoeticsOfFuubutsuHydroStatus, p1_combat_statuses)
        self.assertNotIn(PoeticsOfFuubutsuCryoStatus, p1_combat_statuses)
