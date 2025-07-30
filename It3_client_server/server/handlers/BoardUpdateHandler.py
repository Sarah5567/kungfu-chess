from typing import Any

from server.handlers.Handler import Handler
from shared.enums.EventsNames import EventsNames
from shared.enums.StatesNames import StatesNames


class BoardUpdateHandler(Handler):
    def handle(self, params: dict[str, Any]) -> dict[str, Any] | None:
        pieces: dict[str, dict[str, Any]] = params["pieces"]
        cell_W_pix = params["cell_W_pix"]
        cell_H_pix = params["cell_H_pix"]
        piece_factory = params["piece_factory"]

        updated_pieces = pieces.copy()
        updated_pos_to_piece: dict[tuple[int, int], dict[str, Any]] = {}
        to_remove = set()
        to_promote: list[tuple[str, tuple[int, int]]] = []
        events = []
        captured_pieces: dict[str, dict[str, Any]] = {}

        for piece in list(pieces.values()):
            x, y = map(int, piece["state"]["physics"]["pos"])
            if not x % cell_W_pix == 0 and y % cell_H_pix == 0:
                continue

            cell_x = x // cell_W_pix
            cell_y = y // cell_H_pix
            pos = (cell_y, cell_x)

            if pos in updated_pos_to_piece:
                opponent = updated_pos_to_piece[pos]

                if piece["state"]["current_command"] and piece["state"]["current_command"]["type"] == StatesNames.JUMP:
                    continue

                if self.should_capture(opponent, piece):
                    updated_pos_to_piece[pos] = piece
                    to_remove.add(opponent["id"])
                    captured_pieces[opponent["id"]] = opponent
                    captured, capturer = opponent, piece
                else:
                    to_remove.add(piece["id"])
                    captured_pieces[piece["id"]] = piece
                    captured, capturer = piece, opponent

                event_type = (
                    EventsNames.BLACK_CAPTURE if captured["id"][1] == 'B'
                    else EventsNames.WHITE_CAPTURE
                )
                events.append({
                    "type": event_type,
                    "captured_piece": captured["id"],
                })

            else:
                updated_pos_to_piece[pos] = piece

            if piece["id"][0] == 'P' and (pos[0] == 0 or pos[0] == 7):
                to_promote.append((piece["id"], pos))

        for pid in to_remove:
            updated_pieces.pop(pid, None)

        for pawn_id, pos in to_promote:
            if pawn_id in updated_pieces:
                color = updated_pieces[pawn_id]["id"][1]
                queen = piece_factory.create_piece(f'Q{color}', pos)
                updated_pieces.pop(pawn_id)
                updated_pieces[queen.get_id()] = queen
                updated_pos_to_piece[pos] = {
                    "id": queen.get_id(),
                    "state": {
                        "physics": {
                            "pos": pos,
                            "start_time": queen._state._physics.start_time
                        },
                        "current_command": {
                            "type": queen._state._current_command.type
                        } if queen._state._current_command else None
                    }
                }

        if to_remove or to_promote:
            return {
                "type": "BOARD_UPDATE",
                "pieces": updated_pieces,
                "pos_to_piece": {str(k): v["id"] for k, v in updated_pos_to_piece.items()},
                "captured_pieces": captured_pieces,
                "events": events
            }

        return None

    def should_capture(self, opponent: dict[str, Any], piece: dict[str, Any]) -> bool:
        opponent_cmd = opponent["state"]["current_command"]
        piece_cmd = piece["state"]["current_command"]

        if not opponent_cmd or opponent_cmd["type"] in [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return True
        if piece_cmd and piece_cmd["type"] not in [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return opponent["state"]["physics"]["start_time"] > piece["state"]["physics"]["start_time"]
        return False
