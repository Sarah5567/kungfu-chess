from server.game_logic.Command import Command
from server.game_logic.Moves import Moves
from server.game_logic.Physics import Physics
from typing import Dict, Optional

from server.game_logic.enums.StatesNames import StatesNames


class State:
    def __init__(self, moves: Moves, physics: Physics):
        self._moves = moves
        self._physics = physics
        self.transitions: Dict[StatesNames, "State"] = {}
        self._current_command: Optional[Command] = None

    def set_transition(self, event: StatesNames, target: "State"):
        self.transitions[event] = target

    def reset(self, cmd: Command):
        self._current_command = cmd
        self._physics.reset(cmd)

    def update(self, now_ms: int):
        self._physics.update(now_ms)

    def process_command(self, cmd: Command) -> "State":
        next_state = self.transitions.get(cmd.type)
        next_state.reset(cmd)
        return next_state

    def is_command_possible(self, cmd: Command):
        return cmd.type in self.transitions

    def can_transition(self, now_ms: int) -> bool:
        return self._physics.update(now_ms) is not None

    def get_command(self) -> Optional[Command]:
        return self._current_command