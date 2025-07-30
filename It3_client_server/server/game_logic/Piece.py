from server.game_logic.PhysicsFactory import PhysicsFactory
from server.game_logic.Board import Board
from server.game_logic.Command import Command
from server.game_logic.EventBus import event_bus
from server.game_logic.enums.EventsNames import EventsNames
from server.game_logic.State import State
from typing import Optional
import cv2

from server.game_logic.enums.StatesNames import StatesNames


class Piece:
    def __init__(self, piece_id: str, init_state: State):
        self._id = piece_id
        self._state = init_state
        self._current_cmd: Optional[Command] = None


    def on_command(self, cmd: Command):
        if cmd.type == StatesNames.MOVE:
            self.publish_move(EventsNames.BLACK_MOVE if self._id[1] == 'B' else EventsNames.WHITE_MOVE, cmd, now_ms)
            self._current_cmd = cmd
        if cmd.type == StatesNames.JUMP:
            event_bus.publish(EventsNames('jump'), {'sound': 'jump.wav'})
        self._state = self._state.process_command(cmd)

    def publish_move(self, event_name : EventsNames, cmd : Command, now_ms : int):
        player : str = cmd.piece_id[1]
        source_cell : str = cmd.params[0]
        destination_cell : str = cmd.params[1]
        event_bus.publish(event_name, {'player': player, 'time': now_ms, 'source': source_cell, 'destination': destination_cell, 'sound': 'move.wav'})

    def is_command_possible(self, cmd: Command, dst_empty: bool) -> bool:
        if cmd.type != StatesNames.MOVE:
            return cmd is not None and cmd.type in self._state.transitions

        src = self._state._physics.start_cell
        dst = self._state._physics.board.algebraic_to_cell(cmd.params[1])
        legal = self._state._moves.get_moves(*src)

        # חייל (Pawn)
        if self._id[0] == 'P':
            src_y, src_x = src
            dst_y, dst_x = dst

            direction = -1 if self._id[1] == 'W' else 1  # לבנים עולים, שחורים יורדים

            # תנועה קדימה צעד אחד
            if dst_x == src_x and dst_y == src_y + direction and dst_empty:
                return self._state.is_command_possible(cmd)

            # תנועה קדימה שני צעדים (אם בעמדת פתיחה)
            start_row = 6 if self._id[1] == 'W' else 1
            if (src_y == start_row and
                    dst_x == src_x and
                    dst_y == src_y + 2 * direction and
                    dst_empty):
                return self._state.is_command_possible(cmd)

            # אכילה באלכסון
            if abs(dst_x - src_x) == 1 and dst_y == src_y + direction and not dst_empty:
                return self._state.is_command_possible(cmd)

            return False  # כל השאר לא חוקי

        # כלים אחרים – משתמשים בלוגיקה הרגילה
        return dst in legal and self._state.is_command_possible(cmd)

    def reset(self, start_ms: int):
        if self._current_cmd:
            self._state.reset(self._current_cmd)

    def update(self, now_ms: int):
        self._state.update(now_ms)
        if self._state._physics.finished:
            next_state =  next(iter(self._state.transitions.keys()))
            new_cell = self._state._physics.get_pos_in_cell()
            cmd = Command(now_ms, self._id, next_state, [new_cell, new_cell])
            self.on_command(cmd, now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        pos = self._state._physics.get_pos()
        img = self._state._graphics.get_img().img
        if img is not None:
            h, w = img.shape[:2]
            x, y = int(pos[0]), int(pos[1])

            board_img = board.img.img

            # התאמה אם חורג מגבולות
            h = min(h, board_img.shape[0] - y)
            w = min(w, board_img.shape[1] - x)

            if h > 0 and w > 0:
                piece_img = img[:h, :w]
                base = board_img[y:y + h, x:x + w]

                # התאמת ערוצים
                target_channels = base.shape[2]
                piece_img = self._match_channels(piece_img, target_channels)

                board_img[y:y + h, x:x + w] = self._blend(base, piece_img)

    def _blend(self, base, overlay):
        alpha = 0.8  # Simple fixed alpha
        return cv2.addWeighted(overlay, alpha, base, 1 - alpha, 0)

    def _match_channels(self, img, target_channels=3):
        """Convert image to target_channels (3=BGR, 4=BGRA)."""
        if img.shape[2] == target_channels:
            return img
        if target_channels == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        if target_channels == 4 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        return img

    def get_id(self) -> str:
        return self._id

    def get_color(self) -> str:
        return 'black' if self._id[1] == 'B' else 'white'

    def get_type(self) -> str:
        type_map = {
            'P': 'Pawn',
            'R': 'Rook',
            'N': 'Knight',
            'B': 'Bishop',
            'Q': 'Queen',
            'K': 'King'
        }
        return type_map.get(self._id[0], 'Unknown')

    def get_command(self):
        return self._state.get_command()

    def clone_to(self, cell: tuple[int, int], physics_factory: PhysicsFactory) -> "Piece":
        """
        Clone this piece to a new piece at a different cell.
        Graphics is copied, physics is recreated (new cell), moves are shared.
        """

        graphics_copy = self._state._graphics.copy()


        state_name = self._state._physics.__class__.__name__.replace("Physics", "").lower()
        speed = getattr(self._state._physics, "speed", 1.0)

        cfg = {"physics": {"speed_m_per_sec": speed}}

        new_physics = physics_factory.create(state_name, cell, cfg)

        new_state = State(self._state._moves, graphics_copy, new_physics)

        for event, target in self._state.transitions.items():
            new_state.set_transition(event, target)

        return Piece(self._id, new_state)