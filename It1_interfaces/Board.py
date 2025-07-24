from dataclasses import dataclass
import copy
from typing import Tuple

import cv2

from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    cell_H_m: int
    cell_W_m: int
    W_cells: int
    H_cells: int
    img: Img

    def clone(self) -> "Board":
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=copy.deepcopy(self.img)
        )
    def cell_to_world(self, cell: tuple[int, int]) -> tuple[int, int]:
        row, col = cell
        x = col * self.cell_W_pix
        y = row * self.cell_H_pix
        return x, y
    def algebraic_to_cell(self, notation: str) -> Tuple[int, int]:
        """
        Converts algebraic notation (e.g., "a1") to board coordinates.
        Example: "a1" -> (7, 0) if (0,0) is top-left
        """
        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])  # Assuming board is 8x8
        return row, col
    def world_to_cell(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        x, y = pos
        col = int(x // self.cell_W_pix)
        row = int(y // self.cell_H_pix)
        return row, col

    def cell_to_algebraic(self, cell: Tuple[int, int]) -> str:
        row, col = cell
        col_letter = chr(ord('a') + col)
        row_number = str(8 - row)  # assuming 8x8 board
        return f"{col_letter}{row_number}"

    def is_valid_cell(self, x: int, y: int) -> bool:
        return x % self.cell_W_pix == 0 and y % self.cell_H_pix == 0

    def draw_focus_and_selection(self, board, focus_cell, focus_cell2, selected_source=None, selected_source2=None):
        y, x = focus_cell
        x1 = x * self.cell_W_pix
        y1 = y * self.cell_H_pix
        x2 = (x + 1) * self.cell_W_pix
        y2 = (y + 1) * self.cell_H_pix
        cv2.rectangle(board.img.img, (x1, y1), (x2, y2), (0, 255, 255), 2)

        y2_, x2_ = focus_cell2
        sx1 = x2_ * self.cell_W_pix
        sy1 = y2_ * self.cell_H_pix
        sx2 = (x2_ + 1) * self.cell_W_pix
        sy2 = (y2_ + 1) * self.cell_H_pix
        cv2.rectangle(board.img.img, (sx1, sy1), (sx2, sy2), (255, 0, 0), 2)

        if selected_source:
            sy, sx = selected_source
            sx1 = sx * self.cell_W_pix
            sy1 = sy * self.cell_H_pix
            sx2 = (sx + 1) * self.cell_W_pix
            sy2 = (sy + 1) * self.cell_H_pix
            cv2.rectangle(board.img.img, (sx1, sy1), (sx2, sy2), (0, 0, 255), 2)

        if selected_source2:
            sy, sx = selected_source2
            sx1 = sx * self.cell_W_pix
            sy1 = sy * self.cell_H_pix
            sx2 = (sx + 1) * self.cell_W_pix
            sy2 = (sy + 1) * self.cell_H_pix
            cv2.rectangle(board.img.img, (sx1, sy1), (sx2, sy2), (0, 255, 0), 2)
