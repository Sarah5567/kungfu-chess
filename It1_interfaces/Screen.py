from typing import Tuple, Any, List
import cv2
import numpy as np
from Board import Board
from Img import Img
from Table import Table  # Required that your Table class contains log_to_table_data

class Screen:
    def __init__(self,
                 images: dict[str, Img],
                 headers: List[str],
                 screen_size: Tuple[int, int] = (800, 800),
                 bg_color=(0, 0, 0),
                 max_rows=15):
        self._screen_h, self._screen_w = screen_size
        self._bg_color = bg_color
        self._img = np.full((self._screen_h, self._screen_w, 3), self._bg_color, dtype=np.uint8)

        self._images = images

        self.left_table = Table(headers)
        self.right_table = Table(headers)

    def reset(self):
        if 'opening_img' in self._images and self._images['opening_img'].img is not None:
            img_to_show = self._images['opening_img'].img.copy()
            if img_to_show.shape[:2] != (self._screen_h, self._screen_w):
                img_to_show = cv2.resize(img_to_show, (self._screen_w, self._screen_h), interpolation=cv2.INTER_AREA)
            self._img = img_to_show
        else:
            # fallback רק אם לא הועבר Img
            self._img = np.full((self._screen_h, self._screen_w, 3), self._bg_color, dtype=np.uint8)

        self.left_table.update_data([])
        self.right_table.update_data([])

    def announce_win(self, winner_name: str):
        """
        מציג הודעת ניצחון דרמטית עם רקע מתמונות ניצחון מוכנות לפי צבע השחקן

        Args:
            winner_name: שם השחקן המנצח ("black" או "white")
        """
        import time

        # שמירת המסך המקורי
        original_img = self._img.copy()

        # מיפוי המפתח המתאים לפי שם המנצח
        image_key = f"{winner_name.lower()}_victory"
        selected_img_obj = self._images.get(image_key)

        # בדיקה ו־resize אם צריך
        if selected_img_obj and selected_img_obj.img is not None:
            img_to_show = selected_img_obj.img.copy()
            if img_to_show.shape[:2] != (self._screen_h, self._screen_w):
                img_to_show = cv2.resize(img_to_show, (self._screen_w, self._screen_h), interpolation=cv2.INTER_AREA)
            self._img = img_to_show
        else:
            # fallback רקע שחור אם לא סופקה תמונה
            self._img = np.full((self._screen_h, self._screen_w, 3), (0, 0, 0), dtype=np.uint8)

        # הצגת המסך
        cv2.imshow("Chess", self._img)
        cv2.waitKey(3000)

        # החזרת המסך הקודם
        self._img = original_img

        # ניקוי טבלאות
        self.left_table.update_data([])
        self.right_table.update_data([])

    def update_left(self, log: List[dict[str, Any]]):
        """Update the left table from the log"""
        table_data = Table.log_to_table_data(log)
        if table_data:
            # Remove first row because headers are already fixed
            self.left_table.update_data(table_data[1:])
        else:
            self.left_table.update_data([])

    def update_right(self, log: List[dict[str, Any]]):
        """Update the right table from the log"""
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
        """Draws the board, tables, and scores with clean modern red styling"""
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
            board_offset_y = (self._screen_h - bh) // 2
            board_offset_x = (self._screen_w - bw) // 2
            self._img[board_offset_y:board_offset_y + bh, board_offset_x:board_offset_x + bw] = board_img

        # Modern colors
        player_name_color = (0, 0, 0)  # Black
        score_color = (0, 0, 255)  # Red
        line_color = (50, 50, 50)    # Subtle dark gray for lines
        border_color = (100, 100, 100)  # Light gray for borders

        # --- Left Table (Black Player) ---
        if self.left_table is not None:
            l_img = self.left_table.img
            lh, lw = l_img.shape[:2]
            ly = board_offset_y + (bh - lh) // 2 - 10
            lx = board_offset_x - lw - spacing

            if lx >= 0:
                # Table border
                table_padding = 8
                cv2.rectangle(self._img,
                              (lx - table_padding, ly - table_padding),
                              (lx + lw + table_padding, ly + lh + table_padding),
                              border_color, 1,
                              lineType=cv2.LINE_AA)

                # Table itself
                self._img[ly:ly + lh, lx:lx + lw] = l_img

                # Player name
                title = "Black Player"
                font = cv2.FONT_HERSHEY_SIMPLEX
                title_scale = 0.9
                title_thickness = 2
                title_size = cv2.getTextSize(title, font, title_scale, title_thickness)[0]
                title_x = lx + (lw - title_size[0]) // 2
                title_y = max(35, ly - 15)

                # Draw player name
                cv2.putText(self._img, title, (title_x, title_y),
                            font, title_scale, player_name_color, title_thickness, cv2.LINE_AA)

                # Minimal underline
                cv2.line(self._img,
                         (title_x, title_y + 5),
                         (title_x + title_size[0], title_y + 5),
                         line_color, 1, cv2.LINE_AA)

                # Score with clean design
                score_text = f"Score: {black_score}"
                score_scale = 0.8
                score_thickness = 2
                score_size = cv2.getTextSize(score_text, font, score_scale, score_thickness)[0]
                score_x = lx + (lw - score_size[0]) // 2
                score_y = ly + lh + 30

                # Draw score
                cv2.putText(self._img, score_text, (score_x, score_y),
                            font, score_scale, score_color, score_thickness, cv2.LINE_AA)

        # --- Right Table (White Player) ---
        if self.right_table is not None:
            r_img = self.right_table.img
            rh, rw = r_img.shape[:2]
            ry = board_offset_y + (bh - rh) // 2 - 10
            rx = board_offset_x + bw + spacing

            if rx + rw <= self._screen_w:
                # Table border
                table_padding = 8
                cv2.rectangle(self._img,
                              (rx - table_padding, ry - table_padding),
                              (rx + rw + table_padding, ry + rh + table_padding),
                              border_color, 1,
                              lineType=cv2.LINE_AA)

                # Table itself
                self._img[ry:ry + rh, rx:rx + rw] = r_img

                # Player name
                title = "White Player"
                title_size = cv2.getTextSize(title, font, title_scale, title_thickness)[0]
                title_x = rx + (rw - title_size[0]) // 2
                title_y = max(35, ry - 15)

                # Draw player name
                cv2.putText(self._img, title, (title_x, title_y),
                            font, title_scale, player_name_color, title_thickness, cv2.LINE_AA)

                # Minimal underline
                cv2.line(self._img,
                         (title_x, title_y + 5),
                         (title_x + title_size[0], title_y + 5),
                         line_color, 1, cv2.LINE_AA)

                # Score with clean design
                score_text = f"Score: {white_score}"
                score_size = cv2.getTextSize(score_text, font, score_scale, score_thickness)[0]
                score_x = rx + (rw - score_size[0]) // 2
                score_y = ry + rh + 30

                # Check if there's space below
                if score_y + 25 < self._screen_h:
                    cv2.putText(self._img, score_text, (score_x, score_y),
                                font, score_scale, score_color, score_thickness, cv2.LINE_AA)
                else:
                    # If no space below, put above
                    score_y_alt = ry - 25
                    cv2.putText(self._img, score_text, (score_x, score_y_alt),
                                font, score_scale, score_color, score_thickness, cv2.LINE_AA)

    def show(self, win_name="Screen"):
        cv2.imshow(win_name, self._img)

    @property
    def img(self):
        return self._img