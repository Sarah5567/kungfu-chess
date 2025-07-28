from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from Board import Board
from Game import Game
from Screen import Screen
from Img import Img

@pytest.fixture
def mock_screen():
    screen = MagicMock(spec=Screen)
    screen.draw = MagicMock()
    screen.show = MagicMock()
    screen.reset = MagicMock()
    screen.update_left = MagicMock()
    screen.update_right = MagicMock()
    screen.announce_win = MagicMock()
    return screen

@pytest.fixture
def mock_board():
    board = MagicMock(spec=Board)
    board.img = MagicMock(spec=Img)
    board.H_cells = 8
    board.W_cells = 8
    board.cell_H_pix = 100
    board.cell_W_pix = 100
    board.clone.return_value = board
    board.algebraic_to_cell = MagicMock(return_value=(0,0))
    board.cell_to_algebraic = MagicMock(return_value="a1")
    board.is_valid_cell = MagicMock(return_value=True)
    return board

@pytest.fixture
def game(mock_screen, mock_board):
    base_path = Path(__file__).resolve().parent.parent
    pieces_root = base_path.parent / "PIECES"
    placement_csv = base_path / "board.csv"
    sounds_root = base_path.parent / "sounds"

    with patch('Game.PieceFactory'), \
         patch('Game.playsound'), \
         patch('Game.cv2'), \
         patch('Game.keyboard'):
        game = Game(mock_screen, mock_board, pieces_root, placement_csv, sounds_root)
        return game

def test_game_init(game, mock_screen, mock_board):
    assert game.screen == mock_screen
    assert game.board == mock_board
    assert game._running == True
    assert game._selection_mode == "source"
    assert game._selection_mode2 == "source"

def test_game_reset_selection(game):
    game._selected_source = (0,0)
    game._selection_mode = "dest"
    game._reset_selection()
    assert game._selection_mode == "source"
    assert game._selected_source == None

@patch('Game.cv2')
def test_game_announce_win(mock_cv2, game, mock_screen):
    # Mock a king piece
    king_piece = MagicMock()
    king_piece.get_id.return_value = "KB"
    game.pieces = {"KB": king_piece}

    game._announce_win()
    mock_screen.announce_win.assert_called_once_with("black")

def test_game_is_win_true(game):
    # Only one king left
    king_piece = MagicMock()
    king_piece.get_id.return_value = "KB"
    game.pieces = {"KB": king_piece}

    assert game._is_win() == True

def test_game_is_win_false(game):
    # Both kings present
    king1 = MagicMock()
    king2 = MagicMock()
    king1.get_id.return_value = "KB"
    king2.get_id.return_value = "KW"
    game.pieces = {"KB": king1, "KW": king2}

    assert game._is_win() == False

def test_game_cell_to_rect(game):
    cell = (1, 2)
    expected = (200, 100, 300, 200) # Based on 100px cell size
    assert game._cell_to_rect(cell) == expected

def test_handle_selection_invalid_piece(game):
    # Setup piece that doesn't belong to player
    piece = MagicMock()
    piece.get_id.return_value = "PW"  # White piece
    game.pos_to_piece = {(0,0): piece}

    # Try to select with black player (user 1)
    new_mode, new_source = game._handle_selection(
        user_id=1,
        selection_mode="source",
        selected_source=None,
        focus_cell=(0,0),
        reset_func=game._reset_selection
    )

    assert new_mode == "source"
    assert new_source == None

def test_handle_selection_valid_move(game):
    # Setup valid piece
    piece = MagicMock()
    piece.get_id.return_value = "PB"  # Black piece
    game.pos_to_piece = {(0,0): piece}

    # Select source
    new_mode, new_source = game._handle_selection(
        user_id=1,
        selection_mode="source",
        selected_source=None,
        focus_cell=(0,0),
        reset_func=game._reset_selection
    )

    assert new_mode == "dest"
    assert new_source == (0,0)
