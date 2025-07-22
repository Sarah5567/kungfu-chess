import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from Board   import Board
from Command import Command
from Piece   import Piece
from img     import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = { p.piece_id : p for p in pieces}
        pass

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        pass

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        pass

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        pass

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        self.start_user_input_thread() # QWe2e5

        start_ms = self.game_time_ms()
        for p in self.pieces:
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win():
            now = self.game_time_ms() # monotonic time ! not computer time.

            # (1) update physics & animations
            for p in self.pieces:
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty(): # QWe2e5
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) draw current position
            self._draw()
            if not self._show():           # returns False if user closed window
                break

            # (4) detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd : Command):
        self.pieces[cmd.piece_id].on_command(cmd)

    def _draw(self):
        """Draw the current game state."""
        pass

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        pass

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        pass

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        pass

    def _announce_win(self):
        """Announce the winner."""
        pass
