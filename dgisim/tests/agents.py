from dgisim.src.player_agent import PlayerAgent
from dgisim.src.state.game_state import GameState
from dgisim.src.action import Action, CardSelectAction
from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.card.cards import Cards

class NoneAgent(PlayerAgent):
    pass

class BasicAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, game_state: GameState, pid: GameState.pid) -> Action:
        if isinstance(game_state.get_phase(), CardSelectPhase):
            _, selected_cards = game_state.get_player(pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards)
        return super().choose_action(game_state, pid)
