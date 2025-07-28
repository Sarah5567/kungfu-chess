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

    def reset(self, display_duration: float = 3.0, win_name: str = "Screen"):

        reset_img = np.zeros((self._screen_h, self._screen_w, 3), dtype=np.uint8)

        # יצירת גרדיאנט רקע אלגנטי (שחור לאפור כהה)
        for y in range(self._screen_h):
            gradient_value = int(60 * (1 - y / self._screen_h))  # מ-60 ל-0
            reset_img[y, :] = [gradient_value, gradient_value, gradient_value]

        # הוספת תבנית דקורטיבית ברקע
        for y in range(0, self._screen_h, 40):
            for x in range(0, self._screen_w, 40):
                if (x // 40 + y // 40) % 2 == 0:
                    cv2.rectangle(reset_img, (x, y), (x + 40, y + 40), (25, 25, 25), -1)

        # הטקסט להצגה
        reset_text = "KUNG FU CHESS"

        # הגדרות הטקסט הראשי
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.8
        font_thickness = 5

        # צבעים מעוצבים בשחור-לבן
        main_text_color = (255, 255, 255)  # לבן טהור
        shadow_color = (0, 0, 0)  # שחור טהור
        glow_color = (200, 200, 200)  # אפור בהיר
        accent_color = (128, 128, 128)  # אפור בינוני

        # חישוב גודל הטקסט כדי למרכז אותו
        text_size = cv2.getTextSize(reset_text, font, font_scale, font_thickness)[0]
        text_x = (self._screen_w - text_size[0]) // 2
        text_y = (self._screen_h + text_size[1]) // 2

        # יצירת אפקט זוהר מתקדם (glow effect)
        for offset in range(12, 0, -2):
            glow_intensity = int(150 * (1 - offset / 12))
            glow_thickness = font_thickness + offset
            cv2.putText(reset_img, reset_text, (text_x, text_y),
                        font, font_scale, (glow_intensity, glow_intensity, glow_intensity), glow_thickness)

        # הוספת צללים מרובים לעומק
        shadow_offsets = [(6, 6), (4, 4), (2, 2)]
        shadow_intensities = [0, 40, 80]

        for (offset_x, offset_y), intensity in zip(shadow_offsets, shadow_intensities):
            cv2.putText(reset_img, reset_text,
                        (text_x + offset_x, text_y + offset_y),
                        font, font_scale, (intensity, intensity, intensity), font_thickness)

        # הוספת הטקסט הראשי עם מסגרת
        cv2.putText(reset_img, reset_text, (text_x, text_y),
                    font, font_scale, main_text_color, font_thickness)

        # הוספת מסגרת פנימית לטקסט
        cv2.putText(reset_img, reset_text, (text_x, text_y),
                    font, font_scale, shadow_color, 2)

        # הוספת קווים תחתונים מעוצבים
        underline_y = text_y + 25
        underline_start_x = text_x - 30
        underline_end_x = text_x + text_size[0] + 30

        # קו תחתון עבה
        cv2.line(reset_img, (underline_start_x, underline_y),
                 (underline_end_x, underline_y), main_text_color, 4)
        # קו תחתון דק מעליו
        cv2.line(reset_img, (underline_start_x, underline_y - 3),
                 (underline_end_x, underline_y - 3), accent_color, 2)
        # קו תחתון דק מתחתיו
        cv2.line(reset_img, (underline_start_x, underline_y + 3),
                 (underline_end_x, underline_y + 3), accent_color, 1)

        # הוספת מסגרת מעוצבת מתקדמת סביב הטקסט
        border_margin = 80
        border_top = text_y - text_size[1] - border_margin
        border_bottom = text_y + border_margin
        border_left = text_x - border_margin
        border_right = text_x + text_size[0] + border_margin

        # מסגרת חיצונית עבה
        cv2.rectangle(reset_img, (border_left, border_top),
                      (border_right, border_bottom), main_text_color, 3)

        # מסגרת אמצעית
        inner_margin_1 = 15
        cv2.rectangle(reset_img, (border_left + inner_margin_1, border_top + inner_margin_1),
                      (border_right - inner_margin_1, border_bottom - inner_margin_1),
                      accent_color, 2)

        # מסגרת פנימית דקה
        inner_margin_2 = 25
        cv2.rectangle(reset_img, (border_left + inner_margin_2, border_top + inner_margin_2),
                      (border_right - inner_margin_2, border_bottom - inner_margin_2),
                      glow_color, 1)

        # הוספת יהלומים דקורטיביים בפינות
        diamond_positions = [
            (border_left - 40, border_top - 40),
            (border_right + 40, border_top - 40),
            (border_left - 40, border_bottom + 40),
            (border_right + 40, border_bottom + 40)
        ]

        for diamond_x, diamond_y in diamond_positions:
            # יהלום מעוצב
            diamond_size = 20
            diamond_points = np.array([
                [diamond_x, diamond_y - diamond_size],  # עליון
                [diamond_x + diamond_size, diamond_y],  # ימין
                [diamond_x, diamond_y + diamond_size],  # תחתון
                [diamond_x - diamond_size, diamond_y]  # שמאל
            ], np.int32)

            # מילוי היהלום
            cv2.fillPoly(reset_img, [diamond_points], main_text_color)
            # מסגרת היהלום
            cv2.polylines(reset_img, [diamond_points], True, shadow_color, 2)
            # נקודה במרכז
            cv2.circle(reset_img, (diamond_x, diamond_y), 3, shadow_color, -1)

        # הוספת קישוטים בצדדים
        side_decorations_left = border_left - 60
        side_decorations_right = border_right + 60
        decoration_y_center = (border_top + border_bottom) // 2

        # קישוטים שמאליים
        for i in range(-2, 3):
            y_pos = decoration_y_center + (i * 30)
            cv2.circle(reset_img, (side_decorations_left, y_pos), 8, main_text_color, 2)
            cv2.circle(reset_img, (side_decorations_left, y_pos), 4, accent_color, -1)

        # קישוטים ימניים
        for i in range(-2, 3):
            y_pos = decoration_y_center + (i * 30)
            cv2.circle(reset_img, (side_decorations_right, y_pos), 8, main_text_color, 2)
            cv2.circle(reset_img, (side_decorations_right, y_pos), 4, accent_color, -1)

        # הוספת טקסט משני מעוצב
        subtitle = "GAME RESET"
        subtitle_font_scale = 1.0
        subtitle_thickness = 2
        subtitle_size = cv2.getTextSize(subtitle, font, subtitle_font_scale, subtitle_thickness)[0]
        subtitle_x = (self._screen_w - subtitle_size[0]) // 2
        subtitle_y = border_bottom + 60

        # צל לכותרת המשנה
        cv2.putText(reset_img, subtitle, (subtitle_x + 2, subtitle_y + 2),
                    font, subtitle_font_scale, shadow_color, subtitle_thickness)
        # הכותרת המשנה
        cv2.putText(reset_img, subtitle, (subtitle_x, subtitle_y),
                    font, subtitle_font_scale, glow_color, subtitle_thickness)

        # הוספת קו דקורטיבי מתחת לכותרת המשנה
        subtitle_line_y = subtitle_y + 15
        subtitle_line_start = subtitle_x - 20
        subtitle_line_end = subtitle_x + subtitle_size[0] + 20
        cv2.line(reset_img, (subtitle_line_start, subtitle_line_y),
                 (subtitle_line_end, subtitle_line_y), accent_color, 2)

        # הצגת המסך עם הטקסט המעוצב
        self._img = reset_img

        # ניקוי הטבלאות (איפוס הנתונים)
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
        cv2.imshow("Screen", self._img)
        cv2.waitKey(3000)  # הצגה למשך 3 שניות

        # החזרת המסך למצב המקורי
        self._img = original_img

        # ניקוי הטבלאות
        self.left_table.update_data([])
        self.right_table.update_data([])

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