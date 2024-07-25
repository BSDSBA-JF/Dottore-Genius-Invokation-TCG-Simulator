import unittest

from .common_imports import *

SUPPORT = OperaEpiclese
SUPPORT_STATUS = OperaEpicleseSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestGoldenHouse(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_character(base_state, Pid.P1, Keqing, 1)
        base_state = replace_character(base_state, Pid.P1, Keqing, 2)
        base_state = replace_character(base_state, Pid.P1, Keqing, 3)
        base_state = replace_character(base_state, Pid.P2, HuTao, 1)
        base_state = replace_character(base_state, Pid.P2, HuTao, 2)
        base_state = replace_character(base_state, Pid.P2, HuTao, 3)
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards(()))
        base_state = replace_deck_cards(base_state, Pid.P2, OrderedCards(()))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 2,
            # Artifact
            GamblersEarrings: 3,  # cost 1
            GeneralsAncientHelm: 3,  # cost 2
            TenacityOfTheMillelith: 3, # cost 3
            # Weapon
            TravelersHandySword: 3,  # cost 2
            AquilaFavonia: 3,  # cost 3
            # Talent
            ThunderingPenance: 3,  # cost 3
        }))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({
            # Artifact
            GamblersEarrings: 3,  # cost 1
            GeneralsAncientHelm: 3,  # cost 2
            TenacityOfTheMillelith: 3, # cost 3
            # Weapon
            WhiteTassel: 3,  # cost 2
            LithicSpear: 3,  # cost 3
            # Talent
            SanguineRouge: 3,  # cost 2
        }))
        base_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 20}))

        assert GamblersEarrings._DICE_COST.num_dice() == 1
        assert GeneralsAncientHelm._DICE_COST.num_dice() == 2
        assert TenacityOfTheMillelith._DICE_COST.num_dice() == 3
        assert TravelersHandySword._DICE_COST.num_dice() == 2
        assert AquilaFavonia._DICE_COST.num_dice() == 3
        assert WhiteTassel._DICE_COST.num_dice() == 2
        assert LithicSpear._DICE_COST.num_dice() == 3
        assert ThunderingPenance._DICE_COST.num_dice() == 3
        assert SanguineRouge._DICE_COST.num_dice() == 2

        # equial cost equipments triggers Opera Epiclese
        game_state = base_state
        game_state = play_support_card(game_state, Pid.P1, SUPPORT)
        self.assertEqual(game_state.player1.dice[p1_active_char(game_state).ELEMENT], 1)
        self.assertEqual(p1_support_status(game_state, sid=1).usages, 2)

        # and once per round only
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_swap(game_state, Pid.P2, 2)
        self.assertEqual(game_state.player1.dice[p1_active_char(game_state).ELEMENT], 1)
        self.assertEqual(p1_support_status(game_state, sid=1).usages, 2)
        
        # oppo equip 3
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = play_char_target_card(game_state, Pid.P2, LithicSpear, char_id=1, cost=3)  # P1: 0; P2: 3

        # Opera Epiclese resets the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = replace_dice(game_state, Pid.P1, ActualDice({Element.OMNI: 20}))
        game_state = skip_action_round_until(game_state, Pid.P1)
        
        # Opera Epiclese triggers only when equal or higher cost equipments are equipped
        game_state = play_char_target_card(game_state, Pid.P1, TravelersHandySword, char_id=1, cost=2)  # P1: 2; P2: 3
        self.assertEqual(game_state.player1.dice[p1_active_char(game_state).ELEMENT], 0)
        self.assertEqual(p1_support_status(game_state, sid=1).usages, 2)
        game_state = play_char_target_card(game_state, Pid.P1, GamblersEarrings, char_id=2, cost=1)  # P1: 3; P2: 3
        self.assertEqual(game_state.player1.dice[p1_active_char(game_state).ELEMENT], 1)
        self.assertEqual(p1_support_status(game_state, sid=1).usages, 1)

        # check Opera Epiclese resets and direct trigger (when satisfied) the next round
        game_state = play_dice_only_card(game_state, Pid.P1, ThunderingPenance, cost=3)  # P1: 6; P2: 3
        game_state = play_dice_only_card(game_state, Pid.P2, SanguineRouge, cost=2)  # P1: 6; P2: 5
        game_state = force_roll_element(game_state, Pid.P1, Element.OMNI)
        game_state = end_round(game_state, Pid.P1)
        game_state = end_round(game_state, Pid.P2)
        game_state = auto_step(step_until_phase(game_state, game_state.mode.action_phase))
        assert game_state.waiting_for() is Pid.P1
        self.assertEqual(game_state.player1.dice[p1_active_char(game_state).ELEMENT], 1)
        self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
