import unittest

from .common_imports import *

SUPPORT = JadeChamber
SUPPORT_STATUS = JadeChamberSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestJadeChamber(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards(()))
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({SUPPORT: 2, Paimon: 3}))
        base_state = step_action(base_state, Pid.P1, CardAction(
            card=SUPPORT,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        assert base_state.player1.hand_cards.num_cards() == 4

        chars: list[type[Character]] = [YaeMiko, HuTao, Kaeya, Xingqiu, Ningguang] 
        # check it ensures 2 dice of the element when hand card > 3
        game_state = base_state
        for char in chars:
            with self.subTest(char=char):
                game_state = replace_character(game_state, Pid.P1, char, 1)
                game_state = next_round(game_state)
                self.assertGreaterEqual(game_state.player1.dice[char.ELEMENT], 2)
                self.assertIn(JadeChamberSupport, game_state.player1.supports)

        # check it ensures 2 dice of the element and gives an OMNI when hand card <= 3
        less_card_state = replace_hand_cards(game_state, Pid.P1, Cards({Paimon: 3}))
        less_card_state = replace_character(less_card_state, Pid.P1, Nahida, 1)
        for _ in range(10):
            game_state = next_round(less_card_state)
            self.assertGreaterEqual(game_state.player1.dice[Nahida.ELEMENT], 2)
            self.assertGreaterEqual(game_state.player1.dice[Element.OMNI], 1)
            self.assertNotIn(JadeChamberSupport, game_state.player1.supports)
