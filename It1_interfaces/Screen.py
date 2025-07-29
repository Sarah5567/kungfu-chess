from typing import Tuple, Any, List
import cv2
import numpy as np
from Board import Board
from Img import Img
from Table import Table  # Required that your Table class contains log_to_table_data

class Screen:
    class Screen:
        def __init__(self,
                     headers: List[str],
                     screen_size: Tuple[int, int] = (800, 800),
                     bg_color=(0, 0, 0),
                     opening_img: Img | None = None,
                     max_rows=15):
            self._screen_h, self._screen_w = screen_size
            self._bg_color = bg_color
            self._img = np.full((self._screen_h, self._screen_w, 3), self._bg_color, dtype=np.uint8)

            self._opening_img = opening_img  # שמור את ה־Img

            self.left_table = Table(headers)
            self.right_table = Table(headers)

    def reset(self):
        if self._opening_img and self._opening_img.img is not None:
            img_to_show = self._opening_img.img.copy()
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
        מציג הודעת ניצחון דרמטית ויפה בצבעים שחור-לבן-אדום

        Args:
            winner_name: שם השחקן המנצח
        """
        import time

        # שמירת המצב הנוכחי של המסך

        original_img = self._img.copy()

        # יצירת מסך עם רקע דרמטי
        win_img = np.zeros((self._screen_h, self._screen_w, 3), dtype=np.uint8)

        # יצירת גרדיאנט רקע דרמטי (שחור לאדום כהה)
        for y in range(self._screen_h):
            gradient_factor = y / self._screen_h
            red_intensity = int(40 * gradient_factor)
            win_img[y, :] = [0, 0, red_intensity]  # BGR format

        # הוספת תבנית דרמטית ברקע - קווים אלכסוניים
        for i in range(0, self._screen_w + self._screen_h, 60):
            # קווים אלכסוניים אדומים עמומים
            cv2.line(win_img, (i, 0), (i - self._screen_h, self._screen_h), (0, 0, 25), 2)
            cv2.line(win_img, (0, i), (self._screen_w, i - self._screen_w), (0, 0, 25), 1)

        # הטקסטים להצגה
        main_text = f"{winner_name.upper()}"
        victory_text = "VICTORY"
        subtitle = "CHAMPION OF THE BOARD"

        # הגדרות הטקסט
        font = cv2.FONT_HERSHEY_SIMPLEX
        victory_font_scale = 3.5
        main_font_scale = 2.8
        subtitle_font_scale = 1.0

        # צבעים דרמטיים
        blood_red = (0, 0, 200)  # אדום דם
        bright_red = (0, 50, 255)  # אדום בהיר
        pure_white = (255, 255, 255)  # לבן טהור
        deep_black = (0, 0, 0)  # שחור עמוק
        dark_red = (0, 0, 120)  # אדום כהה
        silver = (192, 192, 192)  # כסף

        # חישוב מיקומי הטקסטים
        victory_size = cv2.getTextSize(victory_text, font, victory_font_scale, 8)[0]
        main_size = cv2.getTextSize(main_text, font, main_font_scale, 6)[0]
        subtitle_size = cv2.getTextSize(subtitle, font, subtitle_font_scale, 2)[0]

        victory_x = (self._screen_w - victory_size[0]) // 2
        victory_y = (self._screen_h // 2) - 100

        main_x = (self._screen_w - main_size[0]) // 2
        main_y = victory_y + 120

        subtitle_x = (self._screen_w - subtitle_size[0]) // 2
        subtitle_y = main_y + 80

        # === יצירת מסגרת דרמטית ===
        border_margin = 120
        border_top = victory_y - victory_size[1] - border_margin
        border_bottom = subtitle_y + 50
        border_left = min(victory_x, main_x, subtitle_x) - border_margin
        border_right = max(victory_x + victory_size[0], main_x + main_size[0],
                           subtitle_x + subtitle_size[0]) + border_margin

        # מסגרת חיצונית עבה באדום
        cv2.rectangle(win_img, (border_left - 10, border_top - 10),
                      (border_right + 10, border_bottom + 10), blood_red, 8)

        # מסגרת שחורה פנימית
        cv2.rectangle(win_img, (border_left, border_top),
                      (border_right, border_bottom), deep_black, 4)

        # מסגרת לבנה דקה ביותר
        cv2.rectangle(win_img, (border_left + 15, border_top + 15),
                      (border_right - 15, border_bottom - 15), pure_white, 2)

        # === רקע שחור מלא לאזור הטקסט ===
        cv2.rectangle(win_img, (border_left + 25, border_top + 25),
                      (border_right - 25, border_bottom - 25), deep_black, -1)

        # === הוספת חרבות צולבות בחלק העליון ===
        sword_center_x = self._screen_w // 2
        sword_center_y = border_top - 80
        sword_length = 80
        sword_width = 8

        # חרב ימנית
        sword1_start_x = sword_center_x - 30
        sword1_end_x = sword1_start_x + int(sword_length * 0.7)
        sword1_start_y = sword_center_y + 30
        sword1_end_y = sword_center_y - int(sword_length * 0.7)

        cv2.line(win_img, (sword1_start_x, sword1_start_y), (sword1_end_x, sword1_end_y), silver, sword_width)
        cv2.line(win_img, (sword1_start_x, sword1_start_y), (sword1_end_x, sword1_end_y), pure_white, 4)

        # חרב שמאלית
        sword2_start_x = sword_center_x + 30
        sword2_end_x = sword2_start_x - int(sword_length * 0.7)
        sword2_start_y = sword_center_y + 30
        sword2_end_y = sword_center_y - int(sword_length * 0.7)

        cv2.line(win_img, (sword2_start_x, sword2_start_y), (sword2_end_x, sword2_end_y), silver, sword_width)
        cv2.line(win_img, (sword2_start_x, sword2_start_y), (sword2_end_x, sword2_end_y), pure_white, 4)

        # ידיות החרבות
        cv2.rectangle(win_img, (sword1_start_x - 15, sword1_start_y - 5),
                      (sword1_start_x + 15, sword1_start_y + 5), dark_red, -1)
        cv2.rectangle(win_img, (sword2_start_x - 15, sword2_start_y - 5),
                      (sword2_start_x + 15, sword2_start_y + 5), dark_red, -1)

        # === טקסט "VICTORY" דרמטי ===
        # צללים מרובים לעומק
        shadow_offsets = [(12, 12), (8, 8), (4, 4)]
        shadow_colors = [deep_black, (20, 20, 20), (40, 40, 40)]

        for (offset_x, offset_y), shadow_color in zip(shadow_offsets, shadow_colors):
            cv2.putText(win_img, victory_text,
                        (victory_x + offset_x, victory_y + offset_y),
                        font, victory_font_scale, shadow_color, 8)

        # אפקט זוהר אדום
        for thickness in range(20, 8, -2):
            glow_intensity = int(255 * (1 - (thickness - 8) / 12))
            cv2.putText(win_img, victory_text, (victory_x, victory_y),
                        font, victory_font_scale, (0, 0, glow_intensity), thickness)

        # הטקסט הראשי בלבן
        cv2.putText(win_img, victory_text, (victory_x, victory_y),
                    font, victory_font_scale, pure_white, 8)

        # מסגרת אדומה לטקסט VICTORY
        cv2.putText(win_img, victory_text, (victory_x, victory_y),
                    font, victory_font_scale, blood_red, 3)

        # === שם המנצח באדום דרמטי ===
        # צל שחור
        cv2.putText(win_img, main_text, (main_x + 6, main_y + 6),
                    font, main_font_scale, deep_black, 6)

        # אפקט זוהר אדום
        for thickness in range(14, 6, -2):
            glow_intensity = int(200 * (1 - (thickness - 6) / 8))
            cv2.putText(win_img, main_text, (main_x, main_y),
                        font, main_font_scale, (0, 0, glow_intensity), thickness)

        # הטקסט הראשי באדום בהיר
        cv2.putText(win_img, main_text, (main_x, main_y),
                    font, main_font_scale, bright_red, 6)

        # === כותרת משנה בכסף ===
        cv2.putText(win_img, subtitle, (subtitle_x + 2, subtitle_y + 2),
                    font, subtitle_font_scale, deep_black, 2)
        cv2.putText(win_img, subtitle, (subtitle_x, subtitle_y),
                    font, subtitle_font_scale, silver, 2)

        # === קווים דקורטיביים אדומים ===
        # קו מעל VICTORY
        line_y1 = victory_y - 40
        cv2.line(win_img, (victory_x - 50, line_y1), (victory_x + victory_size[0] + 50, line_y1), blood_red, 6)
        cv2.line(win_img, (victory_x - 50, line_y1), (victory_x + victory_size[0] + 50, line_y1), pure_white, 2)

        # קו מתחת לשם המנצח
        line_y2 = main_y + 25
        cv2.line(win_img, (main_x - 40, line_y2), (main_x + main_size[0] + 40, line_y2), bright_red, 4)
        cv2.line(win_img, (main_x - 40, line_y2 + 3), (main_x + main_size[0] + 40, line_y2 + 3), pure_white, 1)

        # === יהלומים אדומים בפינות ===
        diamond_positions = [
            (border_left - 60, border_top - 60),
            (border_right + 60, border_top - 60),
            (border_left - 60, border_bottom + 60),
            (border_right + 60, border_bottom + 60)
        ]

        for diamond_x, diamond_y in diamond_positions:
            diamond_size = 25
            diamond_points = np.array([
                [diamond_x, diamond_y - diamond_size],
                [diamond_x + diamond_size, diamond_y],
                [diamond_x, diamond_y + diamond_size],
                [diamond_x - diamond_size, diamond_y]
            ], np.int32)

            # מילוי אדום
            cv2.fillPoly(win_img, [diamond_points], blood_red)
            # מסגרת לבנה
            cv2.polylines(win_img, [diamond_points], True, pure_white, 3)
            # מסגרת שחורה פנימית
            cv2.polylines(win_img, [diamond_points], True, deep_black, 1)
            # נקודה לבנה במרכז
            cv2.circle(win_img, (diamond_x, diamond_y), 4, pure_white, -1)

        # === כוכבים אדומים בצדדים ===
        star_positions = [
            (border_left - 100, (border_top + border_bottom) // 2),
            (border_right + 100, (border_top + border_bottom) // 2)
        ]

        for star_x, star_y in star_positions:
            star_size = 20
            # כוכב 8 קצוות
            for angle in range(0, 360, 45):
                end_x = star_x + int(star_size * np.cos(np.radians(angle)))
                end_y = star_y + int(star_size * np.sin(np.radians(angle)))
                thickness = 4 if angle % 90 == 0 else 2
                cv2.line(win_img, (star_x, star_y), (end_x, end_y), blood_red, thickness)

            # מרכז הכוכב
            cv2.circle(win_img, (star_x, star_y), 6, pure_white, -1)
            cv2.circle(win_img, (star_x, star_y), 3, blood_red, -1)

        # === טיפות דם דקורטיביות ===
        blood_drops = [
            (border_left + 50, border_bottom - 30),
            (border_right - 50, border_bottom - 30),
            (border_left + 100, border_top + 40),
            (border_right - 100, border_top + 40)
        ]

        for drop_x, drop_y in blood_drops:
            # טיפת דם
            cv2.circle(win_img, (drop_x, drop_y), 8, blood_red, -1)
            cv2.circle(win_img, (drop_x, drop_y), 8, pure_white, 2)
            # זנב הטיפה
            cv2.line(win_img, (drop_x, drop_y - 8), (drop_x - 3, drop_y - 20), blood_red, 3)

        # הצגת המסך
        self._img = win_img
        cv2.imshow("Chess", self._img)
        cv2.waitKey(3000)  # הצגה למשך 3 שניות

        # החזרת המסך למצב המקורי
        self._img = original_img

        # ניקוי הטבלאות
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