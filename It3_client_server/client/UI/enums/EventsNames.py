from enum import Enum

class EventsNames(Enum):
    BLACK_MOVE = "black_move"
    WHITE_MOVE = "white_move"
    BLACK_CAPTURE = "black_capture"
    WHITE_CAPTURE = "white_capture"
    JUMP = "jump"
    VICTORY = "victory"
    BOARD_UPDATE = "board_update"
    ACTION_REQUEST = "action_request"
    INIT = "init"
    SEND_REQUEST = "send_request"