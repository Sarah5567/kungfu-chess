from client.UI.Command import Command
from client.UI.Graphics import Graphics
from typing import Dict, Optional

from shared.enums.StatesNames import StatesNames


class State:
    def __init__(self, graphics: Graphics):
        self._graphics = graphics
        self.transitions: Dict[StatesNames, "State"] = {}
        self._current_command: Optional[Command] = None

    def set_transition(self, event: StatesNames, target: "State"):
        self.transitions[event] = target

    def reset(self, time_ms: int):
        self._graphics.reset(time_ms)

    def update(self, now_ms: int):
        self._graphics.update(now_ms)

    def process_command(self, cmd: Command) -> "State":
        next_state = self.transitions.get(cmd.type)
        next_state.reset(cmd.timestamp)
        return next_state

    # def is_command_possible(self, cmd: Command):
    #     return cmd.type in self.transitions

    # def can_transition(self, now_ms: int) -> bool:
    #     return self._physics.update(now_ms) is not None

    def get_command(self) -> Optional[Command]:
        return self._current_command