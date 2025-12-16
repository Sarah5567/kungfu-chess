import csv
import pathlib
import time
import queue
import cv2
from typing import Dict, Tuple, Optional, Callable
import threading
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

from enums.StatesNames import StatesNames


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

        # Mouse input variables
        self._selected_piece: Optional[Tuple[int, int]] = None
        self._is_dragging = False
        self._drag_start_pos: Optional[Tuple[int, int]] = None
        self._last_click_time = 0
        self._last_click_pos: Optional[Tuple[int, int]] = None
        self._double_click_threshold = 0.5  # seconds

        self._lock = threading.Lock()
        self._running = True

        self.black_log: Log = Log()
        self.white_log: Log = Log()
        self.black_score: Score = Score()
        self.white_score: Score = Score()
        self.subscriptions(sounds_root)

        # Mouse callback will be set after window is created

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

    def play_sounds(self, event: Event):
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

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert pixel coordinates to board cell coordinates"""
        # Calculate board offset (assuming board is centered)
        board_h, board_w = self.board.img.img.shape[:2]
        board_offset_y = (self.screen._screen_h - board_h) // 2
        board_offset_x = (self.screen._screen_w - board_w) // 2
        
        # Adjust coordinates relative to board
        board_x = x - board_offset_x
        board_y = y - board_offset_y
        
        # Check if click is within board bounds
        if board_x < 0 or board_y < 0 or board_x >= board_w or board_y >= board_h:
            return None
            
        # Convert to cell coordinates
        cell_x = board_x // self.board.cell_W_pix
        cell_y = board_y // self.board.cell_H_pix
        
        # Validate cell coordinates
        if not self.board.is_valid_cell(cell_y, cell_x):
            return None
            
        return (cell_y, cell_x)

    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events"""
        with self._lock:
            current_time = time.time()
            
            if event == cv2.EVENT_LBUTTONDOWN:
                cell = self._pixel_to_cell(x, y)
                if cell is None:
                    return
                    
                # Check for double click
                if (self._last_click_pos == cell and 
                    current_time - self._last_click_time < self._double_click_threshold):
                    self._handle_double_click(cell)
                else:
                    self._handle_single_click(cell)
                    
                self._last_click_time = current_time
                self._last_click_pos = cell
                
            elif event == cv2.EVENT_MOUSEMOVE and self._is_dragging:
                # Visual feedback during drag could be added here
                pass
                
            elif event == cv2.EVENT_LBUTTONUP:
                if self._is_dragging:
                    cell = self._pixel_to_cell(x, y)
                    if cell is not None:
                        self._handle_drag_end(cell)
                self._is_dragging = False
                self._drag_start_pos = None

    def _handle_single_click(self, cell: Tuple[int, int]):
        """Handle single click - start drag operation"""
        if cell in self.pos_to_piece:
            piece = self.pos_to_piece[cell]
            # Check if player can control this piece
            if hasattr(self, 'color') and piece.get_id()[1].lower() != self.color.lower():
                print(f"Cannot select opponent's piece at {cell}")
                return
                
            self._selected_piece = cell
            self._is_dragging = True
            self._drag_start_pos = cell
            print(f"Selected piece {piece.get_id()} at {cell}")
        else:
            self._selected_piece = None
            self._is_dragging = False

    def _handle_double_click(self, cell: Tuple[int, int]):
        """Handle double click - jump in place"""
        if cell in self.pos_to_piece:
            piece = self.pos_to_piece[cell]
            # Check if player can control this piece
            if hasattr(self, 'color') and piece.get_id()[1].lower() != self.color.lower():
                print(f"Cannot jump opponent's piece at {cell}")
                return
                
            src_alg = self.board.cell_to_algebraic(cell)
            print(f"Jump command for piece {piece.get_id()} at {cell}")
            
            cmd = Command(
                timestamp=self.game_time_ms(),
                piece_id=piece.get_id(),
                type=StatesNames.JUMP,
                params=[src_alg, src_alg]
            )
            self.user_input_queue.put(cmd)
            
            # Send jump to server if client is available
            if hasattr(self, 'client') and self.client:
                move_dict = {
                    "from": list(cell),
                    "to": list(cell),
                    "piece_id": piece.get_id()
                }
                # Use asyncio to send the move
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.client.send_move(move_dict))
                except RuntimeError:
                    # If no event loop is running, we're in sync mode
                    print("Cannot send jump to server - no async loop running")

    def _handle_drag_end(self, dest_cell: Tuple[int, int]):
        """Handle end of drag operation - execute move"""
        if self._selected_piece is None or self._drag_start_pos is None:
            return
            
        src_cell = self._drag_start_pos
        
        # If dragged to same position, ignore
        if src_cell == dest_cell:
            print("Dragged to same position, ignoring")
            return
            
        piece = self.pos_to_piece.get(src_cell)
        if piece is None:
            print("Source piece no longer exists")
            return
            
        src_alg = self.board.cell_to_algebraic(src_cell)
        dst_alg = self.board.cell_to_algebraic(dest_cell)
        
        print(f"Move command: {piece.get_id()} from {src_alg} to {dst_alg}")
        
        cmd = Command(
            timestamp=self.game_time_ms(),
            piece_id=piece.get_id(),
            type=StatesNames.MOVE,
            params=[src_alg, dst_alg]
        )
        self.user_input_queue.put(cmd)
        
        # Send move to server if client is available
        if hasattr(self, 'client') and self.client:
            move_dict = {
                "from": list(src_cell),
                "to": list(dest_cell),
                "piece_id": piece.get_id()
            }
            # Use asyncio to send the move
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.client.send_move(move_dict))
            except RuntimeError:
                # If no event loop is running, we're in sync mode
                print("Cannot send move to server - no async loop running")

    def game_time_ms(self) -> int:
        return int((time.monotonic() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        return self.board.clone()

    def run(self):
        self.start_time = time.monotonic()
        self.screen.reset()
        self.screen.show("Chess")
        
        # Set mouse callback after window is created
        cv2.setMouseCallback("Chess", self._mouse_callback)
        
        # Wait for initial click to start
        while True:
            key = cv2.waitKey(30)
            if key == 13:  # Enter key to start
                break
            elif key == 27:  # ESC key to exit
                return

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

                dst_empty: bool = True
                if dst_cell in self.pos_to_piece:
                    target_piece = self.pos_to_piece[dst_cell]
                    if target_piece.get_id()[1] == moving_piece.get_id()[1] and target_piece.get_id() != moving_piece.get_id():
                        print("Move blocked: Destination occupied by friendly piece.")
                        continue
                    else:
                        dst_empty = False

                # Allow enemy moves even if path is obstructed or destination is occupied
                if hasattr(self, 'client') and moving_piece.get_id()[1].lower() != self.client.color.lower():
                    print("Processing enemy move.")
                elif not self.is_path_clean(dst_cell, src_cell):
                    print("Move blocked: Path is obstructed.")
                    continue

                self.pos_to_piece[src_cell].on_command(cmd, now, dst_empty)

            self._draw()
            self.screen.show("Chess")
            
            # Check for ESC key to exit
            key = cv2.waitKey(1)
            if key == 27:  # ESC key
                self._running = False

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
                self.pieces[new_queen.get_id()] = new_queen
                self.pos_to_piece[pos] = new_queen

    def should_capture(self, opponent, piece):
        if not opponent._state._current_command or opponent._state._current_command.type in [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return True
        if piece._state._current_command and piece._state._current_command.type not in [
            StatesNames.IDLE, StatesNames.LONG_REST, StatesNames.SHORT_REST]:
            return opponent._state._physics.start_time > piece._state._physics.start_time
        return False

    def _draw(self):
        board = self.clone_board()
        now_ms = self.game_time_ms()

        for piece in self.pieces.values():
            piece.draw_on_board(board, now_ms)

        # Highlight selected piece
        if self._selected_piece and self._selected_piece in self.pos_to_piece:
            self._draw_rectangle_on_board(board, self._selected_piece, (0, 255, 0))  # Green for selected
            
        # Show possible moves for selected piece (optional enhancement)
        if self._is_dragging and self._selected_piece:
            self._draw_rectangle_on_board(board, self._selected_piece, (0, 255, 255))  # Cyan for dragging

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

    async def try_move_piece(self, piece_id: str, new_pos: Tuple[int, int]):
        piece = self.pieces.get(piece_id)
        if not piece:
            print("Piece not found.")
            return

        if piece.get_id()[1].lower() != self.color.lower():
            print("You can't move the other player's pieces.")
            return

        move_dict = {
            "from": list(piece.get_pos()),
            "to": list(new_pos),
            "piece_id": piece_id
        }

        await self.client.send_move(move_dict)  # Send move to the server
        print(f"Move sent to server: {move_dict}")

    async def on_enemy_move(self, event: Event):
        data = event.data
        piece_id = data.get("piece_id")
        new_pos = tuple(data.get("to"))

        piece = self.pieces.get(piece_id)
        if not piece:
            print(f"Received move for unknown piece {piece_id}")
            return

        src_alg = self.board.cell_to_algebraic(piece.get_pos())
        dst_alg = self.board.cell_to_algebraic(new_pos)
        print(f"Enemy moved {piece_id} from {src_alg} to {dst_alg}")

        # Update the piece's position directly
        piece.set_pos(new_pos)
        self._update_position_mapping()

        command = Command(
            timestamp=self.game_time_ms(),
            piece_id=piece_id,
            type=StatesNames.MOVE,
            params=[src_alg, dst_alg]
        )
        self.user_input_queue.put(command)
        print("Enemy move command queued.")

    def set_client(self, client):
        self.client = client
        self.color = client.color