from Board import Board
from Physics import *

class PhysicsFactory:
    def __init__(self, board: Board):
        """Initialize physics factory with board."""
        self.board = board

    def create(self, state_name, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
        physics_cfg = cfg.get("physics", {})
        speed = physics_cfg.get("speed_m_per_sec", 1.0)

        if state_name == "idle":
            return IdlePhysics(start_cell, self.board, speed)
        elif state_name == "move":
            return MovePhysics(start_cell, self.board, speed)
        elif state_name == "jump":
            return JumpPhysics(start_cell, self.board, speed)
        elif state_name == "short_rest":
            return ShortRestPhysics(start_cell, self.board, speed)
        elif state_name == "long_rest":
            return LongRestPhysics(start_cell, self.board, speed)
        else:
            raise ValueError(f"Unknown state name: {state_name}")
