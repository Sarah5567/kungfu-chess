import pytest
from pathlib import Path
import json
from Board import Board
from Piece import Piece
from State import State
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from PieceFactory import PieceFactory
from Physics import IdlePhysics
from Graphics import Graphics

# ────────────────────────────── Fixtures ──────────────────────────────

@pytest.fixture
def board():
    return Board(64, 64, 1, 1, 8, 8, img=None)

@pytest.fixture
def physics_factory(board):
    return PhysicsFactory(board)

@pytest.fixture
def graphics(board):
    # גרפיקה קיימת – משתמשים בספרייטים האמיתיים של QW
    sprites_dir = Path("../../pieces/QW/states/jump/sprites")
    return Graphics(sprites_dir, board)

@pytest.fixture
def base_piece(board, graphics):
    moves = Moves(Path("../../pieces/QW/moves.txt"), (board.H_cells, board.W_cells))
    physics = IdlePhysics((0, 0), board)
    state = State(moves, graphics, physics)
    return Piece("QW", state)

@pytest.fixture
def piece_factory(board):
    # ─── ARRANGE: משתמשים ישירות בתיקיות האמיתיות של QW ─────────────
    pieces_root = Path("../../pieces")
    return PieceFactory(board, pieces_root)

# ────────────────────────────── Tests – Piece ─────────────────────────

def test_WhenCloneToCalled_ThenNewPieceCreatedWithCopiedGraphics(physics_factory, base_piece):
    # ─── ARRANGE ──────────────────────────────────────────────────────
    target_cell = (3, 4)

    # ─── ACT ──────────────────────────────────────────────────────────
    cloned = base_piece.clone_to(target_cell, physics_factory)

    # ─── ASSERT ───────────────────────────────────────────────────────
    assert isinstance(cloned, Piece)
    assert cloned is not base_piece
    assert cloned.get_id() == base_piece.get_id()
    assert cloned._state._physics.start_cell == target_cell
    assert cloned._state._graphics is not base_piece._state._graphics

def test_WhenCloneToCalled_ThenOriginalPieceUnchanged(physics_factory, base_piece):
    # ─── ARRANGE ──────────────────────────────────────────────────────
    original_cell = base_piece._state._physics.start_cell

    # ─── ACT ──────────────────────────────────────────────────────────
    _ = base_piece.clone_to((5, 5), physics_factory)

    # ─── ASSERT ───────────────────────────────────────────────────────
    assert base_piece._state._physics.start_cell == original_cell

# ────────────────────────────── Tests – PieceFactory ──────────────────

def test_WhenCreatePieceCalled_ThenTemplateReusedAndCloned(piece_factory):
    # ─── ARRANGE ──────────────────────────────────────────────────────
    cell1 = (2, 3)
    cell2 = (4, 4)

    # ─── ACT ──────────────────────────────────────────────────────────
    piece1 = piece_factory.create_piece("QW", cell1)
    piece2 = piece_factory.create_piece("QW", cell2)

    # ─── ASSERT ───────────────────────────────────────────────────────
    assert isinstance(piece1, Piece)
    assert isinstance(piece2, Piece)
    assert piece1 is not piece2
    assert piece1.get_id() == "QW"
    assert piece2.get_id() == "QW"
    assert piece1._state._physics.start_cell == cell1
    assert piece2._state._physics.start_cell == cell2
