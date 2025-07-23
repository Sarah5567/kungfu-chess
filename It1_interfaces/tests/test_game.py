import unittest
import pathlib
import numpy as np
from Board import Board
from Game import Game
from img import Img

class TestGame(unittest.TestCase):
    def setUp(self):
        img = Img()
        img.img = np.zeros((480, 480, 3), dtype=np.uint8)  # תמונה ריקה
        self.board = Board(
            cell_H_pix=60,
            cell_W_pix=60,
            cell_H_m=1,
            cell_W_m=1,
            W_cells=8,
            H_cells=8,
            img=img
        )
        self.pieces_root = pathlib.Path('.')
        self.placement_csv = pathlib.Path('It1_interfaces/board.csv')
        self.game = Game(self.board, self.pieces_root, self.placement_csv)

    def test_game_time_ms(self):
        ms = self.game.game_time_ms()
        self.assertIsInstance(ms, int)
        self.assertGreaterEqual(ms, 0)

    def test_clone_board(self):
        clone = self.game.clone_board()
        self.assertIs(clone, self.board)

    def test_get_path_cells(self):
        src = (0, 0)
        dst = (0, 3)
        path = self.game.get_path_cells(src, dst)
        self.assertEqual(path, [(0, 1), (0, 2), (0, 3)])
        src = (0, 0)
        dst = (3, 3)
        path = self.game.get_path_cells(src, dst)
        self.assertEqual(path, [(1, 1), (2, 2), (3, 3)])
        src = (0, 0)
        dst = (2, 3)
        path = self.game.get_path_cells(src, dst)
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()
