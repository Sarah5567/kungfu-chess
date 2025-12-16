import pathlib
from graphics import Graphics
from src.core.board import Board


class GraphicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def load(self,
             sprites_dir: pathlib.Path,
             cfg: dict,
             cell_size: tuple[int, int]) -> Graphics:
        """Load graphics from sprites directory with configuration."""
        graphics_cfg = cfg.get("", {})
        fps = graphics_cfg.get("frames_per_sec", 6.0)
        loop = graphics_cfg.get("is_loop", True)

        return Graphics(
            sprites_folder=sprites_dir,
            board=self.board,
            loop=loop,
            fps=fps
        )
