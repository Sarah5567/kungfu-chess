import json
import pathlib
import csv
import queue
import time
from typing import Dict, Tuple, Optional
from server.game_logic.Piece import Piece
from server.game_logic.Board import Board
from server.game_logic.Command import Command
from server.game_logic.enums.StatesNames import StatesNames
from server.game_logic.enums.EventsNames import EventsNames
from server.game_logic.PieceFactory import PieceFactory
from server.game_logic.EventBus import event_bus


class Game:
    def __init__(self, board: Board, pieces_root: pathlib.Path, placement_csv: pathlib.Path):
        self.board = board
        self.piece_factory = PieceFactory(board, pieces_root)
        self.pieces: Dict[str, Piece] = {}
        self.pos_to_piece: Dict[Tuple[int, int], Piece] = {}
        self.start_time = time.monotonic()
        self._load_pieces_from_csv(placement_csv)
        self.user_input_queue = queue.Queue()
        self.subscriptions()

    def subscriptions(self):
        event_bus.subscribe(EventsNames.ACTION_REQUEST, lambda event: self.user_input_queue.put(event.data['cmd']))

    def _load_pieces_from_csv(self, csv_path: pathlib.Path):
        with csv_path.open() as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                for col_idx, code in enumerate(row):
                    code = code.strip()
                    if not code:
                        continue
                    cell = (row_idx, col_idx)
                    piece = self.piece_factory.create_piece(code, cell)
                    self.pieces[piece.get_id()] = piece
                    self.pos_to_piece[cell] = piece

    def game_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def apply_command(self, cmd: Command) -> Optional[Dict]:
        src_cell = self.board.algebraic_to_cell(cmd.params[0])
        dst_cell = self.board.algebraic_to_cell(cmd.params[1])

        if src_cell not in self.pos_to_piece:
            return None  # Source cell is empty

        moving_piece = self.pos_to_piece[src_cell]

        dst_empty = dst_cell not in self.pos_to_piece
        if not dst_empty:
            target_piece = self.pos_to_piece[dst_cell]
            if target_piece.get_id()[1] == moving_piece.get_id()[1]:
                return None  # Destination has friendly piece

        if not self.is_path_clean(dst_cell, src_cell):
            return None  # Move is blocked

        if moving_piece.is_command_possible(cmd, self.game_time_ms(), dst_empty):
            moving_piece.on_command(cmd)

        # Apply the command to the piece
            self._update_position_mapping()

        # Return both the command and updated board state
        return {
            "type": EventsNames.BLACK_MOVE if moving_piece.get_id()[1] == 'B' else EventsNames.WHITE_MOVE,
            "data": {
                "command": cmd
            }
        }

    def is_path_clean(self, dst_cell, src_cell):
        dx = dst_cell[1] - src_cell[1]
        dy = dst_cell[0] - src_cell[0]
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        cur_cell = (src_cell[0] + step_y, src_cell[1] + step_x)
        while cur_cell != dst_cell:
            if cur_cell in self.pos_to_piece:
                return False
            cur_cell = (cur_cell[0] + step_y, cur_cell[1] + step_x)
        return True

    def _update_position_mapping(self):
        self.pos_to_piece.clear()
        to_remove = set()
        to_promote = []

        for piece in list(self.pieces.values()):
            x, y = map(int, piece._state._physics.get_pos())
            if not self.board.is_valid_cell(x, y):
                continue
            cell_x = x // self.board.cell_W_pix
            cell_y = y // self.board.cell_H_pix
            pos = (cell_y, cell_x)

            if pos in self.pos_to_piece:
                opponent = self.pos_to_piece[pos]
                if piece._state._current_command and piece._state._current_command.type == StatesNames.JUMP:
                    continue
                if self.should_capture(opponent, piece):
                    event_bus.publish(
                        EventsNames.BLACK_CAPTURE if piece.get_id()[1] == 'B' else EventsNames.WHITE_CAPTURE,
                        {'capture_piece': piece.get_id(), 'captured_piece': opponent.get_id(), 'sound': 'capture.wav'}
                    )
                    self.pos_to_piece[pos] = piece
                    to_remove.add(opponent.get_id())
                else:
                    to_remove.add(piece.get_id())
                    event_bus.publish(
                        EventsNames.BLACK_CAPTURE if opponent.get_id()[1] == 'B' else EventsNames.WHITE_CAPTURE,
                        {'capture_piece': opponent.get_id(), 'captured_piece': piece.get_id(), 'sound': 'capture.wav'}
                    )
            else:
                self.pos_to_piece[pos] = piece

            if piece.get_id()[0] == 'P' and (pos[0] == 0 or pos[0] == 7):
                to_promote.append((piece.get_id(), pos))

        for k in to_remove:
            self.pieces.pop(k, None)

        for pawn_id, pos in to_promote:
            if pawn_id in self.pieces:
                new_queen = self.piece_factory.create_piece('Q' + self.pieces[pawn_id].get_id()[1], pos)
                self.pieces[new_queen.get_id()] = new_queen
                self.pos_to_piece[pos] = new_queen

    def should_capture(self, opponent, piece):
        if not opponent._state._current_command or opponent._state._current_command.type in [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return True
        if piece._state._current_command and piece._state._current_command.type not in  [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return opponent._state._physics.start_time > piece._state._physics.start_time
        return False

    def get_board_state(self):
        return {
            "pieces": {
                pid: {
                    "id": pid,
                    "pos": piece._state._physics.get_pos(),
                    "state": piece._state
                }
                for pid, piece in self.pieces.items()
            }
        }

    def run(self):
        self.start_time = time.monotonic()
        start_ms = self.game_time_ms()

        # Reset all pieces
        for piece in self.pieces.values():
            piece.reset(start_ms)

        last_state_str = ""

        while not self.winner():
            now = self.game_time_ms()

            # Update physics for each piece
            for piece in self.pieces.values():
                piece.update(now)

            # Update piece-to-position mapping and handle captures/promotions
            self._update_position_mapping()

            # Process user commands from queue
            while not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()

                response = self.apply_command(cmd)
                if response:
                    event_bus.publish(response["type"], response["data"])

            # Publish board state if it changed
            current_state = self.get_board_state()

            event_bus.publish(EventsNames.BOARD_UPDATE, self.get_board_state())
            time.sleep(0.01)  # reduce CPU usage

            # Check win condition
        winner = self.winner()
        event_bus.publish(EventsNames.VICTORY, {"winner": winner})


    def winner(self) -> str | None:
        kings = [piece for piece in self.pieces.values() if piece.get_type() == 'King']
        if len(kings) == 1:
            return kings[0].get_color()
        return None