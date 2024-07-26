import unittest

from .common_imports import *


class TestGamblersEarrings(unittest.TestCase):
    def test_gamblers_earrings(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(
                    3
                ).f_active_character(
                    lambda ac: ac.factory().energy(
                        ac.max_energy
                    ).build()
                ).build()  # Keqing
            ).f_hand_cards(
                lambda hcs: hcs.add(GamblersEarrings).add(GamblersEarrings).add(GamblersEarrings)
            ).build()
        ).f_player2(
            lambda p2: p2.factory().phase(
                Act.END_PHASE
            ).f_combat_statuses(
                lambda cstts: cstts.update_status(IcicleStatus())  # Kaeya's burst
            ).build()
        ).build()
        base_game = kill_character(base_game, char_id=1, hp=1)
        base_game = kill_character(base_game, char_id=3, hp=1)
        for i in range(1, 4):
            base_game = just(base_game.action_step(Pid.P1, CardAction(
                card=GamblersEarrings,
                instruction=StaticTargetInstruction(
                    dice=ActualDice({Element.OMNI: 1}),
                    target=StaticTarget(Pid.P1, Zone.CHARACTERS, i)
                )
            )))
            base_game = auto_step(base_game)
        assert isinstance(base_game.player1.just_get_active_character(), Keqing)
        p1ac = base_game.player1.just_get_active_character()
        self.assertIn(GamblersEarringsStatus, p1ac.character_statuses)
        gamblers = p1ac.character_statuses.just_find(GamblersEarringsStatus)
        self.assertEqual(gamblers.usages, 3)

        # overloaded kill checks swaps before triggering gamblers earrings
        game_state = oppo_aura_elem(base_game, Element.PYRO)
        game_state = just(game_state.action_step(
            Pid.P1,
            SkillAction(
                skill=CharacterSkill.SKILL2,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
            )
        ))
        num_dice = game_state.player1.dice.num_dice()
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_holds(
            lambda gs:
            gs.player1.just_get_active_character().elemental_aura.contains(Element.CRYO),
        )
        self.assertEqual(gsm.get_game_state().player1.dice.num_dice(), num_dice)

        gsm.auto_step()
        self.assertEqual(gsm.get_game_state().player1.dice.num_dice(), num_dice + 2)
        gamblers = p1_active_char(gsm.get_game_state()).character_statuses.just_find(GamblersEarringsStatus)
        self.assertEqual(gamblers.usages, 2)

        # multiple kill rewards correctly
        game_state = oppo_aura_elem(base_game, Element.PYRO)  # overload, so P2 doesn't need to swap
        num_dice = game_state.player1.dice.num_dice() - 4  # burst cost deduction
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST,
            cost=ActualDice({Element.OMNI: 4}),
        )
        self.assertEqual(game_state.player1.dice.num_dice(), num_dice + 4)
        gamblers = p1_active_char(game_state).character_statuses.just_find(GamblersEarringsStatus)
        self.assertEqual(gamblers.usages, 1)
