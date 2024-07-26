import unittest

from .common_imports import *

def p1_echoes_status(game_state: GameState) -> EchoesOfAnOfferingStatus:
    return p1_active_char(game_state).character_statuses.just_find_type(EchoesOfAnOfferingStatus)

class TestEchoesOfAnOffering(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EchoesOfAnOffering: 1, NRE: 3}))
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards((Paimon, Liben)))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=EchoesOfAnOffering,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))

        self.assertEqual(p1_echoes_status(base_state), EchoesOfAnOfferingStatus())

        # check skill can add dice if num dice <= num hand-cards
        game_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 6}))
        dice_before = game_state.player1.dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.OMNI: 3}))
        self.assertEqual(
            game_state.player1.dice - dice_before,
            ActualDice({Element.OMNI: -3, Element.GEO: 1}),
        )
        self.assertEqual(game_state.player1.hand_cards, Cards({NRE: 3}))
        
        # check dice addition cannot be triggered twice per round
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 6}))
        dice_before = game_state.player1.dice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.OMNI: 3}))
        self.assertEqual(
            game_state.player1.dice - dice_before,
            ActualDice({Element.OMNI: -3}),
        )
        self.assertEqual(game_state.player1.hand_cards, Cards({NRE: 3}))

        # check normal attack can trigger card draw once per round
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 6}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, cost=ActualDice({Element.OMNI: 3}))
        self.assertEqual(game_state.player1.hand_cards, Cards({NRE: 3, Liben: 1}))

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, cost=ActualDice({Element.OMNI: 3}))
        self.assertEqual(game_state.player1.hand_cards, Cards({NRE: 3, Liben: 1}))

        # check first skill (normal attack) adds dice then draw card
        a1, a2 = PuppetAgent(), PuppetAgent()
        game_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 6}))
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        gsm.step_until_holds(lambda gs: gs.player1.dice[Element.GEO] == 1)
        self.assertNotIn(Liben, gsm.get_game_state().player1.hand_cards)
        gsm.auto_step()
        self.assertIn(Liben, gsm.get_game_state().player1.hand_cards)

    def test_reset(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EchoesOfAnOffering: 1, NRE: 3}))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=EchoesOfAnOffering,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        base_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 6}))

        # check resets if skill is used
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertNotEqual(p1_echoes_status(game_state), EchoesOfAnOfferingStatus())
        game_state = next_round(game_state)
        self.assertEqual(p1_echoes_status(game_state), EchoesOfAnOfferingStatus())

        # check resets if normal attack is used
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertNotEqual(p1_echoes_status(game_state), EchoesOfAnOfferingStatus())
        game_state = next_round(game_state)
        self.assertEqual(p1_echoes_status(game_state), EchoesOfAnOfferingStatus())
