import csv
import pathlib
import time
import queue
import cv2
from typing import Dict, Tuple, Optional, Callable
import threading
import keyboard
from Board import Board
from Command import Command
from enums.EventsNames import EventsNames
from Log import Log
from Piece import Piece
from Score import Score
from Screen import Screen
from EventBus import event_bus, Event
from PieceFactory import PieceFactory
from playsound import playsound

class Game:
    def __init__(self, screen: Screen, board: Board, pieces_root: pathlib.Path, placement_csv: pathlib.Path, sounds_root: pathlib.Path):
        self.screen = screen
        self._sounds_root = sounds_root
        self.board = board
        self.user_input_queue = queue.Queue()
        self.start_time = 0
        self.piece_factory = PieceFactory(self.board, pieces_root)
        self.pieces: Dict[str, Piece] = {}
        self.pos_to_piece: Dict[Tuple[int, int], Piece] = {}
        self._current_board = None
        self._load_pieces_from_csv(placement_csv)
        self.focus_cell = (0, 0)
        self._selection_mode = "source"
        self._selected_source: Optional[Tuple[int, int]] = None


        self.focus_cell2 = (self.board.H_cells - 1, 0)
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
        event_bus.subscribe(EventsNames.BLACK_MOVE, self.black_log.update_log)
        event_bus.subscribe(EventsNames.WHITE_MOVE, self.white_log.update_log)

        event_bus.subscribe(EventsNames.BLACK_CAPTURE, self.black_score.update_score)
        event_bus.subscribe(EventsNames.WHITE_CAPTURE, self.white_score.update_score)

        for event in [
            EventsNames.BLACK_MOVE,
            EventsNames.WHITE_MOVE,
            EventsNames.BLACK_CAPTURE,
            EventsNames.WHITE_CAPTURE,
            EventsNames.JUMP,
            EventsNames.VICTORY,
        ]:
            event_bus.subscribe(event, self.play_sounds)

    def play_sounds(self, event : Event):
        def _play():
            playsound(str(self._sounds_root / event.data['sound']))

        threading.Thread(target=_play, daemon=True).start()

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

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_keyboard_thread(self):
        def keyboard_loop():
            while self._running:
                time.sleep(0.05)
                with self._lock:
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
        self.screen.show("Chess")
        while True:
            key = cv2.waitKey(0)
            if key == 13:  # 13 הוא הקוד של מקש Enter
                break

        self.start_keyboard_thread()

        start_ms = self.game_time_ms()
        for piece in self.pieces.values():
            piece.reset(start_ms)

        while self._running and not self._is_win():
            now = self.game_time_ms()

            for piece in self.pieces.values():
                piece.update(now)

            self._update_position_mapping()

            while not self.user_input_queue.empty():
                cmd = self.user_input_queue.get()
                src_cell = self.board.algebraic_to_cell(cmd.params[0])
                dst_cell = self.board.algebraic_to_cell(cmd.params[1])

                if src_cell not in self.pos_to_piece:
                    print("Source cell empty. Command ignored.")
                    continue
                moving_piece = self.pos_to_piece[src_cell]

                dst_empty : bool = True
                if dst_cell in self.pos_to_piece:
                    target_piece = self.pos_to_piece[dst_cell]
                    if target_piece.get_id()[1] == moving_piece.get_id()[1] and target_piece.get_id() != moving_piece.get_id():
                        print("Move blocked: Destination occupied by friendly piece.")
                        continue
                    else:
                        dst_empty = False

                if not self.is_path_clean(dst_cell, src_cell):
                    print("Move blocked: Path is obstructed.")
                    continue

                self.pos_to_piece[src_cell].on_command(cmd, now, dst_empty)

            self._draw()

            self.screen.show("Chess")
            cv2.waitKey(1)

        self._announce_win()
        self._running = False
        cv2.destroyAllWindows()

    def is_path_clean(self, dst_cell, src_cell):
        dx = dst_cell[1] - src_cell[1]
        dy = dst_cell[0] - src_cell[0]
        if dx != 0:
            step_x = dx // abs(dx)
        else:
            step_x = 0
        if dy != 0:
            step_y = dy // abs(dy)
        else:
            step_y = 0
        if (step_x != 0 or step_y != 0) and (abs(dx) == abs(dy) or dx == 0 or dy == 0):
            cur_cell = (src_cell[0] + step_y, src_cell[1] + step_x)
            while cur_cell != dst_cell:
                if cur_cell in self.pos_to_piece:
                    return False
                cur_cell = (cur_cell[0] + step_y, cur_cell[1] + step_x)
        return True

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

    def _update_position_mapping(self):
        self.pos_to_piece.clear()
        to_remove = set()
        to_promote = []  # Collect here the pawns that need to be promoted to queen

        for piece in list(self.pieces.values()):  # Use list to freeze values during loop
            x, y = map(int, piece._state._physics.get_pos())
            if not self.board.is_valid_cell(x, y):
                continue
            cell_x = x // self.board.cell_W_pix
            cell_y = y // self.board.cell_H_pix
            pos = (cell_y, cell_x)

            if pos in self.pos_to_piece:
                opponent = self.pos_to_piece[pos]
                if piece._state._current_command and piece._state._current_command.type == 'jump':
                    continue
                if self.should_capture(opponent, piece):
                    event_bus.publish(
                        EventsNames.BLACK_CAPTURE if piece.get_id()[1] == 'B' else EventsNames.WHITE_MOVE,
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

            # Instead of promoting here, save for after the loop
            if piece.get_id()[0] == 'P' and (pos[0] == 0 or pos[0] == 7):
                to_promote.append((piece.get_id(), pos))

        # Remove captured pieces
        for k in to_remove:
            self.pieces.pop(k, None)

        # Handle promotion to queen after all captures are done
        for pawn_id, pos in to_promote:
            if pawn_id in self.pieces:
                new_queen = self.piece_factory.create_piece('Q' + self.pieces[pawn_id].get_id()[1], pos)
                self.pieces[pawn_id] = new_queen
                self.pos_to_piece[pos] = new_queen

    def should_capture(self, opponent, piece):
        if not opponent._state._current_command or  opponent._state._current_command.type in ["idle", "long_rest", "short_rest"]:
            return True
        if piece._state._current_command and piece._state._current_command.type not in ["idle", "long_rest", "short_rest"]:
            return opponent._state._physics.start_time > piece._state._physics.start_time
        return False

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
        event_bus.publish(EventsNames.VICTORY, {'sound': 'victory.WAV'})
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
                move_type = "jump" if src_cell == dst_cell else "move"
                cmd = Command(
                    timestamp=self.game_time_ms(),
                    piece_id=piece.get_id(),
                    type=move_type,
                    params=[src_alg, dst_alg]
                )
                self.user_input_queue.put(cmd)
            reset_func()
            return "source", None

        return selection_mode, selected_source

    def _reset_selection(self):
        self._selection_mode = "source"
        self._selected_source = None

    def _reset_selection2(self):
        self._selection_mode2 = "source"
        self._selected_source2 = None

