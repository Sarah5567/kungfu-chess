from typing import Tuple
import cv2
import numpy as np
from Board import Board

class Screen:
    def __init__(self, screen_size: Tuple[int, int] = (800, 800), bg_color=(50, 50, 50)):
        """
        :param board: אובייקט Board שמכיל את הלוח
        :param screen_size: גודל המסך הכולל בפיקסלים (גובה, רוחב)
        :param bg_color: צבע הרקע של המסך בפורמט BGR
        """
        self._screen_h, self._screen_w = screen_size
        self._bg_color = bg_color
        self._img = np.full((self._screen_h, self._screen_w, 3), self._bg_color, dtype=np.uint8)


    def draw(self, board: Board = None):
        board_img = board.img.img
        if board_img.shape[2] == 4:
            board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)

        h, w = board_img.shape[:2]
        offset_y = (self._screen_h - h) // 2
        offset_x = (self._screen_w - w) // 2

        self._img[:, :] = self._bg_color
        self._img[offset_y:offset_y + h, offset_x:offset_x + w] = board_img


    def show(self, win_name="Screen"):
        cv2.imshow(win_name, self._img)

    @property
    def img(self):
        """גישה לתמונת המסך המלאה במקרה שצריך"""
        return self._img
