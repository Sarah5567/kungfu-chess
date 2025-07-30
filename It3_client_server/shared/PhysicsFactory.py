from shared.Physics import *
from shared.enums.StatesNames import StatesNames


class PhysicsFactory:
    def __init__(self, board: Board):
        """Initialize physics factory with board."""
        self.board = board

    def create(self, state_name, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
        physics_cfg = cfg.get("physics", {})
        speed = physics_cfg.get("speed_m_per_sec", 1.0)

        match state_name:
            case StatesNames.IDLE:
                return IdlePhysics(start_cell, self.board, speed)
            case StatesNames.MOVE:
                return MovePhysics(start_cell, self.board, speed)
            case StatesNames.JUMP:
                return JumpPhysics(start_cell, self.board, speed)
            case StatesNames.SHORT_REST:
                return ShortRestPhysics(start_cell, self.board, speed)
            case StatesNames.LONG_REST:
                return LongRestPhysics(start_cell, self.board, speed)
            case _:
                raise ValueError(f"Unknown state name: {state_name}")

