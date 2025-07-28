from enum import Enum

class StatesEnum(Enum):
    IDLE = "idle",
    MOVE = "move",
    LONG_REST = "long_rest",
    JUMP = "jump",
    SHORT_REST = "short_rest"