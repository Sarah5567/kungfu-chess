import csv
import pathlib
import time
import queue
import cv2
from typing import Dict, Tuple, Optional, Callable, Any
import threading
import keyboard
from client.UI.Board import Board
from client.UI.Command import Command
from client.UI.Log import Log
from client.UI.Piece import Piece
from client.UI.Score import Score
from client.UI.Screen import Screen
from client.UI.EventBus import event_bus, Event
from client.UI.PieceFactory import PieceFactory
from playsound import playsound


class Game:
    def __init__(self, screen: Screen, board: Board, pieces_root: pathlib.Path, placement_csv: pathlib.Path,
                 sounds_root: pathlib.Path, websocket, role: str, board_state: dict[str, Any]):
        self.screen = screen
        self._sounds_root = sounds_root
        self.board = board
        self.websocket = websocket
        self.role = role
        self.user_input_queue = queue.Queue()
        self.start_time = 0
        self.piece_factory = PieceFactory(self.board, pieces_root)
        self.pieces: Dict[str, Piece] = {}
        self.pos_to_piece: Dict[Tuple[int, int], Piece] = {}
        self._current_board = None
        self._handle_board_update(Event("INIT", board_state))

        self.focus_cell = (0, 0)
        self.focus_cell2 = (self.board.H_cells - 1, 0)

        self._selection_mode = "source"
        self._selected_source: Optional[Tuple[int, int]] = None
        self._selection_mode2 = "source"
        self._selected_source2: Optional[Tuple[int, int]] = None

        self._lock = threading.Lock()
        self._running = True

        self.black_log: Log = Log()
        self.white_log: Log = Log()
        self.black_score: Score = Score()
        self.white_score: Score = Score()
        self.subscriptions(sounds_root)

    def subscriptions(self, sounds_root):
        event_bus.subscribe("BLACK_MOVE", self.black_log.update_log)
        event_bus.subscribe("WHITE_MOVE", self.white_log.update_log)

        event_bus.subscribe('BLACK_CAPTURE', self.black_score.update_score)
        event_bus.subscribe('WHITE_CAPTURE', self.white_score.update_score)

        for event in [
            "BLACK_MOVE",
            "WHITE_MOVE",
            "BLACK_CAPTURE",
            "WHITE_CAPTURE",
            "JUMP",
            "VICTORY",
        ]:
            event_bus.subscribe(event, self.play_sounds)

        event_bus.subscribe("BOARD_UPDATE", self._handle_board_update)

    def _handle_board_update(self, event: Event):
        self.pieces.clear()
        self.pos_to_piece.clear()

        updated_pieces = event.data.get("pieces", {})
        for pid, piece_data in updated_pieces.items():
            pos : tuple[int, int] = piece_data["pos"]
            state = piece_data["state"]

            if not pid in self.pieces:
                piece = self.piece_factory.create_piece(pid, pos)
                self.pieces[pid] = piece
            self.pieces[pid]._state = state["name"]



    def _get_response(self, event : Event):
        event_type: str = event.data['type']

        match event_type:
            case 'MOVE':
                self.pieces['piece_id'].on_command(event.data['cmd'])
            case 'BOARD_UPDATE':
                self.pieces = event.data['pieces']

        for e in event.data['events']:
            event_bus.publish(e['type'], e)


    def play_sounds(self, event : Event):
        def _play():
            playsound(str(self._sounds_root / event.data['sound']))

        threading.Thread(target=_play, daemon=True).start()

    def game_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_keyboard_thread(self):
        def keyboard_loop():
            while self._running:
                time.sleep(0.05)
                with self._lock:
                    if self.role == "BLACK":
                        dy, dx = 0, 0
                        if keyboard.is_pressed('esc'):
                            self._running = False
                            break
                        if keyboard.is_pressed('left'):
                            dx = -1
                        elif keyboard.is_pressed('right'):
                            dx = 1
                        if keyboard.is_pressed('up'):
                            dy = -1
                        elif keyboard.is_pressed('down'):
                            dy = 1
                        if dx != 0 or dy != 0:
                            h, w = self.board.H_cells, self.board.W_cells
                            y, x = self.focus_cell
                            self.focus_cell = ((y + dy) % h, (x + dx) % w)
                            time.sleep(0.2)
                        if keyboard.is_pressed('enter'):
                            self._on_enter_pressed()
                            time.sleep(0.2)
                    elif self.role == "WHITE":
                        dy2, dx2 = 0, 0
                        if keyboard.is_pressed('a'):
                            dx2 = -1
                        elif keyboard.is_pressed('d'):
                            dx2 = 1
                        if keyboard.is_pressed('w'):
                            dy2 = -1
                        elif keyboard.is_pressed('s'):
                            dy2 = 1
                        if dx2 != 0 or dy2 != 0:
                            h, w = self.board.H_cells, self.board.W_cells
                            y2, x2 = self.focus_cell2
                            self.focus_cell2 = ((y2 + dy2) % h, (x2 + dx2) % w)
                            time.sleep(0.2)
                        if keyboard.is_pressed('space'):
                            self._on_space_pressed()
                            time.sleep(0.2)

        threading.Thread(target=keyboard_loop, daemon=True).start()

    def run(self):
        self.start_time = time.monotonic()
        self.screen.reset()

        # while True:
        #     key = cv2.waitKey(0)
        #     if key == 13:  # Enter
        #         break

        for piece in self.pieces.values():
            piece.reset(self.game_time_ms())
        self.screen.show("Chess")


        self.start_keyboard_thread()

        while self._running and not self._is_win():
            self._draw()
            for piece in self.pieces.values():
                piece.update(self.game_time_ms())
            self.screen.show("Chess")
            cv2.waitKey(1)

        self._announce_win()
        self._running = False
        cv2.destroyAllWindows()

    def get_path_cells(self, src: Tuple[int, int], dst: Tuple[int, int]) -> list[Tuple[int, int]]:
        path = []
        dx = dst[1] - src[1]
        dy = dst[0] - src[0]
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        cur = (src[0] + step_y, src[1] + step_x)
        while cur != dst:
            path.append(cur)
            cur = (cur[0] + step_y, cur[1] + step_x)
        return path

    def _draw(self):
        board = self.clone_board()
        now_ms = self.game_time_ms()

        for piece in self.pieces.values():
            piece.draw_on_board(board, now_ms)

        self._draw_rectangle_on_board(board, self.focus_cell, (0, 255, 255))
        self._draw_rectangle_on_board(board, self.focus_cell2, (255, 0, 0))

        if self._selected_source:
            self._draw_rectangle_on_board(board, self._selected_source, (0, 0, 255))

        if self._selected_source2:
            self._draw_rectangle_on_board(board, self._selected_source2, (0, 255, 0))

        self._current_board = board
        self.screen.update_left(self.black_log.log)
        self.screen.update_right(self.white_log.log)
        self.screen.draw(self._current_board, white_score=self.white_score.score, black_score=self.black_score.score)

    def _cell_to_rect(self, cell: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Receives a cell and returns the coordinates of the rectangle surrounding it in pixels"""
        y, x = cell
        x1 = x * self.board.cell_W_pix
        y1 = y * self.board.cell_H_pix
        x2 = (x + 1) * self.board.cell_W_pix
        y2 = (y + 1) * self.board.cell_H_pix
        return x1, y1, x2, y2

    def _draw_rectangle_on_board(self, board, cell: Tuple[int, int], color: Tuple[int, int, int]):
        """Draws a rectangle on a cell in the given color"""
        x1, y1, x2, y2 = self._cell_to_rect(cell)
        cv2.rectangle(board.img.img, (x1, y1), (x2, y2), color, 2)

    def _is_win(self) -> bool:
        kings = [p for p in self.pieces.values() if p.get_id().lower().startswith("k")]
        return len(kings) <= 1

    def _announce_win(self):
        event_bus.publish("VICTORY", {'sound': 'victory.WAV'})
        king = next(p for p in self.pieces.values() if p.get_id().lower().startswith("k"))
        winner_name = 'black' if king.get_id()[1] == 'B' else 'white'
        self.screen.announce_win(winner_name)

    def _on_enter_pressed(self):
        self._selection_mode, self._selected_source = self._handle_selection(
            user_id=1,
            selection_mode=self._selection_mode,
            selected_source=self._selected_source,
            focus_cell=self.focus_cell,
            reset_func=self._reset_selection
        )

    def _on_space_pressed(self):
        self._selection_mode2, self._selected_source2 = self._handle_selection(
            user_id=2,
            selection_mode=self._selection_mode2,
            selected_source=self._selected_source2,
            focus_cell=self.focus_cell2,
            reset_func=self._reset_selection2
        )

    def _handle_selection(self, user_id: int, selection_mode: str, selected_source: Optional[Tuple[int, int]],
                          focus_cell: Tuple[int, int], reset_func: Callable[[], None]):
        is_user1 = user_id == 1
        player_color = 'B' if is_user1 else 'W'

        if selection_mode == "source":
            if focus_cell in self.pos_to_piece:
                piece = self.pos_to_piece[focus_cell]
                if not piece.get_id()[1] == player_color:
                    print(f"User {user_id} cannot select this piece.")
                    return selection_mode, selected_source
                src_alg = self.board.cell_to_algebraic(focus_cell)
                print(f"User {user_id} source selected at {focus_cell} -> {src_alg}")
                return "dest", focus_cell
        elif selection_mode == "dest":
            if selected_source is None:
                return selection_mode, selected_source
            src_cell = selected_source
            dst_cell = focus_cell
            src_alg = self.board.cell_to_algebraic(src_cell)
            dst_alg = self.board.cell_to_algebraic(dst_cell)
            print(f"User {user_id} destination selected at {dst_cell} -> {dst_alg}")
            piece = self.pos_to_piece.get(src_cell)
            if piece:
                move_type = 'JUMP' if src_cell == dst_cell else 'MOVE'
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=piece.get_id(),
                    type=move_type,
                    params=[src_alg, dst_alg]
                )
                event_bus.subscribe("SEND_REQUEST", {'name': "ACTION_REQUEST", 'cmd': cmd})
            reset_func()
            return "source", None

        return selection_mode, selected_source

    def _reset_selection(self):
        self._selection_mode = "source"
        self._selected_source = None

    def _reset_selection2(self):
        self._selection_mode2 = "source"
        self._selected_source2 = None