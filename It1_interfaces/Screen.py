import cv2
import numpy as np
from typing import Tuple

from Board import Board


class Screen:
    def __init__(self, width: int, height: int, board: Board, background_color: Tuple[int, int, int] = (50, 50, 50)):
        """
        width, height: הגודל הכולל של המסך בפיקסלים
        board: מופע של Board
        background_color: צבע רקע (BGR)
        """
        self.width = width
        self.height = height
        self.board = board
        self.background_color = background_color

        # תמונת המסך הראשית
        self.img = np.full((height, width, 3), background_color, dtype=np.uint8)

        # מיקום הלוח במסך (אפשר לשנות בעתיד)
        self.board_offset_x = 50
        self.board_offset_y = 50

    def draw_board(self):
        """מצייר את הלוח בתוך המסך"""
        # משכפל את תמונת הלוח כדי לא לפגוע במקור
        board_img = self.board.img.img.copy()

        # ממיר מ-RGBA ל-BGR אם צריך
        if board_img.shape[2] == 4:
            board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        # גודל הלוח
        h, w = board_img.shape[:2]

        # ממקם את הלוח במסך
        y1 = self.board_offset_y
        y2 = y1 + h
        x1 = self.board_offset_x
        x2 = x1 + w

        # מציב את הלוח בתוך תמונת המסך
        self.img[y1:y2, x1:x2] = board_img

    def show(self, window_name: str = "Screen"):
        """מציג את המסך המלא"""
        cv2.imshow(window_name, self.img)
        cv2.waitKey(1)

    def clear(self):
        """מנקה את המסך (ממלא מחדש בצבע רקע)"""
        self.img[:, :] = self.background_color

    def get_board(self):
        return self.board
