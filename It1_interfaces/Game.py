import csv
import pathlib
import time
import queue
import threading
import cv2
from typing import Dict, Tuple, Optional

from Board import Board
from Command import Command
from Piece import Piece
from img import Img
from PieceFactory import PieceFactory

class Game:
    def __init__(self, board: Board, pieces_root: pathlib.Path, placement_csv: pathlib.Path):
        self.board = board
        self.user_input_queue = queue.Queue()
        self.start_time = time.monotonic()
        self.piece_factory = PieceFactory(board, pieces_root)
        self.pieces: Dict[str, Piece] = {}
        self.pos_to_piece: Dict[Tuple[int, int], Piece] = {}
        self._current_board = None
        self._load_pieces_from_csv(placement_csv)

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
                    self.pieces[piece.get_unique()] = piece
                    self.pos_to_piece[cell] = piece

    def game_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_user_input_thread(self):
        def listen_to_input():
            while True:
                cmd_str = input("Command (e.g. RW Move a2 a4): ")
                parts = cmd_str.strip().split()
                if len(parts) < 2:
                    continue
                cmd_type, *params = parts
                if not self.board.algebraic_to_cell(params[0]) in self.pos_to_piece:
                    continue
                piece_id = self.pos_to_piece[self.board.algebraic_to_cell(params[0])].get_id()
                cmd = Command(timestamp=self.game_time_ms(), piece_id=piece_id, type=cmd_type.lower(), params=params)
                self.user_input_queue.put(cmd)
        threading.Thread(target=listen_to_input, daemon=True).start()

    def run(self):
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for piece in self.pieces.values():
            piece.reset(start_ms)

        while not self._is_win():
            now = self.game_time_ms()

            for piece in self.pieces.values():
                piece.update(now)

            while not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()
                self._process_input(cmd, now)

            self._update_position_mapping()
            self._draw()
            if not self._show():
                break

            # self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    def _process_input(self, cmd: Command, now_ms: int):
        self.pos_to_piece[self.board.algebraic_to_cell(cmd.params[0])].on_command(cmd, now_ms)

    def _draw(self):
        board = self.clone_board()
        now_ms = self.game_time_ms()
        for piece in self.pieces.values():
            piece.draw_on_board(board, now_ms)
        self._current_board = board

    def _show(self) -> bool:
        cv2.imshow("Chess", self._current_board.img.img)
        key = cv2.waitKey(30)
        return key != 27  # ESC = quit

    # def _resolve_collisions(self):
    #     pos_to_piece = {}
    #     for pid, piece in list(self.pieces.items()):
    #         pos = tuple(map(int, piece._state._physics.get_pos()))
    #         if pos in pos_to_piece:
    #             # שני כלים על אותה משבצת - מחק אחד מהם
    #             del self.pieces[pid]
    #         else:
    #             pos_to_piece[pos] = piece
    #     self._update_position_mapping()

    def _update_position_mapping(self):
        self.pos_to_piece.clear()
        for piece in self.pieces.values():
            x, y = map(int, piece._state._physics.get_pos())
            cell_x = x // self.board.cell_W_pix
            cell_y = y // self.board.cell_H_pix
            self.pos_to_piece[(cell_y, cell_x)] = piece

    def _is_win(self) -> bool:
        kings = [p for p in self.pieces.values() if p.get_id().lower().startswith("k")]
        return len(kings) <= 1

    def _announce_win(self):
        if len(self.pieces) == 0:
            print("Draw.")
        elif len(self.pieces) == 1:
            print(f"{list(self.pieces.values())[0].get_id()} wins!")
        else:
            print("Game over.")
