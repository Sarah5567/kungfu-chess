from datetime import datetime
from typing import Any

from server.handlers.Handler import Handler
from shared import Piece
from shared.Command import Command
from shared.enums.EventsNames import EventsNames


class MoveHandler(Handler):
    def handle(self, params: dict[str, Any]) -> dict[str, Any] | None:
        src_cell: (int, int) = params["src_cell"]
        dst_cell: (int, int) = params["dst_cell"]

        pieces: dict[str, Piece] = params["pieces"]
        cmd: Command = params["command"]

        piece = pieces.get(cmd.piece_id)
        if not piece:
            return None

        src_alg = cmd.params[0]
        dst_alg = cmd.params[1]

        # בדיקה אם בכלל יש כלי במקור
        if src_cell != piece._state._physics.start_cell:
            return None

        # בדיקה האם התא ביעד תפוס ע"י כלי ידידותי
        dst_piece = next((p for p in pieces.values()
                          if p._state._physics.get_pos_cell() == dst_cell), None)

        dst_empty = dst_piece is None or dst_piece.get_id() == piece.get_id()

        if not self.is_path_clean(src_cell, dst_cell, pieces):
            return None

        if not piece.is_command_possible(cmd, dst_empty):
            return None

        event_data = {
            "type": EventsNames.BLACK_MOVE if piece.get_id()[1] == 'B' else EventsNames.WHITE_MOVE,
            "piece_id": piece.get_id(),
            "command": cmd,
            "source": src_alg,
            "destination": dst_alg,
            "time": int(datetime.now().timestamp() * 1000)
        }

        return {
            "type": "MOVE",
            "piece_id": piece.get_id(),
            "cmd": cmd,
            "event": [event_data]
        }

    def is_path_clean(self, src_cell: tuple[int, int], dst_cell: tuple[int, int], pieces: dict[str, Piece]) -> bool:
        dx = dst_cell[1] - src_cell[1]
        dy = dst_cell[0] - src_cell[0]
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        if (step_x != 0 or step_y != 0) and (abs(dx) == abs(dy) or dx == 0 or dy == 0):
            cur_cell = (src_cell[0] + step_y, src_cell[1] + step_x)
            while cur_cell != dst_cell:
                if any(p._state._physics.get_pos_cell() == cur_cell for p in pieces.values()):
                    return False
                cur_cell = (cur_cell[0] + step_y, cur_cell[1] + step_x)
        return True
