from typing import Tuple, Any, List
import cv2
import numpy as np
from Board import Board
from Table import Table  # נדרש שהמחלקה שלך Table תכיל log_to_table_data

class Screen:
    def __init__(self,
                 headers: List[str],
                 screen_size: Tuple[int, int] = (800, 800),
                 bg_color=(50, 50, 50),
                 max_rows=15):
        self._screen_h, self._screen_w = screen_size
        self._bg_color = bg_color
        self._img = np.full((self._screen_h, self._screen_w, 3), self._bg_color, dtype=np.uint8)

        # יצירת טבלאות ריקות בהתחלה
        self.left_table = Table(headers)
        self.right_table = Table(headers)

    def update_left(self, log: List[dict[str, Any]]):
        """עדכון הטבלה השמאלית מתוך הלוג"""
        table_data = Table.log_to_table_data(log)
        if table_data:
            # מסירים את השורה הראשונה כי הכותרות כבר קבועות
            self.left_table.update_data(table_data[1:])
        else:
            self.left_table.update_data([])

    def update_right(self, log: List[dict[str, Any]]):
        """עדכון הטבלה הימנית מתוך הלוג"""
        table_data = Table.log_to_table_data(log)
        if table_data:
            self.right_table.update_data(table_data[1:])
        else:
            self.right_table.update_data([])

    def draw(self,
             board: Board = None,
             spacing=20,
             white_score: int = 0,
             black_score: int = 0):
        """Draws the board, tables, and scores"""
        self._img[:, :] = self._bg_color

        # Draw the board
        board_offset_x = 0
        board_offset_y = 0
        bh, bw = 0, 0
        if board is not None:
            board_img = board.img.img
            if board_img.shape[2] == 4:
                board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)
            bh, bw = board_img.shape[:2]
            board_offset_y = (self._screen_h - bh) // 2 - 50
            board_offset_x = (self._screen_w - bw) // 2
            self._img[board_offset_y:board_offset_y + bh, board_offset_x:board_offset_x + bw] = board_img

        # --- Left Table (Black Player) ---
        if self.left_table is not None:
            l_img = self.left_table.img
            lh, lw = l_img.shape[:2]
            ly = board_offset_y + (bh - lh) // 2 - 10
            lx = board_offset_x - lw - spacing
            if lx >= 0:
                self._img[ly:ly + lh, lx:lx + lw] = l_img

                title = "Black Player"
                score_text = f"Score: {black_score}"

                title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]

                # Draw title
                title_x = lx + (lw - title_size[0]) // 2
                title_y = max(5, ly - 50)
                cv2.putText(self._img, title, (title_x, title_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

                # Draw score
                score_x = lx + (lw - score_size[0]) // 2
                score_y = ly + lh + score_size[1] - 675
                cv2.putText(self._img, score_text, (score_x, score_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # --- Right Table (White Player) ---
        if self.right_table is not None:
            r_img = self.right_table.img
            rh, rw = r_img.shape[:2]
            ry = board_offset_y + (bh - rh) // 2 - 10
            rx = board_offset_x + bw + spacing
            if rx + rw <= self._screen_w:
                self._img[ry:ry + rh, rx:rx + rw] = r_img

                title = "White Player"
                score_text = f"Score: {white_score}"

                title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]

                title_x = rx + (rw - title_size[0]) // 2
                title_y = max(5, ry - 50)
                cv2.putText(self._img, title, (title_x, title_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

                score_x = rx + (rw - score_size[0]) // 2
                score_y = ry + rh + score_size[1] - 675
                if score_y + 5 < self._screen_h:
                    cv2.putText(self._img, score_text, (score_x, score_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                else:
                    cv2.putText(self._img, score_text, (score_x, ry - 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    def show(self, win_name="Screen"):
        cv2.imshow(win_name, self._img)

    @property
    def img(self):
        return self._img
