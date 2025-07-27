import time
import unittest
from unittest.mock import MagicMock, patch
import pathlib
from Game import Game
from Board import Board
from Screen import Screen
from PieceFactory import PieceFactory
from Command import Command
from Piece import Piece

class TestGame(unittest.TestCase):
    def setUp(self):
        self.screen = MagicMock(spec=Screen)
        self.board = MagicMock(spec=Board)
        self.board.H_cells = 8
        self.board.W_cells = 8
        self.board.cell_W_pix = 100
        self.board.cell_H_pix = 100
        self.board.is_valid_cell.return_value = True
        self.board.clone.return_value = self.board
        self.board.algebraic_to_cell = lambda a: (0, 0) if a == 'a1' else (1, 1)
        self.board.cell_to_algebraic = lambda cell: 'a1' if cell == (0, 0) else 'b2'

        self.pieces_root = pathlib.Path('.')
        self.placement_csv = pathlib.Path('../../board.csv')
        self.sounds_root = pathlib.Path('.')

        # mock PieceFactory
        patcher2 = patch('Game.PieceFactory')
        self.MockPieceFactory = patcher2.start()
        self.addCleanup(patcher2.stop)
        self.factory_instance = self.MockPieceFactory.return_value
        self.mock_piece = MagicMock(spec=Piece)
        self.mock_piece.get_id.return_value = 'PB1'
        self.factory_instance.create_piece.return_value = self.mock_piece

        self.game = Game(self.screen, self.board, self.pieces_root, self.placement_csv, self.sounds_root)

    def test_game_initialization_loads_pieces(self):
        self.assertIn('PB1', self.game.pieces)
        self.assertEqual(self.game.pos_to_piece[(0, 0)], self.mock_piece)

    def test_game_time_ms_returns_positive_int(self):
        ms = self.game.game_time_ms()
        self.assertIsInstance(ms, int)
        self.assertGreaterEqual(ms, 0)

    def test_add_command_and_process_move(self):
        self.game.user_input_queue.put(Command(
            timestamp=123,
            piece_id='PB1',
            type='move',
            params=['a1', 'b2']
        ))
        self.game.pos_to_piece[(0, 0)] = self.mock_piece
        self.mock_piece.get_id.return_value = 'PB1'
        self.mock_piece._state._current_command = None
        self.mock_piece.on_command = MagicMock()

        self.game._update_position_mapping = MagicMock()
        self.game._draw = MagicMock()
        self.game._is_win = MagicMock(side_effect=[False, True])

        self.game.run()

        self.mock_piece.on_command.assert_called()

    def test_keyboard_input_triggers_enter(self):
        with patch('keyboard.is_pressed') as mock_key:
            mock_key.side_effect = lambda k: k == 'enter'
            self.game._on_enter_pressed = MagicMock()
            self.game._running = False
            self.game.start_keyboard_thread()
            time.sleep(0.1)
            self.game._on_enter_pressed.assert_called()

if __name__ == '__main__':
    unittest.main()
