import pathlib
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy
from img import Img
from Command import Command
from Board import Board


class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        self.board = board  # קודם כל שומרים את ה-board
        self.loop = loop
        self.fps = fps
        self.frame_time_ms = 1000 / fps  # ms per frame
        self.current_frame = 0
        self.start_time = time.monotonic()
        self.sprites: List[Img] = self._load_sprites(sprites_folder)

    def copy(self):
        """Create a shallow copy of the graphics object."""
        g = Graphics.__new__(Graphics)  # יצירה בלי קריאה ל־__init__
        g.sprites = self.sprites
        g.loop = self.loop
        g.fps = self.fps
        g.frame_time_ms = self.frame_time_ms
        g.current_frame = self.current_frame
        g.start_time = self.start_time
        g.board = self.board
        return g

    def reset(self, cmd: Command):
        self.start_time = cmd.timestamp
        self.current_frame = 0

    def update(self, now_ms: int):
        elapsed = now_ms - self.start_time
        if elapsed < 0:
            self.current_frame = 0
            return

        frame_index = int(elapsed / self.frame_time_ms)

        if self.loop:
            self.current_frame = frame_index % len(self.sprites)
        else:
            self.current_frame = min(frame_index, len(self.sprites) - 1)

    def get_img(self) -> Img:
        return self.sprites[self.current_frame]

    # ─── internal helper ──────────────────────────────────────────────
    def _load_sprites(self, folder: pathlib.Path) -> List[Img]:
        """Load all sprite images from a folder in sorted order and resize to cell size."""
        images = []
        cell_w, cell_h = self.board.cell_W_pix, self.board.cell_H_pix
        for img_path in sorted(folder.iterdir()):
            if img_path.suffix.lower() in (".png", ".jpg", ".jpeg"):
                images.append(Img().read(img_path, size=(cell_w, cell_h)))
        return images


