from dgisim.src.state.game_state import GameState


class Phase:
    def run(self, game_state: GameState) -> GameState:
        raise Exception("Not Overriden")

    def run_action(self, game_state: GameState, pid: GameState.pid, action) -> GameState:
        raise Exception("Not Overriden")
