from Command import Command
from Moves import Moves
from Graphics import Graphics
from Physics import Physics
from typing import Dict, Optional


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        self._moves = moves
        self._graphics = graphics
        self._physics = physics
        self.transitions: Dict[str, "State"] = {}
        self._current_command: Optional[Command] = None

    def set_transition(self, event: str, target: "State"):
        self.transitions[event] = target

    def reset(self, cmd: Command):
        self._current_command = cmd
        self._graphics.reset(cmd)
        self._physics.reset(cmd)

    def update(self, now_ms: int) -> "State":
        self._graphics.update(now_ms)
        cmd = self._physics.update(now_ms)
        if cmd is not None:
            return self.process_command(cmd, now_ms)
        return self

    def process_command(self, cmd: Command, now_ms: int) -> "State":
        next_state = self.transitions.get(cmd.type)
        if next_state is None:
            return self  # stay in current state
        next_state.reset(cmd)
        return next_state

    def can_transition(self, now_ms: int) -> bool:
        return self._physics.update(now_ms) is not None

    def get_command(self) -> Optional[Command]:
        return self._current_command

