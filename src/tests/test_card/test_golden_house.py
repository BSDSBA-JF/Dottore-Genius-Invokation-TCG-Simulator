import unittest

from .common_imports import *

SUPPORT = GoldenHouse
SUPPORT_STATUS = GoldenHouseSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestGoldenHouse(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards(()))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 2,
            # Artifact
            FlowingRings: 2,  # cost 0
            GamblersEarrings: 2,  # cost 1
            GeneralsAncientHelm: 2,  # cost 2
            TenacityOfTheMillelith: 2, # cost 3
            # Weapon
            MagicGuide: 2,  # cost 2
            AThousandFloatingDreams: 2,  # cost 3
        }))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))

        assert FlowingRings._DICE_COST.num_dice() == 0
        assert GamblersEarrings._DICE_COST.num_dice() == 1
        assert GeneralsAncientHelm._DICE_COST.num_dice() == 2
        assert TenacityOfTheMillelith._DICE_COST.num_dice() == 3

        # check 0 cost card is still zero
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FlowingRings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))

        # check 1 cost card is still 1
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        
        # check 2 cost card is still 2
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GeneralsAncientHelm,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=MagicGuide,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))

        # check >= 3 cost card get 1 discount (once per round)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AThousandFloatingDreams,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))

        # check resets next round, and two golden house can work together, and one will be removed
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(p1_support_status(game_state, 2).usages, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AThousandFloatingDreams,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))
        self.assertIsNone(game_state.player1.supports.find(SUPPORT_STATUS, 1))
        self.assertEqual(p1_support_status(game_state, 2).usages, 1)
