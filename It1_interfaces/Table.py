import cv2
import numpy as np
from typing import List, Dict, Any


class Table:
    def __init__(self, headers: List[str], max_rows=15,
                 cell_size=(120, 40),
                 text_color=(0, 0, 0), bg_color=(255, 255, 255)):
        """
        :param headers: Column names
        :param max_rows: Maximum number of rows (excluding the header row)
        """
        self.headers = headers
        self.max_rows = max_rows
        self.cell_w, self.cell_h = cell_size
        self.text_color = text_color
        self.bg_color = bg_color

        # Empty data at start
        self.rows: List[List[str]] = []
        self._img = self._create_table_img()

    def update_data(self, rows: List[List[str]]):
        """Update new data (excluding headers)"""
        self.rows = rows[-self.max_rows:]  # Take the last max_rows
        self._img = self._create_table_img()

    def _create_table_img(self):
        total_rows = self.max_rows + 1  # Including the header row
        cols = len(self.headers)

        img = np.full((total_rows * self.cell_h, cols * self.cell_w, 3),
                      self.bg_color, dtype=np.uint8)

        # Draw headers
        for j, text in enumerate(self.headers):
            x = j * self.cell_w
            y = 0
            cv2.rectangle(img, (x, y), (x + self.cell_w, self.cell_h), (0, 0, 0), 1)
            cv2.putText(img, str(text), (x + 5, y + int(self.cell_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.text_color, 1)

        # Draw rows
        for i in range(self.max_rows):
            for j in range(len(self.headers)):
                x = j * self.cell_w
                y = (i + 1) * self.cell_h
                cv2.rectangle(img, (x, y), (x + self.cell_w, y + self.cell_h), (0, 0, 0), 1)
                text = self.rows[i][j] if i < len(self.rows) and j < len(self.rows[i]) else ""
                cv2.putText(img, str(text), (x + 5, y + int(self.cell_h * 0.7)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.text_color, 1)

        return img

    @staticmethod
    def log_to_table_data(log: List[Dict[str, Any]]) -> List[List[str]]:
        if not log:
            return []

        headers = list(log[0].keys())
        table_data = [headers]

        for entry in log:
            table_data.append([str(entry[key]) for key in headers])

        return table_data



    @property
    def img(self):
        return self._img
