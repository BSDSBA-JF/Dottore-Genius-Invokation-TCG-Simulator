import unittest

from .common_imports import *

SUPPORT = MementoLens
SUPPORT_STATUS = MementoLensSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> MementoLensSupport:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestMementoLens(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 1,
            StrategicReserve: 2,  # Talent
            SacrificialFragments: 3,  # Weapon
            AThousandFloatingDreams: 2,  # Weapon
            TenacityOfTheMillelith: 2,  # Artifact
            DawnWinery: 2,  # Location
            ParametricTransformer: 2,  # Item
            Paimon: 2, # Companion
        }))
        base_state = replace_character(base_state, Pid.P1, Ningguang, 1)
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        base_state = grant_all_infinite_revival(base_state)

        assert StrategicReserve._DICE_COST.num_dice() == 4
        assert SacrificialFragments._DICE_COST.num_dice() == 3
        assert AThousandFloatingDreams._DICE_COST.num_dice() == 3
        assert TenacityOfTheMillelith._DICE_COST.num_dice() == 3
        assert DawnWinery._DICE_COST.num_dice() == 2
        assert ParametricTransformer._DICE_COST.num_dice() == 2
        assert Paimon._DICE_COST.num_dice() == 3

        # check talent, item cannot benefit form the support
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=StrategicReserve,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 4})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=StrategicReserve,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 4})),
        ))

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ParametricTransformer,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 2})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ParametricTransformer,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 2})),
        ))
        game_state = RemoveSupportEffect(Pid.P1, sid=2).execute(game_state)
        game_state = RemoveSupportEffect(Pid.P1, sid=3).execute(game_state)

        # check played card can enjoy reduction once per round
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 3}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 1}),
            ),
        ))

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SacrificialFragments,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 3}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SacrificialFragments,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 3}),  # once per round, so no discount
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=DawnWinery,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 2})),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 3})),
        ))
        game_state = RemoveSupportEffect(Pid.P1, sid=2).execute(game_state)
        game_state = RemoveSupportEffect(Pid.P1, sid=3).execute(game_state)

        # check card of the same type but different name cannot enjoy discount
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AThousandFloatingDreams,  # previous used SacrificalFragments
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 3}),
            ),
        ))
        
        # check the rest of cards can enjoy discount
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=DawnWinery,
            instruction=DiceOnlyInstruction(dice=ActualDice({})),
        ))

        game_state = end_round(next_round_with_great_omni(game_state), Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SacrificialFragments,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.GEO: 1}),
            ),
        ))

        game_state = end_round(next_round_with_great_omni(game_state), Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 1})),
        ))
